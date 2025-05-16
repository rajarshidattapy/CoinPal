# src/crypto_portfolio_tool/api_clients/llm_client.py
import requests
import json # Ensure json is imported
from typing import Optional, Dict, Any
from ..config import OPENROUTER_API_KEY, OPENROUTER_DEFAULT_MODEL
from ..core.exceptions import APIRequestError

class LLMInsightsClient:
    def __init__(self, api_key: Optional[str] = None, default_model: Optional[str] = None):
        self.api_key = api_key or OPENROUTER_API_KEY
        self.default_model = default_model or OPENROUTER_DEFAULT_MODEL # Ensure this is a VALID model ID from OpenRouter
        self.base_url = "https://openrouter.ai/api/v1" # This seems to be correct

        if not self.api_key:
            raise ValueError("OpenRouter API key is required for LLMInsightsClient.")

    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json", # Still good to set explicitly
            "HTTP-Referer": "http://localhost", # Replace with your actual site URL if deployed
            "X-Title": "CryptoPortfolioInsights", # Replace with your actual site name if deployed
        }
        
        # Serialize payload to JSON string MANUALLY
        data_payload_str = json.dumps(payload)

        try:
            # Use data=data_payload_str instead of json=payload
            response = requests.post(
                f"{self.base_url}/chat/completions", 
                headers=headers,
                data=data_payload_str,
                timeout=90
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            error_content = "No additional error content."
            try:
                error_content = http_err.response.json()
            except ValueError: 
                error_content = http_err.response.text
            raise APIRequestError(
                f"OpenRouter API HTTP error: {http_err} - {error_content}",
                status_code=http_err.response.status_code
            )
        except requests.exceptions.RequestException as e:
            raise APIRequestError(f"OpenRouter API request failed: {e}")

    def generate_text(self, prompt: str, system_message: Optional[str] = None, model: Optional[str] = None) -> Optional[str]:
        chosen_model = model or self.default_model
        # Ensure chosen_model is a VALID model ID from OpenRouter's list, e.g., "google/gemini-1.5-pro-latest" (no comments)
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": chosen_model, # Ensure this is correct and valid on OpenRouter
            "messages": messages,
            # "temperature": 0.7, # Optional parameters
            # "max_tokens": 500,  # Optional parameters
        }

        try:
            response_data = self._make_request(payload)
            if response_data and response_data.get("choices") and \
               isinstance(response_data["choices"], list) and len(response_data["choices"]) > 0 and \
               response_data["choices"][0].get("message") and \
               response_data["choices"][0]["message"].get("content"):
                return response_data["choices"][0]["message"]["content"].strip()
            else:
                print(f"[LLM_CLIENT_WARN] Unexpected response structure from OpenRouter for model {chosen_model}: {json.dumps(response_data, indent=2)}")
                return None
        except APIRequestError as e:
            print(f"[LLM_CLIENT_ERROR] Failed to generate text via OpenRouter for model {chosen_model}: {e}")
            return None
        except Exception as e_gen:
            print(f"[LLM_CLIENT_ERROR] Unexpected error in generate_text with model {chosen_model}: {e_gen}")
            import traceback
            traceback.print_exc()
            return None