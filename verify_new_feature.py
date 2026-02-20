import utils
import json
from datetime import datetime, timedelta

def verify_new_api_function():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
    flight_no = "501" # LJ501
    departure = "GMP"
    arrival = "CJU"
    
    print(f"Testing utils.get_flight_operation_info_detail_api for {tomorrow} {flight_no} {departure}->{arrival}...")
    
    result = utils.get_flight_operation_info_detail_api(tomorrow, flight_no, departure, arrival)
    
    print("Result:")
    print(json.dumps(result, indent=4, ensure_ascii=False))

    if "FlightInfo" in result and len(result["FlightInfo"]) > 0:
        print("✅ Success: Flight Info received.")
    else:
        print("⚠️ Warning: No flight info or error.")

if __name__ == "__main__":
    verify_new_api_function()
