# app/routers/weather.py
import requests
import reverse_geocoder as rg
from fastapi import APIRouter, HTTPException, Query

from app.core.config import settings
from app.schemas import weather as weather_schemas

router = APIRouter(
    prefix="/weather",
    tags=[settings.MCP_INCLUDE_TAG, "Weather"]
)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
FAHRENHEIT_COUNTRIES = {"US", "LR", "MM"}

@router.get(
    "/forecast",
    # --- 优化点: 移除 ApiResponse, 直接返回核心数据模型 ---
    response_model=weather_schemas.WeatherForecastOutput,
    summary="获取指定地理位置的当前天气和未来预报",
    operation_id="get_weather_forecast"
)
async def get_weather_forecast(
        latitude: float = Query(..., description="目标位置的纬度", examples=[34.0522]),
        longitude: float = Query(..., description="目标位置的经度", examples=[-118.2437])
):
    """
    当用户询问特定地点（由经纬度指定）的天气状况时，使用此工具。
    它能提供实时的气温、风速以及未来几小时的预报。
    温度单位会根据国家（美国、利比里亚、缅甸使用华氏度，其他使用摄氏度）自动选择。
    """
    try:
        geo_results = rg.search((latitude, longitude), mode=1)
        country_code = geo_results[0]['cc'] if geo_results else None
        temperature_unit = "fahrenheit" if country_code in FAHRENHEIT_COUNTRIES else "celsius"
    except Exception:
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
        response.raise_for_status()
        data = response.json()

        if "current" not in data or "hourly" not in data:
            raise HTTPException(status_code=500, detail="从 Open-Meteo API 收到了意外的响应格式")

        return data

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"连接 Open-Meteo API 时出错: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发生内部错误: {e}")