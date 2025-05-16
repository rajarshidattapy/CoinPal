import requests
from typing import Optional, Dict, Any
from ..core.exceptions import APIRequestError # We'll create this exception file next
class BaseAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/') # Ensure no trailing slash

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Any:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(method, url, params=params, json=data, timeout=10)
            response.raise_for_status()  # Raises HTTPError for bad responses (4XX or 5XX)
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            error_content = None
            try:
                error_content = response.json()
            except requests.exceptions.JSONDecodeError:
                error_content = response.text
            raise APIRequestError(f"HTTP error occurred: {http_err} - {error_content}", status_code=response.status_code)
        except requests.exceptions.RequestException as e:
            raise APIRequestError(f"API request failed: {e}")

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        return self._request("POST", endpoint, data=data)
    