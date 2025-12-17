"""
Скрипт для проверки CTE `sessions` из session_duration_by_number.sql.

Что делает:
1. Берёт тот же базовый расчёт сессий (device_id + session),
   что и в CTE `sessions`.
2. Выводит несколько строк: device_id, session, session_start,
   session_end, session_duration_sec.
3. Позволяет глазами убедиться, что длительность считается адекватно.

Запуск из корня проекта:
    poetry run python src/dev/test_session_duration_cte.py
"""

from typing import List

from core.db import get_client


def main() -> None:
    """
    Выполняет "сырую" выборку по сессиям и печатает первые строки.
    """
    sql = """
    SELECT
        e.device_id,
        e.session,
        min(e.server_time) AS session_start,
        max(e.server_time) AS session_end,
        dateDiff('second', min(e.server_time), max(e.server_time)) AS session_duration_sec
    FROM test.events AS e
    GROUP BY
        e.device_id,
        e.session
    ORDER BY
        e.device_id,
        session_start
    LIMIT 20
    """

    client = get_client()
    rows, columns_with_types = client.execute(sql, with_column_types=True)
    columns: List[str] = [name for name, _ in columns_with_types]

    print(f"Всего строк в выборке: {len(rows)} (ограничено LIMIT 20)\n")

    for row in rows:
        row_dict = dict(zip(columns, row))
        print(row_dict)


if __name__ == "__main__":
    main()
