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

## Highlights

- Processed 307,511 applicants across application, credit-history, and installment-payment datasets
- Built a layered Snowflake + dbt analytics pipeline with staging, intermediate, scoring, segmentation, and mart layers
- Developed applicant-level financial risk scores from 0 to 100 using repayment behavior and affordability features
- Created five reusable analytical marts for portfolio-level risk analysis
- Implemented 60 dbt tests and custom business-rule validations
- Achieved a full dbt build with 75/75 successful operations
- Reconciled Snowflake + dbt outputs against the original DuckDB pipeline

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

```
## Workflow Orchestration

Apache Airflow orchestrates the Fintinel analytics pipeline through a dependency-based DAG.

```text
Source File Validation
        |
        v
Snowflake Raw Upload
        |
        v
dbt Build
        |
        v
Final Data Quality Validation
