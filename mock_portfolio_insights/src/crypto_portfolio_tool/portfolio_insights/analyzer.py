from typing import Dict, Optional, List, Any
import json
import os

from ..api_clients.portfolio_api import PortfolioAPIClient
from ..api_clients.market_data_api import MarketDataAPIClient
from ..api_clients.asset_news_api import AssetNewsAPIClient
from ..core.exceptions import APIRequestError, LogicError, DataValidationError
from ..core.models import Portfolio, AssetHolding, AssetNewsItem, MarketAssetInfo

from ..api_clients.llm_client import LLMInsightsClient


class PortfolioAnalyzer:
    def __init__(self, portfolio_client=None, market_client=None, asset_news_client=None, llm_client=None):
        self.portfolio_client = portfolio_client
        self.market_client = market_client
        self.asset_news_client = asset_news_client
        self.llm_client = llm_client
        
        # Load mock data
        mock_data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'mock_services', 'mock_data', 'portfolios.json')
        with open(mock_data_path, 'r') as f:
            self.mock_data = json.load(f)

    def get_enriched_portfolio(self, user_id: str) -> Portfolio:
        try:
            portfolio_data = self.portfolio_client.get_user_portfolio(user_id)
            
            # Enrich with historical performance from mock data
            if user_id in self.mock_data:
                mock_user_data = self.mock_data[user_id]
                portfolio_data.historical_summary = mock_user_data.get('historical_performance_metrics', {})
                
            return portfolio_data
            
        except Exception as e:
            raise LogicError(f"Error enriching portfolio: {str(e)}")

    def get_portfolio_composition(self, user_id: str) -> Dict:
        try:
            enriched_portfolio = self.get_enriched_portfolio(user_id)
            
            composition_details = []
            if enriched_portfolio.assets:
                for asset_id, asset in enriched_portfolio.assets.items():
                    percentage = (asset.current_value / enriched_portfolio.total_value * 100) if enriched_portfolio.total_value else 0
                    composition_details.append({
                        "asset_id": asset_id,
                        "name": asset.name,
                        "symbol": asset.symbol,
                        "quantity": asset.quantity,
                        "current_price": asset.current_price,
                        "current_value": asset.current_value,
                        "percentage": round(percentage, 2),
                        # Add these fields for cost basis and P&L
                        "cost_basis_total": asset.cost_basis_total,
                        "unrealized_gain_loss_abs": asset.unrealized_pnl,
                        "unrealized_gain_loss_percent": asset.unrealized_pnl_percent
                    })

            cash_percentage = (enriched_portfolio.cash_balance / enriched_portfolio.total_value * 100) if enriched_portfolio.total_value else 100

            return {
                "user_id": user_id,
                "total_portfolio_value": round(enriched_portfolio.total_value, 2),
                "asset_composition": composition_details,
                "cash_balance": round(enriched_portfolio.cash_balance, 2),
                "cash_percentage": round(cash_percentage, 2),
                "hhi_score": self.calculate_hhi(composition_details)
            }
        except Exception as e:
            raise ValueError(f"Error in portfolio composition: {str(e)}")

    def calculate_hhi(self, asset_composition_details: List[Dict[str, Any]]) -> Optional[float]:
        if not asset_composition_details:
            return 0.0

        hhi_score = 0.0
        try:
            for detail in asset_composition_details:
                percentage = detail.get('percentage')
                if percentage is None or not isinstance(percentage, (int, float)):
                    print(f"Warning: Skipping asset in HHI calculation due to invalid percentage: {detail.get('asset_id')}")
                    continue
                hhi_score += percentage ** 2
            return round(hhi_score, 2)
        except TypeError:
            print("Error: HHI calculation failed due to non-numeric percentage value.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during HHI calculations: {str(e)}")
            return None

    def get_insights_for_asset(self, asset_id: str, news_limit: int = 2) -> Dict[str, Any]:
        processed_news_list = []
        error_message = None

        try:
            news_items_models: List[AssetNewsItem] = self.asset_news_client.get_news_for_asset(
                asset_id, limit=news_limit
            )

            if not news_items_models:
                return {
                    "asset_id": asset_id.upper(),
                    "processed_news": [],
                    "error": "No raw news found to process."
                }

            for news_item_model in news_items_models:
                headline = news_item_model.headline

                prompt = (
                    f"Analyze the following news headline regarding {asset_id.upper()}:\n"
                    f"Headline: \"{headline}\"\n\n"
                    "Provide:\n"
                    "1. A concise one-sentence summary of the headline's main point.\n"
                    "2. A sentiment label (choose one: very positive, positive, neutral, negative, very negative).\n"
                    "Format your response as JSON with keys 'summary' and 'sentiment_label'."
                )
                system_prompt = "You are a financial news analyst. Provide responses in the requested JSON format. Ensure the JSON is valid."

                llm_response_str = self.llm_client.generate_text(prompt, system_message=system_prompt)

                llm_summary = "LLM processing failed or no summary provided."
                llm_sentiment = "unknown"

                if llm_response_str:
                    try:
                        llm_data = json.loads(llm_response_str)
                        llm_summary = llm_data.get("summary", "Summary not provided by LLM.")
                        llm_sentiment_raw = llm_data.get("sentiment_label", "Sentiment not provided by LLM.")
                        llm_sentiment = str(llm_sentiment_raw).lower()
                    except json.JSONDecodeError:
                        print(f"[ANALYZER_WARN] LLM response for '{headline}' was not valid JSON: {llm_response_str}")
                        llm_summary = headline
                        llm_sentiment = (news_item_model.sentiment_label or "unknown").lower()
                    except Exception as e_parse:
                        print(f"[ANALYZER_WARN] Error parsing LLM response for '{headline}': {e_parse}")
                        llm_summary = headline
                        llm_sentiment = (news_item_model.sentiment_label or "unknown").lower()
                else:
                    print(f"[ANALYZER_WARN] LLM generate_text returned None for headline: '{headline}'")
                    llm_summary = headline
                    llm_sentiment = (news_item_model.sentiment_label or "unknown").lower()

                processed_news_list.append({
                    "original_headline": headline,
                    "source": news_item_model.source,
                    "timestamp": news_item_model.timestamp.isoformat() if news_item_model.timestamp else None,
                    "llm_summary": llm_summary.strip(),
                    "llm_sentiment_label": llm_sentiment.strip()
                })

        except APIRequestError as e_api:
            print(f"[ANALYZER_ERROR] API error getting/processing news for asset {asset_id}: {e_api}")
            error_message = f"API error: {str(e_api)}"
        except Exception as e_gen:
            print(f"[ANALYZER_ERROR] Unexpected error getting/processing news for asset {asset_id}: {e_gen}")
            error_message = f"Failed to process news: {str(e_gen)}"
            import traceback
            traceback.print_exc()

        return {
            "asset_id": asset_id.upper(),
            "processed_news": processed_news_list,
            "error": error_message
        }
