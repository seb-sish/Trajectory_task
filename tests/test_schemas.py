# type: ignore
from datetime import date, time
import pytest
from pydantic import ValidationError

from schemas.day import DaySchema
from schemas.timeslot import TimeSlotSchema
from schemas.interval import (
    IntervalSchema,
    IsFreeIntervalSchema,
    FreeIntervalInScheduleSchema,
)
from schemas.schedule import ScheduleSchema


class TestDaySchema:
    """Тесты для DaySchema"""

    def test_day_schema_valid(self):
        """Тест валидного создания DaySchema"""
        day = DaySchema(id=1, date=date(2024, 1, 15), start=time(9, 0), end=time(18, 0))
        assert day.id == 1
        assert day.date == date(2024, 1, 15)
        assert day.start == time(9, 0)
        assert day.end == time(18, 0)

    def test_day_schema_with_string_date(self):
        """Тест создания DaySchema с датой в виде строки"""
        day = DaySchema(id=1, date="2024-01-15", start="09:00", end="18:00")
        assert day.date == date(2024, 1, 15)
        assert day.start == time(9, 0)
        assert day.end == time(18, 0)

    def test_day_schema_invalid_date_format(self):
        """Тест с невалидным форматом даты"""
        with pytest.raises(ValidationError) as exc_info:
            DaySchema(
                id=1,
                date="15-01-2024",  # Неправильный формат
                start="09:00",
                end="18:00",
            )
        assert "Date must be in YYYY-MM-DD format" in str(exc_info.value)

    def test_day_schema_invalid_time_format(self):
        """Тест с невалидным форматом времени"""
        with pytest.raises(ValidationError) as exc_info:
            DaySchema(
                id=1,
                date="2024-01-15",
                start="00:10:00",  # Неправильный формат
                end="18:00",
            )
        assert "Time must be in HH:MM format" in str(exc_info.value)

    def test_day_schema_end_before_start(self):
        """Тест с временем окончания раньше начала"""
        with pytest.raises(ValidationError) as exc_info:
            DaySchema(id=1, date="2024-01-15", start="18:00", end="09:00")
        assert "End time must be after start time" in str(exc_info.value)

    def test_day_schema_equal_times(self):
        """Тест с равными временами начала и окончания"""
        with pytest.raises(ValidationError) as exc_info:
            DaySchema(id=1, date="2024-01-15", start="09:00", end="09:00")
        assert "End time must be after start time" in str(exc_info.value)


class TestTimeSlotSchema:
    """Тесты для TimeSlotSchema"""

    def test_timeslot_schema_valid(self):
        """Тест валидного создания TimeSlotSchema"""
        slot = TimeSlotSchema(id=1, day_id=1, start=time(10, 0), end=time(11, 0))
        assert slot.id == 1
        assert slot.day_id == 1
        assert slot.start == time(10, 0)
        assert slot.end == time(11, 0)

    def test_timeslot_schema_with_string_time(self):
        """Тест создания TimeSlotSchema с временем в виде строки"""
        slot = TimeSlotSchema(id=1, day_id=1, start="10:00", end="11:00")
        assert slot.start == time(10, 0)
        assert slot.end == time(11, 0)

    def test_timeslot_schema_invalid_time_format(self):
        """Тест с невалидным форматом времени"""
        with pytest.raises(ValidationError) as exc_info:
            TimeSlotSchema(
                id=1,
                day_id=1,
                start="10:00",
                end="11",  # Неправильный формат
            )
        assert "Time must be in HH:MM format" in str(exc_info.value)

    def test_timeslot_schema_end_before_start(self):
        """Тест с временем окончания раньше начала"""
        with pytest.raises(ValidationError) as exc_info:
            TimeSlotSchema(id=1, day_id=1, start="11:00", end="10:00")
        assert "End time must be after start time" in str(exc_info.value)


class TestIntervalSchema:
    """Тесты для IntervalSchema"""

    def test_interval_schema_valid(self):
        """Тест валидного создания IntervalSchema"""
        interval = IntervalSchema(start=time(9, 0), end=time(10, 0))
        assert interval.start == time(9, 0)
        assert interval.end == time(10, 0)

    def test_interval_overlaps_true(self):
        """Тест пересечения интервалов"""
        interval1 = IntervalSchema(start=time(9, 0), end=time(11, 0))
        interval2 = IntervalSchema(start=time(10, 0), end=time(12, 0))
        assert interval1.overlaps(interval2) is True

    def test_interval_overlaps_false(self):
        """Тест отсутствия пересечения интервалов"""
        interval1 = IntervalSchema(start=time(9, 0), end=time(10, 0))
        interval2 = IntervalSchema(start=time(11, 0), end=time(12, 0))
        assert interval1.overlaps(interval2) is False

    def test_interval_overlaps_touching(self):
        """Тест соприкасающихся интервалов"""
        interval1 = IntervalSchema(start=time(9, 0), end=time(10, 0))
        interval2 = IntervalSchema(start=time(10, 0), end=time(11, 0))
        assert interval1.overlaps(interval2) is False

    def test_interval_duration(self):
        """Тест расчета продолжительности интервала"""
        interval = IntervalSchema(start=time(9, 0), end=time(10, 30))
        assert interval.duration() == 90  # 1 час 30 минут = 90 минут

    def test_interval_duration_zero(self):
        """Тест расчета продолжительности нулевого интервала"""
        with pytest.raises(ValidationError) as exc_info:
            IntervalSchema(start=time(9, 0), end=time(9, 0))
        assert "End time must be after start time" in str(exc_info.value)

    def test_interval_schema_end_before_start(self):
        """Тест с временем окончания раньше начала"""
        with pytest.raises(ValidationError) as exc_info:
            IntervalSchema(start=time(11, 0), end=time(10, 0))
        assert "End time must be after start time" in str(exc_info.value)


class TestIsFreeIntervalSchema:
    """Тесты для IsFreeIntervalSchema"""

    def test_is_free_interval_schema_free(self):
        """Тест создания схемы свободного интервала"""
        schema = IsFreeIntervalSchema(is_free=True, overlaps=[])
        assert schema.is_free is True
        assert schema.overlaps == []

    def test_is_free_interval_schema_not_free(self):
        """Тест создания схемы занятого интервала"""
        slot = TimeSlotSchema(id=1, day_id=1, start=time(10, 0), end=time(11, 0))
        schema = IsFreeIntervalSchema(is_free=False, overlaps=[slot])
        assert schema.is_free is False
        assert len(schema.overlaps) == 1
        assert schema.overlaps[0].id == 1


class TestFreeIntervalInScheduleSchema:
    """Тесты для FreeIntervalInScheduleSchema"""

    def test_free_interval_in_schedule_schema_found(self):
        """Тест создания схемы найденного интервала"""
        schema = FreeIntervalInScheduleSchema(
            founded=True, date=date(2024, 1, 15), start=time(9, 0), end=time(10, 0)
        )
        assert schema.founded is True
        assert schema.date == date(2024, 1, 15)
        assert schema.start == time(9, 0)
        assert schema.end == time(10, 0)

    def test_free_interval_in_schedule_schema_not_found(self):
        """Тест создания схемы не найденного интервала"""
        schema = FreeIntervalInScheduleSchema(
            founded=False, date=date(1900, 1, 1), start=time(0, 0), end=time(23, 59)
        )
        assert schema.founded is False
        assert schema.date == date(1900, 1, 1)


class TestScheduleSchema:
    """Тесты для ScheduleSchema"""

    def test_schedule_schema_valid(self):
        """Тест валидного создания ScheduleSchema"""
        day = DaySchema(id=1, date=date(2024, 1, 15), start=time(9, 0), end=time(18, 0))
        slot = TimeSlotSchema(id=1, day_id=1, start=time(10, 0), end=time(11, 0))
        schedule = ScheduleSchema(days={date(2024, 1, 15): day}, timeslots=[slot])
        assert len(schedule.days) == 1
        assert len(schedule.timeslots) == 1
        assert schedule.days[date(2024, 1, 15)].id == 1
        assert schedule.timeslots[0].id == 1

    def test_schedule_schema_empty(self):
        """Тест создания пустого расписания"""
        schedule = ScheduleSchema(days={}, timeslots=[])
        assert len(schedule.days) == 0
        assert len(schedule.timeslots) == 0
