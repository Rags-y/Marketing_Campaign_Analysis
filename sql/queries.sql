-- =========================================================
-- 1. CONVERSION PERFORMANCE ACROSS ALL SIX CAMPAIGNS
-- =========================================================

SELECT
    'Campaign 1' AS campaign,
    SUM(AcceptedCmp1) AS conversions,
    COUNT(*) AS customers_contacted,
    ROUND(100.0 * SUM(AcceptedCmp1) / COUNT(*), 2) AS conversion_rate_pct
FROM customers

UNION ALL

SELECT
    'Campaign 2',
    SUM(AcceptedCmp2),
    COUNT(*),
    ROUND(100.0 * SUM(AcceptedCmp2) / COUNT(*), 2)
FROM customers

UNION ALL

SELECT
    'Campaign 3',
    SUM(AcceptedCmp3),
    COUNT(*),
    ROUND(100.0 * SUM(AcceptedCmp3) / COUNT(*), 2)
FROM customers

UNION ALL

SELECT
    'Campaign 4',
    SUM(AcceptedCmp4),
    COUNT(*),
    ROUND(100.0 * SUM(AcceptedCmp4) / COUNT(*), 2)
FROM customers

UNION ALL

SELECT
    'Campaign 5',
    SUM(AcceptedCmp5),
    COUNT(*),
    ROUND(100.0 * SUM(AcceptedCmp5) / COUNT(*), 2)
FROM customers

UNION ALL

SELECT
    'Campaign 6',
    SUM(Response),
    COUNT(*),
    ROUND(100.0 * SUM(Response) / COUNT(*), 2)
FROM customers;


-- =========================================================
-- 2. CAMPAIGN 6 PROFIT IF ALL CUSTOMERS ARE CONTACTED
-- =========================================================

SELECT
    COUNT(*) AS customers_contacted,
    SUM(Response) AS conversions,
    MAX(Z_CostContact) AS cost_per_contact,
    MAX(Z_Revenue) AS revenue_per_conversion,
    COUNT(*) * MAX(Z_CostContact) AS total_contact_cost,
    SUM(Response) * MAX(Z_Revenue) AS total_conversion_revenue,
    SUM(Response) * MAX(Z_Revenue)
        - COUNT(*) * MAX(Z_CostContact) AS campaign_profit
FROM customers;


-- =========================================================
-- 3. CAMPAIGN 6 CONVERSION RATE BY EDUCATION
-- =========================================================

SELECT
    Education AS segment,
    COUNT(*) AS customers,
    SUM(Response) AS conversions,
    ROUND(100.0 * SUM(Response) / COUNT(*), 2) AS conversion_rate_pct,
    ROUND(AVG(
        MntWines + MntFruits + MntMeatProducts
        + MntFishProducts + MntSweetProducts + MntGoldProds
    ), 2) AS mean_total_spend
FROM customers
GROUP BY Education
ORDER BY conversion_rate_pct DESC;


-- =========================================================
-- 4. CAMPAIGN 6 CONVERSION RATE BY CLEANED MARITAL STATUS
-- =========================================================

SELECT
    Marital_Status_Clean AS segment,
    COUNT(*) AS customers,
    SUM(Response) AS conversions,
    ROUND(100.0 * SUM(Response) / COUNT(*), 2) AS conversion_rate_pct,
    ROUND(AVG(
        MntWines + MntFruits + MntMeatProducts
        + MntFishProducts + MntSweetProducts + MntGoldProds
    ), 2) AS mean_total_spend
FROM customers
GROUP BY Marital_Status_Clean
ORDER BY conversion_rate_pct DESC;
