import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from api.db.engine import init_db
from api.models import (  # noqa: F401 — registers all tables with SQLModel.metadata
    Counterparty,
    Instrument,
    MarketDataSnapshot,
    Order,
    Portfolio,
    Position,
    Trade,
    Trader,
)
from api.routers.trades import router as trades_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path("data").mkdir(exist_ok=True)
    await init_db()
    yield


app = FastAPI(title="ag-grid-demo API", version="0.1.0", lifespan=lifespan)
app.include_router(trades_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    count = 0
    try:
        while True:
            await websocket.send_json({
                "type": "ping",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "count": count,
            })
            count += 1
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
