import pandas as pd
import os

# Load files
# Get the directory of the current script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Build absolute paths to the CSV files
supabase_path = os.path.join(base_dir, "Supabase Snippet Job Listing.csv")
scraped_jobs_path = os.path.join(base_dir, "Scraped Jobs 6-16-2025 - test-jobs (2).csv")

supabase_companies_df = pd.read_csv(supabase_path)  # company_id, name
scraped_jobs_df = pd.read_csv(scraped_jobs_path)  # includes company_name

# Drop any existing company_id column to avoid conflicts before merging
scraped_jobs_df = scraped_jobs_df.drop(columns=["company_id"], errors="ignore")

# Merge based on exact match between scraped job's company_name and Supabase company name
merged_df = scraped_jobs_df.merge(
    supabase_companies_df,
    how="left",
    left_on="company_name",
    right_on="name"
)

# Rename company_id from Supabase to the expected output field
merged_df.rename(columns={"company_id": "company_id"}, inplace=True)

# Drop redundant 'name' column (from Supabase side)
merged_df.drop(columns=["name"], inplace=True)

# Move company_id next to company_name
cols = merged_df.columns.tolist()
if "company_id" in cols and "company_name" in cols:
    cols.insert(cols.index("company_name") + 1, cols.pop(cols.index("company_id")))
    merged_df = merged_df[cols]

# Export to new CSV
output_path = os.path.join(base_dir, "Updated_Scraped_Jobs_With_Company_ID2.csv")
merged_df.to_csv(output_path, index=False)
print(f"✅ Updated file saved to: {output_path}")

# Optional: Print first few matched results to terminal
print("\n🔍 Sample matched company names and IDs:")
print(merged_df[["company_name", "company_id"]].drop_duplicates().head(10))
