import argparse
from pathlib import Path

import duckdb

# This function finds the root of the project by looking for a .git folder 
# in the current directory or any of its parent directories. If it doesn't 
# find a .git folder, it raises a FileNotFoundError.
def find_project_root(start: Path) -> Path:
    for directory in [start, *start.parents]:
        if (directory / ".git").exists():
            return directory
    raise FileNotFoundError(f"No .git folder found above {start}")


PROJECT_ROOT = find_project_root(Path(__file__).resolve().parent) #get the folder of the current file in full
RAW_DATA_ROOT = PROJECT_ROOT / "raw data"
DB_PATHS = {
    "prod": PROJECT_ROOT / "database" / "nhs_data.duckdb",
    "dev": PROJECT_ROOT / "database" / "nhs_data_dev.duckdb",
}


def load_domain(domain: str, target: str):
    domain_folder = RAW_DATA_ROOT / domain
    csv_glob = str(domain_folder / "*.csv")

    con = duckdb.connect(str(DB_PATHS[target]))
    con.execute(
        #this will concatenate all the csvs in the folder into one file.
        # union_by_name aligns columns by name across files instead of position,
        # filling NULL for any column a given file doesn't have (e.g. older files
        # missing the booked-appointments columns, or using different header wording).
        f'CREATE OR REPLACE TABLE "{domain}" AS '
        f"SELECT * FROM read_csv_auto('{csv_glob}', union_by_name=true)"
    )
    count = con.execute(f'SELECT COUNT(*) FROM "{domain}"').fetchone()[0]
    print(f"Loaded {count} rows into {domain} ({target})") #might want to print other things here in future
    con.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "domain",
        help="Name of the raw data subfolder to load (also used as the table name)",
    )
    parser.add_argument(
        "--target",
        choices=sorted(DB_PATHS),
        default="dev",
        help="Which database to load into (default: dev)",
    )
    args = parser.parse_args()
    load_domain(args.domain, args.target)
