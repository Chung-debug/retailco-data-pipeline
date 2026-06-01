import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# TEAM SETTINGS
TEAM_NAME = "Team E"
TEAM_ID = "716e01fe-788e-404d-a6cf-e7643836b935"

# API SETTINGS
API_BASE_URL = "https://hngstage8da-55c7f5f769c8.herokuapp.com"
API_KEY = os.getenv("RETAILCO_API_KEY")

# REQUEST SETTINGS
DEFAULT_PAGE_SIZE = 100
REQUEST_TIMEOUT = 60
MAX_RETRIES = 5
BACKOFF_BASE_SECONDS = 1

# DATABASE SETTINGS
DB_HOST = os.getenv("LAKE_DB_HOST")
DB_PORT = os.getenv("LAKE_DB_PORT")
DB_NAME = os.getenv("LAKE_DB_NAME")
DB_USER = os.getenv("LAKE_DB_USER")
DB_PASSWORD = os.getenv("LAKE_DB_PASSWORD")

# PIPELINE SETTINGS
RAW_SCHEMA = "raw"
META_SCHEMA = "meta"
WATERMARK_TABLE = "watermarks"
RUN_LOG_TABLE = "extract_run_log"
