"""
Скрипт для запуска всех тестов приложения
"""

import sys
import os
import pytest

# Добавляем корневую папку проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def main():  # pragma: no cover
    """
    Основная функция для запуска тестов
    """
    # Настройки для pytest
    pytest_args = [
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Strict marker handling
        "--cov=.",  # Coverage report
        "--cov-report=html",  # HTML coverage report
        "--cov-report=term-missing",  # Terminal coverage report
        "--cov-fail-under=80",  # Minimum coverage threshold
        "tests/",  # Test directory
    ]

    # Запускаем тесты
    exit_code = pytest.main(pytest_args)

    if exit_code == 0:
        print("\n✅ Все тесты прошли успешно!")
    else:
        print(f"\n❌ Тесты завершились с кодом {exit_code}")

    return exit_code


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
