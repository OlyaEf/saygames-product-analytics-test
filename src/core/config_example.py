
"""
Пример файла настроек для подключения к ClickHouse.

Как пользоваться:
1. Скопируйте этот файл под именем config.py:
      cp src/config_example.py src/config.py
2. В файле config.py подставьте реальные значения доступа к базе.

ВАЖНО:
Файл config.py добавлен в .gitignore и не должен попадать в репозиторий.
"""

CLICKHOUSE_HOST = "blackpearl.saygames.io"
CLICKHOUSE_PORT = 9000
CLICKHOUSE_USER = "your_user"
CLICKHOUSE_PASSWORD = "your_password"
CLICKHOUSE_DB = "test"
