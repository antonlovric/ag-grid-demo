from __future__ import annotations

from typing import Any

from sqlalchemy import asc, desc, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from api.ssrm.filters import build_filter_clause
from api.ssrm.schema import SSRMRequest

_AGG_FN_MAP = {
    "sum": func.sum,
    "avg": func.avg,
    "min": func.min,
    "max": func.max,
    "count": func.count,
}


async def execute_ssrm(
    session: AsyncSession,
    model: type[SQLModel],
    col_map: dict[str, Any],
    req: SSRMRequest,
) -> dict:
    is_grouping = len(req.row_group_cols) > 0
    all_groups_open = len(req.group_keys) == len(req.row_group_cols)

    if is_grouping and not all_groups_open:
        return await _group_query(session, model, col_map, req)
    return await _flat_query(session, model, col_map, req)


async def _flat_query(
    session: AsyncSession,
    model: type[SQLModel],
    col_map: dict,
    req: SSRMRequest,
) -> dict:
    where = _build_where(col_map, req)

    count_stmt = select(func.count()).select_from(model)
    if where:
        count_stmt = count_stmt.where(*where)
    total = (await session.execute(count_stmt)).scalar_one()

    stmt = select(model)
    if where:
        stmt = stmt.where(*where)
    stmt = _apply_group_key_filters(stmt, col_map, req)

    for s in req.sort_model:
        col_attr = col_map.get(s.col_id)
        if col_attr is not None:
            stmt = stmt.order_by(asc(col_attr) if s.sort == "asc" else desc(col_attr))

    if req.start_row is not None and req.end_row is not None:
        stmt = stmt.offset(req.start_row).limit(req.end_row - req.start_row)

    rows = (await session.execute(stmt)).scalars().all()
    return {"rowData": [_serialize(r) for r in rows], "rowCount": total}


async def _group_query(
    session: AsyncSession,
    model: type[SQLModel],
    col_map: dict,
    req: SSRMRequest,
) -> dict:
    depth = len(req.group_keys)
    group_col_def = req.row_group_cols[depth]
    group_attr = col_map.get(group_col_def.field or group_col_def.id)

    if group_attr is None:
        return {"rowData": [], "rowCount": 0}

    agg_exprs = []
    agg_names = []
    for vc in req.value_cols:
        vc_attr = col_map.get(vc.field or vc.id)
        if vc_attr is None:
            continue
        agg_fn = _AGG_FN_MAP.get((vc.agg_func or "sum").lower(), func.sum)
        col_name = vc.field or vc.id
        agg_exprs.append(agg_fn(vc_attr).label(col_name))
        agg_names.append(col_name)

    where = _build_where(col_map, req)

    stmt = select(group_attr, *agg_exprs).select_from(model)
    if where:
        stmt = stmt.where(*where)
    stmt = _apply_group_key_filters(stmt, col_map, req)
    stmt = stmt.group_by(group_attr).order_by(group_attr)

    count_stmt = select(func.count(distinct(group_attr))).select_from(model)
    if where:
        count_stmt = count_stmt.where(*where)
    count_stmt = _apply_group_key_filters(count_stmt, col_map, req)
    total = (await session.execute(count_stmt)).scalar_one()

    result = (await session.execute(stmt)).all()
    field_name = group_col_def.field or group_col_def.id
    rows = []
    for row in result:
        d = {field_name: row[0]}
        for i, name in enumerate(agg_names):
            d[name] = row[i + 1]
        rows.append(d)

    return {"rowData": rows, "rowCount": total}


def _build_where(col_map: dict, req: SSRMRequest) -> list:
    clauses = []
    for col_id, entry in req.filter_model.items():
        col_attr = col_map.get(col_id)
        if col_attr is not None:
            clauses.append(build_filter_clause(col_attr, entry))
    return clauses


def _apply_group_key_filters(stmt, col_map: dict, req: SSRMRequest):
    for i, key in enumerate(req.group_keys):
        if i < len(req.row_group_cols):
            col_def = req.row_group_cols[i]
            col_attr = col_map.get(col_def.field or col_def.id)
            if col_attr is not None:
                stmt = stmt.where(col_attr == key)
    return stmt


def _serialize(obj) -> dict:
    return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
