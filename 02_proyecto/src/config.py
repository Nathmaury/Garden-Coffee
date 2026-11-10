from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DB_PATH = DATA_PROCESSED / "coffee.duckdb"
RAW_FILE = DATA_RAW / "coffee_db.parquet"

LLM_MODEL = os.getenv("LLM_MODEL", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")