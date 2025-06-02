import os
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv()
USPS_USER_ID = os.getenv("USPS_USER_ID")

def get_usps_tracking_info(tracking_number):
    if not USPS_USER_ID:
        return {"error": "Missing USPS_USER_ID in environment variables."}

    url = "https://secure.shippingapis.com/ShippingAPI.dll"
    xml_request = f"""
    <TrackRequest USERID="{USPS_USER_ID}">
        <TrackID ID="{tracking_number}"></TrackID>
    </TrackRequest>
    """
    params = {
        "API": "TrackV2",
        "XML": xml_request
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        return {
            "tracking_number": tracking_number,
            "carrier": "USPS",
            "status": f"Request failed: {e}",
            "ETA": "N/A"
        }

    try:
        root = ET.fromstring(response.text)
        track_info = root.find("TrackInfo")
        if track_info is None:
            return {
                "tracking_number": tracking_number,
                "carrier": "USPS",
                "status": "No tracking information found",
                "ETA": "N/A"
            }

        status = track_info.findtext("TrackSummary", default="No status found")
        expected_delivery = track_info.findtext("ExpectedDeliveryDate", default="Not available")

        return {
            "tracking_number": tracking_number,
            "carrier": "USPS",
            "status": status,
            "ETA": expected_delivery
        }

    except ET.ParseError:
        return {
            "tracking_number": tracking_number,
            "carrier": "USPS",
            "status": "Invalid XML response",
            "ETA": "N/A"
        }
