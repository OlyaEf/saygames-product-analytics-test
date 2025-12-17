"""
Модуль для работы с ClickHouse.

Содержит функцию get_client(), которая создаёт подключение к базе данных
по настройкам из config.py.
"""

from clickhouse_driver import Client

from core.config import (
    CLICKHOUSE_HOST,
    CLICKHOUSE_PORT,
    CLICKHOUSE_USER,
    CLICKHOUSE_PASSWORD,
    CLICKHOUSE_DB,
)


def get_client() -> Client:
    """
    Создаёт и возвращает клиент ClickHouse.

    :return: объект Client для выполнения запросов.
    """
    client = Client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        user=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
        database=CLICKHOUSE_DB,
        settings={"use_numpy": False},
    )
    return client
