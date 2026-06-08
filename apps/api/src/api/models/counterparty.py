from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from api.models.enums import CounterpartyType, CreditRating

if TYPE_CHECKING:
    from api.models.trade import Trade


class Counterparty(SQLModel, table=True):
    __tablename__ = "counterparty"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    code: str = Field(index=True, unique=True, max_length=20)
    type: CounterpartyType = Field(index=True)
    country: str = Field(max_length=2)
    credit_rating: CreditRating = Field(default=CreditRating.NR)
    is_active: bool = Field(default=True)
    credit_limit: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    trades: list["Trade"] = Relationship(back_populates="counterparty")
