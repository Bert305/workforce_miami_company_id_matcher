import pandas as pd

# File paths
new_jobs_file = "new_jobs.csv"
output_file = "new_jobs_cleaned_no_duplicates.csv"

# IDs that already exist in the DB
existing_db_ids = {
    100885, 98829, 100861, 100974, 100837, 100982, 100992, 100988,
    100762, 100810, 100854, 100653, 100886, 100794, 100292, 100117,
    100129, 100445, 100968, 100858, 100630, 100879, 100341, 100957,
    100267, 100250, 100213, 100342, 100270, 100788, 100851, 100429,
    100434, 100470, 100390, 100730, 100405, 100402, 100688, 100711,
    100820, 100464, 99011, 99013, 100844, 100753, 99030, 100984,
    100422, 100463, 100562, 100397, 98989, 98995, 100791, 100864,
    100797, 100798, 96482, 96481, 100418, 98834, 100252, 98832
}

# Load CSV
df = pd.read_csv(new_jobs_file)

# Make sure id column is numeric
df["Job ID"] = pd.to_numeric(df["Job ID"], errors="coerce")

# Remove rows where id already exists in DB
cleaned_df = df[~df["Job ID"].isin(existing_db_ids)]

# Save cleaned file
cleaned_df.to_csv(output_file, index=False)

print(f"Original rows: {len(df)}")
print(f"Rows removed: {len(df) - len(cleaned_df)}")
print(f"Rows kept: {len(cleaned_df)}")
print(f"Cleaned file saved as: {output_file}")