from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from api.models.enums import Desk, Region, Seniority

if TYPE_CHECKING:
    from api.models.order import Order
    from api.models.trade import Trade


class Trader(SQLModel, table=True):
    __tablename__ = "trader"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    code: str = Field(index=True, unique=True, max_length=20)
    email: str = Field(unique=True, max_length=200)
    desk: Desk = Field(index=True)
    region: Region = Field(index=True)
    seniority: Seniority = Field(index=True)
    is_active: bool = Field(default=True)
    hire_date: date
    pnl_ytd: float = Field(default=0.0)

    orders: list["Order"] = Relationship(back_populates="trader")
    trades: list["Trade"] = Relationship(back_populates="trader")
