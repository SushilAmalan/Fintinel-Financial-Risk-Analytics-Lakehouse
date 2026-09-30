# Fintinel | Financial Risk Analytics Lakehouse

Fintinel is an end-to-end financial risk analytics project that transforms large-scale credit and repayment data into reusable risk features, applicant scores, portfolio segments, and analytical marts.

## Project Overview

The project processes applicant, previous-credit, and installment-payment data through a layered analytics pipeline using Python, Snowflake, and dbt.

The final pipeline produces:

- Applicant-level repayment and affordability features
- Composite financial risk scores from 0 to 100
- Risk tiers: Low, Moderate, Elevated, High, and Unavailable
- Portfolio-level analytical marts
- Automated data-quality and business-rule tests
- Reconciled outputs across DuckDB and Snowflake implementations

## Architecture

```text
Raw CSV Data
    |
    v
Python Ingestion / Validation
    |
    v
Snowflake RAW Layer
    |
    v
dbt Staging Models
    |
    v
dbt Intermediate Models
    |
    v
Risk Features + Scoring
    |
    v
Risk Segmentation
    |
    v
Analytical Marts