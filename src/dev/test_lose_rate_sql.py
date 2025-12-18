"""
Скрипт для проверки SQL-запроса лузрейта по уровням.

Что делает:
1. Загружает SQL из sql/lose_rate_by_level.sql.
2. Выполняет запрос в ClickHouse.
3. Печатает количество строк и первые 10 строк результата.
4. Проверяет, что пустых стран (''/NULL) больше нет, а вместо них используется 'Unknown'.
5. Печатает статистику по 'Unknown'.
6. Проверяет по сырым данным (test.events) количество уникальных значений level.

Запуск из корня проекта:
    poetry run python src/dev/test_lose_rate_sql.py
"""

from pathlib import Path
from typing import List

from core.db import get_client


def load_sql(filename: str) -> str:
    """
    Загружает текст SQL-запроса из папки sql в корне проекта.

    :param filename: Имя файла (например, 'lose_rate_by_level.sql').
    :return: Строка с SQL-запросом.
    """
    project_root = Path(__file__).resolve().parents[2]
    sql_path = project_root / "sql" / filename
    with sql_path.open("r", encoding="utf-8") as f:
        return f.read()


def main() -> None:
    """
    Выполняет запрос лузрейта и выводит несколько строк результата,
    а также проверяет нормализацию поля country.
    Дополнительно выводит количество уникальных level в сырых данных test.events.
    """
    sql = load_sql("lose_rate_by_level.sql")
    client = get_client()

    rows, columns_with_types = client.execute(sql, with_column_types=True)
    columns: List[str] = [name for name, _ in columns_with_types]

    print(f"Всего строк в результате: {len(rows)}")
    print("Первые 10 строк:\n")
    for row in rows[:10]:
        print(dict(zip(columns, row)))

    # --- ДОБАВЛЕНО: проверка уникальных level в сырых данных ---
    raw_levels_sql = """
    SELECT uniqExact(level) AS uniq_levels
    FROM test.events
    """
    uniq_levels = client.execute(raw_levels_sql)[0][0]
    print("\n=== Проверка сырых данных test.events ===")
    print(f"Уникальных значений level в test.events: {uniq_levels}")
    # ----------------------------------------------------------

    # Проверяем наличие поля country
    try:
        country_idx = columns.index("country")
    except ValueError:
        print("\nПоле 'country' не найдено в результатах — проверь SQL (SELECT country ...).")
        return

    # 1) Проверка: не осталось ли пустых/NULL стран
    bad_country_rows = [
        dict(zip(columns, row))
        for row in rows
        if row[country_idx] in ("", None)
    ]

    print(f"\nСтрок с пустой страной (country = '' или NULL): {len(bad_country_rows)}")
    if bad_country_rows:
        print("Первые 5 строк с пустой страной (это плохо, значит нормализация не сработала):\n")
        for row_dict in bad_country_rows[:5]:
            print(row_dict)

    # 2) Проверка: сколько строк теперь с 'Unknown'
    unknown_rows = [
        dict(zip(columns, row))
        for row in rows
        if str(row[country_idx]).strip() == "Unknown"
    ]

    print(f"\nСтрок со страной 'Unknown': {len(unknown_rows)}")
    if unknown_rows:
        print("Первые 5 строк с 'Unknown':\n")
        for row_dict in unknown_rows[:5]:
            print(row_dict)

    # 3) Итоговая подсказка
    if not bad_country_rows:
        print("\n✅ Нормализация country выглядит корректно: пустых/NULL значений нет.")
    else:
        print("\n❌ Остались пустые/NULL значения country — проверь coalesce/nullIf в SQL.")


if __name__ == "__main__":
    main()
