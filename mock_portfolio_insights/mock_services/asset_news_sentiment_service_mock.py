from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

# Construct the correct path to the data file
# Assumes this script is in 'mock_services/' and data is in 'mock_services/mock_data/'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'mock_data', 'asset_news_sentiment.json')

asset_news_data = {}
try:
    with open(DATA_FILE, 'r', encoding='utf-8') as f: # Added encoding
        asset_news_data = json.load(f)
    print(f"Successfully loaded mock news data from {DATA_FILE}")
except FileNotFoundError:
    print(f"ERROR: Mock data file not found at {DATA_FILE}. Service will return empty data for news.")
except json.JSONDecodeError:
    print(f"ERROR: Could not decode JSON from {DATA_FILE}. Service will return empty data for news.")
except Exception as e:
    print(f"ERROR: An unexpected error occurred loading mock news data: {e}")

@app.route('/api/v1/assets/<path:asset_id>/news', methods=['GET']) # Use <path:asset_id> if asset_id can contain slashes (e.g. 'uniswap/uni')
def get_asset_news(asset_id):
    # Normalize asset_id (e.g., convert to uppercase if your keys are uppercase)
    # For this example, we'll assume direct match or keys are already normalized in JSON
    normalized_asset_id = asset_id.upper() # Example: if keys in JSON are "BTC", "ETH"

    if normalized_asset_id not in asset_news_data or not asset_news_data[normalized_asset_id]:
        return jsonify({"error": f"No news found for asset: {asset_id}"}), 404

    news_list = asset_news_data[normalized_asset_id]

    try:
        limit_str = request.args.get('limit')
        if limit_str is not None:
            limit = int(limit_str)
            if limit <= 0:
                return jsonify({"error": "Limit parameter must be a positive integer."}), 400
            news_list = news_list[:limit]
    except ValueError:
        return jsonify({"error": "Invalid limit parameter. Must be an integer."}), 400

    return jsonify(news_list), 200

if __name__ == '__main__':
    # Ensure this port matches your .env config for MOCK_ASSET_NEWS_SERVICE_BASE_URL
    # Your .env specified port 5003
    service_port = 5003 
    print(f"Starting Asset News Mock Service on http://localhost:{service_port}")
    app.run(debug=True, port=service_port)