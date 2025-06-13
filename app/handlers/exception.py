import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from app.schemas.response import ApiResponse

# 获取一个 logger 实例
logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    全局HTTPException异常处理器。
    捕获业务逻辑中主动抛出的 HTTPException，并将其格式化为统一的 ApiResponse 格式。
    """
    response_model = ApiResponse(code=exc.status_code, msg=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=response_model.model_dump(exclude_none=True) # exclude_none=True 可以让 data 字段为 None 时不显示
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    全局通用Exception异常处理器。
    捕获所有未被处理的异常，防止敏感信息泄露，并返回一个标准的服务器内部错误响应。
    """
    logger.exception(f"在处理请求 {request.url} 时发生未处理的异常: {exc}", exc_info=exc)
    
    response_model = ApiResponse(
        code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
        msg="服务器内部错误，请联系管理员。"
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_model.model_dump(exclude_none=True)
    )

def register_exception_handlers(app: FastAPI):
    """
    将异常处理器注册到 FastAPI 应用实例。
    """
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)