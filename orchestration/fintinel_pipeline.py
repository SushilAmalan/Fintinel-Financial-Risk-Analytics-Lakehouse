from datetime import datetime, timedelta

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


FINTINEL_ROOT = r"C:\Users\Sushil Amalan\Documents\Fintinel"
RAW_DIR = "/mnt/c/Users/Sushil Amalan/Documents/Fintinel/data/raw"
WINDOWS_PYTHON = r"C:\Users\Sushil Amalan\Documents\Fintinel\.venv\Scripts\python.exe"
DBT_EXE = r"C:\Users\Sushil Amalan\.local\bin\dbt.exe"
DBT_PROJECT = r"C:\Users\Sushil Amalan\Documents\Fintinel\fintinel_dbt"


default_args = {
    "owner": "sushil",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="fintinel_financial_risk_pipeline",
    description="Orchestrates the Fintinel financial risk analytics pipeline",
    start_date=datetime(2026, 9, 30),
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["fintinel", "financial-risk", "dbt", "snowflake"],
) as dag:

    validate_source_files = BashOperator(
        task_id="validate_source_files",
        execution_timeout=timedelta(minutes=30),
        bash_command=f"""
        set -e
        test -f "{RAW_DIR}/application_train.csv"
        test -f "{RAW_DIR}/previous_application.csv"
        test -f "{RAW_DIR}/installments_payments.csv"
        echo "All required Fintinel source files are present."
        """,
    )

    upload_raw_to_snowflake = BashOperator(
        task_id="upload_raw_to_snowflake",
        execution_timeout=timedelta(minutes=30),
        bash_command=f"""
        powershell.exe -NoProfile -Command "& '{WINDOWS_PYTHON}' '{FINTINEL_ROOT}\\scripts\\upload_raw_to_snowflake.py'"
        """,
    )

    run_dbt_build = BashOperator(
        task_id="run_dbt_build",
        execution_timeout=timedelta(minutes=30),
        bash_command=f"""
        powershell.exe -NoProfile -Command "cd '{DBT_PROJECT}'; & '{DBT_EXE}' build"
        """,
    )

    validate_final_output = BashOperator(
        task_id="validate_final_output",
        execution_timeout=timedelta(minutes=30),
        bash_command=f"""
        powershell.exe -NoProfile -Command "
        cd '{DBT_PROJECT}';
        & '{DBT_EXE}' test --select applicant_risk_segments mart_risk_tier_summary mart_score_distribution
        "
        """,
    )

    validate_source_files >> upload_raw_to_snowflake >> run_dbt_build >> validate_final_output