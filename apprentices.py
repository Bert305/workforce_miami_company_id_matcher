import argparse
import pandas as pd
from pathlib import Path

# Required columns in your CSVs
REQ = ["ID", "Title"]

def read_csv_required(path: Path) -> pd.DataFrame:
    """Read CSV, validate required columns, and normalize strings."""
    if path.suffix.lower() != ".csv":
        raise ValueError(f"Only CSV files are supported. Got: {path.suffix} for {path}")
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = [c for c in REQ if c not in df.columns]
    if missing:
        raise ValueError(f"{path} missing columns: {missing}")

    # Normalize
    df = df.copy()
    for c in REQ:
        df[c] = df[c].astype(str).str.strip()
    return df

def summarize_by_id(df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize per ID:
      - count of Title rows
      - unique titles set (sorted list)
    """
    return (
        df.groupby("ID", as_index=False)
          .agg(
              count=("Title", "size"),
              titles=("Title", lambda s: sorted({t for t in s if t}))
          )
    )

def compare(old_path: Path, new_path: Path) -> pd.DataFrame:
    """
    Core comparison:
      - New IDs (in NEW, not in OLD) -> change_type = 'new_id'
      - Same ID but different counts OR new titles added in NEW
        -> change_type = 'count_or_title_change'
      - Removals are ignored
    """
    old = summarize_by_id(read_csv_required(old_path)).set_index("ID")
    new = summarize_by_id(read_csv_required(new_path)).set_index("ID")

    rows = []
    for id_, n in new.iterrows():
        if id_ not in old.index:
            # Entirely new apprenticeship ID
            rows.append({
                "change_type": "new_id",
                "ID": id_,
                "old_count": 0,
                "new_count": int(n["count"]),
                "new_titles_added": n["titles"],       # all titles for this new ID
            })
        else:
            o = old.loc[id_]
            # Titles added in NEW vs OLD
            added_titles = sorted(set(n["titles"]) - set(o["titles"]))
            # If counts differ OR new titles appeared, report it
            if int(n["count"]) != int(o["count"]) or added_titles:
                rows.append({
                    "change_type": "count_or_title_change",
                    "ID": id_,
                    "old_count": int(o["count"]),
                    "new_count": int(n["count"]),
                    "new_titles_added": added_titles,    # only titles added in NEW
                })

    return pd.DataFrame(
        rows,
        columns=["change_type", "ID", "old_count", "new_count", "new_titles_added"]
    )

def resolve_under_base(arg_value: str, base_dir: Path) -> Path:
    """
    Resolve a path so that:
      - absolute paths are used as-is
      - relative paths are treated as relative to the script's directory
    """
    p = Path(arg_value).expanduser()
    return p if p.is_absolute() else (base_dir / p)

def main():
    ap = argparse.ArgumentParser(
        description="Compare two CSVs by ID; report new IDs and added titles/count changes."
    )
    # parameters can be updated to match CSV files. But make sure they also match in the Path context.
    ap.add_argument("pre_app_test_old", help="Path to OLD CSV (absolute or relative to this script)") # update old filename here
    ap.add_argument("pre_app_test_new", help="Path to NEW CSV (absolute or relative to this script)") # update new filename here
    ap.add_argument("-o", "--out", default="differences_test_pre_app_4.csv", # update output filename here
                    help="Output CSV path (absolute or relative to this script). Default: differences.csv")
    args = ap.parse_args()
    #Path Context Here--------------Parameters must match!!!!
    base_dir = Path(__file__).resolve().parent
    old_path = resolve_under_base(args.pre_app_test_old, base_dir) # params must match CSV files!!!!!!
    new_path = resolve_under_base(args.pre_app_test_new, base_dir) # params must match CSV files!!!!!!
    out_path = resolve_under_base(args.out, base_dir)
    #Note IMPORTANT:Terminal usage ONLY params must also match files and path!!!--> python apprentices.py old_app_test.csv new_app_test.csv
    out_df = compare(old_path, new_path)

    # Always write a CSV (even if empty), to make automation easy
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)

    if out_df.empty:
        print(f"No changes detected. Empty report written to: {out_path}")
    else:
        print(f"Changes detected. Report written to: {out_path}")

if __name__ == "__main__":
    main()

 #Note IMPORTANT: Terminal usage ONLY params must also match files and path!!!--> python apprentices.py old_app_test.csv new_app_test.csv

