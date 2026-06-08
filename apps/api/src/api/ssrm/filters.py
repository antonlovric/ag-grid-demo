from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import and_, or_


def build_filter_clause(col_attr, entry: dict[str, Any]):
    """Translate one AG Grid filterModel entry into a SQLAlchemy clause."""
    if "operator" in entry:
        sub = [build_filter_clause(col_attr, c) for c in entry.get("conditions", [])]
        return and_(*sub) if entry["operator"] == "AND" else or_(*sub)

    match entry.get("filterType", "text"):
        case "text":
            return _text_clause(col_attr, entry)
        case "number":
            return _number_clause(col_attr, entry)
        case "date":
            return _date_clause(col_attr, entry)
        case "set":
            return _set_clause(col_attr, entry)
        case _:
            return _text_clause(col_attr, entry)


def _text_clause(col, entry: dict):
    v = entry.get("filter") or ""
    match entry.get("type", "contains"):
        case "contains":    return col.ilike(f"%{v}%")
        case "notContains": return ~col.ilike(f"%{v}%")
        case "equals":      return col == v
        case "notEqual":    return col != v
        case "startsWith":  return col.ilike(f"{v}%")
        case "endsWith":    return col.ilike(f"%{v}")
        case "blank":       return or_(col.is_(None), col == "")
        case "notBlank":    return and_(col.is_not(None), col != "")
        case _:             return col.ilike(f"%{v}%")


def _number_clause(col, entry: dict):
    v, v2 = entry.get("filter"), entry.get("filterTo")
    match entry.get("type", "equals"):
        case "equals":             return col == v
        case "notEqual":           return col != v
        case "greaterThan":        return col > v
        case "greaterThanOrEqual": return col >= v
        case "lessThan":           return col < v
        case "lessThanOrEqual":    return col <= v
        case "inRange":            return and_(col >= v, col <= v2)
        case "blank":              return col.is_(None)
        case "notBlank":           return col.is_not(None)
        case _:                    return col == v


def _date_clause(col, entry: dict):
    def _parse(s: str | None) -> date | None:
        if not s:
            return None
        try:
            return datetime.strptime(s[:10], "%Y-%m-%d").date()
        except ValueError:
            return None

    d_from = _parse(entry.get("dateFrom"))
    d_to = _parse(entry.get("dateTo"))
    match entry.get("type", "equals"):
        case "equals":      return col == d_from
        case "notEqual":    return col != d_from
        case "greaterThan": return col > d_from
        case "lessThan":    return col < d_from
        case "inRange":     return and_(col >= d_from, col <= d_to)
        case "blank":       return col.is_(None)
        case "notBlank":    return col.is_not(None)
        case _:             return col >= d_from


def _set_clause(col, entry: dict):
    values = entry.get("values", [])
    non_null = [v for v in values if v is not None]
    has_null = None in values

    if not non_null and not has_null:
        return col.in_([])

    clause = col.in_(non_null) if non_null else None
    if has_null:
        null_clause = col.is_(None)
        clause = or_(clause, null_clause) if clause is not None else null_clause
    return clause
