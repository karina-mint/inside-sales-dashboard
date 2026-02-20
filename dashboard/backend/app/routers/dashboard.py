from fastapi import APIRouter, HTTPException, Query

from ..models import DashboardResponse
from ..parser import parse_dashboard
from ..sheets_client import fetch_dashboard_raw

router = APIRouter()


@router.get("/api/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    month: str = Query(default="", description="対象月 YYYY/MM 形式。省略時は最新月。"),
):
    try:
        raw = fetch_dashboard_raw()
        return parse_dashboard(raw, selected_month=month)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
