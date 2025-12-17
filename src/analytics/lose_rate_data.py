"""
Модуль для подготовки датасета по лузрейту (lose rate) по уровням в разрезе стран.

Задача:
- выполнить SQL-запрос из sql/lose_rate_by_level.sql в ClickHouse;
- вернуть результат в виде pandas.DataFrame.

Этот модуль не занимается сохранением CSV на диск — только подготовкой данных.
"""

from pathlib import Path
from typing import List

import pandas as pd

from core.db import get_client

def load_lose_rate_sql() -> str:
    """
    Загружает текст SQL-запроса лузрейта из файла sql/lose_rate_by_level.sql.

    :return: Строка с SQL-запросом.
    """

    project_root = Path(__file__).resolve().parents[2]
    sql_path = project_root / 'sql' / 'lose_rate_by_level.sql'

    with sql_path.open('r', encoding='utf-8') as f:
        return f.read()

def get_lose_rate_df() -> pd.DataFrame:
    """
    Выполняет запрос лузрейта и возвращает результат в виде DataFrame.

    Ожидаемые колонки (из lose_rate_by_level.sql):
        - level
        - country
        - level_starts
        - level_fails
        - lose_rate              (доля 0–1)
        - lose_rate_percent      (проценты 0–100, с округлением до 2 знаков)
    """

    sql = load_lose_rate_sql()
    client = get_client()

    rows, columns_with_types = client.execute(sql, with_column_types=True)
    columns: List[str] = [name for name, _ in columns_with_types]

    df = pd.DataFrame(rows, columns=columns)

    return df
