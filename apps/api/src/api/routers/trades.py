from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.session import get_session
from api.models.trade import Trade
from api.ssrm.query_builder import execute_ssrm
from api.ssrm.response import SSRMResponse
from api.ssrm.schema import SSRMRequest

router = APIRouter(prefix="/api/trades", tags=["trades"])

TRADE_COLUMN_MAP = {
    "id": Trade.id,
    "trade_ref": Trade.trade_ref,
    "order_id": Trade.order_id,
    "instrument_id": Trade.instrument_id,
    "portfolio_id": Trade.portfolio_id,
    "trader_id": Trade.trader_id,
    "counterparty_id": Trade.counterparty_id,
    "trade_date": Trade.trade_date,
    "settlement_date": Trade.settlement_date,
    "value_date": Trade.value_date,
    "direction": Trade.direction,
    "status": Trade.status,
    "settlement_status": Trade.settlement_status,
    "asset_class": Trade.asset_class,
    "sector": Trade.sector,
    "quantity": Trade.quantity,
    "price": Trade.price,
    "notional": Trade.notional,
    "notional_usd": Trade.notional_usd,
    "currency": Trade.currency,
    "fx_rate_to_usd": Trade.fx_rate_to_usd,
    "commission": Trade.commission,
    "tax": Trade.tax,
    "net_amount": Trade.net_amount,
    "pnl_realized": Trade.pnl_realized,
    "pnl_unrealized": Trade.pnl_unrealized,
    "is_manual": Trade.is_manual,
    "is_amended": Trade.is_amended,
}


@router.post("/ssrm", response_model=SSRMResponse)
async def trades_ssrm(
    req: SSRMRequest,
    session: AsyncSession = Depends(get_session),
) -> SSRMResponse:
    result = await execute_ssrm(session, Trade, TRADE_COLUMN_MAP, req)
    return SSRMResponse(**result)
