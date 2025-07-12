# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
from unittest.mock import Mock, AsyncMock
import pytest
from fastapi.testclient import TestClient

from main import get_app


@pytest.fixture
def client():
    """
    Returns a client that can be used to interact with the application.
    """
    app = get_app()
    return TestClient(app=app, base_url="http://test")


@pytest.fixture
def mock_schedule_data():
    """
    Fixture with test schedule data.
    """
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


@pytest.fixture
def mock_http_session():
    """
    Fixture for mocking HTTP session.
    """
    mock_response = Mock()
    mock_response.status = 200

    mock_session = Mock()
    mock_session.get = AsyncMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    return mock_session, mock_response


@pytest.fixture
def mock_settings():
    """
    Fixture for mocking settings.
    """
    mock_settings = Mock()
    mock_settings.URL = "http://test.com"
    mock_settings.PATH_PREFIX = ""
    mock_settings.APP_HOST = "127.0.0.1"
    mock_settings.APP_PORT = 8000
    return mock_settings
