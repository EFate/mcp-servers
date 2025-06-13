from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置模型，可自动从环境变量读取"""
    PROJECT_NAME: str = "模块化 MCP & API 服务器"
    PROJECT_VERSION: str = "1.0.0"
    DESCRIPTION: str = "一个展示最优美实践的、集成了多个模块的 FastAPI 服务器。"

    # 使用统一的标签来识别所有希望暴露给 MCP 的工具模块
    MCP_INCLUDE_TAG: str = "MCP_ENABLED"

    class Config:
        case_sensitive = True

# 创建一个全局可用的配置实例
settings = Settings()