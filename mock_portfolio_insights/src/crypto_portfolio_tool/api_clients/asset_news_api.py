import requests
from typing import Dict, Optional
from ..core.exceptions import APIRequestError

class AssetNewsAPIClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or "http://localhost:5003"

    def get_asset_news(self, asset_id: str, limit: int = 2) -> Dict:
        """
        Fetch news and LLM-processed insights for a specific asset
        
        Args:
            asset_id (str): The asset identifier (e.g., 'BTC', 'ETH')
            limit (int): Maximum number of news items to return
            
        Returns:
            Dict containing processed news data
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/assets/{asset_id}/news",
                params={"limit": limit},
                timeout=10
            )
            
            if response.status_code == 404:
                return {
                    "asset_id": asset_id,
                    "processed_news": [],
                    "error": "No news found for this asset"
                }
                
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            raise APIRequestError(f"Failed to fetch news for asset {asset_id}: {str(e)}")