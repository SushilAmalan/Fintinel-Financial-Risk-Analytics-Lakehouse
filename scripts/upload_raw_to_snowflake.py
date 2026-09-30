from pathlib import Path
import snowflake.connector

PROJECT_ROOT = Path(__file__).resolve().parents[1]

private_key = PROJECT_ROOT / "secrets" / "rsa_key.p8"

files = [
    ("application_train.csv", "application_train"),
    ("previous_application.csv", "previous_application"),
    ("installments_payments.csv", "installments_payments"),
]

conn = snowflake.connector.connect(
    account="UACPSZW-BN62011",
    user="SUSHILAMALAN",
    private_key_file=str(private_key),
    warehouse="FINTINEL_WH",
    database="FINTINEL",
    schema="RAW",
    role="ACCOUNTADMIN",
)

cursor = conn.cursor()

for filename, stage_folder in files:
    csv_file = PROJECT_ROOT / "data" / "raw" / filename
    file_uri = "file://" + csv_file.as_posix()

    sql = f"""
    PUT '{file_uri}'
    @FINTINEL.RAW.FINTINEL_STAGE/{stage_folder}
    AUTO_COMPRESS=TRUE
    OVERWRITE=TRUE
    PARALLEL=4
    """

    print(f"\nUploading: {filename}")

    result = cursor.execute(sql).fetchall()

    for row in result:
        print(row)

cursor.close()
conn.close()

print("\nAll RAW uploads complete.")