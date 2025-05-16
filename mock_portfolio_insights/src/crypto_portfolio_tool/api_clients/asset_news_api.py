from typing import List, Optional
# `requests` and `RequestException` would be handled by BaseAPIClient

# Relative imports for modules within your application package
from ..config import MOCK_ASSET_NEWS_SERVICE_BASE_URL # Ensure this variable is correctly loaded in config.py
from ..core.models import AssetNewsItem
from ..core.exceptions import APIRequestError # Assuming BaseAPIClient raises this
from .base_client import BaseAPIClient # Assuming your base client file is base_client.py

class AssetNewsAPIClient(BaseAPIClient):
    def __init__(self, base_url: Optional[str] = None):
        """
        Initializes the AssetNewsAPIClient.
        Args:
            base_url: The base URL for the asset news API.
                      Defaults to MOCK_ASSET_NEWS_SERVICE_BASE_URL from config.
        """
        self.base_url = base_url or "http://localhost:5003"

    def get_news_for_asset(self, asset_id: str, limit: Optional[int] = None) -> List[AssetNewsItem]:
        """
        Fetches news/sentiment for a specific asset.

        Args:
            asset_id: The ID of the asset (e.g., "BTC", "ETH").
            limit: Optional limit for the number of news items to return.

        Returns:
            A list of AssetNewsItem objects, or an empty list if no news is found or an error occurs.
        """
        # Endpoint relative to the base_url (e.g., "assets/BTC/news")
        # Normalizing asset_id to uppercase, assuming mock API expects it or handles it.
        endpoint = f"assets/{asset_id.upper()}/news" 
        
        params = {}
        if limit is not None:
            if not isinstance(limit, int) or limit <= 0:
                print(f"[WARN] Invalid limit value '{limit}' for get_news_for_asset. Ignoring limit.")
            else:
                params["limit"] = limit
        
        news_items: List[AssetNewsItem] = []
        try:
            # self.get() is from BaseAPIClient and should return parsed JSON data or raise APIRequestError
            raw_items_data = self.get(endpoint_path=endpoint, params=params)

            # If BaseAPIClient's get method returns None on 404 (if it doesn't raise an error for it)
            # This depends on your BaseAPIClient implementation.
            # Assuming self.get raises APIRequestError for 4xx/5xx.
            
            if not isinstance(raw_items_data, list):
                print(f"[ERROR] Unexpected response format for news for asset '{asset_id}'. Expected a list, got {type(raw_items_data)}.")
                return [] # Return empty list on unexpected format

            for item_data in raw_items_data:
                if not isinstance(item_data, dict):
                    print(f"[WARN] Skipping news item due to unexpected item format (not a dict): {item_data}")
                    continue
                try:
                    news_items.append(AssetNewsItem.model_validate(item_data))
                except Exception as e_pydantic: # Catch Pydantic validation errors or other parsing issues per item
                    print(f"[WARN] Could not parse news item for asset '{asset_id}': '{item_data}'. Error: {e_pydantic}")
            
            return news_items

        except APIRequestError as e:
            # Handle 404 specifically if the API returns it for "no news for asset"
            if e.status_code == 404:
                # print(f"[INFO] No news found for asset '{asset_id}' (404).") # Optional: logging
                return [] # Return empty list as per requirement for "no news"
            else:
                # For other API errors, log and return empty list or re-raise
                print(f"[ERROR] API request failed while fetching news for asset '{asset_id}': {e}")
                return [] # Default to empty list on other API errors
        except Exception as e_general:
            # Catch any other unexpected errors during the process
            print(f"[ERROR] Unexpected error fetching news for asset '{asset_id}': {e_general}")
            return []