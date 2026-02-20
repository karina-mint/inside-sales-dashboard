import json
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (3 levels up: app/ -> backend/ -> dashboard/ -> my-agent-05/)
load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")

SPREADSHEET_ID_2: str = os.environ["SPREADSHEET_ID_2"]
DASHBOARD_SHEET_NAME: str = "全体ダッシュボード"


def get_service_account_info() -> dict:
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not raw:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON is not set")
    return json.loads(raw)
