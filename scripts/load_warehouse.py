from pathlib import Path
import duckdb

# Project paths
CLEAN_DIR = Path("data/cleaned")
WAREHOUSE_DIR = Path("warehouse")
WAREHOUSE_PATH = WAREHOUSE_DIR / "fintinel.duckdb"

# Cleaned datasets produced by Phase 5
APPLICATION_FILE = CLEAN_DIR / "application_clean.parquet"
PREVIOUS_FILE = CLEAN_DIR / "previous_application_clean.parquet"
INSTALLMENTS_FILE = CLEAN_DIR / "installments_payments_clean.parquet"

# Verify that the cleaned inputs actually exist
required_files = [
    APPLICATION_FILE,
    PREVIOUS_FILE,
    INSTALLMENTS_FILE,
]

missing_files = [path for path in required_files if not path.exists()]

if missing_files:
    raise FileNotFoundError(
        f"Missing cleaned dataset(s): {missing_files}"
    )

print("All cleaned Parquet datasets found.")

# Ensure warehouse directory exists
WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)

# Create/open the DuckDB warehouse
con = duckdb.connect(str(WAREHOUSE_PATH))

print(f"DuckDB warehouse created/opened: {WAREHOUSE_PATH}")

# Create the cleaned/base schema
con.execute("""
    CREATE SCHEMA IF NOT EXISTS cleaned;
""")

print("Schema 'cleaned' ready.")

con.execute("""
    CREATE SCHEMA IF NOT EXISTS analytics;
""")

print("Schema 'analytics' ready.")

# Create a view over the cleaned current-application Parquet file
con.execute("""
    CREATE OR REPLACE VIEW cleaned.application AS
    SELECT *
    FROM read_parquet('data/cleaned/application_clean.parquet');
""")

print("View 'cleaned.application' created.")

# Verify the view
application_count = con.execute("""
    SELECT COUNT(*)
    FROM cleaned.application;
""").fetchone()[0]

print(f"cleaned.application rows: {application_count}")



# Create view over cleaned previous applications
con.execute("""
    CREATE OR REPLACE VIEW cleaned.previous_application AS
    SELECT *
    FROM read_parquet('data/cleaned/previous_application_clean.parquet');
""")

print("View 'cleaned.previous_application' created.")

# Create view over cleaned installment payments
con.execute("""
    CREATE OR REPLACE VIEW cleaned.installments AS
    SELECT *
    FROM read_parquet('data/cleaned/installments_payments_clean.parquet');
""")

print("View 'cleaned.installments' created.")


# Verify row counts through DuckDB
application_count = con.execute("""
    SELECT COUNT(*)
    FROM cleaned.application;
""").fetchone()[0]

previous_count = con.execute("""
    SELECT COUNT(*)
    FROM cleaned.previous_application;
""").fetchone()[0]

installments_count = con.execute("""
    SELECT COUNT(*)
    FROM cleaned.installments;
""").fetchone()[0]

print("\n--- WAREHOUSE BASE VIEW VALIDATION ---")
print(f"cleaned.application rows: {application_count}")
print(f"cleaned.previous_application rows: {previous_count}")
print(f"cleaned.installments rows: {installments_count}")


print("\n--- WAREHOUSE RELATIONSHIP VALIDATION ---")

# Current customers with previous-application history
customers_with_history = con.execute("""
    SELECT COUNT(DISTINCT p.SK_ID_CURR)
    FROM cleaned.previous_application p
    INNER JOIN cleaned.application a
        ON p.SK_ID_CURR = a.SK_ID_CURR;
""").fetchone()[0]

# Current customers without previous-application history
customers_without_history = con.execute("""
    SELECT COUNT(*)
    FROM cleaned.application a
    WHERE NOT EXISTS (
        SELECT 1
        FROM cleaned.previous_application p
        WHERE p.SK_ID_CURR = a.SK_ID_CURR
    );
""").fetchone()[0]

# Installment rows linked to a previous application
linked_installments = con.execute("""
    SELECT COUNT(*)
    FROM cleaned.installments i
    WHERE EXISTS (
        SELECT 1
        FROM cleaned.previous_application p
        WHERE i.SK_ID_CURR = p.SK_ID_CURR
          AND i.SK_ID_PREV = p.SK_ID_PREV
    );
""").fetchone()[0]

# Installment rows without a matching previous application
unlinked_installments = con.execute("""
    SELECT COUNT(*)
    FROM cleaned.installments i
    WHERE NOT EXISTS (
        SELECT 1
        FROM cleaned.previous_application p
        WHERE i.SK_ID_CURR = p.SK_ID_CURR
          AND i.SK_ID_PREV = p.SK_ID_PREV
    );
""").fetchone()[0]

print(f"Current customers with previous history: {customers_with_history}")
print(f"Current customers without previous history: {customers_without_history}")
print(f"Installment rows linked to previous applications: {linked_installments}")
print(f"Installment rows without matching previous applications: {unlinked_installments}")

con.close()

print("Warehouse connection closed successfully.")