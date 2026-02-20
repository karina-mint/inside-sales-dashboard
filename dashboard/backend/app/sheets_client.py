from google.oauth2 import service_account
from googleapiclient.discovery import build

from .config import DASHBOARD_SHEET_NAME, SPREADSHEET_ID_2, get_service_account_info

SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def _get_service():
    creds = service_account.Credentials.from_service_account_info(
        get_service_account_info(), scopes=SHEETS_SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def fetch_dashboard_raw() -> list[list[str]]:
    """全体ダッシュボードシートの全データを2次元リストで返す。"""
    service = _get_service()
    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=SPREADSHEET_ID_2,
            range=f"{DASHBOARD_SHEET_NAME}!A:Z",
        )
        .execute()
    )
    return result.get("values", [])
