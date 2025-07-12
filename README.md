# Trajectory API

Микросервис для работы с расписанием, реализующий возможность управления временными интервалами и проверки их доступности.

## Описание проекта

Проект представляет собой FastAPI-приложение, которое предоставляет API для работы с расписанием. Основные функции:
- Управление временными интервалами
- Проверка свободных интервалов в расписании
- Валидация пересечений временных слотов

## Структура проекта

```
trajectory_task/
├── main.py                 # Точка входа приложения FastAPI
├── pyproject.toml          # Конфигурация проекта и зависимости
├── compose.yaml            # Docker Compose конфигурация
├── Dockerfile              # Образ для контейнеризации
├── run_tests.py            # Скрипт для запуска тестов
├── api/                    # API роутеры
│   ├── __init__.py
│   └── main_router.py      # Основные эндпоинты
├── schemas/                # Pydantic схемы
│   ├── day.py
│   ├── interval.py
│   ├── schedule.py
│   └── timeslot.py
├── utils/                  # Утилиты и настройки
│   ├── settings.py         # Конфигурация приложения
│   ├── shedules.py         # Логика работы с расписанием
│   └── time_manager.py     # Управление временем
└── tests/                  # Тесты
    ├── conftest.py
    ├── test_integration.py
    ├── test_schemas.py
    └── test_utils.py
```
## Развертывание сервиса

### Клонирование и подготовка
```bash
# Клонирование репозитория
git clone https://github.com/seb-sish/Trajectory_task
# Перейдите в директорию проекта
cd Trajectory_task/
```

### Создание файла .env
```bash
# Скопируйте пример файла конфигурации:
cp .env.example .env
# Отредактируйте .env файл под свои нужды
```

## Запуск без Docker

### Требования
- Python 3.12+
- uv (пакетный менеджер)

### Установка и запуск

1. Установите зависимости:
```bash
pip install uv
uv sync
```

2. Запустите приложение:
```bash
uv run main.py
```

Приложение будет доступно по адресу: `http://localhost:8000`

### Запуск тестов
```bash
uv run run_tests.py
```

## Запуск с Docker

### Использование Docker Compose (рекомендуется)

1. Запустите сервис:
```bash
docker-compose up -d
```

Приложение будет доступно по адресу: `http://localhost:80`

### Использование Docker напрямую

1. Соберите образ:
```bash
docker build -t trajectory-api .
```

2. Запустите контейнер:
```bash
docker run -p 8000:8000 trajectory-api
```

## API Документация

После запуска приложения документация API доступна по адресу:
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi`
