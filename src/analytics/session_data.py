"""
Модуль для подготовки датасета по средней длительности игровых сессий.

Метрика из ТЗ:
    Средняя продолжительность игровой сессии в зависимости от её номера
    (первая, вторая и т.д.) в разрезе стран, с учётом выбросов.

Задача модуля:
    - выполнить SQL-запрос из sql/session_duration_by_number.sql;
    - вернуть результат в виде pandas.DataFrame;
    - добавить удобную колонку со средней длительностью в минутах.
"""

from pathlib import Path
from typing import List

import pandas as pd

from core.db import get_client


def load_session_duration_sql() -> str:
    """
    Загружает текст SQL-запроса по средней длительности сессий.

    Файл ожидается в корне проекта, в папке sql:
        sql/session_duration_by_number.sql
    """
    project_root = Path(__file__).resolve().parents[2]
    sql_path = project_root / "sql" / "session_duration_by_number.sql"

    with sql_path.open("r", encoding="utf-8") as f:
        return f.read()


def get_session_duration_df() -> pd.DataFrame:
    """
    Выполняет запрос средней длительности сессий и возвращает данные
    в виде DataFrame.

    Ожидаемые колонки из SQL:
    - session_number  — номер сессии (1-я, 2-я, 3-я, ... для игрока)
    - country  — страна игрока
    - sessions_count  — сколько сессий этого номера и страны попало в выборку
    - avg_session_duration_sec  — средняя длительность сессии (в секундах)

    Дополнительно:
    - добавляем колонку avg_session_duration_min (в минутах)
        для удобства визуализации в Tableau.
    """
    sql = load_session_duration_sql()
    client = get_client()

    rows, columns_with_types = client.execute(sql, with_column_types=True)
    columns: List[str] = [name for name, _ in columns_with_types]

    df = pd.DataFrame(rows, columns=columns)

    # Переведём среднюю длительность из секунд в минуты (с плавающей точкой)
    if "avg_session_duration_sec" in df.columns:
        df["avg_session_duration_min"] = df["avg_session_duration_sec"] / 60.0

    return df
