from fastapi import FastAPI
from uvicorn import run

from utils import SettingsBase, get_settings
from api import list_of_routes


def bind_routes(application: FastAPI, setting: SettingsBase) -> None:
    """
    Bind all routes to application.
    """
    for route in list_of_routes:
        application.include_router(route, prefix=setting.PATH_PREFIX)


def get_app() -> FastAPI:
    """
    Creates application and all dependable objects.
    """
    description = "Микросервис, реализующий возможность работы с расписанием."

    tags_metadata = [
        {
            "name": "Application Health",
            "description": "API health check.",
        },
    ]

    application = FastAPI(
        title="timetable",
        description=description,
        docs_url="/docs",
        openapi_url="/openapi",
        version="0.1.0",
        openapi_tags=tags_metadata,
    )
    settings = get_settings()
    bind_routes(application, settings)
    application.state.settings = settings
    return application


app = get_app()


if __name__ == "__main__":  # pragma: no cover
    settings_for_application = get_settings()
    run(
        "main:app",
        host=settings_for_application.APP_HOST,
        port=settings_for_application.APP_PORT,
        reload=True,
        reload_dirs=["."],
        log_level="debug",
    )
