from flask import Flask, jsonify, request
import json
import os
app = Flask(__name__)

MOCK_MARKET_DATA = {
    "BTC": {
        "current_price": 40000,
        "volume_24h": 25000000000,
        "market_cap": 800000000000,
        "price_change_24h": 1500,
        "price_change_percentage_24h": 3.75
    },
    "ETH": {
        "current_price": 2200,
        "volume_24h": 10000000000,
        "market_cap": 260000000000,
        "price_change_24h": 100,
        "price_change_percentage_24h": 4.55
    }
}

@app.route("/api/v1/market/prices", methods=["GET"])
def get_market_prices():
    return jsonify(MOCK_MARKET_DATA)

if __name__ == "__main__":
    app.run(port=5002)