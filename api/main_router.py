from datetime import date, time, timedelta
import aiohttp
from fastapi import APIRouter, HTTPException, Query
from pydantic import ValidationError

from schemas import (
    ScheduleSchema,
    IntervalSchema,
    TimeSlotSchema,
    IsFreeIntervalSchema,
    FreeIntervalInScheduleSchema,
)
from utils import get_schedule, find_free_intervals, interval_has_intersections

mainRouter = APIRouter(
    prefix="", tags=["main"], responses={404: {"detail": "Url not found"}}
)


@mainRouter.get("/")
async def get_simple_schedule() -> ScheduleSchema:
    try:
        return await get_schedule()
    except (aiohttp.ClientError, ValidationError) as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@mainRouter.get("/{date_format}/taken_slots")
async def get_taken_slots_on_date(date_format: date) -> list[TimeSlotSchema]:
    try:
        schedule = await get_schedule()
        # Filter the schedule for the specific date
        day = schedule.days.get(date_format)
        if not day:
            raise HTTPException(status_code=404, detail="Day not found in schedule")
        day_slots = (
            [slot for slot in schedule.timeslots if slot.day_id == day.id]
            if day
            else []
        )
        return day_slots
    except (aiohttp.ClientError, ValidationError) as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@mainRouter.get("/{date_format}/free_intervals")
async def get_free_interval_on_date(date_format: date) -> list[IntervalSchema]:
    try:
        schedule = await get_schedule()
        day = schedule.days.get(date_format)
        if not day:
            raise HTTPException(status_code=404, detail="Day not found in schedule")
        day_slots = (
            [slot for slot in schedule.timeslots if slot.day_id == day.id]
            if day
            else []
        )

        free_intervals = find_free_intervals(day, day_slots)
        return free_intervals

    except (aiohttp.ClientError, ValidationError) as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@mainRouter.post("/{date_format}/is_free")
async def is_this_interval_free_on_date(
    date_format: date, interval: IntervalSchema
) -> IsFreeIntervalSchema:
    try:
        schedule = await get_schedule()
        day = schedule.days.get(date_format)
        if not day:
            raise HTTPException(status_code=404, detail="Day not found in schedule")
        day_slots = (
            [slot for slot in schedule.timeslots if slot.day_id == day.id]
            if day
            else []
        )

        return interval_has_intersections(interval, day_slots)

    except (aiohttp.ClientError, ValidationError) as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@mainRouter.post("/find_free_interval")
async def find_free_interval(
    interval_duration: int = Query(60, ge=0),
) -> FreeIntervalInScheduleSchema:
    try:
        schedule = await get_schedule()
        for day in schedule.days.values():
            day_slots = (
                [slot for slot in schedule.timeslots if slot.day_id == day.id]
                if day
                else []
            )
            free_intervals = find_free_intervals(day, day_slots)
            for free_interval in free_intervals:
                if free_interval.duration() >= interval_duration:
                    end_time = timedelta(
                        hours=free_interval.start.hour,
                        minutes=free_interval.start.minute,
                    ) + timedelta(minutes=interval_duration)
                    end_time_obj = time(
                        hour=(end_time.seconds // 3600) % 24,
                        minute=(end_time.seconds % 3600) // 60,
                    )
                    return FreeIntervalInScheduleSchema(
                        founded=True,
                        date=day.date,
                        start=free_interval.start,
                        end=end_time_obj,
                    )

        return FreeIntervalInScheduleSchema(
            founded=False, date=date(1900, 1, 1), start=time(0, 0), end=time(23, 59)
        )

    except (aiohttp.ClientError, ValidationError) as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
