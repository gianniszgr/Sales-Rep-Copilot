# Phase 2 — Text Profile Generation
# Load loads_monthly from data/processed/ and convert each row into a human-readable text string.
# Embedding granularity: one profile per customer + product family + month.

import os
import pandas as pd

PROCESSED_DIR = "data/processed/"
INPUT_FILE = "loads_monthly.csv"
OUTPUT_FILE = "customer_profiles.csv"


def load_loads_monthly(processed_dir: str = PROCESSED_DIR) -> pd.DataFrame:
    path = os.path.join(processed_dir, INPUT_FILE)
    return pd.read_csv(path)


def build_text_profile(row: pd.Series) -> str:
    employees = int(row["NumberOfEmployees"]) if pd.notna(row["NumberOfEmployees"]) else "N/A"
    group_name = row["group_name__c"] if pd.notna(row["group_name__c"]) else "N/A"
    product_family = row["ProductFamily"] if pd.notna(row["ProductFamily"]) else "N/A"

    return (
        f"Customer: {row['cus_name']} | "
        f"Group: {group_name} | "
        f"Segment: {row['Segment__c']} | "
        f"Employees: {employees} | "
        f"Job Type: {row['JobType']} | "
        f"Salesperson: {row['SalesPerson']} | "
        f"Product Family: {product_family} | "
        f"Month: {row['month']} | "
        f"Revenue: €{row['total_amt']:,.0f} | "
        f"Orders: {int(row['order_count'])}"
    )


def run(processed_dir: str = PROCESSED_DIR) -> pd.DataFrame:
    print("Loading loads_monthly...")
    df = load_loads_monthly(processed_dir)
    print(f"  {len(df):,} rows loaded from {INPUT_FILE}")

    print("Generating text profiles...")
    df["text_profile"] = df.apply(build_text_profile, axis=1)

    output_path = os.path.join(processed_dir, OUTPUT_FILE)
    df.to_csv(output_path, index=False)
    print(f"  Saved to {output_path}")

    print("\nSample profile:")
    print(df["text_profile"].iloc[0])

    return df


if __name__ == "__main__":
    run()
