# Open Source Data Warehouse

A personal project to build a fully open source, self-hosted data warehouse stack from scratch. 

## Stack
- **DuckDB** — analytical query engine
- **dbt** — data transformation
- **Apache Superset** — visualisation and dashboards
- **Apache Airflow** — orchestration
- **MinIO** — object storage
- **Apache Iceberg** — table format

## Prerequisites
- Python 3.12+
- Git

## Installation

1. Clone the repository
```bash
   git clone https://github.com/adrianna-teriakidis/data-warehouse.git
   cd data-warehouse
```

2. Create and activate virtual environment
```bash
   python3 -m venv venv
   source venv/bin/activate
```

3. Install dependencies
```bash
   pip install -r requirements.txt
```

## Project Structure
