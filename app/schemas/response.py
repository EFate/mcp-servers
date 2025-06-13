from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

# 使用 TypeVar 创建一个泛型类型 T
T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """
    一个统一的、支持泛型的 API 响应模型。

    Attributes:
        code (int): 状态码，遵循 HTTP 状态码规范。
        msg (str): 响应消息，可以是 "success" 或具体的错误信息。
        data (Optional[T]): 实际的响应数据，其类型是泛型的，可以是任何 Pydantic 模型、字典、列表等。
                             对于不需要返回数据的操作（如删除），此字段可以为 null。
    """
    code: int = Field(200, description="状态码")
    msg: str = Field("success", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")

    class Config:
        # Pydantic v2 and later uses model_config
        model_config = {
            "json_schema_extra": {
                "examples": [
                    {
                        "code": 200,
                        "msg": "success",
                        "data": {"item_id": 1, "name": "example item"}
                    },
                    {
                        "code": 404,
                        "msg": "资源未找到",
                        "data": None
                    }
                ]
            }
        }