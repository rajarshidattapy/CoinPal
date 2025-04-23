from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import os
from typing import Optional, List, Dict, Any
import requests
from dotenv import load_dotenv
import json
import random
from datetime import datetime, timedelta

load_dotenv()

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Models for API requests
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

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("frontend/templates/index.html") as f:
        return f.read()

@app.post("/api/chat")
async def chat_with_ai(chat_message: ChatMessage):
    try:
        # OpenRouter API endpoint
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Headers for OpenRouter API
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",  # Your app's URL
            "X-Title": "CoinPal"  # Your app's name
        }
        
        # Request body for OpenRouter API
        data = {
            "model": "openai/gpt-3.5-turbo",  # You can change this to other models
            "messages": [
                {"role": "system", "content": "You are CoinPal, a helpful AI assistant for cryptocurrency and Coinbase related questions. You help users with fee analysis, security, KYC, and other crypto-related topics."},
                {"role": "user", "content": chat_message.message}
            ]
        }
        
        # Make request to OpenRouter API
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Parse response
        result = response.json()
        return {"response": result["choices"][0]["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/connect-wallet")
async def connect_wallet(wallet_address: str):
    # Here you would typically verify the wallet signature
    # For now, we'll just return a success message
    return {"status": "success", "message": "Wallet connected successfully"}

@app.post("/api/check-location")
async def check_location(request: LocationRequest):
    # In a real app, you would use the IP address to determine location
    # For demo purposes, we'll just return a mock response
    country = request.country or "United States"
    is_restricted = country in RESTRICTED_LOCATIONS
    
    return {
        "country": country,
        "is_restricted": is_restricted,
        "message": "We've detected you're in a region with limited Coinbase availability. Our AI can help you navigate local regulations and find workarounds." if is_restricted else "Your location is fully supported by Coinbase."
    }

@app.post("/api/fee-analysis")
async def analyze_fees(request: FeeAnalysisRequest):
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

@app.post("/api/altcoins")
async def altcoin_info(request: AltcoinRequest):
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
            raise HTTPException(status_code=404, detail="Coin not found")
        
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
        raise HTTPException(status_code=400, detail="Invalid action")

@app.post("/api/kyc-guide")
async def kyc_guide():
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

@app.post("/api/fraud-alert")
async def fraud_alert(wallet_address: Optional[str] = None):
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

@app.post("/api/support-tickets")
async def support_tickets(request: SupportTicketRequest):
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

@app.post("/api/wallet-comparison")
async def wallet_comparison():
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

@app.post("/api/security-check")
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

@app.post("/api/portfolio-insights")
async def portfolio_insights(wallet_address: Optional[str] = None):
    # In a real app, you would analyze the user's portfolio
    # For demo purposes, we'll return mock data
    return {
        "portfolio": MOCK_PORTFOLIO,
        "recommendations": [
            "Your BTC holdings are over 60% of your portfolio. Consider diversifying.",
            "ETH has strong fundamentals and could be a good addition to your portfolio.",
            "Consider adding some DeFi tokens for higher potential returns (with higher risk)."
        ],
        "market_insights": [
            {"coin": "BTC", "sentiment": "Bullish", "reason": "Institutional adoption increasing"},
            {"coin": "ETH", "sentiment": "Bullish", "reason": "Ethereum 2.0 upgrade complete"},
            {"coin": "SOL", "sentiment": "Neutral", "reason": "Competition with other L1s"}
        ],
        "historical_performance": [
            {"date": "2023-01-01", "value": 10000},
            {"date": "2023-02-01", "value": 12000},
            {"date": "2023-03-01", "value": 11000},
            {"date": "2023-04-01", "value": 13000}
        ]
    }

@app.post("/api/education")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 