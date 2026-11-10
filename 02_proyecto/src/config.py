from pathlib import Path
impo
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

DATA_RAW = ROOT_DIR / "data" / "raw"
DATA_PROCESSED = ROOT_DIR / "data" / "processed"
DB_PATH = DATA_PROCESSED / "coffee.duckdb"
RAW_FILE = DATA_RAW / "coffee_db.parquet"

LLM_FILE = DATA_RAW / "coffee_db.parquet"

LLM_MODEL = os.getenv("LLM_MODEL", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")