import os
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()

FEDEX_CLIENT_ID = os.getenv("FEDEX_CLIENT_ID")
FEDEX_CLIENT_SECRET = os.getenv("FEDEX_CLIENT_SECRET")
FEDEX_BASE_URL = "https://apis.fedex.com"
TOKEN_CACHE_FILE = "fedex_token.json"

def get_cached_token():
    if os.path.exists(TOKEN_CACHE_FILE):
        with open(TOKEN_CACHE_FILE, "r") as f:
            data = json.load(f)
            if data["expires_at"] > time.time():
                return data["access_token"]
    return None

def fetch_new_token():
    url = f"{FEDEX_BASE_URL}/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": FEDEX_CLIENT_ID,
        "client_secret": FEDEX_CLIENT_SECRET
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        expires_in = token_data["expires_in"]  # usually 3600

        # Save with expiry timestamp
        with open(TOKEN_CACHE_FILE, "w") as f:
            json.dump({
                "access_token": access_token,
                "expires_at": time.time() + expires_in - 60  # buffer of 1 min
            }, f)

        return access_token
    else:
        print("❌ Failed to get token:", response.text)
        return None

def get_fedex_token():
    token = get_cached_token()
    if token:
        return token
    return fetch_new_token()

def track_fedex(tracking_number):
    token = get_fedex_token()
    if not token:
        return {
            "tracking_number": tracking_number,
            "carrier": "FedEx",
            "status": "Token Error",
            "ETA": "N/A"
        }

    url = f"{FEDEX_BASE_URL}/track/v1/trackingnumbers"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "trackingInfo": [
            {
                "trackingNumberInfo": {
                    "trackingNumber": tracking_number
                }
            }
        ],
        "includeDetailedScans": False
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        try:
            result = response.json()
            info = result["output"]["completeTrackResults"][0]["trackResults"][0]
            return {
                "tracking_number": tracking_number,
                "carrier": "FedEx",
                "status": info.get("latestStatusDetail", {}).get("statusByLocale", "No status"),
                "ETA": info.get("dateAndTimes", [{}])[0].get("dateTime", "Not Available")
            }
        except Exception as e:
            return {
                "tracking_number": tracking_number,
                "carrier": "FedEx",
                "status": f"Parse Error: {str(e)}",
                "ETA": "N/A"
            }
    else:
        return {
            "tracking_number": tracking_number,
            "carrier": "FedEx",
            "status": f"API Error {response.status_code}",
            "ETA": "N/A"
        }

