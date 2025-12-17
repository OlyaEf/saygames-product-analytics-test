-- session_duration_by_number.sql
-- Средняя длительность игровой сессии в зависимости от её номера
-- в разрезе стран, с обработкой выбросов.

WITH sessions AS
(
    -- Считаем длительность каждой сессии по (device_id, session)
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
)

SELECT
    t.session_number,
    t.country,
    count() AS sessions_count,
    avg(t.session_duration_sec) AS avg_session_duration_sec
FROM
(
    -- Пронумеровываем сессии игрока, добавляем страну и режем выбросы
    SELECT
        s.device_id,
        s.session,
        s.session_start,
        s.session_end,
        s.session_duration_sec,
        row_number() OVER (
            PARTITION BY s.device_id
            ORDER BY s.session_start
        ) AS session_number,
        coalesce(nullIf(d.country, ''), 'Unknown') AS country
    FROM sessions AS s
    LEFT JOIN test.devices AS d
        ON s.device_id = d.device_id
    -- обработка выбросов по длительности:
    -- слишком короткие (< 10 сек) и слишком длинные (> 4 часов)
    WHERE s.session_duration_sec BETWEEN 10 AND 4 * 3600
) AS t
GROUP BY
    t.session_number,
    t.country
ORDER BY
    t.session_number,
    t.country;
