from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from api.models.enums import PositionDirection

if TYPE_CHECKING:
    from api.models.instrument import Instrument
    from api.models.portfolio import Portfolio


class Position(SQLModel, table=True):
    __tablename__ = "position"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "instrument_id", "as_of_date", name="uq_position"),
        {},
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    portfolio_id: int = Field(foreign_key="portfolio.id", index=True)
    instrument_id: int = Field(foreign_key="instrument.id", index=True)
    as_of_date: date = Field(index=True)
    direction: PositionDirection
    quantity: float
    avg_cost: float
    market_price: float
    market_value: float
    cost_basis: float
    unrealized_pnl: float
    realized_pnl: float = Field(default=0.0)
    pnl_pct: float
    weight_pct: float
    currency: str = Field(max_length=3)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    portfolio: Optional["Portfolio"] = Relationship(back_populates="positions")
    instrument: Optional["Instrument"] = Relationship(back_populates="positions")
