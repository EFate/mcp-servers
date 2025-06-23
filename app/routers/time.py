# app/routers/time.py
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import pytz
from dateutil import parser as dateutil_parser

from app.core.config import settings
from app.schemas import time as time_schemas

router = APIRouter(
    prefix="/time",
    tags=[settings.MCP_INCLUDE_TAG, "Time"]
)

@router.get(
    "/current",
    response_model=time_schemas.CurrentTimeData,
    summary="获取当前的 UTC 和服务器本地时间",
    operation_id="get_current_time"
)
async def get_current_time():
    """
    当用户询问“现在几点了？”或“UTC时间是多少？”时使用。
    此工具不接受任何参数，返回当前的 UTC 时间和服务器所在地的本地时间。
    """
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    local_now = datetime.now().astimezone().isoformat()  # 使用 astimezone() 来确保包含时区信息
    return time_schemas.CurrentTimeData(utc_time=utc_now, local_time=local_now)


@router.post(
    "/format",
    response_model=time_schemas.FormattedTimeData,
    summary="按指定格式和时区格式化当前时间",
    operation_id="format_current_time"
)
async def format_current_time(data: time_schemas.FormatTimeInput):
    """
    当用户需要以特定格式显示当前时间时使用。
    例如：“用'年-月-日'的格式告诉我纽约现在的时间”或“现在是星期几？”。
    """
    try:
        tz = pytz.timezone(data.timezone)
        now_in_tz = datetime.now(tz)
        formatted_time = now_in_tz.strftime(data.format)
        return time_schemas.FormattedTimeData(formatted_time=formatted_time)
    except pytz.UnknownTimeZoneError:
        raise HTTPException(status_code=400, detail=f"无效的时区: {data.timezone}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"无效的格式化字符串 '{data.format}': {e}")


@router.post(
    "/convert",
    response_model=time_schemas.ConvertedTimeData,
    summary="在不同时区之间转换时间",
    operation_id="convert_timezone"
)
async def convert_timezone(data: time_schemas.ConvertTimeInput):
    """
    当用户想知道一个特定时间在另一个时区是几点时使用。
    例如：“北京时间晚上8点，是旧金山的几点？”
    """
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
            # 如果提供了时区，先转换为正确的源时区
            dt = dt.astimezone(from_zone)
        converted = dt.astimezone(to_zone)
        return time_schemas.ConvertedTimeData(converted_time=converted.isoformat())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"无效的时间戳格式 '{data.timestamp}': {e}")


@router.post(
    "/elapsed",
    response_model=time_schemas.ElapsedTimeData,
    summary="计算两个时间点之间的时间差",
    operation_id="calculate_elapsed_time"
)
async def calculate_elapsed_time(data: time_schemas.ElapsedTimeInput):
    """
    当用户想要计算两个时间点之间相隔了多久时使用。
    例如：“从2023年1月1日到今天过去了多少天？”
    """
    try:
        start_dt = dateutil_parser.parse(data.start)
        end_dt = dateutil_parser.parse(data.end)
        # 确保时间戳有时区信息以进行准确计算
        if start_dt.tzinfo is None:
            start_dt = pytz.utc.localize(start_dt)
        if end_dt.tzinfo is None:
            end_dt = pytz.utc.localize(end_dt)

        delta = end_dt - start_dt
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"无效的时间戳: {e}")

    seconds = delta.total_seconds()
    if seconds < 0:
        raise HTTPException(status_code=400, detail="结束时间不能早于开始时间")

    result_map = {
        "seconds": seconds,
        "minutes": seconds / 60,
        "hours": seconds / 3600,
        "days": seconds / 86400,
    }
    return time_schemas.ElapsedTimeData(elapsed=result_map[data.units], unit=data.units)


@router.post(
    "/parse",
    response_model=time_schemas.ParsedTimeData,
    summary="将自然语言时间字符串解析为标准UTC时间",
    operation_id="parse_timestamp_to_utc"
)
async def parse_timestamp_to_utc(data: time_schemas.ParseTimestampInput):
    """
    当用户提供一个模糊或非标准的时间描述，需要将其转换为标准格式时使用。
    例如：“下周一中午12点”、“Tomorrow 3pm”、“2024/06/20 10:00 AM”
    此工具会将其解析并返回标准的 UTC ISO 8601 格式时间。
    """
    try:
        tz = pytz.timezone(data.timezone)
        dt = dateutil_parser.parse(data.timestamp)
        if dt.tzinfo is None:
            dt = tz.localize(dt)
        dt_utc = dt.astimezone(pytz.utc)
        return time_schemas.ParsedTimeData(utc_time=dt_utc.isoformat())
    except pytz.UnknownTimeZoneError as e:
        raise HTTPException(status_code=400, detail=f"无效的时区: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"无法解析时间字符串 '{data.timestamp}': {e}")


@router.get(
    "/list_timezones",
    response_model=time_schemas.TimezoneListData,
    summary="获取所有支持的IANA时区名称列表",
    operation_id="list_all_timezones"
)
async def list_all_timezones():
    """
    当用户询问有哪些可用的时区，或者当其他工具需要一个有效的时区名称列表时使用。
    此工具可以为其他时间相关工具提供有效的时区输入。
    """
    return time_schemas.TimezoneListData(timezones=pytz.all_timezones)