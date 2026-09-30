from pathlib import Path
import duckdb

WAREHOUSE_PATH = Path("warehouse/fintinel.duckdb")

if not WAREHOUSE_PATH.exists():
    raise FileNotFoundError(
        f"W​​arehouse not found: {WAREHOUSE_PATH}"
    )

con = duckdb.connect(str(WAREHOUSE_PATH))

print("Connected to Fintinel warehouse.")

con.execute("""
    CREATE OR REPLACE TABLE analytics.previous_credit_repayment AS

    SELECT
        SK_ID_CURR,
        SK_ID_PREV,

        COUNT(*) AS installment_count,

        COUNT(DAYS_ENTRY_PAYMENT) AS observed_payment_count,

        CASE
    WHEN COUNT(*) FILTER (
        WHERE DAYS_ENTRY_PAYMENT IS NOT NULL
          AND AMT_PAYMENT IS NOT NULL
    ) > 0
    THEN
        COUNT(*) FILTER (
            WHERE PAYMENT_DELAY_DAYS > 0
        )::DOUBLE
        /
        COUNT(*) FILTER (
            WHERE DAYS_ENTRY_PAYMENT IS NOT NULL
              AND AMT_PAYMENT IS NOT NULL
        )
    ELSE NULL
    END AS late_payment_rate,

    CASE
    WHEN COUNT(*) FILTER (
        WHERE DAYS_ENTRY_PAYMENT IS NOT NULL
          AND AMT_PAYMENT IS NOT NULL
    ) > 0
    THEN
        COUNT(*) FILTER (
            WHERE PAYMENT_DIFFERENCE > 0
        )::DOUBLE
        /
        COUNT(*) FILTER (
            WHERE DAYS_ENTRY_PAYMENT IS NOT NULL
              AND AMT_PAYMENT IS NOT NULL
        )
    ELSE NULL
    END AS underpayment_rate,

        SUM(
            CASE
                WHEN IS_LATE = TRUE THEN 1
                ELSE 0
            END
        ) AS late_payment_count,

        SUM(
            CASE
                WHEN IS_UNDERPAID = TRUE THEN 1
                ELSE 0
            END
        ) AS underpayment_count

    FROM cleaned.installments

    GROUP BY
        SK_ID_CURR,
        SK_ID_PREV;
""")

print("analytics.previous_credit_repayment created.")

row_count = con.execute("""
    SELECT COUNT(*)
    FROM analytics.previous_credit_repayment;
""").fetchone()[0]

print(f"Previous-credit repayment rows: {row_count}")

source_grain_count = con.execute("""
    SELECT COUNT(*)
    FROM (
        SELECT DISTINCT
            SK_ID_CURR,
            SK_ID_PREV
        FROM cleaned.installments
    );
""").fetchone()[0]

duplicate_grain_count = con.execute("""
    SELECT COUNT(*)
    FROM (
        SELECT
            SK_ID_CURR,
            SK_ID_PREV,
            COUNT(*) AS row_count
        FROM analytics.previous_credit_repayment
        GROUP BY
            SK_ID_CURR,
            SK_ID_PREV
        HAVING COUNT(*) > 1
    );
""").fetchone()[0]

print("\n--- PREVIOUS-CREDIT MODEL VALIDATION ---")
print(f"Distinct source credit pairs: {source_grain_count}")
print(f"Analytical model rows: {row_count}")
print(f"Duplicate credit pairs in model: {duplicate_grain_count}")

sample = con.execute("""
    SELECT *
    FROM analytics.previous_credit_repayment
    LIMIT 10;
""").df()

print("\n--- PREVIOUS-CREDIT REPAYMENT SAMPLE ---")
print(sample.to_string(index=False))

validation = con.execute("""
    SELECT
        COUNT(*) AS total_credits,

        SUM(installment_count) AS total_installments,
        SUM(observed_payment_count) AS total_observed_payments,

        SUM(late_payment_count) AS total_late_payments,
        SUM(underpayment_count) AS total_underpayments,

        COUNT(*) FILTER (
            WHERE observed_payment_count < installment_count
        ) AS credits_with_unobserved_payments,

        COUNT(*) FILTER (
            WHERE late_payment_count > observed_payment_count
        ) AS invalid_late_counts,

        COUNT(*) FILTER (
            WHERE underpayment_count > observed_payment_count
        ) AS invalid_underpayment_counts

    FROM analytics.previous_credit_repayment;
""").df()

print("\n--- REPAYMENT AGGREGATION VALIDATION ---")
print(validation.to_string(index=False))

zero_observed = con.execute("""
    SELECT
        COUNT(*) AS credits_with_zero_observed_payments
    FROM analytics.previous_credit_repayment
    WHERE observed_payment_count = 0;
""").df()

print("\n--- ZERO OBSERVED PAYMENT CHECK ---")
print(zero_observed.to_string(index=False))


null_rate_check = con.execute("""
    SELECT
        COUNT(*) FILTER (
            WHERE observed_payment_count = 0
              AND late_payment_rate IS NULL
              AND underpayment_rate IS NULL
        ) AS zero_observed_with_null_rates,

        COUNT(*) FILTER (
            WHERE observed_payment_count = 0
              AND (
                  late_payment_rate IS NOT NULL
                  OR underpayment_rate IS NOT NULL
              )
        ) AS zero_observed_with_invalid_rates

    FROM analytics.previous_credit_repayment;
""").df()

print("\n--- REPAYMENT RATE NULL VALIDATION ---")
print(null_rate_check.to_string(index=False))

credit_relationship = con.execute("""
    SELECT
        COUNT(*) AS repayment_credits,

        COUNT(*) FILTER (
            WHERE p.SK_ID_PREV IS NOT NULL
        ) AS matched_previous_credits,

        COUNT(*) FILTER (
            WHERE p.SK_ID_PREV IS NULL
        ) AS unmatched_previous_credits

    FROM analytics.previous_credit_repayment r

    LEFT JOIN cleaned.previous_application p
        ON r.SK_ID_CURR = p.SK_ID_CURR
       AND r.SK_ID_PREV = p.SK_ID_PREV;
""").df()

print("\n--- CREDIT-LEVEL RELATIONSHIP CHECK ---")
print(credit_relationship.to_string(index=False))

customer_population = con.execute("""
    SELECT
        COUNT(DISTINCT SK_ID_CURR) AS customers_with_repayment_history
    FROM analytics.previous_credit_repayment;
""").df()

print("\n--- REPAYMENT CUSTOMER POPULATION ---")
print(customer_population.to_string(index=False))

con.execute("""
    CREATE OR REPLACE TABLE analytics.customer_repayment_history AS

    SELECT
        SK_ID_CURR,

        COUNT(*) AS previous_credit_count,

        SUM(installment_count) AS total_installments,
        SUM(observed_payment_count) AS observed_payment_count,

        SUM(late_payment_count) AS late_payment_count,
        SUM(underpayment_count) AS underpayment_count,

        CASE
            WHEN SUM(observed_payment_count) > 0
            THEN SUM(late_payment_count)::DOUBLE
                 / SUM(observed_payment_count)
            ELSE NULL
        END AS late_payment_rate,

        CASE
            WHEN SUM(observed_payment_count) > 0
            THEN SUM(underpayment_count)::DOUBLE
                 / SUM(observed_payment_count)
            ELSE NULL
        END AS underpayment_rate,

        COUNT(*) FILTER (
            WHERE observed_payment_count < installment_count
        ) AS credits_with_unobserved_payments

    FROM analytics.previous_credit_repayment

    GROUP BY SK_ID_CURR;
""")

print("analytics.customer_repayment_history created.")

customer_rows = con.execute("""
    SELECT COUNT(*)
    FROM analytics.customer_repayment_history;
""").fetchone()[0]

print(f"Customer repayment-history rows: {customer_rows}")


customer_validation = con.execute("""
    SELECT
        COUNT(*) AS total_customers,

        COUNT(DISTINCT SK_ID_CURR) AS distinct_customers,

        SUM(previous_credit_count) AS total_previous_credits,
        SUM(total_installments) AS total_installments,
        SUM(observed_payment_count) AS total_observed_payments,
        SUM(late_payment_count) AS total_late_payments,
        SUM(underpayment_count) AS total_underpayments,

        COUNT(*) FILTER (
            WHERE late_payment_count > observed_payment_count
        ) AS invalid_late_counts,

        COUNT(*) FILTER (
            WHERE underpayment_count > observed_payment_count
        ) AS invalid_underpayment_counts,

        COUNT(*) FILTER (
            WHERE late_payment_rate < 0
               OR late_payment_rate > 1
        ) AS invalid_late_rates,

        COUNT(*) FILTER (
            WHERE underpayment_rate < 0
               OR underpayment_rate > 1
        ) AS invalid_underpayment_rates

    FROM analytics.customer_repayment_history;
""").df()

print("\n--- CUSTOMER REPAYMENT MODEL VALIDATION ---")
print(customer_validation.to_string(index=False))


# ---------------------------------------------------------
# 5F.5A - CURRENT APPLICANT -> REPAYMENT HISTORY COVERAGE
# ---------------------------------------------------------

applicant_repayment_coverage = con.execute("""
    SELECT
        COUNT(*) AS total_applicants,

        COUNT(DISTINCT a.SK_ID_CURR) AS distinct_applicants,

        COUNT(r.SK_ID_CURR) AS applicants_with_repayment_history,

        COUNT(*) - COUNT(r.SK_ID_CURR)
            AS applicants_without_repayment_history

    FROM cleaned.application AS a

    LEFT JOIN analytics.customer_repayment_history AS r
        ON a.SK_ID_CURR = r.SK_ID_CURR
""").fetchdf()

print("\n--- CURRENT APPLICANT REPAYMENT COVERAGE ---")
print(applicant_repayment_coverage.to_string(index=False))

# ---------------------------------------------------------
# 5F.5B - BUILD CURRENT APPLICANT RISK BASE
# ---------------------------------------------------------

con.execute("""
    CREATE OR REPLACE TABLE analytics.applicant_risk_base AS

    SELECT
        -- Current application
        a.SK_ID_CURR,
        a.TARGET,
        a.AMT_INCOME_TOTAL,
        a.AMT_CREDIT,
        a.AMT_ANNUITY,
        a.AMT_CREDIT / a.AMT_INCOME_TOTAL AS credit_income_ratio,
        a.AMT_ANNUITY / a.AMT_INCOME_TOTAL AS annuity_income_ratio,

        -- Historical repayment activity
        CASE 
            WHEN r.SK_ID_CURR IS NOT NULL THEN 1
            ELSE 0
        END AS has_repayment_history,
        r.previous_credit_count,
        CASE
            WHEN r.SK_ID_CURR IS NOT NULL
            THEN CAST(r.total_installments AS DOUBLE) / r.previous_credit_count
            ELSE NULL
        END AS avg_installments_per_credit,
        CASE
            WHEN r.SK_ID_CURR IS NULL THEN NULL
            WHEN r.late_payment_count > 0
            OR r.underpayment_count > 0 THEN 1
            ELSE 0
        END AS has_repayment_issue,
        r.total_installments,
        r.observed_payment_count,
        r.late_payment_count,
        r.underpayment_count,
        r.late_payment_rate,
        r.underpayment_rate

    FROM cleaned.application AS a

    LEFT JOIN analytics.customer_repayment_history AS r
        ON a.SK_ID_CURR = r.SK_ID_CURR
""")

print("analytics.applicant_risk_base created.")

risk_base_check = con.execute("""
    SELECT
        COUNT(*) AS rows,
        COUNT(DISTINCT SK_ID_CURR) AS distinct_applicants
    FROM analytics.applicant_risk_base
""").df()

print("\n--- APPLICANT RISK BASE CHECK ---")
print(risk_base_check.to_string(index=False))

# ============================================================
# APPLICANT RISK SEGMENTS
# Persistent, interpretable applicant-level segmentation layer
# ============================================================

con.execute("""
CREATE OR REPLACE TABLE analytics.applicant_risk_segments AS

SELECT
    a.*,

    -- --------------------------------------------------------
    -- Affordability segmentation
    -- Fixed thresholds derived from applicant population
    -- annuity_income_ratio quartiles during segmentation design
    -- --------------------------------------------------------
    CASE
        WHEN a.annuity_income_ratio IS NULL THEN 'Unknown'
        WHEN a.annuity_income_ratio <= 0.1148 THEN 'Low burden'
        WHEN a.annuity_income_ratio <= 0.1628 THEN 'Moderate burden'
        WHEN a.annuity_income_ratio <= 0.2291 THEN 'Elevated burden'
        ELSE 'High burden'
    END AS affordability_segment,

    -- --------------------------------------------------------
    -- Repayment-history segmentation
    -- --------------------------------------------------------
    CASE
    WHEN has_repayment_history = 0 THEN 'No history'
    WHEN observed_payment_count = 0 THEN 'No observed payments'
    WHEN has_repayment_issue = 0 THEN 'Clean observed history'
    WHEN has_repayment_issue = 1 THEN 'Observed repayment issue'
    ELSE 'Unknown'
    END AS repayment_segment,

    -- --------------------------------------------------------
    -- Late-payment severity
    -- Thresholds derived from positive late-payment-rate
    -- distribution during segmentation design
    -- --------------------------------------------------------
    CASE
        WHEN has_repayment_history = 0 THEN 'No history'
        WHEN observed_payment_count = 0 THEN 'No observed payments'
        WHEN late_payment_rate = 0 THEN 'None'
        WHEN late_payment_rate <= 0.0492 THEN 'Low'
        WHEN late_payment_rate <= 0.1020 THEN 'Moderate'
        WHEN late_payment_rate <= 0.2000 THEN 'Elevated'
        ELSE 'High'
    END AS late_payment_severity,

    -- --------------------------------------------------------
    -- Underpayment severity
    -- --------------------------------------------------------
    CASE
        WHEN has_repayment_history = 0 THEN 'No history'
        WHEN observed_payment_count = 0 THEN 'No observed payments'
        WHEN underpayment_rate = 0 THEN 'None'
        WHEN underpayment_rate <= 0.0656 THEN 'Low'
        WHEN underpayment_rate <= 0.1379 THEN 'Moderate'
        WHEN underpayment_rate <= 0.2799 THEN 'Elevated'
        ELSE 'High'
    END AS underpayment_severity,

    -- --------------------------------------------------------
    -- Repayment issue pattern
    -- --------------------------------------------------------
    CASE
    WHEN has_repayment_history = 0 THEN 'No history'
    WHEN observed_payment_count = 0 THEN 'No observed payments'
    WHEN late_payment_count = 0 AND underpayment_count = 0 THEN 'Neither issue'
    WHEN late_payment_count > 0 AND underpayment_count = 0 THEN 'Late only'
    WHEN late_payment_count = 0 AND underpayment_count > 0 THEN 'Underpayment only'
    WHEN late_payment_count > 0 AND underpayment_count > 0 THEN 'Both issues'
    ELSE 'Unknown'
    END AS repayment_pattern

FROM analytics.applicant_risk_base a;
""")

segment_rows = con.execute("""
SELECT COUNT(*)
FROM analytics.applicant_risk_segments
""").fetchone()[0]

print("analytics.applicant_risk_segments created.")
print(f"Applicant risk segment rows: {segment_rows}")

# ============================================================
# APPLICANT RISK SCORES
# Interpretable analytical score built from validated
# repayment behavior and affordability components
# ============================================================

con.execute("""
CREATE OR REPLACE TABLE analytics.applicant_risk_scores AS

WITH components AS (

    SELECT
        s.*,

        -- ----------------------------------------------------
        -- Repayment severity levels
        -- Only meaningful when repayment observations exist
        -- ----------------------------------------------------
        CASE s.late_payment_severity
            WHEN 'None' THEN 0
            WHEN 'Low' THEN 1
            WHEN 'Moderate' THEN 2
            WHEN 'Elevated' THEN 3
            WHEN 'High' THEN 4
            ELSE NULL
        END AS late_severity_level,

        CASE s.underpayment_severity
            WHEN 'None' THEN 0
            WHEN 'Low' THEN 1
            WHEN 'Moderate' THEN 2
            WHEN 'Elevated' THEN 3
            WHEN 'High' THEN 4
            ELSE NULL
        END AS underpayment_severity_level,

        -- ----------------------------------------------------
        -- Affordability component: 0–30
        -- ----------------------------------------------------
        CASE s.affordability_segment
            WHEN 'Low burden' THEN 0
            WHEN 'Moderate burden' THEN 10
            WHEN 'Elevated burden' THEN 20
            WHEN 'High burden' THEN 30
            ELSE NULL
        END AS affordability_score

    FROM analytics.applicant_risk_segments s
),

scored AS (

    SELECT
        *,

        -- ----------------------------------------------------
        -- Repayment behavior component: 0–70
        -- Average late + underpayment severity, rescaled
        -- from 0–4 to 0–70
        -- ----------------------------------------------------
        CASE
            WHEN observed_payment_count > 0
            THEN ROUND(
                (
                    (
                        late_severity_level
                        + underpayment_severity_level
                    ) / 2.0
                ) / 4.0 * 70.0,
                2
            )
            ELSE NULL
        END AS behavior_score

    FROM components
),

final AS (

    SELECT
        *,

        -- ----------------------------------------------------
        -- Full analytical score: 0–100
        -- Only produced when both components are available
        -- ----------------------------------------------------
        CASE
            WHEN behavior_score IS NOT NULL
                 AND affordability_score IS NOT NULL
            THEN ROUND(
                behavior_score + affordability_score,
                2
            )
            ELSE NULL
        END AS risk_score,

        -- ----------------------------------------------------
        -- Explicit score availability state
        -- ----------------------------------------------------
        CASE
            WHEN has_repayment_history = 0
                THEN 'No repayment history'

            WHEN observed_payment_count = 0
                THEN 'No observed payments'

            WHEN affordability_score IS NULL
                THEN 'Missing affordability data'

            ELSE 'Full score'
        END AS score_status

    FROM scored
)

SELECT
    *,

    -- --------------------------------------------------------
    -- Distribution-derived analytical tier
    -- --------------------------------------------------------
    CASE
        WHEN risk_score IS NULL THEN 'Unavailable'
        WHEN risk_score <= 17.5 THEN 'Low'
        WHEN risk_score <= 30 THEN 'Moderate'
        WHEN risk_score <= 55 THEN 'Elevated'
        ELSE 'High'
    END AS risk_tier

FROM final;
""")

risk_score_rows = con.execute("""
SELECT COUNT(*)
FROM analytics.applicant_risk_scores
""").fetchone()[0]

print("analytics.applicant_risk_scores created.")
print(f"Applicant risk score rows: {risk_score_rows}")

# ============================================================
# MART: RISK TIER SUMMARY
# ============================================================

con.execute("""
CREATE OR REPLACE TABLE analytics.mart_risk_tier_summary AS

SELECT
    risk_tier,

    COUNT(*) AS applicants,

    ROUND(
        100.0 * COUNT(*) /
        SUM(COUNT(*)) OVER (),
        4
    ) AS pct_of_total_applicants,

    COUNT(*) FILTER (
        WHERE score_status = 'Full score'
    ) AS scored_applicants,

    SUM(TARGET) AS target_1_count,

    ROUND(
        100.0 * AVG(TARGET),
        4
    ) AS target_1_rate,

    ROUND(AVG(risk_score), 2) AS avg_risk_score,

    ROUND(MIN(risk_score), 2) AS min_risk_score,

    ROUND(MAX(risk_score), 2) AS max_risk_score

FROM analytics.applicant_risk_scores

GROUP BY risk_tier;
""")

mart_risk_tier_rows = con.execute("""
SELECT COUNT(*)
FROM analytics.mart_risk_tier_summary
""").fetchone()[0]

print("analytics.mart_risk_tier_summary created.")
print(f"Risk-tier mart rows: {mart_risk_tier_rows}")

# ============================================================
# MART: RISK SCORE DISTRIBUTION
# One row per exact analytical risk score
# ============================================================

con.execute("""
CREATE OR REPLACE TABLE analytics.mart_score_distribution AS

SELECT
    risk_score,
    risk_tier,

    COUNT(*) AS applicants,

    ROUND(
        100.0 * COUNT(*) /
        SUM(COUNT(*)) OVER (),
        4
    ) AS pct_of_scored_applicants,

    SUM(TARGET) AS target_1_count,

    ROUND(
        100.0 * AVG(TARGET),
        4
    ) AS target_1_rate

FROM analytics.applicant_risk_scores

WHERE score_status = 'Full score'
  AND risk_score IS NOT NULL

GROUP BY
    risk_score,
    risk_tier;
""")

mart_score_distribution_rows = con.execute("""
SELECT COUNT(*)
FROM analytics.mart_score_distribution
""").fetchone()[0]

print("analytics.mart_score_distribution created.")
print(f"Score-distribution mart rows: {mart_score_distribution_rows}")

# ============================================================
# MART: AFFORDABILITY × REPAYMENT
# ============================================================

con.execute("""
CREATE OR REPLACE TABLE analytics.mart_affordability_repayment AS

SELECT
    affordability_segment,
    repayment_segment,

    COUNT(*) AS applicants,

    ROUND(
        100.0 * COUNT(*) /
        SUM(COUNT(*)) OVER (),
        4
    ) AS pct_of_total_applicants,

    COUNT(*) FILTER (
        WHERE score_status = 'Full score'
    ) AS scored_applicants,

    ROUND(
        AVG(risk_score),
        2
    ) AS avg_risk_score,

    SUM(TARGET) AS target_1_count,

    ROUND(
        100.0 * AVG(TARGET),
        4
    ) AS target_1_rate

FROM analytics.applicant_risk_scores

GROUP BY
    affordability_segment,
    repayment_segment;
""")

mart_affordability_repayment_rows = con.execute("""
SELECT COUNT(*)
FROM analytics.mart_affordability_repayment
""").fetchone()[0]

print("analytics.mart_affordability_repayment created.")
print(
    f"Affordability-repayment mart rows: "
    f"{mart_affordability_repayment_rows}"
)

# ============================================================
# MART: REPAYMENT BEHAVIOR
# ============================================================

con.execute("""
CREATE OR REPLACE TABLE analytics.mart_repayment_behavior AS

SELECT
    repayment_pattern,
    late_payment_severity,
    underpayment_severity,

    COUNT(*) AS applicants,

    COUNT(*) FILTER (
        WHERE score_status = 'Full score'
    ) AS scored_applicants,

    ROUND(
        AVG(risk_score),
        2
    ) AS avg_risk_score,

    SUM(TARGET) AS target_1_count,

    ROUND(
        100.0 * AVG(TARGET),
        4
    ) AS target_1_rate

FROM analytics.applicant_risk_scores

GROUP BY
    repayment_pattern,
    late_payment_severity,
    underpayment_severity;
""")

mart_repayment_behavior_rows = con.execute("""
SELECT COUNT(*)
FROM analytics.mart_repayment_behavior
""").fetchone()[0]

print("analytics.mart_repayment_behavior created.")
print(
    f"Repayment-behavior mart rows: "
    f"{mart_repayment_behavior_rows}"
)

# ============================================================
# MART: SCORE AVAILABILITY
# One row per score availability status
# ============================================================

con.execute("""
CREATE OR REPLACE TABLE analytics.mart_score_availability AS

SELECT
    score_status,

    COUNT(*) AS applicants,

    ROUND(
        100.0 * COUNT(*) /
        SUM(COUNT(*)) OVER (),
        4
    ) AS pct_of_total_applicants,

    COUNT(*) FILTER (
        WHERE risk_score IS NOT NULL
    ) AS scored_applicants,

    COUNT(*) FILTER (
        WHERE risk_score IS NULL
    ) AS unscored_applicants,

    SUM(TARGET) AS target_1_count,

    ROUND(
        100.0 * AVG(TARGET),
        4
    ) AS target_1_rate,

    ROUND(
        AVG(risk_score),
        2
    ) AS avg_risk_score

FROM analytics.applicant_risk_scores

GROUP BY score_status;
""")

mart_score_availability_rows = con.execute("""
SELECT COUNT(*)
FROM analytics.mart_score_availability
""").fetchone()[0]

print("analytics.mart_score_availability created.")
print(
    f"Score-availability mart rows: "
    f"{mart_score_availability_rows}"
)

con.close()

print("Warehouse connection closed successfully.")