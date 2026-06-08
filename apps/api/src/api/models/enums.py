from enum import Enum


class AssetClass(str, Enum):
    EQUITY = "EQUITY"
    FIXED_INCOME = "FIXED_INCOME"
    FX = "FX"
    COMMODITY = "COMMODITY"
    DERIVATIVE = "DERIVATIVE"
    ETF = "ETF"
    CRYPTO = "CRYPTO"


class Exchange(str, Enum):
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    LSE = "LSE"
    EURONEXT = "EURONEXT"
    CME = "CME"
    ICE = "ICE"
    CBOE = "CBOE"
    OTC = "OTC"
    CRYPTO_EX = "CRYPTO_EX"


class Sector(str, Enum):
    TECHNOLOGY = "TECHNOLOGY"
    FINANCIALS = "FINANCIALS"
    ENERGY = "ENERGY"
    HEALTHCARE = "HEALTHCARE"
    CONSUMER_DISC = "CONSUMER_DISC"
    CONSUMER_STAPLES = "CONSUMER_STAPLES"
    INDUSTRIALS = "INDUSTRIALS"
    MATERIALS = "MATERIALS"
    UTILITIES = "UTILITIES"
    REAL_ESTATE = "REAL_ESTATE"
    COMMUNICATION = "COMMUNICATION"
    GOVERNMENT = "GOVERNMENT"
    OTHER = "OTHER"


class CounterpartyType(str, Enum):
    BROKER = "BROKER"
    BANK = "BANK"
    FUND = "FUND"
    EXCHANGE = "EXCHANGE"
    MARKET_MAKER = "MARKET_MAKER"


class CreditRating(str, Enum):
    AAA = "AAA"
    AA = "AA"
    A = "A"
    BBB = "BBB"
    BB = "BB"
    B = "B"
    CCC = "CCC"
    CC = "CC"
    C = "C"
    D = "D"
    NR = "NR"


class PortfolioLevel(str, Enum):
    FUND = "FUND"
    PORTFOLIO = "PORTFOLIO"
    ACCOUNT = "ACCOUNT"


class Desk(str, Enum):
    EQUITIES = "EQUITIES"
    FIXED_INCOME = "FIXED_INCOME"
    FX = "FX"
    DERIVATIVES = "DERIVATIVES"
    COMMODITIES = "COMMODITIES"


class Region(str, Enum):
    EMEA = "EMEA"
    AMERICAS = "AMERICAS"
    APAC = "APAC"


class Seniority(str, Enum):
    JUNIOR = "JUNIOR"
    SENIOR = "SENIOR"
    LEAD = "LEAD"
    HEAD = "HEAD"


class Direction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class PositionDirection(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"
    IOC = "IOC"
    FOK = "FOK"
    GTC = "GTC"


class OrderStatus(str, Enum):
    OPEN = "OPEN"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class TimeInForce(str, Enum):
    DAY = "DAY"
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"


class TradeStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SETTLED = "SETTLED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    AMENDED = "AMENDED"


class SettlementStatus(str, Enum):
    PENDING = "PENDING"
    MATCHED = "MATCHED"
    INSTRUCTED = "INSTRUCTED"
    SETTLED = "SETTLED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
