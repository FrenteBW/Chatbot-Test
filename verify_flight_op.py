import utils
import json

def test_flight_op_api():
    date = "20240206"
    departure = "ICN"
    arrival = "NRT"
    
    print(f"Testing Flight Operation Info API for {date} {departure}->{arrival}")
    
    result = utils.get_flight_operation_info_api(date, departure, arrival)
    
    print(json.dumps(result, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    test_flight_op_api()
