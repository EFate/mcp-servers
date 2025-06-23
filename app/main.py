# app/main.py
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, APIRouter  # 1. 导入 APIRouter
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi  # 2. 导入 get_openapi
from fastapi.responses import JSONResponse  # 3. 导入 JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP

from app.handlers.exception import register_exception_handlers
from app.core.config import settings
from app.core.setup import setup_logging
from app.routers import api_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理器"""
    setup_logging()
    print(f"--- {settings.PROJECT_NAME} (v{settings.PROJECT_VERSION}) 开始启动 ---")
    yield
    print("--- 服务关闭 ---")


# +++ 新增辅助函数 +++
def create_router_docs_endpoints(router: APIRouter, prefix: str, tags: list[str]):
    """
    为单个路由器动态创建其独立的 openapi.json 和 docs 页面。

    Args:
        router (APIRouter): 路由器实例。
        prefix (str): 路由器的前缀。
        tags (list[str]): 路由器的标签，用于文档标题。

    Returns:
        tuple: 包含 (openapi_handler, swagger_ui_handler) 的元组。
    """

    # 闭包：为当前路由生成专属的 openapi.json
    async def get_router_openapi_schema():
        openapi_schema = get_openapi(
            title=f"{settings.PROJECT_NAME} - {tags[0] if tags else prefix.strip('/').capitalize()} API",
            version=settings.PROJECT_VERSION,
            description=f"这是为 {prefix} 模块生成的专属API文档",
            routes=router.routes,
        )
        # 关键: 指定服务器地址为该路由的前缀，确保 "Try it out" 功能可用
        openapi_schema["servers"] = [{"url": prefix}]
        return JSONResponse(openapi_schema)

    # 闭包：为当前路由生成专属的 /docs 页面
    async def get_router_swagger_ui():
        return get_swagger_ui_html(
            openapi_url=f"{prefix}/openapi.json",  # 指向该路由专属的 openapi.json
            title=f"{settings.PROJECT_NAME} - {tags[0] if tags else prefix.strip('/').capitalize()} Docs",
            swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui/swagger-ui.css",
        )

    return get_router_openapi_schema, get_router_swagger_ui


# +++ 结束新增 +++


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例"""
    app = FastAPI(
        lifespan=lifespan,
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description=settings.DESCRIPTION,
        docs_url=None,  # 禁用全局 /docs
        redoc_url=None,  # 禁用全局 /redoc
    )

    # 1. 注册全局异常处理器
    register_exception_handlers(app)

    # 2. 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    mcp = FastApiMCP(app)

    # 3. 注册API路由、MCP 和 独立的文档
    for api, prefix in api_routers:
        # 首先，正常包含API路由，使其生效
        app.include_router(api)

        # 注册并挂载 MCP 服务 (您的原始逻辑)
        mcp.name = f"{str(api.tags[0]).capitalize()} Tools"
        mcp.description = f"通过MCP协议暴露的 {prefix} 模块下的工具集。"
        mcp.include_tags = api.tags,
        mcp.describe_all_responses = True,
        mcp.describe_full_response_schema = True
        mcp.mount(router=app, mount_path=f"{prefix}/mcp/sse")

        # +++ 为每个路由动态添加 /docs 和 /openapi.json +++
        openapi_handler, swagger_ui_handler = create_router_docs_endpoints(
            router=api,
            prefix=prefix,
            tags=api.tags
        )

        # 添加专属的 openapi.json 路由
        app.add_api_route(
            path=f"{prefix}/openapi.json",
            endpoint=openapi_handler,
            include_in_schema=False  # 不在任何文档中显示这个辅助路由
        )

        # 添加专属的 /docs 路由
        app.add_api_route(
            path=f"{prefix}/docs",
            endpoint=swagger_ui_handler,
            include_in_schema=False  # 不在任何文档中显示这个辅助路由
        )
        # +++ 结束添加 +++

    # 5. 挂载静态文件 (用于自定义Swagger UI)
    STATIC_FILES_DIR = Path(__file__).parent / "static"
    if STATIC_FILES_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=STATIC_FILES_DIR), name="static")

    # 6. 自定义Swagger文档路径 (此部分可以删除或保留作为全局文档入口)
    # 由于我们为每个路由创建了独立的文档，这个全局的 /docs 可能不再需要
    # 如果想保留一个能看所有API的全局文档，可以取消下面的注释
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - 全局API文档",
            swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui/swagger-ui.css",
        )

    # 7. 根路径
    @app.get("/", tags=["System"], include_in_schema=False)
    async def read_root():
        # 在根路径返回所有可用文档的链接，方便访问
        doc_urls = {f"Docs for '{prefix.strip('/')}' module": f"{prefix}/docs" for _, prefix in api_routers}
        return {
            "message": f"欢迎使用 {settings.PROJECT_NAME}!",
            "available_docs": doc_urls
        }

    return app


app = create_app()