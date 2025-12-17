"""
Скрипт для проверки подключения к ClickHouse и первичного знакомства с данными.

Запуск из корня проекта:
    poetry run python src/test_connection.py
"""

from typing import List, Tuple

import pandas as pd
from core.db import get_client


def print_table_sample(client, table_name: str, limit: int = 5) -> None:
    """
    Выводит количество строк в таблице и несколько первых строк
    в виде таблички (pandas DataFrame).

    :param client: Клиент ClickHouse, созданный в get_client().
    :param table_name: Полное имя таблицы, например 'test.devices'.
    :param limit: Количество строк для примера.
    """
    # Считаем количество строк в таблице
    count_query = f"SELECT count() FROM {table_name}"
    count_result = client.execute(count_query)
    total_rows = count_result[0][0]

    # Берём несколько строк для примера
    sample_query = f"SELECT * FROM {table_name} LIMIT {limit}"
    rows, columns_with_types = client.execute(sample_query, with_column_types=True)
    column_names: List[str] = [col_name for col_name, _ in columns_with_types]

    df = pd.DataFrame(rows, columns=column_names)

    print(
        f"\n=== Пример данных из {table_name} "
        f"(первые {limit} строк из {total_rows}) ==="
    )
    # Красивый вывод без индекса
    if df.empty:
        print("Таблица пустая.")
    else:
        print(df.to_string(index=False))


def main() -> None:
    """
    Подключается к базе и выполняет тестовые запросы:
    1. Проверяет, что база отвечает (SELECT 1).
    2. Выводит версию ClickHouse.
    3. Показывает список таблиц в базе test.
    4. Для каждой таблицы выводит количество строк и пример данных.
    """
    client = get_client()

    # Простой тестовый запрос
    result = client.execute("SELECT 1")
    print("Результат SELECT 1:", result)

    # Версия ClickHouse
    version = client.execute("SELECT version()")
    print("Версия ClickHouse:", version)

    # Список таблиц
    tables: List[Tuple[str]] = client.execute("SHOW TABLES FROM test")
    table_names = [row[0] for row in tables]
    print("Таблицы в базе test:", table_names)

    # Прогоняемся по всем таблицам базы test
    for table in table_names:
        full_name = f"test.{table}"
        print_table_sample(client, full_name, limit=5)


if __name__ == "__main__":
    main()
