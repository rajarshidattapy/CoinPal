from flask import Flask, jsonify, request
import json
import os
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'mock_data', 'asset_news_sentiment.json')

def load_news_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading news data: {e}")
        return {}

@app.route('/api/v1/assets/<asset_id>/news', methods=['GET'])
def get_asset_news(asset_id):
    clean_asset_id = asset_id.split('/')[0].upper()
    news_data = load_news_data()

    if clean_asset_id not in news_data:
        return jsonify({
            "error": f"No news found for asset: {clean_asset_id}",
            "asset_id": clean_asset_id,
            "processed_news": []
        }), 404

    news_list = news_data[clean_asset_id]
    
    try:
        limit = int(request.args.get('limit', 2))
        if limit > 0:
            news_list = news_list[:limit]
    except ValueError:
        return jsonify({"error": "Invalid limit parameter"}), 400

    processed_news = []
    for item in news_list:
        # Get timestamp from either published_at or timestamp field
        timestamp = item.get("published_at") or item.get("timestamp") or datetime.now().isoformat()
        
        news_item = {
            "original_headline": item["headline"],
            "source": item["source"],
            "timestamp": timestamp,
            "url": item.get("url", ""),
            "llm_summary": item["llm_processed"]["summary"],
            "llm_sentiment_label": item["llm_processed"]["sentiment_label"],
            "llm_analysis": item["llm_processed"]["analysis"]
        }
        processed_news.append(news_item)

    return jsonify({
        "asset_id": clean_asset_id,
        "processed_news": processed_news,
        "error": None
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5003))
    print(f"Starting news service on port {port}")
    print(f"Mock data file location: {DATA_FILE}")
    app.run(host="0.0.0.0", port=port, debug=True)