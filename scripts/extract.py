from pathlib import Path
import pandas as pd

# Path to the project's raw source data
RAW_DIR = Path("data/raw")

SOURCE_FILES = [
    "application_train.csv",
    "previous_application.csv",
    "installments_payments.csv",
]

for filename in SOURCE_FILES:
    filepath = RAW_DIR / filename

    if not filepath.exists():
        raise FileNotFoundError(f"Missing source file: {filepath}")

print("All required source files found.")

application = pd.read_csv(RAW_DIR / "application_train.csv")
previous = pd.read_csv(RAW_DIR / "previous_application.csv")
installments = pd.read_csv(RAW_DIR / "installments_payments.csv")

print("Application:", application.shape)
print("Previous applications:", previous.shape)
print("Installment payments:", installments.shape)

print("\n--- APPLICATION COLUMNS ---")
print(application.columns.tolist())

print("\n--- PREVIOUS APPLICATION COLUMNS ---")
print(previous.columns.tolist())

print("\n--- INSTALLMENT PAYMENT COLUMNS ---")
print(installments.columns.tolist())

print("\n--- APPLICATION SAMPLE ---")
print(application.head(3))

print("\n--- PREVIOUS APPLICATION SAMPLE ---")
print(previous.head(3))

print("\n--- INSTALLMENT PAYMENT SAMPLE ---")
print(installments.head(3))


