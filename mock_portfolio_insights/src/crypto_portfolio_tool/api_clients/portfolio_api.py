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
            # Mock data with complete values including cost basis and P&L
            mock_data = {
                "user_id": user_id,
                "wallet_address": f"mock_wallet_{user_id}",
                "assets": {
                    "BTC": AssetHolding(
                        asset_id="BTC",
                        name="Bitcoin",
                        symbol="BTC",
                        quantity=1.5,
                        average_buy_price=35000.0,    # Bought at $35,000
                        current_price=40000.0,        # Current price $40,000
                        current_value=60000.0,        # 1.5 * $40,000
                        cost_basis_total=52500.0,     # 1.5 * $35,000
                        unrealized_pnl=7500.0,        # (40000 - 35000) * 1.5
                        unrealized_pnl_percent=14.29  # (7500 / 52500) * 100
                    ),
                    "ETH": AssetHolding(
                        asset_id="ETH",
                        name="Ethereum",
                        symbol="ETH",
                        quantity=10.0,
                        average_buy_price=2500.0,    # Bought at $2,500
                        current_price=2200.0,        # Current price $2,200
                        current_value=22000.0,       # 10 * $2,200
                        cost_basis_total=25000.0,    # 10 * $2,500
                        unrealized_pnl=-3000.0,      # (2200 - 2500) * 10
                        unrealized_pnl_percent=-12.0 # (-3000 / 25000) * 100
                    )
                },
                "cash_balance": 1000.0,
                "total_value": 83000.0,
                "historical_summary": {
                    "24h_change_percent": 1.50,
                    "7d_change_percent": 2.50,
                    "30d_change_percent": 5.10,
                    "ytd_pnl": 1500.75
                }
            }
            
            return Portfolio(**mock_data)
        except Exception as e:
            raise DataValidationError(f"Error processing portfolio data: {str(e)}")