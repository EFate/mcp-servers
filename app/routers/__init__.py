# app/routers/__init__.py
from . import time
from . import weather

# 包含所有 API路由 和 prefix 的元组
api_routers = (
    (time.router, "/time"),
    (weather.router, "/weather"),
)
