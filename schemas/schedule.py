from datetime import date
from pydantic import BaseModel
from .day import DaySchema
from .timeslot import TimeSlotSchema

class ScheduleSchema(BaseModel):
    days: dict[date, DaySchema]
    timeslots: list[TimeSlotSchema]
