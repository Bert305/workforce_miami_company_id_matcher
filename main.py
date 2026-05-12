import pandas as pd
import os

# Load files
# Get the directory of the current script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Build absolute paths to the CSV files
supabase_path = os.path.join(base_dir, "Supabase_name_id_export_go7.csv")  # company_id, name export from Supabase
scraped_path = os.path.join(base_dir, "5_11_2026_jobs_to_Python_go.csv")  # jobs OR companies file (auto-detected)
industries_path = os.path.join(base_dir, "industries_rows.csv")  # id, name mapping for industries

supabase_companies_df = pd.read_csv(supabase_path, encoding="latin1")  # company_id, name
scraped_df = pd.read_csv(scraped_path, encoding="latin1")
industries_df = pd.read_csv(industries_path, encoding="latin1")  # id, name

# Normalize headers: strip whitespace and BOM artifacts that can sneak in via encoding mismatches
for df in (supabase_companies_df, scraped_df, industries_df):
    df.columns = df.columns.str.strip().str.lstrip("﻿").str.lstrip("ï»¿")

print(f"\n📋 Input file columns: {scraped_df.columns.tolist()}")

# --- Auto-detect mode based on which name column is present -------------------
# Jobs file → has `company_name` referring to the company that posted the job
# Companies file → has `name` referring to the company itself (no `company_name`)
if "company_name" in scraped_df.columns:
    mode = "jobs"
    join_key = "company_name"  # left-side column in the scraped file
    id_output_name = "company_id"  # what the matched id is called in the output
elif "name" in scraped_df.columns:
    mode = "companies"
    join_key = "name"
    id_output_name = "id"  # Supabase companies table PK convention
else:
    raise KeyError(
        f"Couldn't find 'company_name' or 'name' in {os.path.basename(scraped_path)}. "
        f"Actual columns: {scraped_df.columns.tolist()}"
    )

print(f"🔧 Detected mode: {mode!r} (joining on '{join_key}', output id column: '{id_output_name}')")

# --- Look up the company id from Supabase -------------------------------------
# Drop any existing id column to avoid conflicts before merging
scraped_df = scraped_df.drop(columns=[id_output_name], errors="ignore")
if mode == "jobs":
    # Also drop a stale 'id' if present, since we're keying on company_name
    scraped_df = scraped_df.drop(columns=["id"], errors="ignore")

# Supabase export has columns (company_id, name). Rename to avoid 'name' collision in companies mode.
supabase_lookup = supabase_companies_df.rename(
    columns={"company_id": id_output_name, "name": "_supabase_name"}
)

merged_df = scraped_df.merge(
    supabase_lookup,
    how="left",
    left_on=join_key,
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

# --- Enforce target schema column order (post-migration) ----------------------
if mode == "jobs":
    # Mirrors 5_11_2026_jobs_to_Python.csv with `industry` removed
    schema_columns = [
        "title", "description", "company_name", "location", "application_url",
        "created_at", "expires_at", "is_active", "approval_status", "is_bulk_upload",
        "company_id", "industry_id", "salary_min", "salary_max", "salary_period",
        "job_type", "experience_level", "remote_type", "contact_email",
        "applicant_count", "category", "creator_id", "outbound_clicks", "posted_at",
        "qualifications", "responsibilities", "verified", "is_featured",
        "applications_count", "keywords", "external_clicks",
    ]
    output_filename = "SQL_Jobs_Ready_5_11_2026_go!!!.csv"
else:  # companies
    # Companies schema: id first (PK), then input columns with industry → industry_id
    schema_columns = [
        "id", "name", "description", "logo_url", "website", "location",
        "industry_id", "email", "phone", "founded", "size", "is_approved", "verified",
    ]
    output_filename = "SQL_Companies_Ready_5_11_2026_p2!!!.csv"

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
display_name_col = "company_name" if mode == "jobs" else "name"
print(f"\n🔍 Sample matched {display_name_col}s and ids:")
print(merged_df[[display_name_col, id_output_name]].drop_duplicates().head(10))

print(f"\n🔍 Sample matched industry_ids:")
print(merged_df[[display_name_col, "industry_id"]].drop_duplicates().head(10))
