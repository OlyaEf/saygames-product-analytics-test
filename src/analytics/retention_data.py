"""
Модуль с логикой подготовки датасета по ретеншену D1/D7.

Здесь:
- загрузка SQL для ретеншена,
- выполнение запроса в ClickHouse,
- возврат результата в виде pandas.DataFrame.
"""

from pathlib import Path
from typing import List

import pandas as pd

from core.db import get_client

def load_retention_sql() -> str:
    """
    Загружает SQL-запрос ретеншена из sql/retention_by_country.sql.

    :return: Строка с SQL-запросом.
    """
    project_root = Path(__file__).resolve().parents[2]
    sql_path = project_root / "sql" / "retention_by_country.sql"

    with sql_path.open("r", encoding="utf-8") as f:
        return f.read()

def get_retention_df() -> pd.DataFrame:
    """
    Выполняет запрос ретеншена D1/D7 в ClickHouse
    и возвращает результат в виде DataFrame.

    Колонки:
        - first_date
        - country
        - installs
        - retained_d1
        - retained_d7
        - retention_d1
        - retention_d7
        - retention_d1_percent
        - retention_d7_percent
    """
    sql = load_retention_sql()
    client = get_client()

    rows, columns_with_types = client.execute(sql, with_column_types=True)
    columns: List[str] = [name for name, _ in columns_with_types]

    df = pd.DataFrame(rows, columns=columns)
    return df
