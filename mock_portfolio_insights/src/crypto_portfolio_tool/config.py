import os
from dotenv import load_dotenv
# Load environment variables from .env file, if it exists
# This is useful for development. In production, env vars are usually set directly.
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env') # Points to root .env
load_dotenv(dotenv_path=dotenv_path)

MOCK_PORTFOLIO_SERVICE_BASE_URL = os.getenv("MOCK_PORTFOLIO_SERVICE_BASE_URL")
MOCK_MARKET_DATA_SERVICE_BASE_URL = os.getenv("MOCK_MARKET_DATA_SERVICE_BASE_URL")
MOCK_NEWS_SENTIMENT_SERVICE_BASE_URL = os.getenv("MOCK_NEWS_SENTIMENT_SERVICE_BASE_URL")
MOCK_COINBASE_SERVICE_BASE_URL = os.getenv("MOCK_COINBASE_SERVICE_BASE_URL")
MOCK_ASSET_NEWS_SERVICE_BASE_URL = os.getenv("MOCK_ASSET_NEWS_SERVICE_BASE_URL", "http://localhost:5003/api/v1")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_DEFAULT_MODEL = os.getenv("OPENROUTER_DEFAULT_MODEL", "google/gemini-pro") # Default if not in .env

if not OPENROUTER_API_KEY:
    print("WARNING: OPENROUTER_API_KEY not found in .env. GenAI features will not work.")
if not MOCK_PORTFOLIO_SERVICE_BASE_URL or not MOCK_MARKET_DATA_SERVICE_BASE_URL:
    raise EnvironmentError("Required mock service URLs are not set in .env file or environment.")