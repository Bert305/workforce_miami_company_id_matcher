from datetime import datetime, timezone

import pandas as pd

# File paths
new_jobs_file = "new_jobs4.csv" # Output all of the rows with IDs that are not in the existing DB. Update filename as needed.
industries_file = "industries_rows.csv"
output_file = "new_jobs_cleaned_no_duplicates4.csv"

# IDs that already exist in the DB
existing_db_ids = {
    98829, 100854, 100292, 100858, 100470, 100390, 100730, 100405,
    100402, 100688, 99011, 99013, 99030, 100463, 100562, 100397,
    98989, 98995, 101075, 101102, 100764, 100852, 101083, 92041,
    101110, 100606, 100403, 100890, 100872, 100888, 100904, 100915,
    100902, 100899, 100875, 100893, 100892, 100900, 100878, 101024,
    100839, 100845, 100799, 96482, 96481, 98834, 100252, 98832
}

# Constant column values applied to every row
constants = {
    "company_name": "Miami-Dade County",
    "location": "Miami, FL",
    "job_type": "Full-time",
    "application_url": "https://www.miamidade.gov/global/humanresources/jobs/home.page",
    "is_active": "TRUE",
    "salary_period": "year",
    "is_bulk_upload": "TRUE",
    "remote_type": "",
    "approval_status": "Approved",
    "experience_level": "",
    "contact_email": "",
    "company_id": "d1dd1eb7-2686-4a8a-92be-3bf2e2e51cce",
    "category": "",
    "qualifications": "",
    "responsibilities": "",
    "is_featured": "",
    "verified": "",
    "applicant_count": 0,
    "outbound_clicks": 0,
    "applications_count": 0,
    "keywords": "",
    "external_clicks": 0,
}

# Final column order matching the target schema
output_cols = [
    "title", "posted_at", "expires_at", "created_at",
    "salary_min", "salary_max", "industry_id", "description",
    "company_name", "location", "job_type", "application_url",
    "is_active", "salary_period", "is_bulk_upload", "remote_type",
    "approval_status", "experience_level", "contact_email", "company_id",
    "category", "qualifications", "responsibilities", "is_featured",
    "verified", "applicant_count", "outbound_clicks", "applications_count",
    "keywords", "external_clicks",
]

# Load CSV
df = pd.read_csv(new_jobs_file)

# Make sure id column is numeric
df["Job ID"] = pd.to_numeric(df["Job ID"], errors="coerce")

# Remove rows where id already exists in DB
cleaned_df = df[~df["Job ID"].isin(existing_db_ids)].copy()

# Map industry name -> industry_id via industries_rows.csv
industries_df = pd.read_csv(industries_file)
industry_map = dict(zip(industries_df["name"], industries_df["id"]))
cleaned_df["industry_id"] = cleaned_df["industry"].map(industry_map).astype("Int64")

unmapped = cleaned_df.loc[cleaned_df["industry_id"].isna(), "industry"].dropna().unique()
if len(unmapped) > 0:
    print(f"WARNING: industries not found in {industries_file}: {list(unmapped)}")

# posted_at and created_at are set to the current UTC timestamp at script run
now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
cleaned_df["posted_at"] = now_utc
cleaned_df["created_at"] = now_utc

# Apply constant columns
for col, val in constants.items():
    cleaned_df[col] = val

# Drop columns not in the output schema
cleaned_df = cleaned_df.drop(columns=["Job ID", "industry"])

# Reorder to match the target schema
cleaned_df = cleaned_df[output_cols]

# Save cleaned file
cleaned_df.to_csv(output_file, index=False)

print(f"Original rows: {len(df)}")
print(f"Rows removed: {len(df) - len(cleaned_df)}")
print(f"Rows kept: {len(cleaned_df)}")
print(f"Cleaned file saved as: {output_file}")
