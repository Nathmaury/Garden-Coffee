from pathlib import Path
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DB_PATH = DATA_PROCESSED / "coffee.duckdb"
RAW_FILE = DATA_RAW / "coffee_db.parquet"

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")


def azure_base_url():
    partes = urlparse(AZURE_OPENAI_ENDPOINT)
    return f"{partes.scheme}://{partes.netloc}/openai/v1/"