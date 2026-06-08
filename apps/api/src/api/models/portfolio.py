from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, SQLModel

from api.models.enums import PortfolioLevel

if TYPE_CHECKING:
    from api.models.order import Order
    from api.models.position import Position
    from api.models.trade import Trade


class Portfolio(SQLModel, table=True):
    __tablename__ = "portfolio"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    code: str = Field(index=True, unique=True, max_length=20)
    # sa_column required for self-referential FK — foreign_key= shorthand doesn't work here
    parent_id: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("portfolio.id"), nullable=True, index=True),
    )
    level: PortfolioLevel = Field(index=True)
    currency: str = Field(max_length=3, default="USD")
    aum: float = Field(default=0.0)
    risk_limit: float = Field(default=0.0)
    manager: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    orders: list["Order"] = Relationship(back_populates="portfolio")
    trades: list["Trade"] = Relationship(back_populates="portfolio")
    positions: list["Position"] = Relationship(back_populates="portfolio")
