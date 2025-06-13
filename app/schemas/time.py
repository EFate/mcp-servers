from pydantic import BaseModel, Field
from typing import Literal, List

# --- 输入模型 ---

class FormatTimeInput(BaseModel):
    format: str = Field(
        default="%Y-%m-%d %H:%M:%S", description="Python strftime format string"
    )
    timezone: str = Field(
        default="UTC", description="IANA timezone name (e.g., UTC, America/New_York)"
    )

class ConvertTimeInput(BaseModel):
    timestamp: str = Field(
        ..., description="ISO 8601 formatted time string (e.g., 2024-01-01T12:00:00Z)"
    )
    from_tz: str = Field(
        ..., description="Original IANA time zone of input (e.g. UTC or Europe/Berlin)"
    )
    to_tz: str = Field(..., description="Target IANA time zone to convert to")

class ElapsedTimeInput(BaseModel):
    start: str = Field(..., description="Start timestamp in ISO 8601 format")
    end: str = Field(..., description="End timestamp in ISO 8601 format")
    units: Literal["seconds", "minutes", "hours", "days"] = Field(
        default="seconds", description="Unit for elapsed time"
    )

class ParseTimestampInput(BaseModel):
    timestamp: str = Field(
        ..., description="Flexible input timestamp string (e.g., '2024-06-01 12:00 PM')"
    )
    timezone: str = Field(
        default="UTC", description="Assumed timezone if none is specified in input"
    )

# --- 为每个端点创建对应的输出（Data）模型 ---

class TimeData(BaseModel):
    time: str

class FormattedTimeData(BaseModel):
    formatted_time: str

class ConvertedTimeData(BaseModel):
    converted_time: str

class ElapsedTimeData(BaseModel):
    elapsed: float
    unit: str

class TimezoneListData(BaseModel):
    timezones: List[str]