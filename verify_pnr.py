import utils
import requests
import json

url = utils.PNR_API_URL
payload = {"searchNumber": "X3AJUP"}
headers = {"User-Agent": "Mozilla/5.0"}
resp = requests.post(url, json=payload, headers=headers)
data = resp.json()

print("Top level keys:", list(data.keys()))
if "guestDetails" in data:
    print("Guest 0 keys:", list(data["guestDetails"][0].keys()))
    print("Guest 0 sample:", {k: data["guestDetails"][0].get(k) for k in ["firstName", "lastName", "paxType"]})
if "itineraryDetails" in data:
    print("Itinerary 0 Segments length:", len(data["itineraryDetails"][0].get("itinerarySegments", [])))
    if len(data["itineraryDetails"][0].get("itinerarySegments", [])) > 0:
        print("Segment 0 keys:", list(data["itineraryDetails"][0]["itinerarySegments"][0].keys()))

