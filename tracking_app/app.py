import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# .env 파일에서 API 키 로드
load_dotenv()
AVSTACK_KEY = os.getenv("AVSTACK_KEY")

# Carrier 로고 URL
carrier_logos = {
    "FedEx": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/FedEx_Express.svg/120px-FedEx_Express.svg.png",
    "UPS": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/UPS_Logo_Shield_2017.svg/120px-UPS_Logo_Shield_2017.svg.png",
    "USPS": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/USPS_logo.svg/120px-USPS_logo.svg.png"
}

# 기존 더미 트래커 함수 예시 (필요하면 대체)
def track_fedex(tracking_number):
    return {
        "carrier": "FedEx",
        "tracking_number": tracking_number,
        "status": "In Transit",
        "ETA": "2025-06-10T15:00:00-05:00",
        "origin": "Memphis, TN",
        "destination": "Austin, TX"
    }

def track_ups(tracking_number):
    return {
        "carrier": "UPS",
        "tracking_number": tracking_number,
        "status": "Delivered",
        "ETA": "2025-06-09T12:00:00-05:00",
        "origin": "Louisville, KY",
        "destination": "Austin, TX"
    }

def track_usps(tracking_number):
    return {
        "carrier": "USPS",
        "tracking_number": tracking_number,
        "status": "Out for Delivery",
        "ETA": "2025-06-10T09:00:00-05:00",
        "origin": "Dallas, TX",
        "destination": "Round Rock, TX"
    }

def detect_carrier(tracking_number):
    if tracking_number.startswith("1Z"):
        return "UPS"
    elif tracking_number.isdigit() and len(tracking_number) in [20, 22]:
        return "USPS"
    else:
        return "FedEx"

def format_eta(eta_str):
    try:
        dt = datetime.fromisoformat(eta_str)
        return dt.strftime("%m/%d/%Y %H:%M")
    except:
        return eta_str

# Aviationstack API 호출해서 실시간 항공편 정보 가져오기
def track_flight(flight_number):
    url = "http://api.aviationstack.com/v1/flights"
    params = {
        "access_key": AVSTACK_KEY,
        "flight_iata": flight_number
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("data") and len(data["data"]) > 0:
            flight_info = data["data"][0]
            return {
                "Flight": flight_number,
                "Airline": flight_info.get("airline", {}).get("name", "Unknown"),
                "Status": flight_info.get("flight_status", "Unknown"),
                "Departure": format_eta(flight_info.get("departure", {}).get("scheduled", "-")),
                "Arrival": format_eta(flight_info.get("arrival", {}).get("scheduled", "-"))
            }
        else:
            return {
                "Flight": flight_number,
                "Airline": "N/A",
                "Status": "No data found",
                "Departure": "-",
                "Arrival": "-"
            }
    except Exception as e:
        return {
            "Flight": flight_number,
            "Airline": "N/A",
            "Status": f"API error: {e}",
            "Departure": "-",
            "Arrival": "-"
        }

# Streamlit UI 시작
st.set_page_config(page_title="Logistics & Flight Tracker", layout="wide")
st.title("📦 Logistics & Flight Tracker")

tab1, tab2 = st.tabs(["📍 Domestic Tracking", "✈️ Flight Tracking"])

with tab1:
    st.header("Domestic Package Tracking")
    tracking_input = st.text_input("Enter multiple tracking numbers (comma-separated):")

    if tracking_input:
        tracking_numbers = [t.strip() for t in tracking_input.split(",") if t.strip()]
        results = []
        for tn in tracking_numbers:
            carrier = detect_carrier(tn)
            if carrier == "FedEx":
                data = track_fedex(tn)
            elif carrier == "UPS":
                data = track_ups(tn)
            elif carrier == "USPS":
                data = track_usps(tn)
            else:
                continue

            results.append({
                "Tracking Number": data["tracking_number"],
                "Carrier": carrier,
                "Status": data["status"],
                "ETA": format_eta(data["ETA"]),
                "Origin": data["origin"],
                "Destination": data["destination"],
                "Logo": carrier_logos.get(carrier, "")
            })

        df = pd.DataFrame(results)
        st.dataframe(df.drop(columns=["Logo"]))

with tab2:
    st.header("International Flight Tracking")
    flight_input = st.text_input("Enter multiple flight numbers (comma-separated):")

    if flight_input:
        flight_numbers = [f.strip().upper() for f in flight_input.split(",") if f.strip()]
        flight_results = []
        for fn in flight_numbers:
            res = track_flight(fn)
            flight_results.append({
                "Flight": res["Flight"],
                "Airline": res["Airline"],
                "Status": res["Status"],
                "Departure": res["Departure"],
                "Arrival": res["Arrival"]
            })

        st.dataframe(pd.DataFrame(flight_results))
