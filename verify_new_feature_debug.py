import utils
import json
import requests
from datetime import datetime, timedelta

# Monkey patch utils to debug if needed, or just use the function and catch error
# Actually, let's just inspect the response in the script by manually calling requests if utils hides it, 
# but utils returns {"error": str(e)} so we saw the error from json decoding.

# Let's try to reproduce the call exactly as utils does it, but printing response.text
def debug_new_api_function():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
    flight_no = "501" # LJ501
    departure = "GMP"
    arrival = "CJU"
    
    url = utils.FLIGHT_OPERATION_INFO_API_URL
    payload = {
        "lang": "ko",
        "date": tomorrow,
        "flight": flight_no,
        "departure": departure,
        "arrival": arrival
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(f"DEBUG: Calling {url} with {payload}")
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"DEBUG: Status Code: {response.status_code}")
        print(f"DEBUG: Response Text: {response.text[:500]}") # Print first 500 chars
        
        try:
            json_response = response.json()
            print("DEBUG: JSON parsed successfully.")
        except json.JSONDecodeError:
            print("DEBUG: JSON Decode Failed.")
            
    except Exception as e:
        print(f"DEBUG: Request failed: {e}")

if __name__ == "__main__":
    debug_new_api_function()
