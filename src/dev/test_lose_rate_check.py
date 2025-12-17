"""
Скрипт для проверки корректности расчёта лузрейта по уровням.

Идея:
1. Выполнить агрегирующий запрос из sql/lose_rate_by_level.sql.
2. Взять одну строку (level + country) из результата.
3. Ещё раз отдельно пересчитать для этой пары:
   - сколько было level_started,
   - сколько было level_failed
   по "сырым" событиям test.events + test.devices.
4. Сравнить агрегированные значения с пересчитанными.

Запуск из корня проекта:
    poetry run python src/dev/test_lose_rate_check.py
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
    client = get_client()

    # 1. Выполняем агрегирующий запрос
    agg_sql = load_sql("lose_rate_by_level.sql")
    agg_rows, agg_columns_with_types = client.execute(agg_sql, with_column_types=True)
    agg_columns: List[str] = [name for name, _ in agg_columns_with_types]

    print(f"Всего строк в агрегате: {len(agg_rows)}")

    if not agg_rows:
        print("Агрегатный запрос вернул 0 строк, проверять нечего.")
        return

    # Берём одну строку для проверки (для простоты — первую)
    sample_row = agg_rows[0]
    sample = dict(zip(agg_columns, sample_row))

    level = sample["level"]
    country = sample["country"]
    level_starts_agg = sample["level_starts"]
    level_fails_agg = sample["level_fails"]
    lose_rate_agg = sample["lose_rate"]

    print("\nПроверяем одну пару (level, country) из агрегата:")
    print(f"level   = {level}")
    print(f"country = {repr(country)}")
    print(f"Агрегат: level_starts = {level_starts_agg}, level_fails = {level_fails_agg}, lose_rate = {lose_rate_agg}")

    # 2. Пересчитываем те же значения "в лоб" по сырым событиям
    country_escaped = country.replace("'", "''") if country is not None else ""

    raw_sql = f"""
    SELECT
        countIf(e.event = 'level_started') AS level_starts_raw,
        countIf(e.event = 'level_failed') AS level_fails_raw
    FROM test.events AS e
    LEFT JOIN test.devices AS d
        ON e.device_id = d.device_id
    WHERE e.level = {int(level)}
      AND d.country = '{country_escaped}'
    """

    raw_rows, raw_columns_with_types = client.execute(raw_sql, with_column_types=True)
    if not raw_rows:
        print("\n⚠ raw-запрос вернул 0 строк — что-то странно, должно быть минимум 1.")
        return

    level_starts_raw, level_fails_raw = raw_rows[0]

    print("\nПересчёт по сырым событиям:")
    print(f"level_starts_raw = {level_starts_raw}")
    print(f"level_fails_raw  = {level_fails_raw}")

    # 3. Сравниваем counts
    ok_starts = (level_starts_raw == level_starts_agg)
    ok_fails = (level_fails_raw == level_fails_agg)

    # 4. Явно проверяем формулу лузрейта
    if level_starts_raw > 0:
        lose_rate_raw = level_fails_raw / float(level_starts_raw)
    else:
        lose_rate_raw = None

    print(f"\nЛузрейт, пересчитанный в Python: {lose_rate_raw}")

    # сравниваем с некоторой допустимой погрешностью (на всякий случай)
    tol = 1e-9
    ok_lose_rate = (
        lose_rate_raw is None and lose_rate_agg is None
        or lose_rate_raw is not None and abs(lose_rate_raw - lose_rate_agg) < tol
    )

    if ok_starts and ok_fails and ok_lose_rate:
        print("\n✅ OK: и counts, и формула лузрейта совпадают с сырыми данными.")
    else:
        print("\n⚠️ НЕСОВПАДЕНИЕ!")
        if not ok_starts:
            print(f"- level_starts: агрегат = {level_starts_agg}, raw = {level_starts_raw}")
        if not ok_fails:
            print(f"- level_fails: агрегат = {level_fails_agg}, raw = {level_fails_raw}")
        if not ok_lose_rate:
            print(f"- lose_rate: агрегат = {lose_rate_agg}, raw = {lose_rate_raw}")


if __name__ == "__main__":
    main()
