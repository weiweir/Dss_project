import requests

# 🔐 Foursquare API Key
FOURSQUARE_API_KEY = "YOUR_API_KEY_HERE"  # ← thay bằng key thật của bạn
HEADERS = {
    "Accept": "application/json",
    "Authorization": FOURSQUARE_API_KEY
}

def search_places(lat, lon, radius=1000, price_range=None, limit=50):
    """
    Gọi Foursquare Places API để lấy địa điểm xung quanh (lat, lon)
    Có thể lọc theo khoảng giá (price_range: (min, max))
    """
    url = "https://api.foursquare.com/v3/places/search"
    params = {
        "ll": f"{lat},{lon}",
        "radius": radius,
        "limit": limit,
    }

    # ⛓ Thêm lọc khoảng giá nếu có
    if price_range:
        price_min, price_max = price_range
        if price_min:
            params["min_price"] = price_min
        if price_max:
            params["max_price"] = price_max

    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=15)
        if response.status_code != 200:
            print("Foursquare API error:", response.status_code)
            return []

        data = response.json()
        results = []
        for item in data.get("results", []):
            results.append({
                "name": item.get("name"),
                "main_category": item.get("categories", [{}])[0].get("id", "unknown"),
                "lat": item.get("geocodes", {}).get("main", {}).get("latitude"),
                "lon": item.get("geocodes", {}).get("main", {}).get("longitude"),
            })
        return results

    except Exception as e:
        print("Error calling Foursquare:", e)
        return []
