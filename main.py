import pandas as pd
import os
from datetime import datetime, timezone

# Load files
# Get the directory of the current script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Build absolute paths to the CSV files
supabase_path = os.path.join(base_dir, "Supabase_name_id_export_go.csv")  # company_id, name export from Supabase
scraped_path = os.path.join(base_dir, "5_12_2026_jobs_to_Python_test.csv")  # jobs file
industries_path = os.path.join(base_dir, "industries_rows.csv")  # id, name mapping for industries

supabase_companies_df = pd.read_csv(supabase_path, encoding="latin1")  # company_id, name
scraped_df = pd.read_csv(scraped_path, encoding="latin1")
industries_df = pd.read_csv(industries_path, encoding="latin1")  # id, name

# Normalize headers: strip whitespace and BOM artifacts that can sneak in via encoding mismatches
for df in (supabase_companies_df, scraped_df, industries_df):
    df.columns = df.columns.str.strip().str.lstrip("﻿").str.lstrip("ï»¿")

print(f"\n📋 Input file columns: {scraped_df.columns.tolist()}")

# --- Look up the company id from Supabase -------------------------------------
if "company_name" not in scraped_df.columns:
    raise KeyError(
        f"Couldn't find 'company_name' in {os.path.basename(scraped_path)}. "
        f"Actual columns: {scraped_df.columns.tolist()}"
    )

# Drop any existing company_id / id columns to avoid conflicts before merging
scraped_df = scraped_df.drop(columns=["company_id", "id"], errors="ignore")

supabase_lookup = supabase_companies_df.rename(
    columns={"name": "_supabase_name"}
)

merged_df = scraped_df.merge(
    supabase_lookup,
    how="left",
    left_on="company_name",
    right_on="_supabase_name",
)
merged_df.drop(columns=["_supabase_name"], inplace=True)

# --- Map industry (string) → industry_id (number) using industries_rows.csv ---
# Drop any existing industry_id column to avoid conflicts before merging
merged_df = merged_df.drop(columns=["industry_id"], errors="ignore")

# Coerce industry to object dtype before merging. If every row is NaN, pandas infers
# float64, which pandas refuses to merge against the string lookup column.
merged_df["industry"] = merged_df["industry"].astype(object)

# Merge on exact match between scraped row's industry and industries lookup name
merged_df = merged_df.merge(
    industries_df.rename(columns={"id": "industry_id", "name": "industry_name_lookup"}),
    how="left",
    left_on="industry",
    right_on="industry_name_lookup",
)

# Report any industries that didn't match (so they can be added to the lookup table)
unmatched = merged_df.loc[merged_df["industry"].notna() & merged_df["industry_id"].isna(), "industry"].unique()
if len(unmatched) > 0:
    print(f"\n⚠️  Unmatched industries (no id assigned): {list(unmatched)}")

# Convert industry_id to nullable integer (avoids .0 suffix from NaN-induced float)
merged_df["industry_id"] = merged_df["industry_id"].astype("Int64")

# Drop the original industry string column and the lookup helper column
merged_df.drop(columns=["industry", "industry_name_lookup"], inplace=True)

# --- Stamp created_at / posted_at with current UTC time -----------------------
run_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00")
merged_df["created_at"] = run_timestamp
merged_df["posted_at"] = run_timestamp

# --- Enforce target schema column order (post-migration) ----------------------
schema_columns = [
    "title", "description", "company_name", "location", "application_url",
    "created_at", "expires_at", "is_active", "approval_status", "is_bulk_upload",
    "company_id", "industry_id", "salary_min", "salary_max", "salary_period",
    "job_type", "experience_level", "remote_type", "contact_email",
    "applicant_count", "category", "creator_id", "outbound_clicks", "posted_at",
    "qualifications", "responsibilities", "verified", "is_featured",
    "applications_count", "keywords", "external_clicks",
]
output_filename = "SQL_Jobs_Ready_5_12_2026_test2!!!.csv"

# Keep only schema columns that exist, then append any extras at the end so nothing is silently lost
ordered = [c for c in schema_columns if c in merged_df.columns]
extras = [c for c in merged_df.columns if c not in ordered]
if extras:
    print(f"\nℹ️  Extra columns not in target schema (appended at end): {extras}")
merged_df = merged_df[ordered + extras]

# Export to new CSV
output_path = os.path.join(base_dir, output_filename)
merged_df.to_csv(output_path, index=False)
print(f"✅ Updated file saved to: {output_path}")

# Optional: Print first few matched results to terminal
print(f"\n🔍 Sample matched company_names and ids:")
print(merged_df[["company_name", "company_id"]].drop_duplicates().head(10))

print(f"\n🔍 Sample matched industry_ids:")
print(merged_df[["company_name", "industry_id"]].drop_duplicates().head(10))
