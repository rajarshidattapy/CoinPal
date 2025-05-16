import json
import os
from typing import List, Dict, Optional
from ..core.models import MarketAssetInfo, MarketDataResponse, GlobalSentiment
from ..core.exceptions import APIRequestError, DataValidationError
from pydantic import ValidationError

class MarketDataAPIClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url
        
        # Load mock data
        mock_data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'mock_services', 'mock_data', 'portfolios.json')
        with open(mock_data_path, 'r') as f:
            self.mock_data = json.load(f)

    def get_current_prices(self, asset_ids: list[str]) -> Dict[str, MarketAssetInfo]:
        try:
            # Mock data for demonstration
            mock_data = {
                "BTC": MarketAssetInfo(
                    current_price=40000,
                    volume_24h=25000000000,
                    market_cap=800000000000,
                    price_change_24h=1500,
                    price_change_percentage_24h=3.75
                ),
                "ETH": MarketAssetInfo(
                    current_price=2200,
                    volume_24h=10000000000,
                    market_cap=260000000000,
                    price_change_24h=100,
                    price_change_percentage_24h=4.55
                )
            }

            # Filter and return only requested assets
            return {
                asset_id: mock_data[asset_id] 
                for asset_id in asset_ids 
                if asset_id in mock_data
            }

        except Exception as e:
            raise DataValidationError(f"Failed to process market data: {str(e)}")

    def get_global_sentiment(self) -> Dict:
        """Get global market sentiment from mock data"""
        mock_user_data = self.mock_data.get('user_001', {})  # Use user_001 as default
        return mock_user_data.get('market_sentiment', {
            "score": 0.5,
            "sentiment": "Neutral"
        })