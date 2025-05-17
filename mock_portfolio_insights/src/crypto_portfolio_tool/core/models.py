from typing import List, Optional, Dict
from pydantic import BaseModel, Field, RootModel
from datetime import datetime, date, timezone

class AssetNewsItem(BaseModel):
    """Represents a news item for a specific asset"""
    title: str
    source: str
    published_at: datetime
    url: str
    summary: Optional[str] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None

class MarketAssetInfo(BaseModel):
    """Market information for a specific asset"""
    current_price: float
    volume_24h: float
    market_cap: Optional[float] = None
    price_change_24h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None

    @property
    def price(self) -> float:
        return self.current_price

class AcquisitionRecord(BaseModel):
    """Record of an asset acquisition"""
    date: datetime
    quantity: float
    price_per_unit: float
    transaction_id: str
    source: Optional[str] = None

class AssetHolding(BaseModel):
    """Represents a holding of a specific asset"""
    asset_id: str
    name: str
    symbol: str
    quantity: float
    average_buy_price: float
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    cost_basis_total: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    unrealized_pnl_percent: Optional[float] = None
    last_updated: Optional[datetime] = Field(default_factory=datetime.now)

class Portfolio(BaseModel):
    """Represents a user's complete portfolio"""
    user_id: str
    wallet_address: str
    assets: Dict[str, AssetHolding]
    cash_balance: Optional[float] = 0.0
    total_value: Optional[float] = None
    last_updated: Optional[datetime] = Field(default_factory=datetime.now)
    historical_summary: Optional[Dict] = Field(default_factory=dict)

class AssetDetail(BaseModel):
    """Represents details of an asset in portfolio composition"""
    asset_id: str
    name: str
    quantity: float
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    percentage: Optional[float] = None
    cost_basis_total: Optional[float] = None
    unrealized_gain_loss_abs: Optional[float] = None
    unrealized_gain_loss_percent: Optional[float] = None

class GlobalSentiment(BaseModel):
    """Represents global market sentiment data"""
    score: float = Field(ge=-1.0, le=1.0)  # Sentiment score between -1 and 1
    sentiment: str = Field(...)  # e.g., "Bullish", "Bearish", "Neutral"
    timestamp: datetime = Field(default_factory=datetime.now)
    contributing_factors: Optional[List[str]] = Field(default_factory=list)
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)

class MarketDataResponse(RootModel[Dict[str, MarketAssetInfo]]):
    """Root model for market data response"""
    pass