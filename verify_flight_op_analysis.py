import utils
import json
from datetime import datetime, timedelta

def test_flight_op_api():
    # Use a route that definitely has flights. GMP->CJU is usually busy.
    date = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
    departure = "GMP"
    arrival = "CJU"
    
    print(f"Testing Flight Operation Info API for {date} {departure}->{arrival}")
    
    result = utils.get_flight_operation_info_api(date, departure, arrival)
    
    # Check if we got a list and print the first item's keys
    if "FlightInfo" in result:
        flights = result["FlightInfo"]
        print(f"Found {len(flights)} flights.")
        if len(flights) > 0:
            first_flight = flights[0]
            print("\nFirst Flight Data Keys:")
            print(list(first_flight.keys()))
            print("\nFirst Flight Data Sample:")
            print(json.dumps(first_flight, indent=4, ensure_ascii=False))
            
            # Check for user requested fields
            required_fields = ["FlightNo", "ArrivalScheduleTitle", "DepartureScheduleTitle", "Status"]
            missing = [f for f in required_fields if f not in first_flight]
            if not missing:
                print("\n✅ All required fields are present.")
            else:
                print(f"\n❌ Missing fields: {missing}")
    else:
        print("No FlightInfo found or error:", result)

if __name__ == "__main__":
    test_flight_op_api()
