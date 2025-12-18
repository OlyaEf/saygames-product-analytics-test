# Описание расчёта метрик

Ниже описано, как были посчитаны метрики для дашборда по проекту **Helicopter Escape 3D** на данных ClickHouse.

## Источники данных

- `test.devices` — агрегированная информация по игроку:
  - `device_id` — идентификатор игрока
  - `first_date` — дата регистрации/инсталла (когортная дата)
  - `dates` — массив дат, когда игрок заходил в игру
  - `country` — страна игрока

- `test.events` — события игрока:
  - `device_id`, `session`
  - `server_time`, `server_date`
  - `event` (`app_start`, `level_started`, `level_completed`, `level_failed`)
  - `level`
  - `param1` (для `level_completed/failed` — время прохождения уровня в секундах)

### Нормализация country
Во всех запросах страна приводится к единому значению, если она отсутствует:
- `country = NULL` или пустая строка `''` → `'Unknown'`

Это сделано, чтобы:
- не появлялись отдельные группы с пустым `country`
- фильтр по стране в Tableau работал корректно и предсказуемо

Используется выражение:
`coalesce(nullIf(country, ''), 'Unknown')`

---

## Метрика 1. Retention D1 и D7 (классический, по когортам)

**Задача:** посчитать ретеншен 1-го и 7-го дней в разрезе:
- `first_date` (дата инсталла/регистрации)
- `country`

### Определения
- **Когорта**: все игроки с одинаковыми `first_date` и `country`
- **Installs**: количество игроков в когорте
- **Retained D1**: игрок считается вернувшимся на D1, если в массиве `dates` есть дата `first_date + 1`
- **Retained D7**: игрок считается вернувшимся на D7, если в массиве `dates` есть дата `first_date + 7`

### Формулы
- `retention_d1 = retained_d1 / installs`
- `retention_d7 = retained_d7 / installs`

Также дополнительно считаются проценты:
- `retention_d1_percent = round(retained_d1 / installs * 100, 2)`
- `retention_d7_percent = round(retained_d7 / installs * 100, 2)`

### Реализация в SQL
- `installs = count()`
- `retained_d1 = sum(has(dates, first_date + 1))`
- `retained_d7 = sum(has(dates, first_date + 7))`

### Визуализация в Tableau (Retention)
- Ось X: `WEEK(first_date)` — когорты агрегируются по неделям (чтобы график был стабильнее и читабельнее).
- Значение на графике: `AVG(retention_d1_percent)` и `AVG(retention_d7_percent)` по когортам недели.
  > Почему AVG: каждая точка = среднее по когортам, попавшим в неделю.
  > Если нужен “общий” ретеншен недели, корректнее считать взвешенно: SUM(retained) / SUM(installs).
- Фильтр качества когорты: `Min installs (cohort)` — исключаем маленькие когорты, чтобы убрать шум.

---

## Метрика 2. Lose Rate по уровням

**Задача:** посчитать лузрейт (долю фейлов) для каждого уровня в разрезе стран.

### Определения
- **Level starts**: число запусков уровня (события `level_started`)
- **Level fails**: число неудачных прохождений (события `level_failed`)
- **Lose rate**: отношение фейлов к стартам

### Формулы
- `lose_rate = level_fails / level_starts`
- `lose_rate_percent = round(level_fails / level_starts * 100, 2)`

### Реализация в SQL
- Берём события из `test.events`
- Присоединяем страну из `test.devices` по `device_id` через `LEFT JOIN`
- Считаем:
  - `level_starts = countIf(event = 'level_started')`
  - `level_fails = countIf(event = 'level_failed')`
- Группируем по `(level, country)`
- Исключаем строки, где `level_starts = 0`, чтобы не было деления на ноль:
  - `WHERE level_starts > 0`

### Tableau: Top N уровней для Lose Rate
Чтобы график lose rate был читаемым при большом числе уровней, добавлены параметр и calculated fields:

- **Параметр:** `Top N levels` (Integer; например 10/20/30/50) — сколько уровней показывать.
- **Ранг уровня по lose rate:**
```tableau
RANK_DENSE(AVG([lose_rate_percent]), 'desc')
```

## Фильтр Top N: 
```tableau 
[Level rank by lose rate] <= [Top N levels]
```

---

## Метрика 3. Средняя длительность игровой сессии по её номеру (с обработкой выбросов)

**Задача:** посчитать среднюю длительность 1-й, 2-й, 3-й и т.д. сессии игрока
в разрезе стран, учитывая, что в данных могут быть выбросы.

### Шаг 1. Расчёт длительности каждой сессии
Сессия идентифицируется парой `(device_id, session)`.

Для каждой сессии считаем:
- `session_start = min(server_time)`
- `session_end = max(server_time)`
- `session_duration_sec = dateDiff('second', session_start, session_end)`

> Примечание: длительность оценивается по `server_time` (времени прихода событий на сервер).

### Шаг 2. Нумерация сессий игрока
Для каждого игрока (`device_id`) упорядочиваем его сессии по времени старта
и присваиваем номер:
- `session_number = row_number() over (partition by device_id order by session_start)`

То есть:
- первая по времени сессия игрока → `session_number = 1`
- вторая → `2` и т.д.

### Шаг 3. Обработка выбросов по длительности
Чтобы исключить аномальные значения, применён фильтр:
- удаляем слишком короткие сессии `< 10 секунд`
- удаляем слишком длинные сессии `> 4 часов`

Реализация:
`WHERE session_duration_sec BETWEEN 10 AND 4 * 3600`

### Шаг 4. Агрегация метрики
После фильтрации считаем среднюю длительность по:
- `session_number`
- `country`

Поля результата:
- `sessions_count = count()` — сколько сессий попало в расчёт
- `avg_session_duration_sec = avg(session_duration_sec)` — средняя длительность

### Визуализация в Tableau (Session Duration)
- Лист: `Session Duration by Session Number`, тип — Line.
- X: `session_number`
- Y: `AVG(avg_session_duration_min)` (средняя длительность сессии в минутах)
- Цвет: `country` (линии по странам)
- Фильтр: `country` (выбор стран)
- Фильтр качества: `sessions_count >= 50` (по умолчанию)
- Фильтр диапазона: `session_number 1–50` (по умолчанию, можно расширять)

---

## Что используется в визуализации (Tableau)

В Tableau загружаются CSV-витрины, сформированные этими SQL-запросами.

Для удобного анализа предусмотрен разрез по странам:
- фильтр `country` применяется ко всем трём графикам
- отсутствующие страны представлены как `'Unknown'`

## Дашборд (Tableau)

- Tableau Public (онлайн): 
<https://public.tableau.com/views/SayGamesHelicopterEscape-draftv1/HelicopterEscape3DRetentionGameplayFunnel?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link>
- Файл воркбука в репозитории: `dashboards/SayGames Helicopter Escape - draft v1.twbx`

> Если онлайн-ссылка недоступна, дашборд можно открыть локально из `.twbx`
> (внутри уже упакованы данные/источники).
