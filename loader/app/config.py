import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# LAKE DATABASE
LAKE_DB_HOST = os.getenv("LAKE_DB_HOST", "localhost")
LAKE_DB_PORT = os.getenv("LAKE_DB_PORT", "5432")
LAKE_DB_NAME = os.getenv("LAKE_DB_NAME", "lake")
LAKE_DB_USER = os.getenv("LAKE_DB_USER", "postgres")
LAKE_DB_PASSWORD = os.getenv("LAKE_DB_PASSWORD", "postgres")

# WAREHOUSE DATABASE
WAREHOUSE_DB_HOST = os.getenv("WAREHOUSE_DB_HOST", "localhost")
WAREHOUSE_DB_PORT = os.getenv("WAREHOUSE_DB_PORT", "5432")
WAREHOUSE_DB_NAME = os.getenv("WAREHOUSE_DB_NAME", "warehouse")
WAREHOUSE_DB_USER = os.getenv("WAREHOUSE_DB_USER", "postgres")
WAREHOUSE_DB_PASSWORD = os.getenv("WAREHOUSE_DB_PASSWORD", "postgres")