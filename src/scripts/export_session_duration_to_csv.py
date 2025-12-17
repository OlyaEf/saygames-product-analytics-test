"""
Скрипт для выгрузки метрики средней длительности сессий в CSV
для дальнейшей визуализации в Tableau.

Что делает:
    1. Получает DataFrame из analytics.get_session_duration_df().
    2. Создаёт (при необходимости) папку data/ в корне проекта.
    3. Сохраняет результат в файл:
           data/session_duration_by_number.csv

Запуск из корня проекта:
    poetry run python src/scripts/export_session_duration_to_csv.py
"""

from pathlib import Path

from analytics.session_data import get_session_duration_df


def main() -> None:
    """
    Выгружает данные по средней длительности сессий в CSV.
    """
    # Корень проекта: saygames-product-analytics-test
    project_root = Path(__file__).resolve().parents[2]

    # Папка для подготовленных датасетов
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)

    # Получаем DataFrame с метрикой
    df = get_session_duration_df()

    # Путь к файлу CSV
    output_path = data_dir / "session_duration_by_number.csv"

    # Сохраняем без индекса
    df.to_csv(output_path, index=False)

    print(f"CSV со средней длительностью сессий сохранён в: {output_path}")
    print(f"Строк в файле: {len(df)}")
    print("Колонки:", ", ".join(df.columns))


if __name__ == "__main__":
    main()
