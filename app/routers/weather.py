# app/routers/weather.py
import requests
import reverse_geocoder as rg
from fastapi import APIRouter, HTTPException, Query

from app.core.config import settings
from app.schemas.response import ApiResponse
from app.schemas import weather as weather_schemas

# 这是自动发现的关键：创建一个 APIRouter 实例
# - prefix: 定义此模块下所有 API 的路径前缀
# - tags: 用于 API 文档分组和 MCP 服务命名
router = APIRouter(
    prefix="/weather",
    tags=[settings.MCP_INCLUDE_TAG, "Weather"]
)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
# 官方使用华氏度的国家代码
FAHRENHEIT_COUNTRIES = {"US", "LR", "MM"}  # 美国, 利比里亚, 缅甸


@router.get(
    "/forecast",
    response_model=ApiResponse[weather_schemas.WeatherForecastOutput],
    summary="获取当前天气和预报",
    operation_id="get_weather_forecast"  # <--- 为 MCP 工具提供清晰的名称
)
async def get_weather_forecast(
        latitude: float = Query(..., description="目标位置的纬度 (例如, 34.05)"),
        longitude: float = Query(..., description="目标位置的经度 (例如, -118.24)")
):
    """
    根据指定的经纬度，使用 Open-Meteo API 获取当前天气和小时级预报。
    温度单位（摄氏度/华氏度）会基于地理位置自动判断。
    """
    # 根据地理位置自动判断温度单位
    try:
        geo_results = rg.search((latitude, longitude), mode=1)
        country_code = geo_results[0]['cc'] if geo_results else None
        temperature_unit = "fahrenheit" if country_code in FAHRENHEIT_COUNTRIES else "celsius"
    except Exception:
        # 如果地理反编码失败，默认使用摄氏度
        temperature_unit = "celsius"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,wind_speed_10m",
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "timezone": "auto",
        "temperature_unit": temperature_unit
    }

    try:
        response = requests.get(OPEN_METEO_URL, params=params)
        response.raise_for_status()  # 如果状态码是 4xx 或 5xx，则抛出异常
        data = response.json()

        if "current" not in data or "hourly" not in data:
            raise HTTPException(status_code=500, detail="从 Open-Meteo API 收到了意外的响应格式")

        # 将获取的数据包装在统一的 ApiResponse 模型中返回
        # Pydantic 会自动验证 data 是否符合 WeatherForecastOutput 的结构
        return ApiResponse(data=data)

    except requests.exceptions.RequestException as e:
        # 使用 HTTPException，会被全局异常处理器捕获并格式化
        raise HTTPException(status_code=503, detail=f"连接 Open-Meteo API 时出错: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发生内部错误: {e}")