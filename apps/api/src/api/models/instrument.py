from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from api.models.enums import AssetClass, Exchange, Sector

if TYPE_CHECKING:
    from api.models.market_data import MarketDataSnapshot
    from api.models.order import Order
    from api.models.position import Position
    from api.models.trade import Trade


class Instrument(SQLModel, table=True):
    __tablename__ = "instrument"

    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(index=True, unique=True, max_length=20)
    name: str = Field(max_length=200)
    isin: str = Field(index=True, unique=True, max_length=12)
    cusip: Optional[str] = Field(default=None, max_length=9)
    asset_class: AssetClass = Field(index=True)
    exchange: Exchange = Field(index=True)
    currency: str = Field(max_length=3)
    sector: Sector = Field(index=True)
    country: str = Field(max_length=2)
    is_active: bool = Field(default=True)
    lot_size: int = Field(default=1)
    min_trade_size: float = Field(default=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    orders: list["Order"] = Relationship(back_populates="instrument")
    trades: list["Trade"] = Relationship(back_populates="instrument")
    positions: list["Position"] = Relationship(back_populates="instrument")
    market_data: Optional["MarketDataSnapshot"] = Relationship(back_populates="instrument")
