from os import environ
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class SettingsBase(BaseSettings):
    ENV: str = Field("local", description="Environment type")
    PATH_PREFIX: str = Field("", description="Path prefix for the API")
    APP_HOST: str = Field("127.0.0.1", description="Application host")
    APP_PORT: int = Field(8000, description="Application port")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # case_sensitive=False,
        env_ignore_empty=True,
        extra="ignore",
    )


class Settings(SettingsBase):
    model_config = SettingsConfigDict(env_prefix="API_")

    URL: str = Field("localhost")

    @classmethod
    def load(cls) -> "Settings":
        return cls()  # type: ignore


def get_settings() -> Settings:
    env = environ.get("ENV", "local")
    if env == "local":
        return Settings.load()  # type: ignore
    # ...
    # space for other settings
    # ...
    return Settings.load()  # type: ignore


config = get_settings()


if __name__ == "__main__":
    print(config)
