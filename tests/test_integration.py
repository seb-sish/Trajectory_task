from unittest.mock import Mock, patch, AsyncMock
import pytest
from fastapi.testclient import TestClient

from main import get_app


class TestMainApp:
    """Тесты для главного приложения"""

    def test_get_app_creation(self):
        """Тест создания приложения"""
        app = get_app()
        assert app.title == "timetable"
        assert app.version == "0.1.0"
        assert app.docs_url == "/docs"
        assert app.openapi_url == "/openapi"

    def test_bind_routes(self):
        """Тест привязки маршрутов"""
        app = get_app()
        # Проверяем, что маршруты добавлены
        assert len(app.routes) > 0


class TestAPIEndpoints:
    """Интеграционные тесты для API эндпоинтов"""

    @pytest.fixture
    def client(self):
        """Фикстура для тестового клиента"""
        app = get_app()
        return TestClient(app)

    @pytest.fixture
    def mock_schedule_data(self):
        """Фикстура с тестовыми данными расписания"""
        return {
            "days": [
                {"id": 1, "date": "2024-01-15", "start": "09:00", "end": "18:00"},
                {"id": 2, "date": "2024-01-16", "start": "09:00", "end": "18:00"},
            ],
            "timeslots": [
                {"id": 1, "day_id": 1, "start": "10:00", "end": "11:00"},
                {"id": 2, "day_id": 1, "start": "14:00", "end": "15:00"},
            ],
        }

    def test_get_simple_schedule_success(self, client, mock_schedule_data):
        """Тест успешного получения простого расписания"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_schedule_data)

        mock_session = Mock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch("utils.shedules.aiohttp.ClientSession", return_value=mock_session):
            with patch("utils.shedules.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.URL = "http://test.com"
                mock_get_settings.return_value = mock_settings

                response = client.get("/")

                assert response.status_code == 200
                data = response.json()
                assert "days" in data
                assert "timeslots" in data
                assert len(data["timeslots"]) == 2

    def test_get_simple_schedule_external_error(self, client):
        """Тест обработки внешней ошибки при получении расписания"""
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

                response = client.get("/")

                assert response.status_code == 500

    def test_get_taken_slots_success(self, client, mock_schedule_data):
        """Тест успешного получения занятых слотов"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_schedule_data)

        mock_session = Mock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch("utils.shedules.aiohttp.ClientSession", return_value=mock_session):
            with patch("utils.shedules.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.URL = "http://test.com"
                mock_get_settings.return_value = mock_settings

                response = client.get("/2024-01-15/taken_slots")

                assert response.status_code == 200
                data = response.json()
                assert len(data) == 2
                assert data[0]["id"] == 1
                assert data[1]["id"] == 2

    def test_get_taken_slots_day_not_found(self, client, mock_schedule_data):
        """Тест получения занятых слотов для несуществующего дня"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_schedule_data)

        mock_session = Mock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch("utils.shedules.aiohttp.ClientSession", return_value=mock_session):
            with patch("utils.shedules.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.URL = "http://test.com"
                mock_get_settings.return_value = mock_settings

                response = client.get("/2024-01-20/taken_slots")

                assert response.status_code == 404
                assert "Day not found in schedule" in response.json()["detail"]

    def test_get_free_intervals_success(self, client, mock_schedule_data):
        """Тест успешного получения свободных интервалов"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_schedule_data)

        mock_session = Mock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch("utils.shedules.aiohttp.ClientSession", return_value=mock_session):
            with patch("utils.shedules.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.URL = "http://test.com"
                mock_get_settings.return_value = mock_settings

                response = client.get("/2024-01-15/free_intervals")

                assert response.status_code == 200
                data = response.json()
                assert len(data) == 3  # 09:00-10:00, 11:00-14:00, 15:00-18:00

    def test_get_free_intervals_day_not_found(self, client, mock_schedule_data):
        """Тест получения свободных интервалов для несуществующего дня"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_schedule_data)

        mock_session = Mock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch("utils.shedules.aiohttp.ClientSession", return_value=mock_session):
            with patch("utils.shedules.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.URL = "http://test.com"
                mock_get_settings.return_value = mock_settings

                response = client.get("/2024-01-20/free_intervals")

                assert response.status_code == 404
                assert "Day not found in schedule" in response.json()["detail"]

    def test_is_interval_free_success_free(self, client, mock_schedule_data):
        """Тест проверки свободного интервала"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_schedule_data)

        mock_session = Mock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch("utils.shedules.aiohttp.ClientSession", return_value=mock_session):
            with patch("utils.shedules.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.URL = "http://test.com"
                mock_get_settings.return_value = mock_settings

                interval_data = {"start": "12:00", "end": "13:00"}

                response = client.post("/2024-01-15/is_free", json=interval_data)

                assert response.status_code == 200
                data = response.json()
                assert data["is_free"] is True
                assert len(data["overlaps"]) == 0

    def test_is_interval_free_success_occupied(self, client, mock_schedule_data):
        """Тест проверки занятого интервала"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_schedule_data)

        mock_session = Mock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch("utils.shedules.aiohttp.ClientSession", return_value=mock_session):
            with patch("utils.shedules.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.URL = "http://test.com"
                mock_get_settings.return_value = mock_settings

                interval_data = {"start": "10:30", "end": "11:30"}

                response = client.post("/2024-01-15/is_free", json=interval_data)

                assert response.status_code == 200
                data = response.json()
                assert data["is_free"] is False
                assert len(data["overlaps"]) == 1

    def test_is_interval_free_day_not_found(self, client, mock_schedule_data):
        """Тест проверки интервала для несуществующего дня"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_schedule_data)

        mock_session = Mock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch("utils.shedules.aiohttp.ClientSession", return_value=mock_session):
            with patch("utils.shedules.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.URL = "http://test.com"
                mock_get_settings.return_value = mock_settings

                interval_data = {"start": "12:00", "end": "13:00"}

                response = client.post("/2024-01-20/is_free", json=interval_data)

                assert response.status_code == 404
                assert "Day not found in schedule" in response.json()["detail"]

    def test_find_free_interval_success(self, client, mock_schedule_data):
        """Тест успешного поиска свободного интервала"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_schedule_data)

        mock_session = Mock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch("utils.shedules.aiohttp.ClientSession", return_value=mock_session):
            with patch("utils.shedules.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.URL = "http://test.com"
                mock_get_settings.return_value = mock_settings

                response = client.post("/find_free_interval?interval_duration=60")

                assert response.status_code == 200
                data = response.json()
                assert data["founded"] is True
                assert "date" in data
                assert "start" in data
                assert "end" in data

    def test_find_free_interval_not_found(self, client):
        """Тест поиска свободного интервала когда нет подходящих"""
        mock_schedule_data = {
            "days": [{"id": 1, "date": "2024-01-15", "start": "09:00", "end": "18:00"}],
            "timeslots": [{"id": 1, "day_id": 1, "start": "09:00", "end": "18:00"}],
        }

        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_schedule_data)

        mock_session = Mock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch("utils.shedules.aiohttp.ClientSession", return_value=mock_session):
            with patch("utils.shedules.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.URL = "http://test.com"
                mock_get_settings.return_value = mock_settings

                response = client.post("/find_free_interval?interval_duration=60")

                assert response.status_code == 200
                data = response.json()
                assert data["founded"] is False

    def test_find_free_interval_default_duration(self, client, mock_schedule_data):
        """Тест поиска свободного интервала с дефолтной продолжительностью"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_schedule_data)

        mock_session = Mock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch("utils.shedules.aiohttp.ClientSession", return_value=mock_session):
            with patch("utils.shedules.get_settings") as mock_get_settings:
                mock_settings = Mock()
                mock_settings.URL = "http://test.com"
                mock_get_settings.return_value = mock_settings

                response = client.post("/find_free_interval")

                assert response.status_code == 200
                data = response.json()
                assert data["founded"] is True

    def test_invalid_date_format(self, client):
        """Тест с невалидным форматом даты"""
        response = client.get("/invalid-date/taken_slots")
        assert response.status_code == 422  # Validation error

    def test_invalid_interval_data(self, client):
        """Тест с невалидными данными интервала"""
        invalid_interval = {
            "start": "25:00",  # Невалидное время
            "end": "13:00",
        }

        response = client.post("/2024-01-15/is_free", json=invalid_interval)
        assert response.status_code == 422  # Validation error
