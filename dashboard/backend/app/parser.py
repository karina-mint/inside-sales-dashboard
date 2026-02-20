import re
from datetime import datetime, timezone, timedelta
from typing import Optional

from .models import DashboardResponse, FunnelStage, KpiCard, MonthlyRow

JST = timezone(timedelta(hours=9))

# ── 行ラベル定数（全角スペース \u3000 は strip 後の値に合わせる）─────────────────────
# 案件化セクション
ROW_ANKENJIKA_TARGET = "目標：案件化数"
ROW_ANKENJIKA_ACTUAL = "実績：案件化数"
ROW_ANKENJIKA_RATE_TARGET = "目標：案件化率"
ROW_ANKENJIKA_RATE_ACTUAL = "実績：案件化率"
ROW_APO_JISSHI = "実績：アポ実施数"

# アポ獲得セクション（シート上はスラッシュ前後にスペースあり）
ROW_APO_TARGET = "目標：アポ数"
ROW_APO_ACTUAL = "実績：アポ数"
ROW_APO_RATE_TARGET = "目標：アポ化率（新規アポ数 / 有効リード数）"
ROW_APO_RATE_ACTUAL = "実績：アポ化率（新規アポ数 / 有効リード数）"
ROW_APO_RATE_TSUUDEN = "実績：アポ化率（新規アポ数 / 通電数）"
ROW_TSUUDEN_RATE = "実績：通電率"
ROW_TSUUDEN_COUNT = "実績：通電数"

# リード獲得セクション
ROW_LEAD_TARGET = "目標：リード数"
ROW_LEAD_VALID_TARGET = "目標：有効リード数"
ROW_LEAD_VALID_ACTUAL = "実績：有効リード数"
ROW_LEAD_VALID_RATE = "有効リード率"
ROW_LEAD_NEW = "新規リード数"

# KPI card definitions: (label, target_row, actual_row, unit)
KPI_DEFINITIONS = [
    ("案件獲得", ROW_ANKENJIKA_TARGET, ROW_ANKENJIKA_ACTUAL, "件"),
    ("アポ獲得", ROW_APO_TARGET, ROW_APO_ACTUAL, "件"),
    ("通電数", None, ROW_TSUUDEN_COUNT, "件"),
    ("有効リード数", ROW_LEAD_VALID_TARGET, ROW_LEAD_VALID_ACTUAL, "件"),
    ("新規リード数", None, ROW_LEAD_NEW, "件"),
]

# Funnel: (label, actual_row, benchmark_row, fallback_benchmark)
FUNNEL_DEFINITIONS = [
    ("案件化率", ROW_ANKENJIKA_RATE_ACTUAL, ROW_ANKENJIKA_RATE_TARGET, 0.15),
    ("アポ獲得率", ROW_APO_RATE_TSUUDEN, None, 0.15),
    ("通電率", ROW_TSUUDEN_RATE, None, 0.50),
]

SECTION_ANKENJIKA_ROWS = [
    ROW_ANKENJIKA_TARGET,
    ROW_ANKENJIKA_ACTUAL,
    ROW_ANKENJIKA_RATE_TARGET,
    ROW_ANKENJIKA_RATE_ACTUAL,
    ROW_APO_JISSHI,
]

SECTION_APO_ROWS = [
    ROW_APO_TARGET,
    ROW_APO_ACTUAL,
    ROW_APO_RATE_TSUUDEN,
    "目標：アポ獲得率",
    ROW_TSUUDEN_RATE,
    "目標：通電率",
    ROW_TSUUDEN_COUNT,
]

# 固定ベンチマーク値（シートに存在しない行）
FIXED_VALUE_ROWS: dict[str, float] = {
    "目標：アポ獲得率": 0.15,
    "目標：通電率": 0.50,
}

SECTION_LEAD_ROWS = [
    ROW_LEAD_VALID_TARGET,
    ROW_LEAD_VALID_ACTUAL,
    ROW_LEAD_NEW,
]

# 表示ラベルの上書きマップ（シートのラベル → 表示名）
LABEL_OVERRIDES: dict[str, str] = {
    ROW_APO_TARGET: "目標：アポ獲得数",
    ROW_APO_ACTUAL: "実績：アポ獲得数",
    ROW_APO_RATE_TSUUDEN: "実績：アポ獲得率",
    "目標：アポ獲得率": "目標：アポ獲得率（15%）",
    "目標：通電率": "目標：通電率（50%）",
}


# ── ヘルパー ─────────────────────────────────────────────────────────────────

def _clean(val: str) -> str:
    """先頭・末尾の ASCII 空白および全角スペース(\u3000)を除去。"""
    return val.strip().strip("\u3000").strip()


def _to_float(val: Optional[str]) -> Optional[float]:
    """シート値を float に正規化。パーセント表記と数値表記の両方に対応。"""
    if not val:
        return None
    val = val.strip().replace(",", "")
    if val in ("-", "---", "#DIV/0!", "#N/A", ""):
        return None
    if val.endswith("%"):
        try:
            return float(val[:-1]) / 100
        except ValueError:
            return None
    try:
        return float(val)
    except ValueError:
        return None


def _find_header_row(raw: list[list[str]]) -> Optional[int]:
    """'指標' を A列に持つ行インデックスを返す（ダッシュボードセクションのヘッダー行）。"""
    for i, row in enumerate(raw):
        if row and _clean(row[0]) == "指標":
            return i
    return None


def _parse_month_headers(header_row: list[str]) -> dict[str, int]:
    """'YYYY年MM月' パターンの列ヘッダーから {YYYY/MM: col_index} を返す。"""
    result: dict[str, int] = {}
    for i, h in enumerate(header_row):
        m = re.match(r"(\d{4})年(\d{1,2})月", h.strip())
        if m:
            year = m.group(1)
            month = m.group(2).zfill(2)
            result[f"{year}/{month}"] = i
    return result


def _build_row_index(raw: list[list[str]]) -> dict[str, int]:
    """A列の値（全角スペース除去済み）をキーに行インデックスを返すマップを構築。
    同じラベルが複数行ある場合は最初の行を優先。"""
    result: dict[str, int] = {}
    for i, row in enumerate(raw):
        if row and row[0].strip():
            key = _clean(row[0])
            if key and key not in result:
                result[key] = i
    return result


def _get_cell(
    raw: list[list[str]],
    row_map: dict[str, int],
    metric: str,
    col_idx: int,
) -> Optional[float]:
    row_idx = row_map.get(metric)
    if row_idx is None:
        return None
    row = raw[row_idx]
    if col_idx >= len(row):
        return None
    return _to_float(row[col_idx])


# ── メイン解析関数 ─────────────────────────────────────────────────────────────

def parse_dashboard(raw: list[list[str]], selected_month: str = "") -> DashboardResponse:
    if not raw:
        raise ValueError("シートデータが空です")

    # ダッシュボードセクションのヘッダー行を動的に探す
    header_row_idx = _find_header_row(raw)
    if header_row_idx is None:
        raise ValueError("ダッシュボードヘッダー行（A列='指標'）が見つかりません")

    header_row = raw[header_row_idx]
    month_cols = _parse_month_headers(header_row)
    available_months = sorted(month_cols.keys())

    if not available_months:
        raise ValueError("月列が見つかりません（'YYYY年MM月' 形式の列ヘッダーが必要）")

    # selected_month が未指定 or 不正な場合は最新月を使用
    if not selected_month or selected_month not in month_cols:
        selected_month = available_months[-1]

    sel_col = month_cols[selected_month]
    row_map = _build_row_index(raw)

    # ── KPI cards ─────────────────────────────────────────────────────────────
    kpi_cards: list[KpiCard] = []
    for label, target_row, actual_row, unit in KPI_DEFINITIONS:
        target = _get_cell(raw, row_map, target_row, sel_col) if target_row else None
        actual = _get_cell(raw, row_map, actual_row, sel_col) if actual_row else None
        achievement = (actual / target) if (actual is not None and target and target != 0) else None
        kpi_cards.append(KpiCard(
            label=label,
            target=target,
            actual=actual,
            achievement_rate=achievement,
            unit=unit,
        ))

    # ── Funnel stages ──────────────────────────────────────────────────────────
    funnel_stages: list[FunnelStage] = []
    for label, actual_row, benchmark_row, fallback_benchmark in FUNNEL_DEFINITIONS:
        actual = _get_cell(raw, row_map, actual_row, sel_col)
        benchmark_val = _get_cell(raw, row_map, benchmark_row, sel_col) if benchmark_row else None
        benchmark = benchmark_val if (benchmark_val is not None and benchmark_val != 0) else fallback_benchmark
        achievement = (actual / benchmark) if (actual is not None and benchmark != 0) else None
        funnel_stages.append(FunnelStage(
            label=label,
            actual=actual,
            benchmark=benchmark,
            achievement_rate=achievement,
        ))

    # ── 月別明細セクション ────────────────────────────────────────────────────
    def build_section(metric_labels: list[str]) -> list[MonthlyRow]:
        rows = []
        for metric in metric_labels:
            cols: dict[str, Optional[float]] = {}
            if metric in FIXED_VALUE_ROWS:
                fixed_val = FIXED_VALUE_ROWS[metric]
                for month_key in month_cols:
                    cols[month_key] = fixed_val
            else:
                for month_key, col_idx in month_cols.items():
                    cols[month_key] = _get_cell(raw, row_map, metric, col_idx)
            display_label = LABEL_OVERRIDES.get(metric, metric)
            rows.append(MonthlyRow(metric=display_label, columns=cols))
        return rows

    now_jst = datetime.now(JST).isoformat()

    return DashboardResponse(
        available_months=available_months,
        selected_month=selected_month,
        kpi_cards=kpi_cards,
        funnel_stages=funnel_stages,
        section_ankenjika=build_section(SECTION_ANKENJIKA_ROWS),
        section_apo_kakutoku=build_section(SECTION_APO_ROWS),
        section_lead_kakutoku=build_section(SECTION_LEAD_ROWS),
        last_updated=now_jst,
    )
