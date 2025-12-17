"""
Скрипт для проверки SQL-запроса средней длительности сессий по их номеру.

Что делает:
1. Загружает SQL из sql/session_duration_by_number.sql.
2. Выполняет запрос в ClickHouse.
3. Печатает количество строк и первые 10 строк результата
   в удобном для чтения виде.

Запуск из корня проекта:
    poetry run python src/dev/test_session_duration_sql.py
"""

from pathlib import Path
from typing import List

from core.db import get_client


def load_sql(filename: str) -> str:
    """
    Загружает текст SQL-запроса из папки sql в корне проекта.

    :param filename: Имя файла (например, 'session_duration_by_number.sql').
    :return: Строка с SQL-запросом.
    """
    project_root = Path(__file__).resolve().parents[2]
    sql_path = project_root / "sql" / filename
    with sql_path.open("r", encoding="utf-8") as f:
        return f.read()


def main() -> None:
    """
    Выполняет запрос средней длительности сессий и выводит несколько строк результата.
    """
    sql = load_sql("session_duration_by_number.sql")
    client = get_client()

    # Выполняем запрос с информацией о типах колонок
    rows, columns_with_types = client.execute(sql, with_column_types=True)
    columns: List[str] = [name for name, _ in columns_with_types]

    print(f"Всего строк в результате: {len(rows)}")
    print("Первые 10 строк:\n")

    for row in rows[:10]:
        row_dict = dict(zip(columns, row))
        print(row_dict)


if __name__ == "__main__":
    main()
