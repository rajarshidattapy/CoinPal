from . import config
from .api_clients.portfolio_api import PortfolioAPIClient
from .api_clients.market_data_api import MarketDataAPIClient
from .api_clients.asset_news_api import AssetNewsAPIClient
from .api_clients.llm_client import LLMInsightsClient  
from .portfolio_insights.analyzer import PortfolioAnalyzer
from .portfolio_insights.recommendations import RecommendationEngine
from .core.exceptions import APIRequestError, DataValidationError, LogicError
from .coinpal.assistant import CoinPalAssistant
import json
from typing import Optional


def run_portfolio_analysis(user_id: str):
    print(f"\n--- Analyzing Portfolio for User: {user_id} ---")

    # Instantiate all clients
    portfolio_client = PortfolioAPIClient(base_url=config.MOCK_PORTFOLIO_SERVICE_BASE_URL)
    market_client = MarketDataAPIClient(base_url=config.MOCK_MARKET_DATA_SERVICE_BASE_URL)
    asset_news_client = AssetNewsAPIClient(base_url=config.MOCK_ASSET_NEWS_SERVICE_BASE_URL)
    llm_client = LLMInsightsClient()  
    analyzer = PortfolioAnalyzer(
        portfolio_client=portfolio_client,
        market_client=market_client,
        asset_news_client=asset_news_client,
        llm_client=llm_client  # <--- MODIFIED: Pass LLM client to Analyzer
    )
    reco_engine = RecommendationEngine(
        llm_client=llm_client  # <--- MODIFIED: Pass LLM client to RecommendationEngine
    )

    try:
        enriched_portfolio = analyzer.get_enriched_portfolio(user_id)
        composition = analyzer.get_portfolio_composition(user_id) # Contains HHI

        print("\nPortfolio Composition:")
        print(json.dumps(composition, indent=2))

        if enriched_portfolio.historical_summary:
            print("\nHistorical Performance Summary:")
            print(json.dumps(enriched_portfolio.historical_summary.model_dump(by_alias=True), indent=2))

        # --- Gather All Asset Specific Insights for the Portfolio (processed by LLM via Analyzer) ---
        all_portfolio_asset_insights = {}
        asset_composition_list = composition.get("asset_composition", []) # Get list or empty list
        
        if asset_composition_list: # Check if the list is not empty
            print("\nFetching and Processing News with LLM (this may take a moment)...") # User feedback
            for asset_detail in asset_composition_list:
                # Ensure asset_detail is a dictionary before calling .get()
                if isinstance(asset_detail, dict):
                    asset_id = asset_detail.get("asset_id")
                    if asset_id:
                        # Analyzer.get_insights_for_asset now uses LLM for processing
                        insights_for_one_asset = analyzer.get_insights_for_asset(str(asset_id), news_limit=2) 
                        all_portfolio_asset_insights[str(asset_id).upper()] = insights_for_one_asset
                else:
                    print(f"[MAIN_WARN] Skipping non-dict item in asset_composition: {asset_detail}")

        # --- Recommendations (now potentially with GenAI context) ---
        recommendations = reco_engine.generate_recommendations(
            enriched_portfolio,
            composition,
            all_asset_specific_insights=all_portfolio_asset_insights # Passed with LLM-processed news
        )
        print("\nInvestment Recommendations:")
        for i, reco in enumerate(recommendations):
            print(f"{i+1}. {reco}")
        # --- End Recommendations ---

        # --- Global Market Sentiment ---
        sentiment = market_client.get_global_sentiment()
        print("\nGlobal Market Sentiment:")
        print(json.dumps(sentiment.model_dump(), indent=2))
        # --- End Sentiment ---

        # --- Display LLM Processed Asset News Insights ---
        print("\nLLM Processed Asset News & Sentiment (Top 2 by Current Value):")
        # asset_composition_list is already fetched and checked above
        
        if not asset_composition_list: # Check again for clarity or if logic changes above
            print("  (No assets in portfolio to display news for)")
        else:
            # Ensure asset_composition_list contains dictionaries for sorting
            valid_asset_details_for_sorting = [
                item for item in asset_composition_list if isinstance(item, dict)
            ]

            if not valid_asset_details_for_sorting:
                 print("  (No valid asset details found in portfolio to display news for)")
            else:
                top_assets_details = sorted(
                    valid_asset_details_for_sorting,
                    key=lambda x: x.get("current_value", 0.0) or 0.0, # Handle None for current_value
                    reverse=True
                )[:2]

                if not top_assets_details:
                    print("  (Could not determine top assets for news display)")

                for asset_detail_dict in top_assets_details:
                    # asset_detail_dict is already confirmed to be a dict
                    asset_id_raw = asset_detail_dict.get("asset_id")
                    asset_id_upper = str(asset_id_raw).upper() if asset_id_raw else "UNKNOWN"
                    asset_name = asset_detail_dict.get("name", asset_id_upper)
                    
                    print(f"\n🔹 Processed News for {asset_name} ({asset_id_upper}):")
                    # Get the already fetched and LLM-processed insights
                    insights_for_display = all_portfolio_asset_insights.get(asset_id_upper)

                    if insights_for_display and not insights_for_display.get("error"):
                        processed_news = insights_for_display.get("processed_news", [])
                        if processed_news and isinstance(processed_news, list):
                            for item_dict in processed_news:
                                if isinstance(item_dict, dict):
                                    print(f"  • Headline: '{item_dict.get('original_headline', 'N/A')}'")
                                    print(f"    LLM Summary: '{item_dict.get('llm_summary', 'N/A')}'")
                                    print(f"    LLM Sentiment: [{item_dict.get('llm_sentiment_label', 'N/A')}] (Source: {item_dict.get('source', 'N/A')})")
                                else:
                                    print(f"  Skipping non-dict news item: {item_dict}")
                        elif not processed_news:
                            print("  (No recent news processed by LLM for this asset)")
                        else:
                            print(f"  (Processed news is not in expected list format: {type(processed_news)})")
                    elif insights_for_display and insights_for_display.get("error"):
                        print(f"  Error fetching/processing news: {insights_for_display.get('error')}")
                    else:
                        print(f"  (No news insights data available in all_portfolio_asset_insights for {asset_id_upper})")
        # --- End Top Asset News Insights ---

    except APIRequestError as e:
        print(f"Error: API Request Failed - Status {e.status_code}: {e}")
    except DataValidationError as e:
        print(f"Error: Data Validation Failed: {e}")
    except LogicError as e:
        print(f"Error: Application Logic Failed: {e}")
    except NameError as e: # Keeping existing specific error handling
        print(f"A NameError occurred (likely a variable used before assignment): {e}")
    except Exception as e:
        print(f"An unexpected error occurred in run_portfolio_analysis: {e}")
        import traceback
        traceback.print_exc()


def interact_with_coinpal(portfolio_analyzer: Optional[PortfolioAnalyzer] = None):
    print("\n--- Interacting with CoinPal (type 'quit' to exit) ---")
    
    if portfolio_analyzer is None:
        print("Warning: CoinPal is operating without a portfolio analyzer. Some features may be limited.")
        # Optionally, instantiate a default analyzer here if critical,
        # but the original structure implies it's passed from main.
        # For now, we'll let it proceed and CoinPalAssistant should handle a None analyzer if designed to.

    assistant = CoinPalAssistant(portfolio_analyzer=portfolio_analyzer) # Analyzer is now LLM-enabled

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == 'quit':
                print("CoinPal: Goodbye!")
                break

            user_id_for_action = "user_001" # Assuming a default user for CoinPal interactions
            response = assistant.process_query(user_input, user_id=user_id_for_action)
            print(f"CoinPal: {response}")
        except EOFError: # Handle Ctrl+D or unexpected end of input
            print("\nCoinPal: Input stream closed. Exiting.")
            break
        except KeyboardInterrupt: # Handle Ctrl+C
            print("\nCoinPal: Interaction interrupted. Exiting.")
            break
        except Exception as e:
            print(f"CoinPal Error: An unexpected error occurred during interaction: {e}")
            # Loop continues unless it's a critical error handled by exiting above


if __name__ == "__main__":
    test_user_id_1 = "user_001"
    test_user_id_2 = "user_002"
    non_existent_user = "user_999"

    print("=" * 10 + " PORTFOLIO ANALYSIS " + "=" * 10)
    run_portfolio_analysis(test_user_id_1)
    # run_portfolio_analysis(test_user_id_2) # You can uncomment to run for more users
    # run_portfolio_analysis(non_existent_user)

    print("\n" + "=" * 10 + " COINPAL INTERACTION " + "=" * 10)
    
    # Instantiate clients for CoinPal's analyzer
    portfolio_client_cp = PortfolioAPIClient(base_url=config.MOCK_PORTFOLIO_SERVICE_BASE_URL)
    market_client_cp = MarketDataAPIClient(base_url=config.MOCK_MARKET_DATA_SERVICE_BASE_URL)
    asset_news_client_cp = AssetNewsAPIClient(base_url=config.MOCK_ASSET_NEWS_SERVICE_BASE_URL)
    llm_client_cp = LLMInsightsClient() # <--- NEW: Instantiate LLM Client for CoinPal's analyzer

    analyzer_for_coinpal = PortfolioAnalyzer(
        portfolio_client=portfolio_client_cp,
        market_client=market_client_cp,
        asset_news_client=asset_news_client_cp,
        llm_client=llm_client_cp  # <--- MODIFIED: Pass LLM client to CoinPal's analyzer
    )
    interact_with_coinpal(portfolio_analyzer=analyzer_for_coinpal)