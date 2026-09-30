from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")

application = pd.read_csv(RAW_DIR / "application_train.csv")
previous = pd.read_csv(RAW_DIR / "previous_application.csv")
installments = pd.read_csv(RAW_DIR / "installments_payments.csv")

print("\n--- APPLICATION DATA TYPES ---")
print(application.dtypes.value_counts())

print("\n--- PREVIOUS APPLICATION DATA TYPES ---")
print(previous.dtypes.value_counts())

print("\n--- INSTALLMENT PAYMENT DATA TYPES ---")
print(installments.dtypes.value_counts())


def show_missing_values(df, name):
    missing_count = df.isna().sum()
    missing_percent = (missing_count / len(df)) * 100

    missing_summary = pd.DataFrame({
        "missing_count": missing_count,
        "missing_percent": missing_percent
    })

    missing_summary = missing_summary[
        missing_summary["missing_count"] > 0
    ].sort_values("missing_percent", ascending=False)

    print(f"\n--- {name} MISSING VALUES ---")
    print(missing_summary.head(20))


show_missing_values(application, "APPLICATION")
show_missing_values(previous, "PREVIOUS APPLICATION")
show_missing_values(installments, "INSTALLMENT PAYMENT")

print("\n--- DUPLICATE ROW CHECK ---")

print(
    "Application duplicate rows:",
    application.duplicated().sum()
)

print(
    "Previous application duplicate rows:",
    previous.duplicated().sum()
)

print(
    "Installment payment duplicate rows:",
    installments.duplicated().sum()
)


print("\n--- IDENTIFIER VALIDATION ---")

print("\nApplication:")
print("SK_ID_CURR nulls:", application["SK_ID_CURR"].isna().sum())
print("SK_ID_CURR unique:", application["SK_ID_CURR"].nunique())
print("Total rows:", len(application))

print("\nPrevious applications:")
print("SK_ID_CURR nulls:", previous["SK_ID_CURR"].isna().sum())
print("SK_ID_PREV nulls:", previous["SK_ID_PREV"].isna().sum())
print("Unique SK_ID_CURR:", previous["SK_ID_CURR"].nunique())
print("Unique SK_ID_PREV:", previous["SK_ID_PREV"].nunique())
print("Total rows:", len(previous))

print("\nInstallment payments:")
print("SK_ID_CURR nulls:", installments["SK_ID_CURR"].isna().sum())
print("SK_ID_PREV nulls:", installments["SK_ID_PREV"].isna().sum())
print("Unique SK_ID_CURR:", installments["SK_ID_CURR"].nunique())
print("Unique SK_ID_PREV:", installments["SK_ID_PREV"].nunique())
print("Total rows:", len(installments))


print("\n--- TARGET VALIDATION ---")

print("TARGET nulls:", application["TARGET"].isna().sum())

print("\nTARGET counts:")
print(application["TARGET"].value_counts(dropna=False))

print("\nTARGET percentages:")
print(
    application["TARGET"]
    .value_counts(normalize=True, dropna=False)
    .mul(100)
    .round(2)
)

print("\n--- FINANCIAL FIELD VALIDATION ---")

application_fields = [
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "AMT_ANNUITY"
]

previous_fields = [
    "AMT_APPLICATION",
    "AMT_CREDIT"
]

installment_fields = [
    "DAYS_INSTALMENT",
    "DAYS_ENTRY_PAYMENT",
    "AMT_INSTALMENT",
    "AMT_PAYMENT"
]

print("\nCURRENT APPLICATION:")
print(
    application[application_fields]
    .describe()
    .T
    [["count", "mean", "min", "max"]]
)

print("\nPREVIOUS APPLICATIONS:")
print(
    previous[previous_fields]
    .describe()
    .T
    [["count", "mean", "min", "max"]]
)

print("\nINSTALLMENT PAYMENTS:")
print(
    installments[installment_fields]
    .describe()
    .T
    [["count", "mean", "min", "max"]]
)

print("\nNEGATIVE AMOUNT CHECK:")

print(
    "Application negative income:",
    (application["AMT_INCOME_TOTAL"] < 0).sum()
)

print(
    "Application negative credit:",
    (application["AMT_CREDIT"] < 0).sum()
)

print(
    "Previous negative application amount:",
    (previous["AMT_APPLICATION"] < 0).sum()
)

print(
    "Previous negative credit:",
    (previous["AMT_CREDIT"] < 0).sum()
)

print(
    "Installment negative scheduled amount:",
    (installments["AMT_INSTALMENT"] < 0).sum()
)

print(
    "Installment negative payment:",
    (installments["AMT_PAYMENT"] < 0).sum()
)


print("\n--- RELATIONSHIP INTEGRITY ---")

current_customer_ids = set(application["SK_ID_CURR"])

previous_for_current_customers = previous[
    previous["SK_ID_CURR"].isin(current_customer_ids)
]

print("\nCURRENT APPLICATION -> PREVIOUS APPLICATION")

print(
    "Total previous application rows:",
    len(previous)
)

print(
    "Previous application rows linked to current customers:",
    len(previous_for_current_customers)
)

print(
    "Unique current customers with previous applications:",
    previous_for_current_customers["SK_ID_CURR"].nunique()
)

print(
    "Current customers with no previous application:",
    application["SK_ID_CURR"].nunique()
    - previous_for_current_customers["SK_ID_CURR"].nunique()
)


print("\nPREVIOUS APPLICATION -> INSTALLMENT PAYMENTS")

previous_application_ids = set(previous["SK_ID_PREV"])

installments_linked_to_previous = installments[
    installments["SK_ID_PREV"].isin(previous_application_ids)
]

print(
    "Total installment rows:",
    len(installments)
)

print(
    "Installment rows linked to previous applications:",
    len(installments_linked_to_previous)
)

print(
    "Unique previous applications with installment history:",
    installments_linked_to_previous["SK_ID_PREV"].nunique()
)

print(
    "Installment rows without matching previous application:",
    len(installments) - len(installments_linked_to_previous)
)