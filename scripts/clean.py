from pathlib import Path

import pandas as pd
import yaml


RAW_DIR = Path("data/raw")
CLEANED_DIR = Path("data/cleaned")
CONFIG_PATH = Path("config/cleaning_rules.yaml")


# Load cleaning configuration
with open(CONFIG_PATH, "r") as file:
    rules = yaml.safe_load(file)


# Load raw datasets
application = pd.read_csv(RAW_DIR / "application_train.csv")
previous = pd.read_csv(RAW_DIR / "previous_application.csv")
installments = pd.read_csv(RAW_DIR / "installments_payments.csv")


print("Cleaning configuration loaded.")
print("Raw datasets loaded.")

print("\nApplication:", application.shape)
print("Previous applications:", previous.shape)
print("Installment payments:", installments.shape)


# Columns required for Fintinel analytics

application_columns = [
    "SK_ID_CURR",
    "TARGET",
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "AMT_ANNUITY"
]

previous_columns = [
    "SK_ID_CURR",
    "SK_ID_PREV",
    "NAME_CONTRACT_TYPE",
    "NAME_CONTRACT_STATUS",
    "AMT_APPLICATION",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "DAYS_DECISION"
]

installment_columns = [
    "SK_ID_CURR",
    "SK_ID_PREV",
    "NUM_INSTALMENT_VERSION",
    "NUM_INSTALMENT_NUMBER",
    "DAYS_INSTALMENT",
    "DAYS_ENTRY_PAYMENT",
    "AMT_INSTALMENT",
    "AMT_PAYMENT"
]


# Verify every required column exists before selecting anything

datasets_and_columns = {
    "application": (application, application_columns),
    "previous_application": (previous, previous_columns),
    "installments": (installments, installment_columns)
}

for dataset_name, (df, required_columns) in datasets_and_columns.items():

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{dataset_name} is missing required columns: {missing_columns}"
        )

    print(f"{dataset_name}: all required columns found.")


# Select only the columns required for Fintinel

application_clean = application[application_columns].copy()
previous_clean = previous[previous_columns].copy()
installments_clean = installments[installment_columns].copy()


print("\n--- COLUMN SELECTION ---")

print(
    f"Application: {application.shape} -> {application_clean.shape}"
)

print(
    f"Previous applications: {previous.shape} -> {previous_clean.shape}"
)

print(
    f"Installment payments: {installments.shape} -> {installments_clean.shape}"
)


print("\n--- SELECTED COLUMN DATA TYPES ---")

print("\nApplication:")
print(application_clean.dtypes)

print("\nPrevious applications:")
print(previous_clean.dtypes)

print("\nInstallment payments:")
print(installments_clean.dtypes)


print("\n--- SELECTED COLUMN MISSING VALUES ---")

print("\nApplication:")
print(application_clean.isna().sum())

print("\nPrevious applications:")
print(previous_clean.isna().sum())

print("\nInstallment payments:")
print(installments_clean.isna().sum())



print("\n--- MISSING VALUE PATTERN CHECK ---")

# Application
print("\nApplication rows with missing AMT_ANNUITY:")
print(
    application_clean[
        application_clean["AMT_ANNUITY"].isna()
    ].head(10)
)

# Previous applications
print("\nPrevious applications with missing AMT_CREDIT:")
print(
    previous_clean[
        previous_clean["AMT_CREDIT"].isna()
    ].head(10)
)

print("\nPrevious applications with missing AMT_ANNUITY by contract status:")
print(
    previous_clean.loc[
        previous_clean["AMT_ANNUITY"].isna(),
        "NAME_CONTRACT_STATUS"
    ].value_counts(dropna=False)
)

# Installments
both_missing = (
    installments_clean["DAYS_ENTRY_PAYMENT"].isna()
    & installments_clean["AMT_PAYMENT"].isna()
)

date_only_missing = (
    installments_clean["DAYS_ENTRY_PAYMENT"].isna()
    & installments_clean["AMT_PAYMENT"].notna()
)

payment_only_missing = (
    installments_clean["DAYS_ENTRY_PAYMENT"].notna()
    & installments_clean["AMT_PAYMENT"].isna()
)

print("\nInstallment missing-value relationship:")
print("Both missing:", both_missing.sum())
print("Only DAYS_ENTRY_PAYMENT missing:", date_only_missing.sum())
print("Only AMT_PAYMENT missing:", payment_only_missing.sum())

print("\nSample installment rows where both are missing:")
print(installments_clean[both_missing].head(10))


print("\n--- MISSING INSTALLMENT INVESTIGATION ---")

missing_payment = installments_clean[
    installments_clean["AMT_PAYMENT"].isna()
].copy()

print("\nMissing-payment row count:")
print(len(missing_payment))

print("\nScheduled installment day range:")
print(missing_payment["DAYS_INSTALMENT"].describe())

print("\nScheduled installment amount range:")
print(missing_payment["AMT_INSTALMENT"].describe())

print("\nInstallment number distribution:")
print(
    missing_payment["NUM_INSTALMENT_NUMBER"]
    .value_counts()
    .sort_index()
    .head(30)
)

print("\nInstallment version distribution:")
print(
    missing_payment["NUM_INSTALMENT_VERSION"]
    .value_counts()
    .sort_index()
)

print("\nUnique previous credits affected:")
print(missing_payment["SK_ID_PREV"].nunique())

print("\nUnique customers affected:")
print(missing_payment["SK_ID_CURR"].nunique())


print("\n--- STRING STANDARDIZATION ---")

string_columns = [
    "NAME_CONTRACT_TYPE",
    "NAME_CONTRACT_STATUS"
]

for column in string_columns:
    previous_clean[column] = (
        previous_clean[column]
        .str.strip()
    )

print("Previous application string fields standardized.")

print("\nContract types:")
print(
    previous_clean["NAME_CONTRACT_TYPE"]
    .value_counts(dropna=False)
)

print("\nContract statuses:")
print(
    previous_clean["NAME_CONTRACT_STATUS"]
    .value_counts(dropna=False)
)



print("\n--- REPAYMENT FIELD DERIVATION ---")

# Positive value = paid after scheduled date
# Zero/negative value = paid on or before scheduled date
installments_clean["PAYMENT_DELAY_DAYS"] = (
    installments_clean["DAYS_ENTRY_PAYMENT"]
    - installments_clean["DAYS_INSTALMENT"]
)

# Positive value = paid less than scheduled amount
# Zero = paid scheduled amount
# Negative value = paid more than scheduled amount
installments_clean["PAYMENT_DIFFERENCE"] = (
    installments_clean["AMT_INSTALMENT"]
    - installments_clean["AMT_PAYMENT"]
)

print("\nPAYMENT_DELAY_DAYS:")
print(installments_clean["PAYMENT_DELAY_DAYS"].describe())

print("\nPAYMENT_DIFFERENCE:")
print(installments_clean["PAYMENT_DIFFERENCE"].describe())

print("\nMissing derived values:")
print(
    installments_clean[
        ["PAYMENT_DELAY_DAYS", "PAYMENT_DIFFERENCE"]
    ].isna().sum()
)


print("\n--- REPAYMENT BEHAVIOR FLAGS ---")

# Nullable boolean flags preserve unknown payment outcomes.
installments_clean["IS_LATE"] = (
    installments_clean["PAYMENT_DELAY_DAYS"] > 0
).astype("boolean")

installments_clean["IS_UNDERPAID"] = (
    installments_clean["PAYMENT_DIFFERENCE"] > 0
).astype("boolean")

# Restore unknown status for records with no actual payment information.
unknown_payment = installments_clean["AMT_PAYMENT"].isna()

installments_clean.loc[unknown_payment, "IS_LATE"] = pd.NA
installments_clean.loc[unknown_payment, "IS_UNDERPAID"] = pd.NA

print("\nIS_LATE:")
print(
    installments_clean["IS_LATE"]
    .value_counts(dropna=False)
)

print("\nIS_UNDERPAID:")
print(
    installments_clean["IS_UNDERPAID"]
    .value_counts(dropna=False)
)

print("\nUnknown-payment records:")
print(unknown_payment.sum())



print("\n--- FINAL CLEANING VALIDATION ---")

# Row counts must remain unchanged
assert len(application_clean) == len(application)
assert len(previous_clean) == len(previous)
assert len(installments_clean) == len(installments)

# Critical identifiers must remain populated
assert application_clean["SK_ID_CURR"].notna().all()

assert previous_clean["SK_ID_CURR"].notna().all()
assert previous_clean["SK_ID_PREV"].notna().all()

assert installments_clean["SK_ID_CURR"].notna().all()
assert installments_clean["SK_ID_PREV"].notna().all()

# TARGET must remain binary
assert set(application_clean["TARGET"].unique()).issubset({0, 1})

# Financial amounts that we established cannot be negative
assert (application_clean["AMT_INCOME_TOTAL"] >= 0).all()
assert (application_clean["AMT_CREDIT"] >= 0).all()

assert previous_clean["AMT_APPLICATION"].dropna().ge(0).all()
assert previous_clean["AMT_CREDIT"].dropna().ge(0).all()

assert installments_clean["AMT_INSTALMENT"].ge(0).all()
assert installments_clean["AMT_PAYMENT"].dropna().ge(0).all()

print("Application rows preserved:", len(application_clean))
print("Previous application rows preserved:", len(previous_clean))
print("Installment rows preserved:", len(installments_clean))

print("Critical identifiers: OK")
print("TARGET domain: OK")
print("Financial amount constraints: OK")
print("Final cleaning validation passed.")


print("\n--- WRITING CLEANED DATASETS ---")

CLEAN_DIR = Path("data/cleaned")
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

application_clean.to_parquet(
    CLEAN_DIR / "application_clean.parquet",
    index=False
)

previous_clean.to_parquet(
    CLEAN_DIR / "previous_application_clean.parquet",
    index=False
)

installments_clean.to_parquet(
    CLEAN_DIR / "installments_payments_clean.parquet",
    index=False
)

print("application_clean.parquet written.")
print("previous_application_clean.parquet written.")
print("installments_payments_clean.parquet written.")
print("Cleaned datasets successfully persisted.")