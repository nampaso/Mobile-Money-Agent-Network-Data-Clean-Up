import numpy as np
import pandas as pd


def generate_raw_data(seed=44):
    np.random.seed(seed)

    # 1. Generate Agents Registry
    agent_ids = [f"A{str(i).zfill(3)}" for i in range(1, 51)]
    counties = [
        "Nairobi",
        "Mombasa",
        "Kisumu",
        "Nakuru",
        "Eldoret",
        "Kiambu",
        "Machakos",
    ]

    agents_df = pd.DataFrame(
        {
            "agent_id": agent_ids,
            "agent_name": [f"Agent_{i}" for i in range(1, 51)],
            "county": np.random.choice(counties, size=50),
            "registration_date": pd.date_range(
                start="2023-01-01", periods=50, freq="D"
            ).strftime("%Y-%m-%d"),
        }
    )

    # Introduce messiness into Agents
    agents_df.loc[2:4, "agent_id"] = agents_df.loc[2:4, "agent_id"].str.lower()
    agents_df = pd.concat([agents_df, agents_df.iloc[[10, 10]]], ignore_index=True)

    # 2. Generate Transactions Dataset
    n_rows = 1200
    txn_ids = [f"TXN{str(i).zfill(5)}" for i in range(1, n_rows + 1)]

    # Dates with mixed formats
    dates_iso = pd.date_range(
        start="2024-01-01", periods=n_rows, freq="h"
    ).strftime("%Y-%m-%d %H:%M:%S")
    dates_slash = pd.date_range(
        start="2024-01-01", periods=n_rows, freq="h"
    ).strftime("%d/%m/%Y %H:%M")
    dates_mixed = np.where(
        np.random.rand(n_rows) > 0.5, dates_iso, dates_slash
    )

    # Types with typos
    types_raw = np.random.choice(
        ["Deposit", "Withdrawal", "dep", "WITHDRAWAL", "depo", "Withdraw"],
        size=n_rows,
        p=[0.4, 0.4, 0.05, 0.05, 0.05, 0.05],
    )

    # Amounts with missing values & extreme outliers
    amounts = np.random.exponential(scale=5000, size=n_rows) + 100
    amounts[
        np.random.choice(n_rows, size=40, replace=False)
    ] = np.nan  # Missing amounts
    amounts[15] = 1_500_000  # Extreme positive outlier
    amounts[88] = -50_000  # Invalid negative amount

    # Assign agent IDs (including non-existent agents and casing issues)
    assigned_agents = np.random.choice(agent_ids + ["A999", "a001"], size=n_rows)

    txns_df = pd.DataFrame(
        {
            "txn_id": txn_ids,
            "txn_date": dates_mixed,
            "agent_id": assigned_agents,
            "txn_type": types_raw,
            "amount": amounts,
        }
    )

    # Introduce duplicate transactions
    txns_df = pd.concat([txns_df, txns_df.iloc[[5, 12, 100]]], ignore_index=True)

    return txns_df, agents_df


if __name__ == "__main__":
    txns, agents = generate_raw_data(seed=44)
    txns.to_csv("agent_transactions_raw.csv", index=False)
    agents.to_csv("agents_registry_raw.csv", index=False)
    print("Raw datasets generated successfully!")
