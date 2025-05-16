import sys
import os

# Adjust this path to where your crypto_portfolio_tool is located
portfolio_insights_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../mock_portfolio_insights/src'))

if portfolio_insights_src_path not in sys.path:
    print(f"INFO: Added {portfolio_insights_src_path} to sys.path")
    sys.path.insert(0, portfolio_insights_src_path)
mock_services_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../mock_portfolio_insights/mock_services'))
if mock_services_path not in sys.path:
    print(f"INFO: Added {mock_services_path} to sys.path")
    sys.path.insert(0, mock_services_path)