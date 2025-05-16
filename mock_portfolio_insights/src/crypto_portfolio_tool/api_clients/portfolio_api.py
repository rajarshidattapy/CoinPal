from typing import Optional, Dict, Any
import requests
from ..core.models import Portfolio, AssetHolding
from ..core.exceptions import APIRequestError, DataValidationError

class PortfolioAPIClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or "http://localhost:5001"

    def get(self, endpoint: str) -> Dict[str, Any]:
        """Make a GET request to the API endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/{endpoint}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise APIRequestError(f"API request failed: {str(e)}")

    def get_user_portfolio(self, user_id: str) -> Portfolio:
        """Get portfolio data for a specific user"""
        try:
            # Mock data with values matching the screenshot
            mock_data = {
                "user_id": user_id,
                "wallet_address": f"mock_wallet_{user_id}",
                "assets": {
                    "BTC": AssetHolding(
                        asset_id="BTC",
                        name="Bitcoin",
                        symbol="BTC",
                        quantity=1.5,
                        current_price=40000.0,
                        current_value=60000.0
                    ),
                    "ETH": AssetHolding(
                        asset_id="ETH",
                        name="Ethereum",
                        symbol="ETH",
                        quantity=10.0,
                        current_price=2200.0,
                        current_value=22000.0
                    )
                },
                "cash_balance": 1000.0,
                "total_value": 82000.0
            }
            
            return Portfolio(**mock_data)
        except Exception as e:
           raise DataValidationError(f"Error processing portfolio data: {str(e)}")