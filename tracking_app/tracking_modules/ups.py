import requests
import os
from dotenv import load_dotenv
load_dotenv()

def track_ups(tracking_number):
    # 실제로는 OAuth 인증을 통해 토큰을 먼저 받아야 함 (여기선 간단화)
    token = os.getenv("UPS_ACCESS_TOKEN")
    url = f"https://onlinetools.ups.com/api/track/v1/details/{tracking_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "transId": "test123",
        "transactionSrc": "testing",
        "Content-Type": "application/json"
    }
    res = requests.get(url, headers=headers)
    try:
        data = res.json()
        shipment = data['trackResponse']['shipment'][0]['package'][0]
        return {
            "tracking_number": tracking_number,
            "carrier": "UPS",
            "status": shipment['activity'][0]['status']['description'],
            "ETA": shipment.get("deliveryDate", {}).get("date", "N/A")
        }
    except Exception as e:
        return {
            "tracking_number": tracking_number,
            "carrier": "UPS",
            "status": f"Error: {e}",
            "ETA": "N/A"
        }
