from datetime import date, time
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
import pytest

from utils.time_manager import find_free_intervals, interval_has_intersections
from utils.shedules import get_schedule
from schemas.day import DaySchema
from schemas.timeslot import TimeSlotSchema
from schemas.interval import IntervalSchema
from schemas.schedule import ScheduleSchema


class TestTimeManager:
    """Тесты для модуля time_manager"""

    def test_find_free_intervals_empty_slots(self):
        """Тест поиска свободных интервалов без занятых слотов"""
        day = DaySchema(id=1, date=date(2024, 1, 15), start=time(9, 0), end=time(18, 0))
        day_slots = []

        free_intervals = find_free_intervals(day, day_slots)

        assert len(free_intervals) == 1
        assert free_intervals[0].start == time(9, 0)
        assert free_intervals[0].end == time(18, 0)

    def test_find_free_intervals_with_slots(self):
        """Тест поиска свободных интервалов с занятыми слотами"""
        day = DaySchema(id=1, date=date(2024, 1, 15), start=time(9, 0), end=time(18, 0))
        day_slots = [
            TimeSlotSchema(id=1, day_id=1, start=time(10, 0), end=time(11, 0)),
            TimeSlotSchema(id=2, day_id=1, start=time(14, 0), end=time(15, 0)),
        ]

        free_intervals = find_free_intervals(day, day_slots)

        assert len(free_intervals) == 3
        assert free_intervals[0].start == time(9, 0)
        assert free_intervals[0].end == time(10, 0)
        assert free_intervals[1].start == time(11, 0)
        assert free_intervals[1].end == time(14, 0)
        assert free_intervals[2].start == time(15, 0)
        assert free_intervals[2].end == time(18, 0)

    def test_find_free_intervals_full_day(self):
        """Тест поиска свободных интервалов для полностью занятого дня"""
        day = DaySchema(id=1, date=date(2024, 1, 15), start=time(9, 0), end=time(18, 0))
        day_slots = [TimeSlotSchema(id=1, day_id=1, start=time(9, 0), end=time(18, 0))]

        free_intervals = find_free_intervals(day, day_slots)

        assert len(free_intervals) == 0

    def test_find_free_intervals_unordered_slots(self):
        """Тест поиска свободных интервалов с неупорядоченными слотами"""
        day = DaySchema(id=1, date=date(2024, 1, 15), start=time(9, 0), end=time(18, 0))
        day_slots = [
            TimeSlotSchema(id=2, day_id=1, start=time(14, 0), end=time(15, 0)),
            TimeSlotSchema(id=1, day_id=1, start=time(10, 0), end=time(11, 0)),
        ]

        free_intervals = find_free_intervals(day, day_slots)

        assert len(free_intervals) == 3
        assert free_intervals[0].start == time(9, 0)
        assert free_intervals[0].end == time(10, 0)
        assert free_intervals[1].start == time(11, 0)
        assert free_intervals[1].end == time(14, 0)
        assert free_intervals[2].start == time(15, 0)
        assert free_intervals[2].end == time(18, 0)

    def test_interval_has_intersections_no_overlaps(self):
        """Тест проверки пересечений без пересечений"""
        target = IntervalSchema(start=time(12, 0), end=time(13, 0))
        day_slots = [
            TimeSlotSchema(id=1, day_id=1, start=time(10, 0), end=time(11, 0)),
            TimeSlotSchema(id=2, day_id=1, start=time(14, 0), end=time(15, 0)),
        ]

        result = interval_has_intersections(target, day_slots)

        assert result.is_free is True
        assert len(result.overlaps) == 0

    def test_interval_has_intersections_with_overlaps(self):
        """Тест проверки пересечений с пересечениями"""
        target = IntervalSchema(start=time(10, 30), end=time(11, 30))
        day_slots = [
            TimeSlotSchema(id=1, day_id=1, start=time(10, 0), end=time(11, 0)),
            TimeSlotSchema(id=2, day_id=1, start=time(14, 0), end=time(15, 0)),
        ]

        result = interval_has_intersections(target, day_slots)

        assert result.is_free is False
        assert len(result.overlaps) == 1
        assert result.overlaps[0].id == 1

    def test_interval_has_intersections_multiple_overlaps(self):
        """Тест проверки пересечений с несколькими пересечениями"""
        target = IntervalSchema(start=time(10, 30), end=time(14, 30))
        day_slots = [
            TimeSlotSchema(id=1, day_id=1, start=time(10, 0), end=time(11, 0)),
            TimeSlotSchema(id=2, day_id=1, start=time(14, 0), end=time(15, 0)),
        ]

        result = interval_has_intersections(target, day_slots)

        assert result.is_free is False
        assert len(result.overlaps) == 2
        assert result.overlaps[0].id == 1
        assert result.overlaps[1].id == 2

    def test_interval_has_intersections_empty_slots(self):
        """Тест проверки пересечений с пустым списком слотов"""
        target = IntervalSchema(start=time(10, 0), end=time(11, 0))
        day_slots = []

        result = interval_has_intersections(target, day_slots)

        assert result.is_free is True
        assert len(result.overlaps) == 0


class TestSchedules:
    """Тесты для модуля schedules"""

    @pytest.mark.asyncio
    async def test_get_schedule_success(self):
        """Тест успешного получения расписания"""
        mock_data = {
            "days": [{"id": 1, "date": "2024-01-15", "start": "09:00", "end": "18:00"}],
            "timeslots": [{"id": 1, "day_id": 1, "start": "10:00", "end": "11:00"}],
        }

        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_data)

        mock_session = Mock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch("utils.shedules.aiohttp.ClientSession", return_value=mock_session):
            with patch("utils.shedules.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.URL = "http://test.com"
                mock_get_settings.return_value = mock_settings

                schedule = await get_schedule()

                assert isinstance(schedule, ScheduleSchema)
                assert len(schedule.days) == 1
                assert len(schedule.timeslots) == 1
                assert schedule.days[date(2024, 1, 15)].id == 1
                assert schedule.timeslots[0].id == 1

    @pytest.mark.asyncio
    async def test_get_schedule_http_error(self):
        """Тест обработки HTTP ошибки при получении расписания"""
        mock_response = Mock()
        mock_response.status = 500

        mock_session = Mock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch("utils.shedules.aiohttp.ClientSession", return_value=mock_session):
            with patch("utils.shedules.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.URL = "http://test.com"
                mock_get_settings.return_value = mock_settings

                with pytest.raises(HTTPException) as exc_info:
                    await get_schedule()
                assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_get_schedule_empty_data(self):
        """Тест получения расписания с пустыми данными"""
        mock_data = {"days": [], "timeslots": []}

        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_data)

        mock_session = Mock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch("utils.shedules.aiohttp.ClientSession", return_value=mock_session):
            with patch("utils.shedules.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.URL = "http://test.com"
                mock_get_settings.return_value = mock_settings

                schedule = await get_schedule()

                assert isinstance(schedule, ScheduleSchema)
                assert len(schedule.days) == 0
                assert len(schedule.timeslots) == 0

    @pytest.mark.asyncio
    async def test_get_schedule_missing_keys(self):
        """Тест получения расписания с отсутствующими ключами"""
        mock_data = {}

        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_data)

        mock_session = Mock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch("utils.shedules.aiohttp.ClientSession", return_value=mock_session):
            with patch("utils.shedules.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.URL = "http://test.com"
                mock_get_settings.return_value = mock_settings

                schedule = await get_schedule()

                assert isinstance(schedule, ScheduleSchema)
                assert len(schedule.days) == 0
                assert len(schedule.timeslots) == 0
