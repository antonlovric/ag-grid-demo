from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

from api.models.enums import Direction, OrderStatus, OrderType, TimeInForce

if TYPE_CHECKING:
    from api.models.instrument import Instrument
    from api.models.portfolio import Portfolio
    from api.models.trade import Trade
    from api.models.trader import Trader


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Order(SQLModel, table=True):
    # "order" is a reserved SQL keyword — use trade_order
    __tablename__ = "trade_order"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_ref: str = Field(index=True, unique=True, max_length=30)
    order_date: date = Field(index=True)
    instrument_id: int = Field(foreign_key="instrument.id", index=True)
    portfolio_id: int = Field(foreign_key="portfolio.id", index=True)
    trader_id: int = Field(foreign_key="trader.id", index=True)
    direction: Direction = Field(index=True)
    quantity: float
    filled_quantity: float = Field(default=0.0)
    order_type: OrderType
    limit_price: Optional[float] = Field(default=None)
    stop_price: Optional[float] = Field(default=None)
    currency: str = Field(max_length=3)
    status: OrderStatus = Field(index=True, default=OrderStatus.OPEN)
    time_in_force: TimeInForce = Field(default=TimeInForce.DAY)
    notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, default=_utcnow, onupdate=_utcnow),
    )

    instrument: Optional["Instrument"] = Relationship(back_populates="orders")
    portfolio: Optional["Portfolio"] = Relationship(back_populates="orders")
    trader: Optional["Trader"] = Relationship(back_populates="orders")
    trades: list["Trade"] = Relationship(back_populates="order")
