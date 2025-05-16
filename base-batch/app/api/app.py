from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from requests import get
import collections
import os
import sys
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import random
import pymongo
from datetime import datetime

# Add mock_portfolio_insights paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
src_path = os.path.abspath(os.path.join(project_root, 'mock_portfolio_insights', 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)
    print(f"INFO: Added {src_path} to sys.path")

# Import crypto_portfolio_tool modules and config
import crypto_portfolio_tool.config as portfolio_tool_config
from crypto_portfolio_tool.core.models import Portfolio
# In base-batch/app/api/app.py
# After sys.path manipulation

try:
    from crypto_portfolio_tool.core.exceptions import APIRequestError, LogicError, DataValidationError # << CORRECTED
    # ... other crypto_portfolio_tool imports ...
    print("INFO (app.py): Successfully imported all crypto_portfolio_tool modules.")
except ImportError as e:
    # ...
    raise
from crypto_portfolio_tool.portfolio_insights.recommendations import RecommendationEngine
from crypto_portfolio_tool.api_clients.portfolio_api import PortfolioAPIClient
from crypto_portfolio_tool.api_clients.market_data_api import MarketDataAPIClient
from crypto_portfolio_tool.api_clients.asset_news_api import AssetNewsAPIClient
from crypto_portfolio_tool.api_clients.llm_client import LLMInsightsClient
from crypto_portfolio_tool.portfolio_insights.analyzer import PortfolioAnalyzer
     
# Load environment variables
load_dotenv(os.path.join(project_root, 'mock_portfolio_insights', '.env'))

# Initialize configuration with defaults
if not hasattr(portfolio_tool_config, 'MOCK_PORTFOLIO_SERVICE_BASE_URL'):
    portfolio_tool_config.MOCK_PORTFOLIO_SERVICE_BASE_URL = os.getenv('MOCK_PORTFOLIO_SERVICE_BASE_URL', 'http://localhost:5001')
if not hasattr(portfolio_tool_config, 'MOCK_MARKET_DATA_SERVICE_BASE_URL'):
    portfolio_tool_config.MOCK_MARKET_DATA_SERVICE_BASE_URL = os.getenv('MOCK_MARKET_DATA_SERVICE_BASE_URL', 'http://localhost:5002')
if not hasattr(portfolio_tool_config, 'MOCK_ASSET_NEWS_SERVICE_BASE_URL'):
    portfolio_tool_config.MOCK_ASSET_NEWS_SERVICE_BASE_URL = os.getenv('MOCK_ASSET_NEWS_SERVICE_BASE_URL', 'http://localhost:5003')

# Initialize API clients
try:
    portfolio_client_global = PortfolioAPIClient(
        base_url=os.getenv('MOCK_PORTFOLIO_SERVICE_BASE_URL', 'http://localhost:5001')
    )
    market_client_global = MarketDataAPIClient(
        base_url=os.getenv('MOCK_MARKET_DATA_SERVICE_BASE_URL', 'http://localhost:5002')
    )
    asset_news_client_global = AssetNewsAPIClient(
        base_url=os.getenv('MOCK_ASSET_NEWS_SERVICE_BASE_URL', 'http://localhost:5003')
    )

    # Initialize LLM client if API key is available
    llm_client_global = None
    if os.getenv('OPENROUTER_API_KEY'):
        llm_client_global = LLMInsightsClient(
            api_key=os.getenv('OPENROUTER_API_KEY'),
            default_model=os.getenv('OPENROUTER_DEFAULT_MODEL', 'gpt-3.5-turbo')
        )
    else:
        print("WARNING: OPENROUTER_API_KEY not found. LLM features will be limited.")

    # Initialize analyzers
    analyzer_global = PortfolioAnalyzer(
        portfolio_client=portfolio_client_global,
        market_client=market_client_global,
        asset_news_client=asset_news_client_global,
        llm_client=llm_client_global
    )
    reco_engine_global = RecommendationEngine(llm_client=llm_client_global)

except Exception as e:
    print(f"Error initializing services: {str(e)}")
    sys.exit(1)

app = Flask(__name__)
collections.Iterable = collections.abc.Iterable
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "supports_credentials": True,
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

class ChatMessage(BaseModel):
    message: str
    wallet_address: Optional[str] = None

class LocationRequest(BaseModel):
    ip_address: Optional[str] = None
    country: Optional[str] = None

class SecurityCheckRequest(BaseModel):
    wallet_address: Optional[str] = None
    email: Optional[str] = None

class SupportTicketRequest(BaseModel):
    issue_type: str
    description: str
    wallet_address: Optional[str] = None

class FeeAnalysisRequest(BaseModel):
    transaction_type: str
    amount: float
    currency: str

class AltcoinRequest(BaseModel):
    coin_name: Optional[str] = None
    action: str  # "search", "compare", "transfer"

# Mock data for demonstration
MOCK_TRANSACTIONS = [
    {"id": "TX123456", "type": "BTC Purchase", "amount": -50.00, "fee_percentage": 3.5, "date": "2023-04-22"},
    {"id": "TX789012", "type": "ETH Transfer", "amount": -15.00, "fee_percentage": 1.2, "date": "2023-04-21"},
    {"id": "TX345678", "type": "BTC Sale", "amount": 120.00, "fee_percentage": 2.8, "date": "2023-04-20"},
]

MOCK_PORTFOLIO = {
    "BTC": 60,
    "ETH": 25,
    "Other": 15
}

MOCK_ALTCOINS = [
    {"name": "Polkadot", "symbol": "DOT", "logo": "https://cryptologos.cc/logos/polkadot-dot-logo.png", "available_on": ["Binance", "Kraken", "KuCoin"]},
    {"name": "Cardano", "symbol": "ADA", "logo": "https://cryptologos.cc/logos/cardano-ada-logo.png", "available_on": ["Binance", "Kraken", "KuCoin"]},
    {"name": "Solana", "symbol": "SOL", "logo": "https://cryptologos.cc/logos/solana-sol-logo.png", "available_on": ["Binance", "Kraken", "KuCoin"]},
    {"name": "Chainlink", "symbol": "LINK", "logo": "https://cryptologos.cc/logos/chainlink-link-logo.png", "available_on": ["Binance", "Kraken", "KuCoin"]},
]

MOCK_SUPPORT_TICKETS = [
    {"id": "ST123456", "issue": "ETH withdrawal pending for 24 hours", "status": "in-progress", "diagnosis": "Network congestion on Ethereum blockchain. Expected resolution: 2-4 hours.", "action": "No action needed. Your transaction is queued and will process automatically."},
    {"id": "ST789012", "issue": "ID verification failed", "status": "resolved", "diagnosis": "Blurry image submitted. New submission required.", "action": "Resubmit with clearer image in good lighting."},
]

RESTRICTED_LOCATIONS = ["China", "Iran", "North Korea", "Cuba", "Syria"]

def dbConnect(): 
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    return myclient


@app.route("/api/check-location", methods=["GET"])
def check_location():
    try:
        ip = get('https://api.ipify.org').text
        response = get(f"http://ip-api.com/json/{ip}")
        data = response.json()

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch IP data"}), 500
        
        region_name = data.get("regionName", "Unknown region")
        country = data.get("country", "")
        is_restricted = country in RESTRICTED_LOCATIONS

        return jsonify({
            "is_restricted": is_restricted,
            "country": country,
            "region_name": region_name
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/api/chat", methods=["POST"])
def chat_with_ai():
    chat_message = request.get_json()
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json",
        "X-Title": "CoinPal"  
    }

    data = {
        "model": "openai/gpt-4o",  # You can change this to other models
        "messages": [
            {"role": "system", "content": "You are CoinPal, a helpful AI assistant for cryptocurrency and Coinbase related questions. You help users with fee analysis, security, KYC, and other crypto-related topics."},
            {"role": "user", "content": chat_message['message']},
        ],
        "max_tokens": 1024,
    }
        
    # Make request to OpenRouter API
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    print(result.get("choices")[0].get("message").get("content"))
    return result.get("choices")[0].get("message").get("content")

@app.route("/api/fee-analysis", methods=["POST"])
def analyze_fees(request: FeeAnalysisRequest):
    # In a real app, you would calculate actual fees based on the transaction
    # For demo purposes, we'll return mock data
    standard_fee = request.amount * 0.035  # 3.5% standard fee
    pro_fee = request.amount * 0.006  # 0.6% pro fee
    savings = standard_fee - pro_fee
    
    return {
        "standard_fee": standard_fee,
        "pro_fee": pro_fee,
        "savings": savings,
        "recommendation": f"Use Coinbase Pro for lower fees (0.6% vs 3.5%). Your transaction could save ${savings:.2f}.",
        "transactions": MOCK_TRANSACTIONS
    }

@app.route("/api/altcoins", methods=["POST"])
def altcoin_info(request: AltcoinRequest):
    if request.action == "search":
        # Search for altcoins
        if request.coin_name:
            filtered_coins = [coin for coin in MOCK_ALTCOINS if request.coin_name.lower() in coin["name"].lower()]
            return {"coins": filtered_coins}
        else:
            return {"coins": MOCK_ALTCOINS}
    elif request.action == "compare":
        # Compare exchanges for a specific coin
        coin = next((coin for coin in MOCK_ALTCOINS if request.coin_name.lower() in coin["name"].lower()), None)
        if not coin:
            return {"error": "Coin not found","status_code": 400}
        
        return {
            "coin": coin,
            "exchanges": [
                {"name": "Binance", "fees": "0.1%", "availability": "Global"},
                {"name": "Kraken", "fees": "0.16%", "availability": "Most countries"},
                {"name": "KuCoin", "fees": "0.1%", "availability": "Global"}
            ]
        }
    elif request.action == "transfer":
        # Guide for transferring to another exchange
        return {
            "steps": [
                "1. Create an account on the destination exchange",
                "2. Complete KYC verification if required",
                "3. Get the deposit address for your coin",
                "4. Initiate withdrawal from Coinbase to the new address",
                "5. Wait for the transfer to complete (can take 10-60 minutes)"
            ],
            "warnings": [
                "Always verify the deposit address carefully",
                "Start with a small test transfer first",
                "Be aware of network fees for withdrawals"
            ]
        }
    else:
        return {"error": "Invalid action","status_code": 400}

@app.route("/api/kyc-guide", methods=["POST"])
def kyc_guide():
    myclient = dbConnect()
    mydb = myclient["coinpalDb"]
    myCollection=mydb['coinpal']
    
    record = {
        "name": request.json.get("name"),
        "email": request.json.get("email"),
        "phone": request.json.get("phone"),
        "uploadUrl": request.json.get("uploadUrl"),
    }
    print(record)
    rec = myCollection.insert_one(record)
    print("Record inserted with id", rec.inserted_id)
    return {
        "steps": [
            {
                "step": 1,
                "title": "Identity Verification",
                "description": "Required by law to prevent fraud and money laundering.",
                "documents": ["Government ID", "Passport", "Driver's License"]
            },
            {
                "step": 2,
                "title": "Document Upload",
                "description": "Your documents are encrypted and stored securely.",
                "requirements": ["Clear image", "All corners visible", "Not expired"]
            },
            {
                "step": 3,
                "title": "Selfie Verification",
                "description": "Ensures the person submitting documents is the account owner.",
                "requirements": ["Good lighting", "Face clearly visible", "Match ID photo"]
            },
            {
                "step": 4,
                "title": "Address Verification",
                "description": "Confirms your residential address for regulatory compliance.",
                "documents": ["Utility bill", "Bank statement", "Tax document"]
            },
            {
                "step": 5,
                "title": "Transaction Monitoring",
                "description": "Helps protect you from suspicious activities.",
                "benefits": ["Fraud prevention", "Regulatory compliance", "Account security"]
            }
        ],
        "privacy_info": {
            "data_storage": "Your data is encrypted and stored securely",
            "data_sharing": "We only share data when required by law",
            "data_retention": "We retain data only as long as necessary",
            "your_rights": "You have the right to access and delete your data"
        }
    }

@app.route("/api/fraud-alert", methods=["POST"])
def fraud_alert(wallet_address: Optional[str] = None):
    # In a real app, you would analyze transaction patterns
    # For demo purposes, we'll return mock data
    return {
        "risk_score": 65,  # 0-100, higher is more risk
        "alerts": [
            {"type": "Large transfers detected", "severity": "high", "details": "Multiple transfers over $10,000 in the last 30 days"},
            {"type": "Multiple transactions in short time", "severity": "medium", "details": "15 transactions in 24 hours"},
            {"type": "New withdrawal addresses", "severity": "low", "details": "3 new addresses added in the last week"}
        ],
        "recommendations": [
            "Split large transactions into smaller amounts",
            "Verify your identity early to avoid delays",
            "Use whitelisted addresses for withdrawals",
            "Enable 2FA with authenticator app (not SMS)"
        ]
    }

@app.route("/api/support-tickets", methods=["POST"])
def support_tickets(request: SupportTicketRequest):
    # In a real app, you would create and manage support tickets
    # For demo purposes, we'll return mock data
    ticket_id = f"ST{random.randint(100000, 999999)}"
    status = "open"
    
    # Generate AI diagnosis based on issue type
    diagnosis = ""
    action = ""
    
    if "withdrawal" in request.description.lower():
        diagnosis = "Network congestion on Ethereum blockchain. Expected resolution: 2-4 hours."
        action = "No action needed. Your transaction is queued and will process automatically."
    elif "verification" in request.description.lower():
        diagnosis = "Blurry image submitted. New submission required."
        action = "Resubmit with clearer image in good lighting."
    else:
        diagnosis = "We're analyzing your issue. Please provide more details if possible."
        action = "Our team will review your ticket and respond within 24 hours."
    
    new_ticket = {
        "id": ticket_id,
        "issue": request.description,
        "status": status,
        "diagnosis": diagnosis,
        "action": action
    }
    
    return {
        "ticket": new_ticket,
        "existing_tickets": MOCK_SUPPORT_TICKETS
    }

@app.route("/api/wallet-comparison", methods=["POST"])
def wallet_comparison():
    return {
        "custodial": {
            "name": "Coinbase (Custodial)",
            "features": [
                "Coinbase holds your private keys",
                "Easier to use",
                "Less secure",
                "Limited control"
            ],
            "pros": ["User-friendly", "Customer support", "Insurance coverage"],
            "cons": ["Not your keys", "Limited privacy", "Can freeze accounts"]
        },
        "non_custodial": {
            "name": "Coinbase Wallet (Non-Custodial)",
            "features": [
                "You control your private keys",
                "More secure",
                "Full control",
                "More responsibility"
            ],
            "pros": ["Your keys, your coins", "More privacy", "No account freezes"],
            "cons": ["More complex", "No password recovery", "You're responsible for security"]
        },
        "transfer_steps": [
            "1. Install Coinbase Wallet app",
            "2. Create a new wallet",
            "3. Back up your recovery phrase securely",
            "4. Connect your Coinbase account",
            "5. Transfer funds to your new wallet"
        ],
        "security_tips": [
            "Never share your recovery phrase",
            "Store it offline in a secure location",
            "Consider a hardware wallet for large amounts",
            "Enable biometric authentication if available"
        ]
    }

@app.route("/api/security-check", methods=["POST"])
async def security_check(request: SecurityCheckRequest):
    # In a real app, you would perform actual security checks
    # For demo purposes, we'll return mock data
    score = random.randint(60, 95)  # Random score between 60-95
    
    checklist = [
        {"item": "Strong password", "status": random.choice([True, True, True, False])},
        {"item": "2FA enabled", "status": random.choice([True, True, True, False])},
        {"item": "Hardware wallet", "status": random.choice([True, False, False, False])},
        {"item": "Email notifications", "status": random.choice([True, True, True, False])},
        {"item": "Whitelisted addresses", "status": random.choice([True, False, False, False])}
    ]
    
    recommendations = []
    if not checklist[0]["status"]:
        recommendations.append("Enable 2FA with authenticator app (not SMS)")
    if not checklist[2]["status"]:
        recommendations.append("Use a hardware wallet for large holdings")
    if not checklist[4]["status"]:
        recommendations.append("Check for suspicious login attempts")
    
    if not recommendations:
        recommendations = ["Your security is good! Keep it up.", "Consider a hardware wallet for extra security."]
    
    return {
        "score": score,
        "checklist": checklist,
        "recommendations": recommendations,
        "risk_factors": [
            {"factor": "SMS 2FA", "risk": "High", "explanation": "SMS can be intercepted via SIM swap attacks"},
            {"factor": "No hardware wallet", "risk": "Medium", "explanation": "Software wallets are more vulnerable to malware"},
            {"factor": "Reused passwords", "risk": "High", "explanation": "If one service is compromised, others may be at risk"}
        ]
    }

@app.route("/api/v1/portfolio/<string:wallet_address>/insights", methods=["GET"])
def get_wallet_portfolio_insights(wallet_address: str):
    try:
        # Map wallet address to mock user ID for testing
        user_mock_id = "user_001"
        
        # Get enriched portfolio data
        enriched_portfolio = analyzer_global.get_enriched_portfolio(user_mock_id)
        
        response_data = {
            "requested_wallet_address": wallet_address,
            "mock_user_id": user_mock_id,
            "portfolio_composition": {
                "total_value": enriched_portfolio.total_value,
                "assets": {
                    asset_id: {
                        "quantity": holding.quantity,
                        "current_price": holding.current_price,
                        "current_value": holding.current_value
                    }
                    for asset_id, holding in enriched_portfolio.assets.items()
                }
            },
            "performance_metrics": {
                "24h_change": 5.2,  # Mock data
                "7d_change": -2.1,
                "30d_change": 15.3
            }
        }
        
        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "detail": str(e)
        }), 500

@app.route("/api/education", methods=["POST"])
async def education_resources():
    return {
        "topics": [
            {
                "title": "Custodial vs Non-Custodial",
                "description": "Learn the differences and when to use each",
                "content": "Custodial wallets are managed by a third party like Coinbase, while non-custodial wallets give you full control of your private keys.",
                "video_url": "https://example.com/videos/custodial-vs-non-custodial"
            },
            {
                "title": "SIM Swap Protection",
                "description": "How to prevent this common attack vector",
                "content": "SIM swap attacks occur when attackers convince your carrier to transfer your phone number to their device, allowing them to intercept 2FA codes.",
                "video_url": "https://example.com/videos/sim-swap-protection"
            },
            {
                "title": "Private Key Security",
                "description": "Best practices for storing your keys",
                "content": "Never share your private keys or recovery phrase with anyone. Store them offline in a secure location like a safe or safety deposit box.",
                "video_url": "https://example.com/videos/private-key-security"
            },
            {
                "title": "Transaction Privacy",
                "description": "How to maintain privacy while using crypto",
                "content": "Use different addresses for different purposes, avoid linking your identity to your addresses, and consider privacy-focused cryptocurrencies.",
                "video_url": "https://example.com/videos/transaction-privacy"
            }
        ],
        "quiz": [
            {
                "question": "What is the main difference between custodial and non-custodial wallets?",
                "options": ["Cost", "Who controls the private keys", "Supported cryptocurrencies", "User interface"],
                "correct": 1
            },
            {
                "question": "Which is the most secure form of 2FA?",
                "options": ["SMS", "Email", "Authenticator app", "Security questions"],
                "correct": 2
            }
        ]
    }


if __name__ == '__main__':
    app.run(debug=True, port=3001)