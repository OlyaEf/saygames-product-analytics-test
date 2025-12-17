"""
Скрипт для точечной проверки расчёта ретеншена по одной когорте.

Что делает:
1. Выполняет запрос по таблице test.devices для когорты:
   first_date = '2021-11-17', country = 'AD'.
2. Для каждого игрока выводит:
   - device_id
   - first_date
   - массив dates
   - флаг has_d1: есть ли визит на день +1 (D1)
   - флаг has_d7: есть ли визит на день +7 (D7)

Так мы можем руками проверить, что:
- сумма has_d1 == retained_d1
- сумма has_d7 == retained_d7
из агрегированного запроса retention_by_country.sql.

Запуск из корня проекта:
    poetry run python src/scripts/test_retention_cohort.py
"""

from typing import List

from core.db import get_client


def main() -> None:
    """
    Выполняет выборку по одной когорте и печатает все строки.
    """
    sql = """
    SELECT
        device_id,
        first_date,
        dates,
        has(dates, first_date + 1) AS has_d1,
        has(dates, first_date + 7) AS has_d7
    FROM test.devices
    WHERE first_date = '2021-11-17'
      AND country = 'AD'
    """

    client = get_client()

    # Выполняем запрос с типами колонок
    rows, columns_with_types = client.execute(sql, with_column_types=True)
    columns: List[str] = [name for name, _ in columns_with_types]

    print(f"Строк в когорте: {len(rows)}\n")

    for row in rows:
        row_dict = dict(zip(columns, row))
        print(row_dict)

    # Дополнительно можно посчитать сумму флагов прямо здесь
    total_d1 = sum(row_dict["has_d1"] for row_dict in map(lambda r: dict(zip(columns, r)), rows))
    total_d7 = sum(row_dict["has_d7"] for row_dict in map(lambda r: dict(zip(columns, r)), rows))

    print("\nПроверка сумм флагов:")
    print(f"Суммарно has_d1 = {total_d1}")
    print(f"Суммарно has_d7 = {total_d7}")
    print("Эти числа должны совпадать с retained_d1 и retained_d7 для "
          "first_date = '2021-11-17' и country = 'AD' в агрегированном запросе.")


if __name__ == "__main__":
    main()
