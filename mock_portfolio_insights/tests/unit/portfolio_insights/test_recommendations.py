# tests/unit/portfolio_insights/test_recommendations.py
import pytest
from src.crypto_portfolio_tool.portfolio_insights.recommendations import RecommendationEngine
from src.crypto_portfolio_tool.core.models import Portfolio, AssetHolding, HistoricalSummary

@pytest.fixture
def recommendation_engine_instance():
    """Pytest fixture to provide a RecommendationEngine instance."""
    return RecommendationEngine()


def test_recommendation_high_hhi(recommendation_engine_instance):
    """Test that a 'high concentration' recommendation is given for a high HHI score."""
    engine = recommendation_engine_instance
    # Arrange: Create mock portfolio and composition data
    mock_portfolio = Portfolio(
        user_id="test_user_hhi_high",
        assets=[ # Need at least one asset for some rules to make sense
            AssetHolding(asset_id="BTC", name="Bitcoin", quantity=1, average_buy_price=30000)
        ],
        cash_balance=1000,
        historical_summary=None # Or a mock HistoricalSummary if testing rules that use it
    )
    mock_composition = {
        "user_id": "test_user_hhi_high",
        "total_portfolio_value": 31000.0,
        "asset_composition": [ # This list is used by the "single asset concentration" rule
            {"asset_id": "BTC", "name": "Bitcoin", "quantity": 1, "current_value": 30000, "percentage": 96.77}
        ],
        "cash_balance": 1000.0,
        "cash_percentage": 3.23,
        "hhi_score": 3000.0 # Simulate a high HHI
    }

    # Act: Generate recommendations
    recommendations = engine.generate_recommendations(mock_portfolio, mock_composition)

    # Assert: Check for the expected recommendation string
    # Hint: You might want to check if a specific substring is present in any of the recommendation strings.
    # Example:
    found_expected_rec=any(
        "high concentration" in rec.lower() and "hhi" in rec.lower() for rec in recommendations
    )
    assert found_expected_rec,"High HHI recommendations not found or incorrect."
        # found_expected_rec = False
    # for rec in recommendations:
    #     if "high concentration" in rec and "HHI is 3000" in rec:
    #         found_expected_rec = True
    #         break
    # assert found_expected_rec, "High HHI recommendation not found or incorrect."
    # YOUR CODE HERE: Implement the assertion
    

def test_recommendation_moderate_hhi(recommendation_engine_instance):
    """Test for 'moderate concentration' recommendation."""
    engine = recommendation_engine_instance
    mock_portfolio = Portfolio(user_id="test_user_hhi_mod", assets=[], cash_balance=10000) # Simplified
    mock_composition = {
        "user_id": "test_user_hhi_mod",
        "hhi_score": 1800.0, # Moderate HHI
        "asset_composition": [], # Keep it simple if not testing asset-specific rules here
        "cash_percentage": 100.0
    }
    recommendations = engine.generate_recommendations(mock_portfolio, mock_composition)
    found_expected_rec = any(
        "moderate concentration" in rec.lower() and "1800" in rec for rec in recommendations
    )
    assert found_expected_rec, "Moderate HHI recommendation not found or incorrect."

def test_recommendation_good_diversification_hhi(recommendation_engine_instance):
    """Test for 'good diversification' HHI recommendation and fallback messages."""
    engine = recommendation_engine_instance

    # Arrange: Create a mock portfolio with a dummy asset and low cash
    mock_portfolio = Portfolio(
        user_id="test_user_hhi_good",
        assets=[AssetHolding(asset_id="DUMMY", name="Dummy", quantity=1, average_buy_price=1)],
        cash_balance=100  # Low cash
    )

    mock_composition_low_cash = {
        "user_id": "test_user_hhi_good",
        "hhi_score": 1000.0,  # Good diversification
        "asset_composition": [
            {"asset_id": "DUMMY", "name": "Dummy", "percentage": 5.0}
        ],
        "cash_percentage": 10.0
    }

    # Act: Generate recommendations
    recommendations = engine.generate_recommendations(mock_portfolio, mock_composition_low_cash)

    # Debug: Print the generated recommendations
    print("\n--- DEBUG: test_recommendation_good_diversification_hhi ---")
    print(f"Generated recommendations ({len(recommendations)}):")
    for r_idx, rec_item in enumerate(recommendations):
        print(f"  REC {r_idx + 1}: '{rec_item}'")  # Print with quotes to inspect spacing/punctuation
    print("--- END DEBUG ---")

    # Assert: Check for expected messages
    found_diversification_msg = any("good diversification" in rec.lower() for rec in recommendations)
    found_fallback_msg = any(rec.lower().startswith("overall, things look good") for rec in recommendations)

    assert len(recommendations) == 2, f"Expected 2 recommendations, got {len(recommendations)}"
    assert found_diversification_msg, "'Good diversification' message not found."
    assert found_fallback_msg, "'Overall, things look good' fallback message not found."

def test_recommendation_hhi_not_calculated(recommendation_engine_instance):
    """Test when HHI score is None (e.g., calculation failed)."""
    engine = recommendation_engine_instance
    mock_portfolio = Portfolio(user_id="test_user_hhi_none", assets=[], cash_balance=0)
    mock_composition = {
        "user_id": "test_user_hhi_none",
        "hhi_score": None,  # HHI calculation failed
        "asset_composition": [],
        "cash_percentage": 0.0
    }

    recommendations = engine.generate_recommendations(mock_portfolio, mock_composition)

    # Assert: The expected error message is present
    found_error_msg = any(
        "could not calculate portfolio concentration" in rec.lower() for rec in recommendations
    )

    assert found_error_msg, "Missing message about failure to calculate HHI."


def test_recommendation_single_asset_concentration_alert(recommendation_engine_instance):
    """Test the specific alert for high concentration in a single asset."""
    engine = recommendation_engine_instance
    mock_portfolio = Portfolio(
        user_id="test_user_single_conc",
        assets=[AssetHolding(asset_id="XYZ", name="MegaCoin", quantity=1, average_buy_price=100)]
    )
    mock_composition = {
        "user_id": "test_user_single_conc",
        "hhi_score": 7000.0,  # High HHI
        "asset_composition": [
            {"asset_id": "XYZ", "name": "MegaCoin", "percentage": 80.0}  # > 60%
        ],
        "cash_percentage": 20.0
    }

    recommendations = engine.generate_recommendations(mock_portfolio, mock_composition)

    # Assert the "heavily concentrated" alert for MegaCoin and the HHI message
    found_concentration_alert = any(
        "heavily concentrated" in rec.lower() and "megacoin" in rec.lower() for rec in recommendations
    )
    found_hhi_msg = any(
        "hhi" in rec.lower() and "7000" in rec for rec in recommendations
    )

    assert found_concentration_alert, "Specific concentration alert for MegaCoin not found."
    assert found_hhi_msg, "HHI message with score 7000 not found."


def test_recommendation_high_cash_balance(recommendation_engine_instance):
    """Test recommendation for high cash balance."""
    engine = recommendation_engine_instance
    mock_portfolio = Portfolio(user_id="test_user_high_cash", assets=[], cash_balance=5000)
    mock_composition = {
        "user_id": "test_user_high_cash",
        "hhi_score": 1000.0,  # Good HHI (to isolate cash rule)
        "asset_composition": [],
        "cash_percentage": 80.0  # High cash
    }

    recommendations = engine.generate_recommendations(mock_portfolio, mock_composition)

    # Assert for the "significant cash balance" message
    found_cash_balance_msg = any(
        "significant cash balance" in rec.lower() for rec in recommendations
    )

    assert found_cash_balance_msg, "High cash balance recommendation message not found."

def test_recommendation_significant_drop_historical(recommendation_engine_instance):
    """Test recommendation for significant historical drop."""
    engine = recommendation_engine_instance

    # Arrange: Create mock portfolio data with a significant 7-day drop
    mock_portfolio_data = {
        "user_id": "test_user_hist_drop",
        "assets": [],
        "cash_balance": 1000,
        "historical_summary": {"7d_change_percent": -15.0}  # Key matches Pydantic alias
    }

    historical_summary_obj = HistoricalSummary.model_validate(mock_portfolio_data["historical_summary"])

    mock_portfolio = Portfolio(
        user_id=mock_portfolio_data["user_id"],
        assets=mock_portfolio_data["assets"],
        cash_balance=mock_portfolio_data["cash_balance"],
        historical_summary=historical_summary_obj
    )

    mock_composition = {
        "user_id": "test_user_hist_drop",
        "hhi_score": 1000.0,
        "asset_composition": [],
        "cash_percentage": 50.0
    }

    # --- ADD THIS PRINT BEFORE CALLING generate_recommendations ---
    print(f"\n--- DEBUG: test_recommendation_significant_drop_historical (INPUT) ---")
    print(f"mock_portfolio.historical_summary: {mock_portfolio.historical_summary}")
    if mock_portfolio.historical_summary:
        print(f"mock_portfolio.historical_summary.seven_d_change_percent: {mock_portfolio.historical_summary.seven_d_change_percent}")
    # --- END PRINT BLOCK ---

    recommendations = engine.generate_recommendations(mock_portfolio, mock_composition)

    # --- ADD THIS PRINT BLOCK ---
    print(f"\n--- DEBUG: test_recommendation_significant_drop_historical (OUTPUT) ---")
    print(f"Generated recommendations ({len(recommendations)}):")
    for r_idx, rec_item in enumerate(recommendations):
        print(f"  REC {r_idx + 1}: '{rec_item}'")
    print("--- END DEBUG ---")
    # --- END PRINT BLOCK ---

    found_drop_msg = any(
        "significant drop" in rec.lower() and "last 7 days" in rec.lower() for rec in recommendations
    )
    assert found_drop_msg, "Significant historical drop recommendation not found."
def test_recommendation_no_crypto_assets_with_cash(recommendation_engine_instance):
    """Test recommendation when there are no crypto assets but cash is present."""
    engine = recommendation_engine_instance
    mock_portfolio = Portfolio(user_id="test_user_no_assets_cash", assets=[], cash_balance=1000)
    mock_composition = {
        "user_id": "test_user_no_assets_cash",
        "hhi_score": 0.0,  # No assets, HHI is 0
        "asset_composition": [],
        "cash_percentage": 100.0
    }

    recommendations = engine.generate_recommendations(mock_portfolio, mock_composition)

    # Assert for the "no crypto assets. Ready to start investing?" message
    found_no_crypto_msg = any(
        "no crypto assets" in rec.lower() and "ready to start investing?" in rec.lower() for rec in recommendations
    )

    assert found_no_crypto_msg, "Message about no crypto assets and starting investing not found."

def test_recommendation_empty_portfolio_no_cash(recommendation_engine_instance):
    """Test recommendation for a completely empty portfolio (no assets, no cash)."""
    engine = recommendation_engine_instance
    mock_portfolio = Portfolio(user_id="test_user_empty_all", assets=[], cash_balance=0)
    mock_composition = {
        "user_id": "test_user_empty_all",
        "hhi_score": 0.0,
        "asset_composition": [],
        "cash_percentage": 0.0
    }

    recommendations = engine.generate_recommendations(mock_portfolio, mock_composition)

    # Assert for the "portfolio is currently empty. Consider depositing funds" message
    found_empty_portfolio_msg = any(
        "portfolio is currently empty" in rec.lower() and "consider depositing funds" in rec.lower() for rec in recommendations
    )

    assert found_empty_portfolio_msg, "Message about empty portfolio and depositing funds not found."


def test_recommendation_default_fallback_message(recommendation_engine_instance):
    """
    Test that a default fallback message is provided when no specific rules trigger,
    and HHI is good, but the "Overall, things look good..." isn't the primary focus.
    """
    engine = recommendation_engine_instance
    mock_portfolio = Portfolio(
        user_id="test_user_default_fallback",
        assets=[AssetHolding(asset_id="ETH", name="Ethereum", quantity=1, average_buy_price=2000)],
        cash_balance=100,
        historical_summary=HistoricalSummary(seven_d_change_percent=1.0)
    )
    mock_composition = {
        "user_id": "test_user_default_fallback",
        "hhi_score": 1000.0,
        "asset_composition": [
            {"asset_id": "ETH", "name": "Ethereum", "percentage": 50.0},
            {"asset_id": "BTC", "name": "Bitcoin", "percentage": 50.0}
        ],
        "cash_percentage": 5.0
    }

    recommendations = engine.generate_recommendations(mock_portfolio, mock_composition)
    print("\nRecommendations for good_diversification_hhi:")
    for r_idx, rec_item in enumerate(recommendations):
      print(f"{r_idx + 1}. {rec_item}")
     # Assertions
    found_hhi_good_msg = any("good diversification" in rec.lower() for rec in recommendations)
    found_fallback_msg = any("overall, things look good" in rec.lower() for rec in recommendations)

    assert found_hhi_good_msg, "'Good diversification' HHI message not found."
    assert found_fallback_msg, "'Overall, things look good' fallback message not found."
    assert len(recommendations) == 2, f"Expected 2 recommendations, got {len(recommendations)}"
