import requests, pandas as pd

API_KEY = "Bearer JR4BE2E5QYVC1OB3HHNWWRTFZPN0OCIUDLOEU1VCCOSMMIZB"

def get_venues(lat, lon, radius=1000, category=None, min_price=None, max_price=None):
    url = "https://places-api.foursquare.com/places/search"
    headers = {
        "accept": "application/json",
        "X-Places-Api-Version": "2025-06-17",
        "authorization": API_KEY
    }
    params = {"ll": f"{lat},{lon}", "radius": radius, "limit": 50}
    if category: params["fsq_category_ids"] = category
    if min_price: params["min_price"] = min_price
    if max_price: params["max_price"] = max_price

    resp = requests.get(url, headers=headers, params=params)
    data = resp.json()
    venues = [{
        "name": v["name"], "lat": v["latitude"], "lon": v["longitude"],
        "address": v.get("location", {}).get("formatted_address", "")
    } for v in data.get("results", [])]
    return pd.DataFrame(venues)
