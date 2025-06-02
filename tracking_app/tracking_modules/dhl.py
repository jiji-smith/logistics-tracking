import requests
import os
from dotenv import load_dotenv
load_dotenv()

def track_dhl(tracking_number):
    api_key = os.getenv("DHL_API_KEY")
    url = f"https://api-eu.dhl.com/track/shipments?trackingNumber={tracking_number}"
    headers = {
        "DHL-API-Key": api_key
    }
    res = requests.get(url, headers=headers)
    try:
        data = res.json()
        shipment = data['shipments'][0]
        return {
            "tracking_number": tracking_number,
            "carrier": "DHL",
            "status": shipment['status']['statusCode'],
            "ETA": shipment.get("estimatedTimeOfDelivery", "N/A")
        }
    except Exception as e:
        return {
            "tracking_number": tracking_number,
            "carrier": "DHL",
            "status": f"Error: {e}",
            "ETA": "N/A"
        }
