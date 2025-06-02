import streamlit as st
import pandas as pd
from tracking_modules.detect_carrier import detect_carrier
from tracking_modules.fedex import track_fedex
from tracking_modules.ups import track_ups
from tracking_modules.usps import get_usps_tracking_info  
from tracking_modules.dhl import track_dhl

def get_tracking_info(number):
    carrier = detect_carrier(number)

    if carrier == "fedex":
        return track_fedex(number)
    elif carrier == "ups":
        return track_ups(number)
    elif carrier == "usps":
        return get_usps_tracking_info(number)  
    elif carrier == "dhl":
        return track_dhl(number)
    else:
        return {
            "tracking_number": number,
            "carrier": "Unknown",
            "status": "Not supported or invalid",
            "ETA": "N/A"
        }

def main():
    st.title("📦 Multi-Carrier Tracker (FedEx / UPS / USPS / DHL)")
    numbers = st.text_area("Enter tracking numbers (comma-separated)", "123456789012, 1Z12345E1512345676")

    if st.button("🔍 Track Now"):
        tracking_numbers = [x.strip() for x in numbers.split(",") if x.strip()]
        results = [get_tracking_info(tn) for tn in tracking_numbers]
        df = pd.DataFrame(results)
        st.dataframe(df)

if __name__ == "__main__":
    main()
