import pytest 
from src.crypto_portfolio_tool.portfolio_insights.analyzer import PortfolioAnalyzer


def test_calculate_hhi_empty_list():
    
    analyzer = PortfolioAnalyzer(portfolio_client=None, market_client=None)
    asset_details = []
    expected_hhi = 0.0
    assert analyzer.calculate_hhi(asset_details) == expected_hhi
def test_calculate_hhi_single_asset_100_percent():
   
    analyzer = PortfolioAnalyzer(portfolio_client=None, market_client=None)
    asset_details = [{"asset_id": "BTC", "name": "Bitcoin", "percentage": 100.0}]
    expected_hhi = 10000.0
    assert analyzer.calculate_hhi(asset_details)== expected_hhi

def test_calculate_hhi_two_equal_assets():
    """
    Test HHI with two assets, each holding 50%.
    Expected HHI = 50^2 + 50^2 = 2500 + 2500 = 5000.0
    """
    analyzer = PortfolioAnalyzer(portfolio_client=None, market_client=None)
    asset_details = [
        {"asset_id": "BTC", "name": "Bitcoin", "percentage": 50.0},
        {"asset_id": "ETH", "name": "Ethereum", "percentage": 50.0}
    ]
    expected_hhi = 5000.0
    assert analyzer.calculate_hhi(asset_details) == expected_hhi
    

def test_calculate_hhi_multiple_varied_assets():
    """
    Test HHI with multiple assets with different percentages.
    Assets: 60%, 30%, 10%
    Expected HHI = 60^2 + 30^2 + 10^2 = 3600 + 900 + 100 = 4600.0
    """
    analyzer = PortfolioAnalyzer(portfolio_client=None, market_client=None)
    asset_details = [
        {"asset_id": "BTC", "name": "Bitcoin", "percentage": 60.0},
        {"asset_id": "ETH", "name": "Ethereum", "percentage": 30.0},
        {"asset_id": "SOL", "name": "Solana", "percentage": 10.0}
    ]
    expected_hhi = 4600.0
    assert analyzer.calculate_hhi(asset_details) == expected_hhi
    

def test_calculate_hhi_with_zero_percentage_asset():
    """
    Test HHI when an asset has 0% allocation. It should not contribute to HHI.
    Assets: BTC 100%, ETH 0%
    Expected HHI = 100^2 + 0^2 = 10000.0
    """
    analyzer = PortfolioAnalyzer(portfolio_client=None, market_client=None)
    asset_details = [
        {"asset_id": "BTC", "name": "Bitcoin", "percentage": 100.0},
        {"asset_id": "ETH", "name": "Ethereum", "percentage": 0.0}
    ]
    expected_hhi = 10000.0
    assert analyzer.calculate_hhi(asset_details) == expected_hhi
    

def test_calculate_hhi_floats_and_rounding():
    """
    Test HHI with float percentages and check rounding.
    Your calculate_hhi rounds to 2 decimal places.
    Assets: 33.33%, 33.33%, 33.34%
    HHI = 33.33^2 + 33.33^2 + 33.34^2
        = 1110.8889 + 1110.8889 + 1111.5556
        = 3333.3334
    Expected: 3333.33
    """
    analyzer = PortfolioAnalyzer(portfolio_client=None, market_client=None)
    asset_details = [
        {"asset_id": "A", "percentage": 33.33},
        {"asset_id": "B", "percentage": 33.33},
        {"asset_id": "C", "percentage": 33.34} # Sums to 100
    ]
    expected_hhi = 3333.33 # After rounding 3333.3334
    assert analyzer.calculate_hhi(asset_details) == expected_hhi
    

def test_calculate_hhi_invalid_percentage_data_skips_asset():
    """
    Test that if an asset has a missing or non-numeric percentage,
    and your calculate_hhi is designed to skip it (and perhaps print a warning),
    the HHI is calculated based on the valid assets.
    Current calculate_hhi in your code continues if percentage is None or not (int, float).
    Assets: BTC 50%, ETH (invalid), SOL 50%
    Expected HHI = 50^2 + 50^2 = 5000.0
    """
    analyzer = PortfolioAnalyzer(portfolio_client=None, market_client=None)
    asset_details = [
        {"asset_id": "BTC", "name": "Bitcoin", "percentage": 50.0},
        {"asset_id": "ETH", "name": "Ethereum", "percentage": "not-a-number"}, # Invalid
        {"asset_id": "SOL", "name": "Solana", "percentage": 50.0}
    ]
    expected_hhi = 5000.0 
    assert analyzer.calculate_hhi(asset_details) == expected_hhi, "HHI should only include valid percentages"

    
def test_calculate_hhi_all_invalid_percentage_data():
    """
    Test HHI when all assets have invalid percentage data.
    If your method skips all, it might return 0.0. If it returns None on error, test for None.
    Your current calculate_hhi has a try-except TypeError that returns None.
    Let's assume if all are skipped due to non-numeric, and no TypeError is raised before the loop finishes,
    it might return 0.0. If a TypeError *is* raised by `percentage ** 2`, it returns None.
    This test depends on the exact error handling logic.
    If "not-a-number" passes the `isinstance` check (it won't) and then `**2` is attempted, TypeError occurs.
    """
    analyzer = PortfolioAnalyzer(portfolio_client=None, market_client=None)
    asset_details = [
        {"asset_id": "ETH", "name": "Ethereum", "percentage": "not-a-number"},
        {"asset_id": "SOL", "name": "Solana", "percentage": None}
    ]
    # Based on your `calculate_hhi`:
    # - "not-a-number" will fail `isinstance` and be skipped.
    # - None will fail `isinstance` (actually, `percentage is None` check handles it) and be skipped.
    # So, hhi_score remains 0.0.
    expected_hhi = 0.0 # Because both are skipped by the initial check
    assert analyzer.calculate_hhi(asset_details) == expected_hhi, "HHI should be 0.0 when all percentages are invalid"

    pass

# Consider adding a test if your calculate_hhi method is expected to return None
# for certain types of malformed input that might cause an unhandled exception
# or if you explicitly return None in some error paths (like your TypeError except block).
# For example, if an asset_detail is not a dict, or 'percentage' key is missing entirely
# and your .get() default isn't robust enough for all cases.
# However, your current .get('percentage') and isinstance checks are quite robust.