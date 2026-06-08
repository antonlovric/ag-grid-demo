from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ColumnVO(BaseModel):
    id: str
    display_name: str = Field(alias="displayName")
    field: str | None = None
    agg_func: str | None = Field(default=None, alias="aggFunc")

    model_config = {"populate_by_name": True}


class SortModelItem(BaseModel):
    col_id: str = Field(alias="colId")
    sort: Literal["asc", "desc"]

    model_config = {"populate_by_name": True}


class SSRMRequest(BaseModel):
    start_row: int | None = Field(default=None, alias="startRow")
    end_row: int | None = Field(default=None, alias="endRow")
    row_group_cols: list[ColumnVO] = Field(default_factory=list, alias="rowGroupCols")
    value_cols: list[ColumnVO] = Field(default_factory=list, alias="valueCols")
    pivot_cols: list[ColumnVO] = Field(default_factory=list, alias="pivotCols")
    pivot_mode: bool = Field(default=False, alias="pivotMode")
    group_keys: list[str] = Field(default_factory=list, alias="groupKeys")
    # Raw dict — filter entries are parsed dynamically in filters.py
    filter_model: dict[str, Any] = Field(default_factory=dict, alias="filterModel")
    sort_model: list[SortModelItem] = Field(default_factory=list, alias="sortModel")

    model_config = {"populate_by_name": True}
