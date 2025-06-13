# app/routers/time.py
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import pytz
from dateutil import parser as dateutil_parser

from app.core.config import settings
from app.schemas.response import ApiResponse
from app.schemas import time as time_schemas

router = APIRouter(
    prefix="/time",
    # 使用 config 中定义的 MCP 标签，同时可以添加其他描述性标签
    tags=[settings.MCP_INCLUDE_TAG, "Time"]
)

@router.get(
    "/current",
    response_model=ApiResponse[time_schemas.CurrentTimeData],
    summary="获取当前 UTC 和本地时间",
    operation_id="get_current_time"  # <--- 暴露为 MCP 工具
)
async def get_current_time():
    """获取并以 ISO 8601 格式返回当前的 UTC 时间和服务器本地时间。"""
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    local_now = datetime.now().isoformat()
    return ApiResponse(data=time_schemas.CurrentTimeData(utc_time=utc_now, local_time=local_now))

@router.post(
    "/format",
    response_model=ApiResponse[time_schemas.FormattedTimeData],
    summary="格式化当前时间",
    operation_id="format_current_time"  # <--- 暴露为 MCP 工具
)
async def format_current_time(data: time_schemas.FormatTimeInput):
    """根据指定的时区和格式，格式化当前时间。"""
    try:
        tz = pytz.timezone(data.timezone)
        now_in_tz = datetime.now(tz)
        formatted_time = now_in_tz.strftime(data.format)
        return ApiResponse(data=time_schemas.FormattedTimeData(formatted_time=formatted_time))
    except pytz.UnknownTimeZoneError:
        raise HTTPException(status_code=400, detail=f"无效的时区: {data.timezone}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"无效的格式化字符串: {e}")

@router.post(
    "/convert",
    response_model=ApiResponse[time_schemas.ConvertedTimeData],
    summary="时区转换",
    operation_id="convert_timezone"  # <--- 暴露为 MCP 工具
)
async def convert_timezone(data: time_schemas.ConvertTimeInput):
    """将一个时间戳从一个时区转换到另一个时区。"""
    try:
        from_zone = pytz.timezone(data.from_tz)
        to_zone = pytz.timezone(data.to_tz)
    except pytz.UnknownTimeZoneError as e:
        raise HTTPException(status_code=400, detail=f"无效的时区: {e}")

    try:
        dt = dateutil_parser.parse(data.timestamp)
        if dt.tzinfo is None:
            dt = from_zone.localize(dt)
        else:
            dt = dt.astimezone(from_zone)
        converted = dt.astimezone(to_zone)
        return ApiResponse(data=time_schemas.ConvertedTimeData(converted_time=converted.isoformat()))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"无效的时间戳: {e}")

@router.post(
    "/elapsed",
    response_model=ApiResponse[time_schemas.ElapsedTimeData],
    summary="计算时间差",
    operation_id="calculate_elapsed_time"  # <--- 暴露为 MCP 工具
)
async def calculate_elapsed_time(data: time_schemas.ElapsedTimeInput):
    """计算两个时间戳之间的时间差，并以指定单位返回。"""
    try:
        start_dt = dateutil_parser.parse(data.start)
        end_dt = dateutil_parser.parse(data.end)
        delta = end_dt - start_dt
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"无效的时间戳: {e}")

    seconds = delta.total_seconds()
    result_map = {
        "seconds": seconds,
        "minutes": seconds / 60,
        "hours": seconds / 3600,
        "days": seconds / 86400,
    }
    return ApiResponse(data=time_schemas.ElapsedTimeData(elapsed=result_map[data.units], unit=data.units))

@router.post(
    "/parse",
    response_model=ApiResponse[time_schemas.ParsedTimeData],
    summary="解析时间字符串",
    operation_id="parse_timestamp_to_utc"  # <--- 暴露为 MCP 工具
)
async def parse_timestamp_to_utc(data: time_schemas.ParseTimestampInput):
    """解析一个灵活格式的时间字符串，并返回标准化的 UTC ISO 时间。"""
    try:
        tz = pytz.timezone(data.timezone)
        dt = dateutil_parser.parse(data.timestamp)
        if dt.tzinfo is None:
            dt = tz.localize(dt)
        dt_utc = dt.astimezone(pytz.utc)
        return ApiResponse(data=time_schemas.ParsedTimeData(utc_time=dt_utc.isoformat()))
    except pytz.UnknownTimeZoneError as e:
        raise HTTPException(status_code=400, detail=f"无效的时区: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"无法解析时间字符串: {e}")


@router.get(
    "/list_timezones",
    response_model=ApiResponse[time_schemas.TimezoneListData],
    summary="获取所有可用时区",
    operation_id="list_all_timezones"  # <--- 暴露为 MCP 工具
)
async def list_all_timezones():
    """返回一个包含所有可用 IANA 时区名称的列表。"""
    return ApiResponse(data=time_schemas.TimezoneListData(timezones=pytz.all_timezones))