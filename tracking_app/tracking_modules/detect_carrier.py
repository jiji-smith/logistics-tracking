def detect_carrier(tracking_number):
    if tracking_number.startswith("1Z"):
        return "ups"
    elif tracking_number.startswith("9") and len(tracking_number) >= 20:
        return "usps"
    elif len(tracking_number) in [12, 15]:
        return "fedex"
    elif tracking_number.startswith("JD") or "DHL" in tracking_number.upper():
        return "dhl"
    else:
        return "unknown"
