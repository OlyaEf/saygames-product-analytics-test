
"""
Скрипт для выгрузки ретеншена D1/D7 в CSV для Tableau.
"""

from pathlib import Path
from typing import List

from analytics.retention_data import get_retention_df


def main() -> None:
    """
    Выполняет запрос ретеншена и сохраняет результат в CSV.
    """
    project_root = Path(__file__).resolve().parents[2]
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)

    df = get_retention_df()

    output_path = data_dir / "retention_by_country.csv"
    df.to_csv(output_path, index=False)

    print(f"CSV с ретеншеном сохранён в: {output_path}")
    print(f"Строк в файле: {len(df)}")


if __name__ == "__main__":
    main()
