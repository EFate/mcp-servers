# app/main.py
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP

# --- 导入我们的新模块 ---
from app.handlers.exception import register_exception_handlers
from app.core.config import settings
from app.core.setup import setup_logging
from app.routers import all_routers

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理器 (Lifespan Manager)。
    """
    print("MCP Servers 启动中...")
    # 配置日志系统
    setup_logging()
    print(f"--- {settings.PROJECT_NAME} (v{settings.PROJECT_VERSION}) 开始启动 ---")
    yield
    print("MCP Servers 关闭中...")


def create_app() -> FastAPI:
    """
    创建并配置 FastAPI 应用实例的工厂函数。
    """
    app = FastAPI(
        lifespan=lifespan,
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description=settings.DESCRIPTION,
        docs_url=None,  # 禁用默认的 /docs，我们将使用自定义路径
        redoc_url=None,
    )

    # --- 注册全局异常处理器 ---
    # 将异常处理逻辑委托给专门的模块，使主文件更清晰
    register_exception_handlers(app)

    # 注册中间件
    # 此处可添加 CORS、认证等中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 在生产环境中应收紧
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    # 3. 统一注册所有路由并动态挂载模块化 MCP 服务
    print("--- 正在注册路由和模块化 MCP 服务 ---")
    for router in all_routers:
        # 首先，将路由包含到主应用中，使其 API 可用
        app.include_router(router)
        print(f" ✓ API 路由已注册: {router.prefix} (Tags: {', '.join(router.tags)})")

        # 接着，检查此路由是否需要专属的 MCP 服务 (根据我们在 config.py 中定义的标签)
        if settings.MCP_INCLUDE_TAG in router.tags:
            # 找到代表模块的唯一标签 (例如 "Time", "Weather")
            module_tag = next((tag for tag in router.tags if tag != settings.MCP_INCLUDE_TAG), None)
            if not module_tag:
                continue  # 如果找不到唯一模块标签，则跳过

            # 为此模块动态创建一个专属的 FastApiMCP 实例
            # 注意：include_tags 使用模块的唯一标签来确保只包含此模块下的工具
            module_mcp = FastApiMCP(
                app,  # 依然使用主 app 来获取完整的 OpenAPI schema
                name=f"{module_tag} 工具集",
                description=f"专为 {module_tag} 模块提供的 MCP 工具。",
                include_tags=[module_tag]
            )

            # 使用 app.mount() 将这个专属 MCP 服务挂载到模块的子路径下
            mcp_path = f"{router.prefix}/mcp"
            app.mount(mcp_path, module_mcp, name=f"mcp_{module_tag.lower()}")
            print(f" ★ MCP 服务已挂载: {mcp_path}")

    # --- 挂载静态文件 ---
    STATIC_FILES_DIR = Path(__file__).parent / "static"
    if STATIC_FILES_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=STATIC_FILES_DIR), name="static")

    # --- 自定义文档路由 ---
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        """提供自定义的 Swagger UI 界面。"""
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - API 文档",
            swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui/swagger-ui.css",
        )

    @app.get("/", tags=["System"], include_in_schema=False)
    async def read_root():
        """根路径，提供欢迎信息和文档链接。"""
        return {"message": f"欢迎使用 MCP Servers!", "docs_url": "/docs"}

    return app


# 创建 FastAPI 应用实例，供 uvicorn 在 run.py 中通过 "app.main:app" 引用和启动。
app = create_app()