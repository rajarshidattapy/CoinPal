from flask import Flask, jsonify, request
import json
import os
app = Flask(__name__)

MOCK_DATA_PATH = os.path.join(os.path.dirname(__file__), 'mock_data', 'portfolios.json')

def load_portfolios():
    with open(MOCK_DATA_PATH, 'r') as f:
        return json.load(f)

@app.route('/api/v1/portfolio/<user_id>', methods=['GET'])
def get_portfolio(user_id):
    portfolios = load_portfolios()
    portfolio = portfolios.get(user_id)
    if portfolio:
        return jsonify(portfolio)
    return jsonify({"error": "User not found"}), 404

# Add more endpoints later if needed (e.g., POST for transactions)

if __name__ == '__main__':
    # Port 5001 is defined in .env.example for MOCK_PORTFOLIO_SERVICE_BASE_URL
    app.run(debug=True, port=5001)