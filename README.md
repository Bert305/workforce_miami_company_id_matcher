# workforce_miami_company_id_matcher

## Overview

`workforce_miami_company_id_matcher` is a Python tool designed to match company names from a dataset to their corresponding company IDs using fuzzy string matching. This helps standardize company identifiers across different data sources.

## Features

- Reads company names from a CSV file.
- Matches each company name to the closest company ID using fuzzy matching.
- Outputs results to a new CSV file with matched IDs.
- Configurable matching threshold.

## Requirements

- Python 3.7+
- The following Python libraries:
    - `pandas`
    - `fuzzywuzzy`
    - `python-Levenshtein` (optional, for faster fuzzywuzzy performance)

Install dependencies with:

```bash
pip install pandas fuzzywuzzy python-Levenshtein
```

## Usage

1. Place your input CSV file (e.g., `input.csv`) in the project directory.
2. Prepare a reference CSV file containing company names and their IDs (e.g., `reference.csv`).
3. Run the matcher:

```bash
python main.py --input input.csv --reference reference.csv --output output.csv --threshold 85
```

- `--input`: Path to the CSV file with company names to match.
- `--reference`: Path to the CSV file with reference company names and IDs.
- `--output`: Path to save the output CSV with matched IDs.
- `--threshold`: (Optional) Minimum match score (default: 85).

## Example

```bash
python main.py --input companies_to_match.csv --reference company_reference.csv --output matched_companies.csv
```

## ---------------------apprentices.py-----------------------------------------

# Quick Documentation Instructions:
# 1. Update CSV file name old, new and the output
# 2. Update file path name making sure the match, old and new file name
# 3. Must use terminal to run the file (files must match ALSO): python apprentices.py old_app_test.csv new_app_test.csv


# Basic usage - FOR TERMINAL -- **USE THIS ONE**Params must also match files and path!!!!!
python apprentices.py old_app.csv new_app.csv

# With custom output filename
python apprentices.py old_app.csv new_app.csv -o my_changes.csv

# Using full paths
python apprentices.py "C:\path\to\old.csv" "C:\path\to\new.csv"

## ------------------------------------------------------------------------------
## License

MIT License