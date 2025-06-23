# app/schemas/time.py
from pydantic import BaseModel, Field
from typing import List, Literal

# --- 输入模型 (Inputs) ---

class FormatTimeInput(BaseModel):
    format: str = Field(
        default="%Y-%m-%d %H:%M:%S",
        description="Python strftime 标准格式化字符串。",
        examples=["%Y-%m-%d", "%H:%M", "%A, %B %d, %Y"]
    )
    timezone: str = Field(
        default="UTC",
        description="目标时区的 IANA 名称。如果需要有效列表，可调用 list_all_timezones 工具。",
        examples=["America/New_York", "Europe/London", "Asia/Shanghai"]
    )

class ConvertTimeInput(BaseModel):
    timestamp: str = Field(
        description="一个明确的、符合 ISO 8601 格式的时间字符串。",
        examples=["2024-06-21T10:00:00", "2025-01-01T20:00:00+08:00"]
    )
    from_tz: str = Field(
        description="输入时间戳的原始 IANA 时区。",
        examples=["Asia/Shanghai", "UTC"]
    )
    to_tz: str = Field(
        description="需要转换到的目标 IANA 时区。",
        examples=["America/Los_Angeles", "Europe/Paris"]
    )

class ElapsedTimeInput(BaseModel):
    start: str = Field(description="ISO 8601 格式的开始时间戳。", examples=["2024-01-01T00:00:00Z"])
    end: str = Field(description="ISO 8601 格式的结束时间戳。", examples=["2024-06-21T12:00:00Z"])
    units: Literal["seconds", "minutes", "hours", "days"] = Field(
        default="seconds", description="返回的时间差单位。"
    )

class ParseTimestampInput(BaseModel):
    timestamp: str = Field(
        description="一个灵活格式的、人类可读的时间字符串。",
        examples=["today", "next friday 5pm", "2024-07-01 14:30", "june 1st 2025"]
    )
    timezone: str = Field(
        default="UTC",
        description="如果输入的时间字符串本身不包含时区信息，则假定为此处指定的时区。",
        examples=["America/Chicago", "Asia/Tokyo"]
    )

# --- 输出数据模型 (Data models for API Responses) ---

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