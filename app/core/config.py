# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """应用配置模型，可自动从环境变量或 .env 文件读取"""
    PROJECT_NAME: str = "模块化 MCP & API 服务器"
    PROJECT_VERSION: str = "1.0.0"
    DESCRIPTION: str = "一个支持动态挂载模块化MCP服务的FastAPI应用"

    # 使用统一的标签来识别所有希望暴露给 MCP 的工具模块
    MCP_INCLUDE_TAG: str = "MCP_TOOLS"

    # model_config 告诉 Pydantic 如何加载配置
    model_config = SettingsConfigDict(
        env_file='.env',              # 指定要加载的 .env 文件
        env_file_encoding='utf-8',    # 指定编码
        case_sensitive=True           # 保持大小写敏感
    )

# 创建一个全局可用的配置实例
settings = Settings()