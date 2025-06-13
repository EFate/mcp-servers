# app/main.py
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

# --- 导入我们的新模块 ---
from app.handlers.exception import register_exception_handlers
from app.router.time import router as time_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理器 (Lifespan Manager)。
    """
    # 在这里可以添加应用启动时需要执行的代码，例如：
    # - 初始化数据库连接池
    # - 加载机器学习模型
    # - 连接到消息队列
    print("MCP Servers 启动中...")
    yield
    # 在这里可以添加应用关闭时需要执行的代码，例如：
    # - 关闭数据库连接
    # - 清理临时文件
    print("MCP Servers 关闭中...")


def create_app() -> FastAPI:
    """
    创建并配置 FastAPI 应用实例的工厂函数。
    """
    app = FastAPI(
        lifespan=lifespan,
        title="MCP Servers",
        description="MCP 服务器集合",
        version="1.0.0",
        docs_url=None,  # 禁用默认的 /docs，我们将使用自定义路径
        redoc_url=None,
    )

    # --- 注册全局异常处理器 ---
    # 将异常处理逻辑委托给专门的模块，使主文件更清晰
    register_exception_handlers(app)

    # --- 挂载路由和静态文件 ---
    app.include_router(time_router)

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
        # 也可以使用我们统一的 ApiResponse 模型返回成功响应
        # from app.schemas.response import ApiResponse
        # return ApiResponse(data={"message": f"欢迎使用 MCP Servers!", "docs_url": "/docs"})
        return {"message": f"欢迎使用 MCP Servers!", "docs_url": "/docs"}

    return app


# 创建 FastAPI 应用实例，供 uvicorn 在 run.py 中通过 "app.main:app" 引用和启动。
app = create_app()