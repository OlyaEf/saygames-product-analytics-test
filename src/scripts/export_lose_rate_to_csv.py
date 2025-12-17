"""
Скрипт для выгрузки лузрейта по уровням в CSV для дальнейшей визуализации в Tableau.

Что делает:
1. Получает DataFrame с лузрейтом по уровням и странам из analytics.get_lose_rate_df().
2. Создаёт (при необходимости) папку data/ в корне проекта.
3. Сохраняет результат в файл data/lose_rate_by_level.csv без индекса.

Запуск из корня проекта:
    poetry run python src/scripts/export_lose_rate_to_csv.py
"""

from pathlib import Path

from analytics.lose_rate_data import get_lose_rate_df


def main() -> None:
    """
    Выгружает данные по лузрейту в CSV.
    """
    project_root = Path(__file__).resolve().parents[2]

    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)

    # Получаем DataFrame с лузрейтом
    df = get_lose_rate_df()

    output_path = data_dir / "lose_rate_by_level.csv"

    # Сохраняем без индекса
    df.to_csv(output_path, index=False)

    print(f"CSV с лузрейтом сохранён в: {output_path}")
    print(f"Строк в файле: {len(df)}")
    print("Колонки:", ", ".join(df.columns))


if __name__ == "__main__":
    main()
