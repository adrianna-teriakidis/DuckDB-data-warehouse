import argparse
import re
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from load_raw_data import RAW_DATA_ROOT

# The index page links out to one sub-page per fiscal year (April-March) -
# each sub-page's URL contains the fiscal year, e.g. "...-2026-27/".
INDEX_URL = "https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/"
YEAR_PAGE_PATTERN = re.compile(r"ae-attendances-and-emergency-admissions-(\d{4})-\d{2}")

# Years before this only published XLS files, no CSVs, so there's nothing for this script to grab.
EARLIEST_CSV_YEAR = 2018

FISCAL_MONTHS = [
    "April", "May", "June", "July", "August", "September",
    "October", "November", "December", "January", "February", "March",
]


def find_year_pages(index_url: str) -> dict[int, str]:
    """Map each fiscal year's start year (e.g. 2026 for "2026-27") to its stats sub-page URL."""
    response = requests.get(index_url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    year_pages = {}
    for a in soup.find_all("a", href=True):
        match = YEAR_PAGE_PATTERN.search(a["href"])
        if match:
            year_pages[int(match.group(1))] = urljoin(index_url, a["href"])
    return year_pages


def find_csv_links(page_url: str) -> list[str]:
    response = requests.get(page_url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".csv"):
            links.append(urljoin(page_url, href))
    return links


def read_period_month_year(csv_path: Path) -> tuple[str, int] | None:
    """Read the "Period" value from a CSV's first data row, e.g. "MSitAE-DECEMBER-2025" -> ("December", 2025)."""
    with csv_path.open(encoding="utf-8-sig") as f:
        next(f)  # header row
        first_data_row = f.readline()

    period = first_data_row.split(",", 1)[0]
    parts = period.split("-")
    if len(parts) != 3:
        return None

    _, month, year = parts
    return month.capitalize(), int(year)


def scan_downloaded_months(domain_folder: Path) -> dict[tuple[str, int], list[Path]]:
    by_month: dict[tuple[str, int], list[Path]] = {}
    for csv_path in domain_folder.glob("*.csv"):
        key = read_period_month_year(csv_path)
        if key is None:
            print(f"  WARNING: couldn't read a Period value from {csv_path.name}")
            continue
        by_month.setdefault(key, []).append(csv_path)
    return by_month


def check_one_file_per_month(fiscal_start_year: int, by_month: dict[tuple[str, int], list[Path]]):
    for i, month in enumerate(FISCAL_MONTHS):
        year = fiscal_start_year if i < 9 else fiscal_start_year + 1
        matches = by_month.get((month, year), [])
        if not matches:
            print(f"  WARNING: no CSV found for {month} {year}")
        elif len(matches) > 1:
            names = [p.name for p in matches]
            print(f"  WARNING: {len(matches)} CSVs found for {month} {year}: {names}")


def download_new_files(page_url: str, domain_folder: Path):
    domain_folder.mkdir(parents=True, exist_ok=True)
    already_downloaded = {p.name for p in domain_folder.glob("*.csv")}

    csv_links = find_csv_links(page_url)
    new_links = [
        url for url in csv_links if url.rsplit("/", 1)[-1] not in already_downloaded
    ]

    if not new_links:
        print("No new CSVs found.")
        return

    for url in new_links:
        filename = url.rsplit("/", 1)[-1]
        dest = domain_folder / filename

        print(f"Downloading {filename}...")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        dest.write_bytes(response.content)

    print(f"Downloaded {len(new_links)} new file(s)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--from-year",
        type=int,
        default=None,
        help="Fiscal year to start from, e.g. 2023 for 2023-24 "
        "(default: the latest year found on the index page)",
    )
    parser.add_argument(
        "--to-year",
        type=int,
        default=None,
        help="Fiscal year to end at, inclusive (default: same as --from-year)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help=f"Download every year that has CSVs, back to {EARLIEST_CSV_YEAR} "
        "(overrides --from-year/--to-year)",
    )
    parser.add_argument(
        "--domain",
        default="ae_data",
        help="Raw data subfolder to save into (default: ae_data)",
    )
    args = parser.parse_args()

    year_pages = find_year_pages(INDEX_URL)
    if args.all:
        from_year, to_year = EARLIEST_CSV_YEAR, max(year_pages)
    else:
        from_year = args.from_year or max(year_pages)
        to_year = args.to_year or from_year

    domain_folder = RAW_DATA_ROOT / args.domain
    for year, page_url in sorted(year_pages.items()):
        if from_year <= year <= to_year:
            print(f"--- {year}-{str(year + 1)[-2:]} ---")
            download_new_files(page_url, domain_folder)

    by_month = scan_downloaded_months(domain_folder)
    for year in range(from_year, to_year + 1):
        print(f"--- checking {year}-{str(year + 1)[-2:]} ---")
        check_one_file_per_month(year, by_month)
