# app/schemas/time.py
from pydantic import BaseModel, Field
from typing import List, Literal

# --- 输入模型 (Inputs) ---

class FormatTimeInput(BaseModel):
    format: str = Field(
        default="%Y-%m-%d %H:%M:%S", description="Python strftime 格式化字符串"
    )
    timezone: str = Field(
        default="UTC", description="IANA 时区名称 (例如: UTC, America/New_York)"
    )

class ConvertTimeInput(BaseModel):
    timestamp: str = Field(
        description="ISO 8601 格式的时间字符串 (例如: 2024-01-01T12:00:00Z)"
    )
    from_tz: str = Field(
        description="输入时间戳的原始IANA时区 (例如: UTC, Europe/Berlin)"
    )
    to_tz: str = Field(description="需要转换到的目标IANA时区")

class ElapsedTimeInput(BaseModel):
    start: str = Field(description="ISO 8601 格式的开始时间戳")
    end: str = Field(description="ISO 8601 格式的结束时间戳")
    units: Literal["seconds", "minutes", "hours", "days"] = Field(
        default="seconds", description="计算时间差的单位"
    )

class ParseTimestampInput(BaseModel):
    timestamp: str = Field(
        description="灵活输入的时间字符串 (例如: 2024-06-01 12:00 PM)"
    )
    timezone: str = Field(
        default="UTC", description="如果输入中未指定时区，则假定为此处指定的时区"
    )

# --- 输出数据模型 (Data models for ApiResponse) ---

class CurrentTimeData(BaseModel):
    utc_time: str
    local_time: str

class FormattedTimeData(BaseModel):
    formatted_time: str

class ConvertedTimeData(BaseModel):
    converted_time: str

class ElapsedTimeData(BaseModel):
    elapsed: float
    unit: str

class ParsedTimeData(BaseModel):
    utc_time: str

class TimezoneListData(BaseModel):
    timezones: List[str]