import utils
import json
from datetime import datetime, timedelta

def verify_final():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
    flight_no = "LJ501" 
    departure = "GMP"
    arrival = "CJU"
    
    print(f"Testing utils.get_flight_operation_info_detail_api for {tomorrow} {flight_no} {departure}->{arrival}...")
    
    result = utils.get_flight_operation_info_detail_api(tomorrow, flight_no, departure, arrival)
    
    # Check if we got the specific flight object (not a list, not error)
    if "FlightNo" in result and result["FlightNo"] == "501":
        print(f"✅ Success: Found flight 501.")
        # Print a few fields to confirm
        print(f"Status: {result.get('Status')}")
        print(f"Departure: {result.get('DepartureDisplayTitle')} {result.get('DepartureActualTime')}")
    else:
        print("❌ Failed or Flight Not Found.")
        print(json.dumps(result, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    verify_final()
