from datetime import datetime, time
from pydantic import BaseModel, field_validator


class TimeSlotSchema(BaseModel):
    id: int
    day_id: int
    start: time  # формат "HH:MM"
    end: time

    @field_validator("start", "end", mode="before")
    @classmethod
    def parse_time(cls, value):
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%H:%M").time()
            except ValueError as exc:
                raise ValueError("Time must be in HH:MM format") from exc
        return value

    @field_validator("end", mode="after")
    @classmethod
    def check_time_order(cls, end_time, values):
        start_time = values.data.get("start")
        if start_time and end_time <= start_time:
            raise ValueError("End time must be after start time")
        return end_time
