"""
Скрипт для проверки запроса ретеншена D1/D7.

Что делает:
1. Загружает SQL из sql/retention_by_country.sql.
2. Выполняет запрос в ClickHouse.
3. Печатает первые 10 строк результата в читаемом виде.

Запуск из корня проекта:
    poetry run python src/test_retention_sql.py
"""

from pathlib import Path
from typing import List

from core.db import get_client


def load_sql(filename: str) -> str:
    """
    Загружает текст SQL-запроса из папки sql.

    :param filename: Имя файла (например, 'retention_by_country.sql').
    :return: Строка с SQL-запросом.
    """
    project_root = Path(__file__).resolve().parents[2]
    sql_path = project_root / "sql" / filename
    with sql_path.open("r", encoding="utf-8") as f:
        return f.read()


def main() -> None:
    """
    Выполняет запрос ретеншена и выводит несколько строк результата.
    """
    sql = load_sql("retention_by_country.sql")

    client = get_client()

    # Выполняем запрос с типами колонок
    rows, columns_with_types = client.execute(sql, with_column_types=True)
    columns: List[str] = [name for name, _ in columns_with_types]

    print(f"Всего строк в результате: {len(rows)}")
    print("Первые 10 строк:\n")

    for row in rows[:10]:
        row_dict = dict(zip(columns, row))
        print(row_dict)


if __name__ == "__main__":
    main()
