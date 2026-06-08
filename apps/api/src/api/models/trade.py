from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, DateTime, Index
from sqlalchemy.types import JSON
from sqlmodel import Field, Relationship, SQLModel

from api.models.enums import Direction, SettlementStatus, TradeStatus

if TYPE_CHECKING:
    from api.models.counterparty import Counterparty
    from api.models.instrument import Instrument
    from api.models.order import Order
    from api.models.portfolio import Portfolio
    from api.models.trader import Trader


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Trade(SQLModel, table=True):
    __tablename__ = "trade"
    __table_args__ = (
        Index("ix_trade_trade_date", "trade_date"),
        Index("ix_trade_asset_class", "asset_class"),
        Index("ix_trade_status", "status"),
        Index("ix_trade_settlement_status", "settlement_status"),
        Index("ix_trade_direction", "direction"),
        Index("ix_trade_portfolio_id", "portfolio_id"),
        Index("ix_trade_trader_id", "trader_id"),
        Index("ix_trade_instrument_id", "instrument_id"),
        Index("ix_trade_counterparty_id", "counterparty_id"),
        Index("ix_trade_asset_class_status", "asset_class", "status"),
        Index("ix_trade_portfolio_trader", "portfolio_id", "trader_id"),
        {},
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    trade_ref: str = Field(index=True, unique=True, max_length=30)
    order_id: Optional[int] = Field(
        default=None, foreign_key="trade_order.id", index=True
    )
    instrument_id: int = Field(foreign_key="instrument.id")
    portfolio_id: int = Field(foreign_key="portfolio.id")
    trader_id: int = Field(foreign_key="trader.id")
    counterparty_id: int = Field(foreign_key="counterparty.id")

    trade_date: date
    settlement_date: date
    value_date: date

    direction: Direction
    status: TradeStatus
    settlement_status: SettlementStatus

    # Denormalized for fast grouping — avoids JOIN on instrument at query time
    asset_class: str = Field(max_length=20)
    sector: str = Field(max_length=50)

    quantity: float
    price: float
    notional: float
    currency: str = Field(max_length=3)
    fx_rate_to_usd: float = Field(default=1.0)
    notional_usd: float

    commission: float = Field(default=0.0)
    tax: float = Field(default=0.0)
    net_amount: float

    pnl_realized: Optional[float] = Field(default=None)
    pnl_unrealized: Optional[float] = Field(default=None)

    is_manual: bool = Field(default=False)
    is_amended: bool = Field(default=False)
    notes: Optional[str] = Field(default=None)

    # JSON columns — must use sa_column=Column(JSON); plain dict|None gives VARCHAR
    tags: Optional[list] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    extra_data: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )

    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, default=_utcnow, onupdate=_utcnow),
    )

    order: Optional["Order"] = Relationship(back_populates="trades")
    instrument: Optional["Instrument"] = Relationship(back_populates="trades")
    portfolio: Optional["Portfolio"] = Relationship(back_populates="trades")
    trader: Optional["Trader"] = Relationship(back_populates="trades")
    counterparty: Optional["Counterparty"] = Relationship(back_populates="trades")
