from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from requests import get
import collections

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


if __name__ == '__main__':
    app.run(debug=True,port=3001)