-- lose_rate_by_level.sql
-- Лузрейт по уровням в разрезе стран.
-- Лузрейт = количество фейлов уровня / количество стартов уровня.

SELECT
    level,
    country,
    level_starts,
    level_fails,
    -- доля (0–1)
    level_fails / toFloat64(level_starts) AS lose_rate,
    -- проценты (0–100), округлённые до 2 знаков
    round(level_fails / toFloat64(level_starts) * 100, 2) AS lose_rate_percent
FROM
(
    SELECT
        e.level AS level,
        coalesce(nullIf(d.country, ''), 'Unknown') AS country,
        -- сколько раз уровень запускали
        countIf(e.event = 'level_started') AS level_starts,
        -- сколько раз уровень зафейлили
        countIf(e.event = 'level_failed') AS level_fails
    FROM test.events AS e
    LEFT JOIN test.devices AS d
        ON e.device_id = d.device_id
    -- Можно ограничить только реальные уровни, если нужно:
    -- WHERE e.level > 0
    GROUP BY
        e.level,
        country
) AS t
-- отбрасываем уровни/страны, где не было ни одного старта
WHERE level_starts > 0
ORDER BY
    level,
    country;
