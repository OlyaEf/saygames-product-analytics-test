-- retention_by_country.sql
-- Классический ретеншен D1 и D7 по когортам (дата инсталла + страна)

SELECT
    first_date,
    country,
    installs,
    retained_d1,
    retained_d7,
    -- доли (0–1)
    retained_d1 / toFloat64(installs) AS retention_d1,
    retained_d7 / toFloat64(installs) AS retention_d7,
    -- проценты (0–100), округлённые до 2 знаков
    round(retained_d1 / toFloat64(installs) * 100, 2) AS retention_d1_percent,
    round(retained_d7 / toFloat64(installs) * 100, 2) AS retention_d7_percent
FROM
(
    SELECT
        first_date,
        coalesce(nullIf(country, ''), 'Unknown') AS country,
        count() AS installs,
        -- игрок считается вернувшимся на D1,
        -- если в массиве dates есть дата first_date + 1 день
        sum(has(dates, first_date + 1)) AS retained_d1,
        -- игрок считается вернувшимся на D7,
        -- если в массиве dates есть дата first_date + 7 дней
        sum(has(dates, first_date + 7)) AS retained_d7
    FROM test.devices
    GROUP BY
        first_date,
        country
) AS t
ORDER BY
    first_date,
    country;
