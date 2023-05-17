{{ 
    config(
        materialized='view'
    ) 
}}


WITH expenses AS (
    SELECT raw.*
    
    FROM {{ source('finance', 'raw_data') }} AS raw
    JOIN {{ ref('binary_type') }} AS type
    ON raw.type = type.type
    
    WHERE type.binary_type = 'EXPENSES'
)

, income AS (
    SELECT raw.*
    
    FROM {{ source('finance', 'raw_data') }} AS raw
    JOIN {{ ref('binary_type') }} AS type
    ON raw.type = type.type
    
    WHERE type.binary_type = 'INCOME'
    
)


, monthly_expenses AS (
    SELECT
        year
        , month
        , ROUND(SUM(COST), 2) AS expenses
    FROM expenses
    GROUP BY year, month
    ORDER BY year, month
)


, monthly_income AS (
    SELECT
        year
        , month
        , ROUND(SUM(cost), 2) AS income
    FROM income
    GROUP BY year, month
    ORDER BY year, month
)


SELECT
    e.year
    , e.month
    , IFNULL(e.expenses, 0) AS expenses
    , IFNULL(i.income, 0) AS income
    , ROUND(IFNULL(i.income, 0) - IFNULL(e.expenses, 0), 2) AS savings
FROM monthly_expenses AS e
LEFT OUTER JOIN monthly_income AS i
ON e.year = i.year AND e.month = i.month

UNION DISTINCT

SELECT
    i.year
    , i.month
    , IFNULL(e.expenses, 0) AS expenses
    , IFNULL(i.income, 0) AS income
    , ROUND(IFNULL(i.income, 0) - IFNULL(e.expenses, 0), 2) AS savings
FROM monthly_expenses AS e
RIGHT OUTER JOIN monthly_income AS i
ON e.year = i.year AND e.month = i.month

ORDER BY 1,2