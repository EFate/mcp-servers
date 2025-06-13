# app/schemas/weather.py
from pydantic import BaseModel, Field
from typing import List

# --- Open-Meteo API 响应的数据模型 ---

class CurrentWeather(BaseModel):
    time: str = Field(..., description="ISO 8601 格式的时间戳")
    temperature_2m: float = Field(..., alias="temperature_2m", description="离地2米的气温")
    wind_speed_10m: float = Field(..., alias="wind_speed_10m", description="离地10米的Š的风速")

class HourlyUnits(BaseModel):
    time: str
    temperature_2m: str
    relative_humidity_2m: str
    wind_speed_10m: str

class HourlyData(BaseModel):
    time: List[str]
    temperature_2m: List[float]
    relative_humidity_2m: List[int]
    wind_speed_10m: List[float]

# --- 定义最终API输出的完整数据结构 ---
class WeatherForecastOutput(BaseModel):
    latitude: float
    longitude: float
    generationtime_ms: float
    utc_offset_seconds: int
    timezone: str
    timezone_abbreviation: str
    elevation: float
    current: CurrentWeather = Field(..., description="当前天气状况")
    hourly_units: HourlyUnits
    hourly: HourlyData