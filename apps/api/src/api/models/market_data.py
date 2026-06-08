from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from api.models.instrument import Instrument


class MarketDataSnapshot(SQLModel, table=True):
    __tablename__ = "market_data_snapshot"

    id: Optional[int] = Field(default=None, primary_key=True)
    instrument_id: int = Field(foreign_key="instrument.id", unique=True, index=True)
    timestamp: datetime
    bid: float
    ask: float
    mid: float
    last_price: float
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    vwap: float
    change_abs: float
    change_pct: float
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    instrument: Optional["Instrument"] = Relationship(back_populates="market_data")
