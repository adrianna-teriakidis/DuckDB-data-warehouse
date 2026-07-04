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
DB_PATH = PROJECT_ROOT / "database" / "nhs_data.duckdb"


def load_domain(domain: str):
    domain_folder = RAW_DATA_ROOT / domain
    csv_glob = str(domain_folder / "*.csv") 

    con = duckdb.connect(str(DB_PATH))
    con.execute(
        #this will concatenate all the csvs in the folder into one file. 
        # It requires that every CSV in the folder has the same format or it will error.
        f'CREATE OR REPLACE TABLE "{domain}" AS '
        f"SELECT * FROM read_csv_auto('{csv_glob}')"  
    )
    count = con.execute(f'SELECT COUNT(*) FROM "{domain}"').fetchone()[0]
    print(f"Loaded {count} rows into {domain}") #might want to print other things here in future
    con.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "domain",
        help="Name of the raw data subfolder to load (also used as the table name)",
    )
    args = parser.parse_args()
    load_domain(args.domain)
