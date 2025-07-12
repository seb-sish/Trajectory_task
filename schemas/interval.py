from datetime import datetime, timedelta, date, time
from pydantic import BaseModel, field_validator
from schemas.timeslot import TimeSlotSchema


class IntervalSchema(BaseModel):
    start: time
    end: time

    def overlaps(self, other: "IntervalSchema") -> bool:
        return self.start < other.end and self.end > other.start

    def duration(self) -> int:
        return int(
            (
                timedelta(hours=self.end.hour, minutes=self.end.minute)
                - timedelta(hours=self.start.hour, minutes=self.start.minute)
            ).total_seconds()
            // 60
        )

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


class IsFreeIntervalSchema(BaseModel):
    is_free: bool
    overlaps: list[TimeSlotSchema]


class FreeIntervalInScheduleSchema(IntervalSchema):
    founded: bool
    date: date
