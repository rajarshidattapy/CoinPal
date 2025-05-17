# CoinPal – Your Crypto Copilot

CoinPal is an AI-powered assistant that helps users navigate the challenges of using Coinbase and other cryptocurrency platforms. It provides solutions to common Coinbase demerits and enhances the overall crypto experience.

## Features

### 1. Fee Analyzer
- Analyzes transaction history to identify high fees
- Compares Coinbase vs. Coinbase Pro fees
- Provides recommendations for fee optimization
- Shows potential savings on transactions

### 2. Altcoin Explorer
- Recommends platforms for altcoins not available on Coinbase
- Compares exchange fees and availability
- Provides step-by-step guides for transferring to other exchanges
- Lists popular altcoins with their availability

### 3. KYC Guide
- Explains the KYC process and its importance
- Provides document requirements and verification steps
- Offers privacy education and transparency
- Guides users through the verification process

### 4. Fraud Alert
- Monitors transaction patterns for suspicious activity
- Provides risk scores and security recommendations
- Alerts users to potential account freezes
- Suggests preventive measures to avoid issues

### 5. Support AI
- AI-powered support for common issues
- Automated diagnosis of transaction problems
- Provides immediate action steps without waiting for human support
- Tracks support ticket history

### 6. Own Your Keys
- Educates users about custodial vs. non-custodial wallets
- Guides users through transferring to self-custody
- Compares security features of different wallet types
- Provides security tips for managing self-custody

### 7. Security Check
- Evaluates account security settings
- Provides security score and recommendations
- Identifies risk factors and vulnerabilities
- Offers checklist for improving security

### 8. Portfolio Insights
- Analyzes portfolio composition and diversification
- Provides market insights and sentiment analysis
- Tracks historical performance
- Offers investment recommendations

### 9. Education Hub
- Educational resources on crypto security
- Video tutorials on key concepts
- Interactive quizzes to test knowledge
- Guides on privacy and security best practices

### 10. Location Check
- Detects user location and regional restrictions
- Provides guidance for users in restricted regions
- Suggests workarounds for regulatory challenges
- Explains regional availability of Coinbase services

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js (for frontend development)
- Coinbase Wallet extension

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/coinpal.git
   cd coinpal
   ```

2. Install backend dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with the following content:
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

4. Start the backend server:
   ```
   cd backend
   python3 app.py
   ```

5. Open the application in your browser:
   ```
   http://localhost:8000
   ```
6. Starting frontend server:
   ```
   cd base-batch
   npm run dev
   ```

## Usage

1. **Connect Your Wallet**: Click the "Connect Wallet" button to link your wallet.

2. **Navigate Features**: Use the tabs at the top to access different features.

3. **Ask Questions**: Use the chatbot at the bottom to ask questions about any crypto-related topic.

4. **Follow Recommendations**: Each feature provides specific recommendations - follow them to improve your crypto experience.

## API Endpoints

The backend provides the following API endpoints:

- `/api/chat` - AI-powered chat responses
- `/api/connect-wallet` - Connect Coinbase wallet
- `/api/check-location` - Check regional availability
- `/api/fee-analysis` - Analyze transaction fees
- `/api/altcoins` - Search and compare altcoins
- `/api/kyc-guide` - KYC process guidance
- `/api/fraud-alert` - Security and fraud alerts
- `/api/support-tickets` - AI support ticket system
- `/api/wallet-comparison` - Compare wallet types
- `/api/security-check` - Security assessment
- `/api/portfolio-insights` - Portfolio analysis
- `/api/education` - Educational resources

## Technologies Used

- **Backend**: FastAPI, Uvicorn
- **Frontend**: HTML, CSS, JavaScript
- **AI**: OpenRouter API
- **Blockchain**: Coinbase Wallet SDK

## Demo Video: https://youtu.be/u4xDu0mQI-c

## Disclaimer

CoinPal is not affiliated with Coinbase or any other cryptocurrency exchange. This tool is provided for educational and informational purposes only. Always do your own research and exercise caution when dealing with cryptocurrencies. 
