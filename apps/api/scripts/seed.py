"""
Seed script for the ag-grid-demo fintech database.
Generates ~500k trades with supporting reference data.

Run from apps/api/:
    python scripts/seed.py
"""

import json
import os
import random
import sys
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from faker import Faker
from sqlalchemy import MetaData, create_engine, text

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "app.db")
DATABASE_URL = f"sqlite:///{os.path.abspath(DB_PATH)}"

INSTRUMENTS_COUNT = 1_000
COUNTERPARTIES_COUNT = 100
TRADERS_COUNT = 50
ORDERS_COUNT = 50_000
TRADES_COUNT = 500_000
POSITION_PAIRS = 500   # portfolio × instrument pairs
POSITION_DAYS = 20     # daily snapshots per pair → ~10k positions

BATCH_SIZE = 10_000
TRADE_CHUNK = 50_000

START_DATE = date(2023, 1, 2)
END_DATE = date(2025, 12, 31)

fake = Faker()
Faker.seed(42)
random.seed(42)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "HKD", "SGD"]
FX_RATES = {
    "USD": 1.0, "EUR": 1.08, "GBP": 1.27, "JPY": 0.0067, "CHF": 1.11,
    "CAD": 0.74, "AUD": 0.65, "HKD": 0.13, "SGD": 0.74,
}
SETTLEMENT_DAYS = {
    "EQUITY": 2, "ETF": 2, "FIXED_INCOME": 3,
    "FX": 1, "CRYPTO": 0, "COMMODITY": 2, "DERIVATIVE": 1,
}
TRADE_TAGS = [
    "algorithmic", "block", "principal", "agency",
    "risk-reduction", "rebalance", "index-arb", "hedging", "speculative",
]
VENUES = ["LIT", "DARK_POOL", "INTERNALIZED", "CROSSING_NETWORK", "AUCTION"]
STRATEGIES = ["MOMENTUM", "MEAN_REVERSION", "INDEX_REBALANCE", "STAT_ARB", "MARKET_MAKING"]
TOTAL_CALENDAR_DAYS = (END_DATE - START_DATE).days


def random_trading_date() -> date:
    while True:
        d = START_DATE + timedelta(days=random.randint(0, TOTAL_CALENDAR_DAYS))
        if d.weekday() < 5:
            return d


def add_business_days(d: date, n: int) -> date:
    result = d
    while n > 0:
        result += timedelta(days=1)
        if result.weekday() < 5:
            n -= 1
    return result


def bulk_insert(engine, table_name: str, rows: list[dict]) -> None:
    meta = MetaData()
    meta.reflect(bind=engine)
    table = meta.tables[table_name]
    with engine.begin() as conn:
        for i in range(0, len(rows), BATCH_SIZE):
            conn.execute(table.insert(), rows[i : i + BATCH_SIZE])


def apply_wal(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL"))
        conn.execute(text("PRAGMA synchronous=NORMAL"))
        conn.execute(text("PRAGMA cache_size=-64000"))  # 64 MB


# ---------------------------------------------------------------------------
# Phase 1: Instruments
# ---------------------------------------------------------------------------

ASSET_CLASS_CONFIG = {
    "EQUITY": {
        "count": 400, "exchanges": ["NYSE", "NASDAQ", "LSE", "EURONEXT"],
        "currencies": ["USD", "USD", "USD", "GBP", "EUR"],
        "sectors": ["TECHNOLOGY", "FINANCIALS", "HEALTHCARE", "CONSUMER_DISC",
                    "INDUSTRIALS", "ENERGY", "MATERIALS", "COMMUNICATION", "UTILITIES"],
        "countries": ["US", "US", "US", "GB", "DE", "FR", "JP"],
        "price_range": (10.0, 500.0),
    },
    "FIXED_INCOME": {
        "count": 200, "exchanges": ["OTC", "OTC", "ICE"],
        "currencies": ["USD", "EUR", "GBP"],
        "sectors": ["GOVERNMENT", "FINANCIALS", "INDUSTRIALS"],
        "countries": ["US", "DE", "GB", "FR", "JP"],
        "price_range": (85.0, 105.0),
    },
    "FX": {
        "count": 100, "exchanges": ["OTC"],
        "currencies": ["USD"],
        "sectors": ["OTHER"],
        "countries": ["US"],
        "price_range": (0.5, 2.0),
    },
    "COMMODITY": {
        "count": 100, "exchanges": ["CME", "ICE", "CBOE"],
        "currencies": ["USD"],
        "sectors": ["ENERGY", "MATERIALS"],
        "countries": ["US"],
        "price_range": (20.0, 2000.0),
    },
    "DERIVATIVE": {
        "count": 60, "exchanges": ["CBOE", "CME", "EURONEXT"],
        "currencies": ["USD", "EUR"],
        "sectors": ["FINANCIALS", "OTHER"],
        "countries": ["US", "DE"],
        "price_range": (1.0, 50.0),
    },
    "ETF": {
        "count": 80, "exchanges": ["NYSE", "NASDAQ", "LSE"],
        "currencies": ["USD", "EUR", "GBP"],
        "sectors": ["FINANCIALS", "TECHNOLOGY", "INDUSTRIALS", "OTHER"],
        "countries": ["US", "IE", "GB"],
        "price_range": (20.0, 400.0),
    },
    "CRYPTO": {
        "count": 60, "exchanges": ["CRYPTO_EX"],
        "currencies": ["USD"],
        "sectors": ["OTHER"],
        "countries": ["US"],
        "price_range": (0.01, 70000.0),
    },
}

FX_PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD",
    "NZDUSD", "EURGBP", "EURJPY", "GBPJPY", "EURCHF", "AUDJPY",
    "CADJPY", "CHFJPY", "GBPCHF", "AUDNZD", "EURCAD", "GBPCAD",
    "AUDCAD", "NZDCAD", "EURNZD", "GBPNZD", "AUDCHF", "NZDCHF",
]
CRYPTO_SYMBOLS = [
    "BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "AVAX", "DOT",
    "MATIC", "LINK", "UNI", "ATOM", "LTC", "BCH", "ALGO",
]
COMMODITY_SYMBOLS = [
    "GOLD", "SILVER", "CRUDE", "BRENT", "NATGAS", "WHEAT", "CORN",
    "SOYBEAN", "COPPER", "PLATINUM", "PALLADIUM", "COFFEE", "SUGAR", "COTTON",
]


def gen_isin(country: str, counter: int) -> str:
    prefix = country[:2].upper()
    return f"{prefix}{counter:010d}"


def seed_instruments(engine) -> list[dict]:
    print("Seeding instruments...")
    rows = []
    counter = 1
    fx_idx = 0
    crypto_idx = 0
    commodity_idx = 0

    for asset_class, cfg in ASSET_CLASS_CONFIG.items():
        for i in range(cfg["count"]):
            if asset_class == "FX":
                symbol = FX_PAIRS[fx_idx % len(FX_PAIRS)] + f"_{i // len(FX_PAIRS) + 1}" if i >= len(FX_PAIRS) else FX_PAIRS[fx_idx]
                fx_idx += 1
                name = f"{symbol} Spot"
            elif asset_class == "CRYPTO":
                sym = CRYPTO_SYMBOLS[crypto_idx % len(CRYPTO_SYMBOLS)]
                suffix = "" if i < len(CRYPTO_SYMBOLS) else f"{i // len(CRYPTO_SYMBOLS) + 1}"
                symbol = sym + suffix
                crypto_idx += 1
                name = f"{sym} Cryptocurrency"
            elif asset_class == "COMMODITY":
                sym = COMMODITY_SYMBOLS[commodity_idx % len(COMMODITY_SYMBOLS)]
                suffix = "" if i < len(COMMODITY_SYMBOLS) else f"_{i // len(COMMODITY_SYMBOLS) + 1}"
                symbol = sym + suffix
                commodity_idx += 1
                name = f"{sym} Futures"
            elif asset_class == "FIXED_INCOME":
                symbol = f"BOND{counter:04d}"
                name = f"{fake.company()} {random.choice([2, 3, 5, 7, 10, 20, 30])}Y Bond"
            elif asset_class == "DERIVATIVE":
                symbol = f"OPT{counter:04d}"
                name = f"Option Contract {counter}"
            elif asset_class == "ETF":
                symbol = f"ETF{counter:04d}"
                name = f"{fake.company()} ETF"
            else:
                symbol = fake.lexify("????").upper() + str(random.randint(0, 9))
                name = fake.company() + " " + random.choice(["Inc.", "Corp.", "Ltd.", "PLC"])

            country = random.choice(cfg["countries"])
            lo, hi = cfg["price_range"]
            if asset_class == "CRYPTO":
                base_price = random.choice([0.5, 5.0, 50.0, 500.0, 5000.0, 30000.0, 65000.0])
            else:
                base_price = round(random.uniform(lo, hi), 2)

            rows.append({
                "symbol": symbol[:20],
                "name": name[:200],
                "isin": gen_isin(country, counter),
                "cusip": f"{counter:09d}" if asset_class in ("EQUITY", "ETF") else None,
                "asset_class": asset_class,
                "exchange": random.choice(cfg["exchanges"]),
                "currency": random.choice(cfg["currencies"]),
                "sector": random.choice(cfg["sectors"]),
                "country": country,
                "is_active": random.random() > 0.05,
                "lot_size": 1 if asset_class in ("FX", "CRYPTO") else random.choice([1, 10, 100]),
                "min_trade_size": 1.0,
                "created_at": datetime.now(timezone.utc),
                # Store base_price as extra context for seed script use (not in DB)
                "_base_price": base_price,
            })
            counter += 1

    # Strip internal keys before inserting
    base_prices = {i: r.pop("_base_price") for i, r in enumerate(rows)}
    bulk_insert(engine, "instrument", rows)
    print(f"  Inserted {len(rows)} instruments")
    return base_prices  # index → price, used when generating trades


# ---------------------------------------------------------------------------
# Phase 2: Counterparties
# ---------------------------------------------------------------------------

CP_TYPE_WEIGHTS = ["BROKER"] * 40 + ["BANK"] * 25 + ["FUND"] * 15 + ["EXCHANGE"] * 10 + ["MARKET_MAKER"] * 10
RATING_WEIGHTS = ["AAA"] * 5 + ["AA"] * 15 + ["A"] * 25 + ["BBB"] * 25 + ["BB"] * 15 + ["B"] * 10 + ["NR"] * 5
COUNTRIES_2L = ["US", "GB", "DE", "FR", "JP", "CH", "SG", "HK", "AU", "CA"]


def seed_counterparties(engine) -> list[int]:
    print("Seeding counterparties...")
    rows = []
    used_codes: set[str] = set()

    for i in range(COUNTERPARTIES_COUNT):
        name = fake.company()
        code = name[:4].upper().replace(" ", "") + f"{i:03d}"
        while code in used_codes:
            code = code[:4] + f"{i:03d}X"
        used_codes.add(code)

        rows.append({
            "name": name[:200],
            "code": code[:20],
            "type": random.choice(CP_TYPE_WEIGHTS),
            "country": random.choice(COUNTRIES_2L),
            "credit_rating": random.choice(RATING_WEIGHTS),
            "is_active": random.random() > 0.05,
            "credit_limit": round(random.uniform(1e6, 5e9), 2),
            "created_at": datetime.now(timezone.utc),
        })

    bulk_insert(engine, "counterparty", rows)
    print(f"  Inserted {len(rows)} counterparties")
    return list(range(1, COUNTERPARTIES_COUNT + 1))


# ---------------------------------------------------------------------------
# Phase 3: Portfolios (hierarchical: FUND → PORTFOLIO → ACCOUNT)
# ---------------------------------------------------------------------------

FUND_NAMES = [
    "Alpha Global Fund", "Beta Macro Fund", "Gamma Fixed Income Fund",
    "Delta Equity Fund", "Epsilon Multi-Asset Fund",
]
CURRENCIES_MAIN = ["USD", "EUR", "GBP"]


def seed_portfolios(engine) -> list[int]:
    print("Seeding portfolios...")
    rows = []
    codes: set[str] = set()

    def make_code(name: str, suffix: str = "") -> str:
        c = "".join(w[0] for w in name.split()[:3]).upper() + suffix
        while c in codes:
            c += "X"
        codes.add(c)
        return c[:20]

    # 5 FUNDs
    for i, fname in enumerate(FUND_NAMES):
        rows.append({
            "name": fname,
            "code": make_code(fname, str(i + 1)),
            "parent_id": None,
            "level": "FUND",
            "currency": random.choice(CURRENCIES_MAIN),
            "aum": round(random.uniform(500e6, 10e9), 2),
            "risk_limit": round(random.uniform(50e6, 500e6), 2),
            "manager": fake.name(),
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
        })

    # 15 PORTFOLIOs (3 per FUND, parent_id = 1..5)
    for fund_idx in range(5):
        for sub in range(3):
            pname = f"{FUND_NAMES[fund_idx].split()[0]} {fake.word().capitalize()} Portfolio"
            rows.append({
                "name": pname[:200],
                "code": make_code(pname, f"{fund_idx}{sub}"),
                "parent_id": fund_idx + 1,  # FUNDs have IDs 1..5
                "level": "PORTFOLIO",
                "currency": random.choice(CURRENCIES_MAIN),
                "aum": round(random.uniform(50e6, 1e9), 2),
                "risk_limit": round(random.uniform(5e6, 100e6), 2),
                "manager": fake.name(),
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
            })

    # 30 ACCOUNTs (2 per PORTFOLIO, parent_id = 6..20)
    for port_idx in range(15):
        for acc in range(2):
            aname = f"Account {fake.word().capitalize()} {port_idx + 1}{acc}"
            rows.append({
                "name": aname[:200],
                "code": make_code(aname, f"A{port_idx}{acc}"),
                "parent_id": port_idx + 6,  # PORTFOLIOs have IDs 6..20
                "level": "ACCOUNT",
                "currency": random.choice(CURRENCIES_MAIN),
                "aum": round(random.uniform(1e6, 50e6), 2),
                "risk_limit": round(random.uniform(500e3, 10e6), 2),
                "manager": fake.name(),
                "is_active": random.random() > 0.05,
                "created_at": datetime.now(timezone.utc),
            })

    bulk_insert(engine, "portfolio", rows)
    print(f"  Inserted {len(rows)} portfolios")
    return list(range(1, len(rows) + 1))


# ---------------------------------------------------------------------------
# Phase 4: Traders
# ---------------------------------------------------------------------------

DESK_REGION = [
    ("EQUITIES", "EMEA"), ("EQUITIES", "EMEA"), ("EQUITIES", "EMEA"),
    ("EQUITIES", "AMERICAS"), ("EQUITIES", "AMERICAS"), ("EQUITIES", "AMERICAS"),
    ("EQUITIES", "APAC"), ("EQUITIES", "APAC"),
    ("FIXED_INCOME", "EMEA"), ("FIXED_INCOME", "EMEA"),
    ("FIXED_INCOME", "AMERICAS"), ("FIXED_INCOME", "AMERICAS"),
    ("FIXED_INCOME", "APAC"),
    ("FX", "EMEA"), ("FX", "EMEA"),
    ("FX", "AMERICAS"), ("FX", "AMERICAS"),
    ("FX", "APAC"), ("FX", "APAC"),
    ("DERIVATIVES", "EMEA"), ("DERIVATIVES", "EMEA"),
    ("DERIVATIVES", "AMERICAS"), ("DERIVATIVES", "AMERICAS"), ("DERIVATIVES", "AMERICAS"),
    ("DERIVATIVES", "APAC"),
    ("COMMODITIES", "AMERICAS"), ("COMMODITIES", "AMERICAS"),
    ("COMMODITIES", "EMEA"), ("COMMODITIES", "EMEA"),
    ("COMMODITIES", "APAC"), ("COMMODITIES", "APAC"),
]
SENIORITY_WEIGHTS = ["JUNIOR"] * 15 + ["SENIOR"] * 20 + ["LEAD"] * 10 + ["HEAD"] * 5
HIRE_START = date(2005, 1, 1)
HIRE_DAYS = (date(2023, 1, 1) - HIRE_START).days


def seed_traders(engine) -> list[int]:
    print("Seeding traders...")
    rows = []
    emails: set[str] = set()

    for i in range(TRADERS_COUNT):
        desk, region = DESK_REGION[i % len(DESK_REGION)]
        name = fake.name()
        email = fake.email()
        while email in emails:
            email = fake.email()
        emails.add(email)
        hire = HIRE_START + timedelta(days=random.randint(0, HIRE_DAYS))
        rows.append({
            "name": name,
            "code": f"T{i + 1:04d}",
            "email": email,
            "desk": desk,
            "region": region,
            "seniority": random.choice(SENIORITY_WEIGHTS),
            "is_active": random.random() > 0.05,
            "hire_date": hire,
            "pnl_ytd": round(random.uniform(-5e6, 20e6), 2),
        })

    bulk_insert(engine, "trader", rows)
    print(f"  Inserted {len(rows)} traders")
    return list(range(1, TRADERS_COUNT + 1))


# ---------------------------------------------------------------------------
# Phase 5: Orders
# ---------------------------------------------------------------------------

ORDER_TYPE_WEIGHTS = (
    ["MARKET"] * 25 + ["LIMIT"] * 40 + ["STOP"] * 10 +
    ["STOP_LIMIT"] * 10 + ["IOC"] * 5 + ["FOK"] * 5 + ["GTC"] * 5
)
ORDER_STATUS_WEIGHTS = (
    ["FILLED"] * 55 + ["PARTIAL"] * 15 + ["CANCELLED"] * 15 +
    ["OPEN"] * 10 + ["REJECTED"] * 3 + ["EXPIRED"] * 2
)
TIF_WEIGHTS = ["DAY"] * 50 + ["GTC"] * 30 + ["IOC"] * 10 + ["FOK"] * 10

# Pre-built lists of instrument metadata for fast lookups during order/trade gen
instrument_ids: list[int] = []
instrument_asset_classes: list[str] = []
instrument_sectors: list[str] = []
instrument_currencies: list[str] = []
instrument_base_prices: list[float] = []


def load_instrument_cache(engine) -> None:
    meta = MetaData()
    meta.reflect(bind=engine)
    tbl = meta.tables["instrument"]
    with engine.connect() as conn:
        rows = conn.execute(
            tbl.select().with_only_columns(
                tbl.c.id, tbl.c.asset_class, tbl.c.sector,
                tbl.c.currency,
            )
        ).fetchall()
    for r in rows:
        instrument_ids.append(r[0])
        instrument_asset_classes.append(r[1])
        instrument_sectors.append(r[2])
        instrument_currencies.append(r[3])
        # Generate a stable base price per instrument (seeded by instrument id)
        ac = r[1]
        lo, hi = ASSET_CLASS_CONFIG.get(ac, {}).get("price_range", (10.0, 200.0))
        rng = random.Random(r[0])  # stable per instrument
        if ac == "CRYPTO":
            price = rng.choice([0.5, 5.0, 50.0, 500.0, 5000.0, 30000.0, 65000.0])
        else:
            price = round(rng.uniform(lo, hi), 4)
        instrument_base_prices.append(price)


portfolio_ids: list[int] = []
trader_ids: list[int] = []
counterparty_ids: list[int] = []


def load_reference_ids(engine) -> None:
    meta = MetaData()
    meta.reflect(bind=engine)
    with engine.connect() as conn:
        for table_name, id_list in [
            ("portfolio", portfolio_ids),
            ("trader", trader_ids),
            ("counterparty", counterparty_ids),
        ]:
            tbl = meta.tables[table_name]
            rows = conn.execute(tbl.select().with_only_columns(tbl.c.id)).fetchall()
            id_list.extend(r[0] for r in rows)


def seed_orders(engine) -> None:
    print("Seeding orders...")
    rows = []
    for i in range(ORDERS_COUNT):
        inst_idx = random.randint(0, len(instrument_ids) - 1)
        inst_id = instrument_ids[inst_idx]
        currency = instrument_currencies[inst_idx]
        base_price = instrument_base_prices[inst_idx]
        order_date = random_trading_date()
        order_type = random.choice(ORDER_TYPE_WEIGHTS)
        status = random.choice(ORDER_STATUS_WEIGHTS)
        quantity = round(random.uniform(100, 100_000), 2)
        filled = 0.0
        if status == "FILLED":
            filled = quantity
        elif status == "PARTIAL":
            filled = round(quantity * random.uniform(0.1, 0.9), 2)

        limit_price = None
        stop_price = None
        if order_type in ("LIMIT", "STOP_LIMIT", "GTC"):
            limit_price = round(base_price * random.uniform(0.95, 1.05), 4)
        if order_type in ("STOP", "STOP_LIMIT"):
            stop_price = round(base_price * random.uniform(0.90, 0.98), 4)

        rows.append({
            "order_ref": f"ORD-{order_date.year}-{i + 1:07d}",
            "order_date": order_date,
            "instrument_id": inst_id,
            "portfolio_id": random.choice(portfolio_ids),
            "trader_id": random.choice(trader_ids),
            "direction": random.choice(["BUY", "SELL"]),
            "quantity": quantity,
            "filled_quantity": filled,
            "order_type": order_type,
            "limit_price": limit_price,
            "stop_price": stop_price,
            "currency": currency,
            "status": status,
            "time_in_force": random.choice(TIF_WEIGHTS),
            "notes": fake.sentence() if random.random() < 0.1 else None,
            "created_at": datetime.combine(order_date, datetime.min.time()),
            "updated_at": datetime.combine(order_date, datetime.min.time()),
        })

        if len(rows) >= BATCH_SIZE:
            bulk_insert(engine, "trade_order", rows)
            rows = []

    if rows:
        bulk_insert(engine, "trade_order", rows)
    print(f"  Inserted {ORDERS_COUNT} orders")


# ---------------------------------------------------------------------------
# Phase 6: Trades
# ---------------------------------------------------------------------------

TRADE_STATUS_WEIGHTS = (
    ["CONFIRMED"] * 50 + ["SETTLED"] * 35 + ["PENDING"] * 8 +
    ["FAILED"] * 4 + ["CANCELLED"] * 2 + ["AMENDED"] * 1
)
SETTLEMENT_STATUS_WEIGHTS = (
    ["SETTLED"] * 45 + ["INSTRUCTED"] * 20 + ["MATCHED"] * 15 +
    ["PENDING"] * 12 + ["FAILED"] * 5 + ["CANCELLED"] * 3
)


def gen_extra_data() -> dict:
    d: dict = {}
    if random.random() < 0.6:
        d["algo_id"] = f"ALGO-{random.randint(100, 999)}"
    if random.random() < 0.5:
        d["venue"] = random.choice(VENUES)
    if random.random() < 0.4:
        d["strategy"] = random.choice(STRATEGIES)
    return d or None  # type: ignore[return-value]


def seed_trades(engine) -> None:
    print(f"Seeding {TRADES_COUNT:,} trades in chunks of {TRADE_CHUNK:,}...")

    for chunk_start in range(0, TRADES_COUNT, TRADE_CHUNK):
        chunk_end = min(chunk_start + TRADE_CHUNK, TRADES_COUNT)
        rows = []

        for i in range(chunk_start, chunk_end):
            inst_idx = random.randint(0, len(instrument_ids) - 1)
            inst_id = instrument_ids[inst_idx]
            asset_class = instrument_asset_classes[inst_idx]
            sector = instrument_sectors[inst_idx]
            currency = instrument_currencies[inst_idx]
            base_price = instrument_base_prices[inst_idx]

            trade_date = random_trading_date()
            settle_days = SETTLEMENT_DAYS.get(asset_class, 2)
            settlement_date = add_business_days(trade_date, settle_days)
            value_date = settlement_date

            direction = random.choice(["BUY", "SELL"])
            quantity = round(random.uniform(10, 50_000), 2)
            noise = 0.05 if asset_class == "EQUITY" else 0.002
            price = round(base_price * (1 + random.uniform(-noise, noise)), 4)
            notional = round(quantity * price, 2)
            fx_rate = FX_RATES.get(currency, 1.0)
            notional_usd = round(notional * fx_rate, 2)
            commission = round(notional * random.uniform(0.0001, 0.002), 2)
            tax = round(notional * random.uniform(0.0, 0.0005), 2)
            net_amount = round(notional + commission + tax, 2)

            status = random.choice(TRADE_STATUS_WEIGHTS)
            settle_status = random.choice(SETTLEMENT_STATUS_WEIGHTS)

            pnl_realized = None
            pnl_unrealized = None
            if random.random() < 0.4:
                pnl_realized = round(notional * random.uniform(-0.1, 0.15), 2)
            if random.random() < 0.6:
                pnl_unrealized = round(notional * random.uniform(-0.08, 0.12), 2)

            tags = random.sample(TRADE_TAGS, k=random.randint(0, 3)) or None
            extra = gen_extra_data()

            # 20% of trades are manual (no parent order), rest reference a random order
            order_id = None if random.random() < 0.2 else random.randint(1, ORDERS_COUNT)

            rows.append({
                "trade_ref": f"TR-{trade_date.year}-{i + 1:08d}",
                "order_id": order_id,
                "instrument_id": inst_id,
                "portfolio_id": random.choice(portfolio_ids),
                "trader_id": random.choice(trader_ids),
                "counterparty_id": random.choice(counterparty_ids),
                "trade_date": trade_date,
                "settlement_date": settlement_date,
                "value_date": value_date,
                "direction": direction,
                "status": status,
                "settlement_status": settle_status,
                "asset_class": asset_class,
                "sector": sector,
                "quantity": quantity,
                "price": price,
                "notional": notional,
                "currency": currency,
                "fx_rate_to_usd": fx_rate,
                "notional_usd": notional_usd,
                "commission": commission,
                "tax": tax,
                "net_amount": net_amount,
                "pnl_realized": pnl_realized,
                "pnl_unrealized": pnl_unrealized,
                "is_manual": order_id is None,
                "is_amended": random.random() < 0.03,
                "notes": fake.sentence() if random.random() < 0.05 else None,
                "tags": json.dumps(tags) if tags else None,
                "extra_data": json.dumps(extra) if extra else None,
                "created_at": datetime.combine(trade_date, datetime.min.time()),
                "updated_at": datetime.combine(trade_date, datetime.min.time()),
            })

        bulk_insert(engine, "trade", rows)
        done = chunk_end
        print(f"  Trades: {done:,} / {TRADES_COUNT:,}")

    print(f"  Inserted {TRADES_COUNT:,} trades")


# ---------------------------------------------------------------------------
# Phase 7: Positions
# ---------------------------------------------------------------------------

def seed_positions(engine) -> None:
    print("Seeding positions...")
    rows = []
    # Pick POSITION_PAIRS random (portfolio, instrument) combos
    pairs = [
        (random.choice(portfolio_ids), random.choice(instrument_ids))
        for _ in range(POSITION_PAIRS)
    ]
    # Deduplicate
    pairs = list({(p, i) for p, i in pairs})[:POSITION_PAIRS]

    today = END_DATE
    seen: set[tuple] = set()
    row_count = 0

    for port_id, inst_idx_raw in pairs:
        # inst_idx_raw is an instrument ID, map back to list index
        try:
            idx = instrument_ids.index(inst_idx_raw)
        except ValueError:
            continue
        asset_class = instrument_asset_classes[idx]
        currency = instrument_currencies[idx]
        base_price = instrument_base_prices[idx]

        for day_offset in range(POSITION_DAYS):
            as_of = today - timedelta(days=day_offset)
            if as_of.weekday() >= 5:  # skip weekends
                continue
            key = (port_id, inst_idx_raw, as_of)
            if key in seen:
                continue
            seen.add(key)

            quantity = round(random.uniform(100, 500_000), 2)
            avg_cost = round(base_price * random.uniform(0.9, 1.1), 4)
            market_price = round(base_price * random.uniform(0.85, 1.15), 4)
            market_value = round(quantity * market_price, 2)
            cost_basis = round(quantity * avg_cost, 2)
            unrealized_pnl = round(market_value - cost_basis, 2)
            realized_pnl = round(cost_basis * random.uniform(-0.05, 0.10), 2)
            pnl_pct = round((unrealized_pnl / cost_basis * 100) if cost_basis else 0, 4)
            direction = "LONG" if quantity > 0 else "SHORT"

            rows.append({
                "portfolio_id": port_id,
                "instrument_id": inst_idx_raw,
                "as_of_date": as_of,
                "direction": direction,
                "quantity": quantity,
                "avg_cost": avg_cost,
                "market_price": market_price,
                "market_value": market_value,
                "cost_basis": cost_basis,
                "unrealized_pnl": unrealized_pnl,
                "realized_pnl": realized_pnl,
                "pnl_pct": pnl_pct,
                "weight_pct": round(random.uniform(0.1, 15.0), 4),
                "currency": currency,
                "updated_at": datetime.now(timezone.utc),
            })
            row_count += 1

            if len(rows) >= BATCH_SIZE:
                bulk_insert(engine, "position", rows)
                rows = []

    if rows:
        bulk_insert(engine, "position", rows)
    print(f"  Inserted {row_count} positions")


# ---------------------------------------------------------------------------
# Phase 8: MarketDataSnapshot (one per instrument)
# ---------------------------------------------------------------------------

def seed_market_data(engine) -> None:
    print("Seeding market data snapshots...")
    rows = []
    now = datetime.now(timezone.utc)

    for idx, inst_id in enumerate(instrument_ids):
        base = instrument_base_prices[idx]
        spread_pct = 0.0002 if instrument_asset_classes[idx] == "FX" else 0.001
        bid = round(base * (1 - spread_pct), 4)
        ask = round(base * (1 + spread_pct), 4)
        mid = round((bid + ask) / 2, 4)
        last = round(base * random.uniform(0.999, 1.001), 4)
        open_p = round(base * random.uniform(0.99, 1.01), 4)
        close_p = round(base * random.uniform(0.99, 1.01), 4)
        high = round(max(open_p, close_p) * random.uniform(1.0, 1.02), 4)
        low = round(min(open_p, close_p) * random.uniform(0.98, 1.0), 4)
        volume = round(random.uniform(1e4, 1e8), 0)
        vwap = round(random.uniform(low, high), 4)
        change_abs = round(last - close_p, 4)
        change_pct = round((change_abs / close_p * 100) if close_p else 0, 4)

        rows.append({
            "instrument_id": inst_id,
            "timestamp": now,
            "bid": bid,
            "ask": ask,
            "mid": mid,
            "last_price": last,
            "open_price": open_p,
            "high_price": high,
            "low_price": low,
            "close_price": close_p,
            "volume": volume,
            "vwap": vwap,
            "change_abs": change_abs,
            "change_pct": change_pct,
            "updated_at": now,
        })

    bulk_insert(engine, "market_data_snapshot", rows)
    print(f"  Inserted {len(rows)} market data snapshots")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    import time

    print(f"Database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    apply_wal(engine)

    # Ensure tables exist (mirrors what init_db() does at API startup)
    from api.models import (  # noqa: F401
        Counterparty, Instrument, MarketDataSnapshot, Order,
        Portfolio, Position, Trade, Trader,
    )
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)

    t0 = time.time()

    seed_instruments(engine)
    seed_counterparties(engine)
    seed_portfolios(engine)
    seed_traders(engine)

    load_instrument_cache(engine)
    load_reference_ids(engine)

    seed_orders(engine)
    seed_trades(engine)
    seed_positions(engine)
    seed_market_data(engine)

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
