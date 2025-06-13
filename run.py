#!/usr/bin/env python
# run.py
import typer
import uvicorn
from typing_extensions import Annotated

# 创建一个 Typer 应用实例
app = typer.Typer(add_completion=False)

@app.command()
def main(
    app_path: Annotated[str, typer.Argument(
        help="要启动的 FastAPI 应用路径，格式为 'module:variable'。"
    )] = "app.main:app",
    host: Annotated[str, typer.Option(
        "-h", "--host", help="要绑定的主机名或 IP 地址。"
    )] = "0.0.0.0",
    port: Annotated[int, typer.Option(
        "-p", "--port", help="要监听的端口号。"
    )] = 8000,
    reload: Annotated[bool, typer.Option(
        "--reload/--no-reload", help="启用或禁用热重载模式。"
    )] = True,
    log_level: Annotated[str, typer.Option(
        "--log-level", help="设置日志级别 (例如 'info', 'debug', 'warning')。"
    )] = "info",
    workers: Annotated[int, typer.Option(
        "-w", "--workers", help="要启动的 worker 进程数 (仅在 no-reload 模式下生效)。"
    )] = 1,
):
    """
    启动一个 FastAPI 应用服务器。🚀
    """
    print(f"🚀 开始启动应用: {app_path}")
    print(f"   - 访问地址: http://{host if host != '0.0.0.0' else '127.0.0.1'}:{port}")
    print(f"   - 热重载: {'✅' if reload else '❌'}")
    print(f"   - 工作进程数: {workers if not reload else '1 (热重载模式禁用多进程)'}")
    print(f"   - 日志级别: {log_level}")

    uvicorn.run(
        app_path,
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        workers=workers if not reload else 1, # 热重载模式下 workers 必须为 1
    )

if __name__ == "__main__":
    app()