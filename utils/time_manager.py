from schemas import DaySchema, TimeSlotSchema, IntervalSchema
from schemas.interval import IsFreeIntervalSchema


def find_free_intervals(
    day: DaySchema, day_slots: list[TimeSlotSchema]
) -> list[IntervalSchema]:
    free_intervals = []
    if day_slots:
        day_slots.sort(key=lambda x: x.start)
        start_time = day.start
        end_time = day.end
        for slot in day_slots:
            if slot.start > start_time:
                free_intervals.append(IntervalSchema(start=start_time, end=slot.start))
            start_time = slot.end
        if start_time < end_time:
            free_intervals.append(IntervalSchema(start=start_time, end=end_time))
    else:
        free_intervals.append(IntervalSchema(start=day.start, end=day.end))
    return free_intervals


def interval_has_intersections(
    target: IntervalSchema, day_slots: list[TimeSlotSchema]
) -> IsFreeIntervalSchema:
    overlaps = [
        slot
        for slot in day_slots
        if target.overlaps(IntervalSchema(start=slot.start, end=slot.end))
    ]
    return IsFreeIntervalSchema(is_free=not bool(overlaps), overlaps=overlaps)
