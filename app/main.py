# app/main.py
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP  # 导入 MCP 支持

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


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例"""
    app = FastAPI(
        lifespan=lifespan,
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description=settings.DESCRIPTION,
        docs_url=None,
        redoc_url=None,
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

    # 3. 注册API路由 和 MCP
    for api, prefix in api_routers:
        app.include_router(api)

        # 注册并挂载 MCP 服务
        # mcp = FastApiMCP(
        #     app,
        #     name=f"{str(api.tags[0]).capitalize()} Tools",
        #     description=f"通过MCP协议暴露的 {prefix} 模块下的工具集。",
        #     # 使用该路由自身的标签来发现工具
        #     include_tags=api.tags,
        #     # 在工具描述中包含所有可能的响应模式，增强LLM的理解能力
        #     describe_all_responses=True,
        #     describe_full_response_schema=True
        # )
        mcp.name = f"{str(api.tags[0]).capitalize()} Tools"
        mcp.description = f"通过MCP协议暴露的 {prefix} 模块下的工具集。",
        mcp.include_tags=api.tags,
        mcp.describe_all_responses=True,
        mcp.describe_full_response_schema=True

        mcp.mount(router=app, mount_path=f"{prefix}/mcp/sse")

    # 5. 挂载静态文件 (用于自定义Swagger UI)
    STATIC_FILES_DIR = Path(__file__).parent / "static"
    if STATIC_FILES_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=STATIC_FILES_DIR), name="static")

    # 6. 自定义Swagger文档路径
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - API 文档",
            swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui/swagger-ui.css",
        )

    # 7. 根路径
    @app.get("/", tags=["System"], include_in_schema=False)
    async def read_root():
        return {
            "message": f"欢迎使用 {settings.PROJECT_NAME}!",
            "docs_url": "/docs",
        }

    return app


app = create_app()

