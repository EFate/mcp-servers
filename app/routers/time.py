from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List
import pytz
from dateutil import parser as dateutil_parser

from app.core.config import settings
from app.schemas.response import ApiResponse
from app.schemas.time import (
    FormatTimeInput, ConvertTimeInput, ElapsedTimeInput, ParseTimestampInput,
    TimeData, FormattedTimeData, ConvertedTimeData, ElapsedTimeData, TimezoneListData
)

router = APIRouter(
    prefix="/time",
    tags=["Time", settings.MCP_INCLUDE_TAG]
)

@router.get("/current_utc", operation_id="get_current_utc_time", response_model=ApiResponse[TimeData])
async def get_current_utc_time():
    """获取并以 ISO 8601 格式返回当前的 UTC 时间。"""
    utc_now = datetime.now(timezone.utc)
    return ApiResponse(data=TimeData(time=utc_now.isoformat()))

@router.get("/current_local", operation_id="get_current_local_time", response_model=ApiResponse[TimeData])
async def get_current_local_time():
    """获取服务器的当前本地时间，并以 ISO 8601 格式返回。"""
    return ApiResponse(data=TimeData(time=datetime.now().astimezone().isoformat()))

@router.post("/format", operation_id="format_time", response_model=ApiResponse[FormattedTimeData])
async def format_time(data: FormatTimeInput):
    """根据指定的时区和格式，格式化当前时间。"""
    try:
        tz = pytz.timezone(data.timezone)
        now_in_tz = datetime.now(tz)
        formatted_time = now_in_tz.strftime(data.format)
        return ApiResponse(data=FormattedTimeData(formatted_time=formatted_time))
    except pytz.UnknownTimeZoneError:
        raise HTTPException(status_code=400, detail=f"Invalid timezone: {data.timezone}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid format string: {e}")

@router.post("/convert", operation_id="convert_timezone", response_model=ApiResponse[ConvertedTimeData])
async def convert_timezone(data: ConvertTimeInput):
    """将一个时间戳从一个时区转换到另一个时区。"""
    try:
        from_zone = pytz.timezone(data.from_tz)
        to_zone = pytz.timezone(data.to_tz)
        dt = dateutil_parser.parse(data.timestamp)
        if dt.tzinfo is None:
            dt = from_zone.localize(dt)
        converted_dt = dt.astimezone(to_zone)
        return ApiResponse(data=ConvertedTimeData(converted_time=converted_dt.isoformat()))
    except pytz.UnknownTimeZoneError:
        raise HTTPException(status_code=400, detail=f"Invalid timezone provided.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse or convert timestamp: {e}")

@router.post("/elapsed", operation_id="calculate_elapsed_time", response_model=ApiResponse[ElapsedTimeData])
async def calculate_elapsed_time(data: ElapsedTimeInput):
    """计算两个时间戳之间经过的时间。"""
    try:
        start_dt = dateutil_parser.parse(data.start)
        end_dt = dateutil_parser.parse(data.end)
        if start_dt.tzinfo is None: start_dt = start_dt.replace(tzinfo=timezone.utc)
        if end_dt.tzinfo is None: end_dt = end_dt.replace(tzinfo=timezone.utc)
        delta = end_dt - start_dt
        seconds = delta.total_seconds()
        result_map = {"seconds": seconds, "minutes": seconds / 60, "hours": seconds / 3600, "days": seconds / 86400}
        return ApiResponse(data=ElapsedTimeData(elapsed=result_map[data.units], unit=data.units))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse timestamps: {e}")

@router.post("/parse", operation_id="parse_timestamp", response_model=ApiResponse[TimeData])
async def parse_timestamp(data: ParseTimestampInput):
    """将一个灵活格式的时间字符串解析为标准的 UTC ISO 格式。"""
    try:
        assumed_tz = pytz.timezone(data.timezone)
        dt = dateutil_parser.parse(data.timestamp)
        if dt.tzinfo is None:
            dt = assumed_tz.localize(dt)
        dt_utc = dt.astimezone(pytz.utc)
        return ApiResponse(data=TimeData(time=dt_utc.isoformat()))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse timestamp: {e}")

@router.get("/list_timezones", operation_id="list_all_timezones", response_model=ApiResponse[TimezoneListData])
async def list_all_timezones():
    """返回一个包含所有可用 IANA 时区名称的列表。"""
    return ApiResponse(data=TimezoneListData(timezones=pytz.all_timezones))