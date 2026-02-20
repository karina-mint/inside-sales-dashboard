from typing import Optional

from pydantic import BaseModel


class KpiCard(BaseModel):
    label: str
    target: Optional[float] = None
    actual: Optional[float] = None
    achievement_rate: Optional[float] = None
    unit: str  # "件" or "%"


class FunnelStage(BaseModel):
    label: str
    actual: Optional[float] = None
    benchmark: float
    achievement_rate: Optional[float] = None


class MonthlyRow(BaseModel):
    metric: str
    columns: dict[str, Optional[float]]


class DashboardResponse(BaseModel):
    available_months: list[str]
    selected_month: str
    kpi_cards: list[KpiCard]
    funnel_stages: list[FunnelStage]
    section_ankenjika: list[MonthlyRow]
    section_apo_kakutoku: list[MonthlyRow]
    section_lead_kakutoku: list[MonthlyRow]
    last_updated: str
