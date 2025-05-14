from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from requests import get
import collections
import os
import json
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
collections.Iterable = collections.abc.Iterable
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "supports_credentials": True,
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

RESTRICTED_LOCATIONS = ["China", "Iran", "North Korea", "Cuba", "Syria"]

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


if __name__ == '__main__':
    app.run(debug=True,port=3001)