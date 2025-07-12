import aiohttp
from fastapi import HTTPException

from schemas import DaySchema, TimeSlotSchema, ScheduleSchema
from utils import get_settings

async def get_schedule() -> ScheduleSchema:
    async with aiohttp.ClientSession() as session:
        req = await session.get(get_settings().URL)
        if req.status != 200:
            raise HTTPException(status_code=req.status, detail="Failed to fetch data")

        data = await req.json()
        days = {}
        for day in data.get("days", []):
            day = DaySchema(**day)
            days[day.date] = day
        timeslots = [TimeSlotSchema(**slot) for slot in data.get("timeslots", [])]

        return ScheduleSchema(days=days, timeslots=timeslots)
