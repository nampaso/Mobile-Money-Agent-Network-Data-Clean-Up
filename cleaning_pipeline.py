import numpy as np
import pandas as pd


def clean_agent_data(txns: pd.DataFrame, agents: pd.DataFrame):
    """Cleans agent transactions and agent registry data, logs data quality issues,

    and performs a validated merge across both datasets.

    Parameters:
    -----------
    txns : pd.DataFrame
        Raw transaction data.
    agents : pd.DataFrame
        Raw agent registry data.

    Returns:
    --------
    clean_df : pd.DataFrame
        The cleaned and merged agent transaction dataframe.
    log : pd.DataFrame
        Data quality audit log detailing issues found across standard dimensions.
    """
    txns_df = txns.copy()
    agents_df = agents.copy()

    audit_records = []

    # Helper function to track issues
    def log_issue(issue, dimension, column, rows_affected):
        audit_records.append(
            {
                "issue": issue,
                "dimension": dimension,
                "column": column,
                "rows_affected": int(rows_affected),
            }
        )

    # -------------------------------------------------------------
    # 1. CLEAN AGENTS REGISTRY
    # -------------------------------------------------------------
    # Primary Key Casing & Standardisation
    agents_df["agent_id"] = agents_df["agent_id"].astype(str).str.upper().str.strip()

    # Deduplication
    agent_dups = agents_df.duplicated(subset=["agent_id"]).sum()
    log_issue("Duplicate agent_id entries in registry", "Uniqueness", "agent_id", agent_dups)
    agents_clean = agents_df.drop_duplicates(subset=["agent_id"], keep="first").copy()

    # -------------------------------------------------------------
    # 2. CLEAN TRANSACTIONS DATASET
    # -------------------------------------------------------------
    # Primary Key Deduplication
    txn_dups = txns_df.duplicated(subset=["txn_id"]).sum()
    log_issue("Duplicate transaction IDs", "Uniqueness", "txn_id", txn_dups)
    txns_clean = txns_df.drop_duplicates(subset=["txn_id"], keep="first").copy()

    # Standardise Foreign Key Casing
    txns_clean["agent_id"] = txns_clean["agent_id"].astype(str).str.upper().str.strip()

    # Dates to Standard ISO 8601 Format
    invalid_dates_count = txns_clean["txn_date"].isna().sum()
    txns_clean["txn_date"] = pd.to_datetime(txns_clean["txn_date"], dayfirst=False, errors="coerce")
    log_issue("Unparseable transaction dates", "Validity", "txn_date", invalid_dates_count)
    txns_clean["txn_date"] = txns_clean["txn_date"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Transaction Type Standardization
    type_mapping = {
        "Deposit": "Deposit",
        "dep": "Deposit",
        "depo": "Deposit",
        "Withdrawal": "Withdrawal",
        "WITHDRAWAL": "Withdrawal",
        "Withdraw": "Withdrawal",
    }
    non_std_types = (~txns_clean["txn_type"].isin(["Deposit", "Withdrawal"])).sum()
    log_issue("Non-standard transaction types", "Consistency", "txn_type", non_std_types)
    txns_clean["txn_type"] = txns_clean["txn_type"].map(type_mapping).fillna("Other")

    # Negative Amounts Handling
    invalid_negative = (txns_clean["amount"] < 0).sum()
    log_issue("Negative transaction amounts", "Validity", "amount", invalid_negative)
    txns_clean.loc[txns_clean["amount"] < 0, "amount"] = np.nan

    # Imputation of Missing Amounts
    missing_amounts = txns_clean["amount"].isna().sum()
    log_issue("Missing transaction amounts", "Completeness", "amount", missing_amounts)
    median_amount = txns_clean["amount"].median()
    txns_clean["amount_imputed"] = txns_clean["amount"].isna()
    txns_clean["amount"] = txns_clean["amount"].fillna(median_amount)

    # Outlier Detection (IQR Method)
    q1 = txns_clean["amount"].quantile(0.25)
    q3 = txns_clean["amount"].quantile(0.75)
    iqr = q3 - q1
    upper_bound = q3 + (1.5 * iqr)
    lower_bound = q1 - (1.5 * iqr)

    outliers_mask = (txns_clean["amount"] > upper_bound) | (txns_clean["amount"] < lower_bound)
    log_issue("Extreme transaction amount outliers", "Accuracy", "amount", outliers_mask.sum())
    txns_clean["is_outlier"] = outliers_mask

    # -------------------------------------------------------------
    # 3. MERGE & REFERENTIAL INTEGRITY VALIDATION
    # -------------------------------------------------------------
    unmatched_agents = (~txns_clean["agent_id"].isin(agents_clean["agent_id"])).sum()
    log_issue("Transactions with unknown agent_id", "Referential Integrity", "agent_id", unmatched_agents)

    clean_df = pd.merge(
        txns_clean,
        agents_clean[["agent_id", "county"]],
        on="agent_id",
        how="left"
    )

    clean_df["county"] = clean_df["county"].fillna("Unknown")

    log = pd.DataFrame(audit_records)
    return clean_df, log
