import requests

def get_osm_counts(lat, lon, radius):
    tags = ["school", "hospital", "pharmacy", "police", "bus_stop", "subway", "park", "office", "residential"]
    tag_filters = "|".join([f'"{t}"' for t in tags])
    overpass_url = "https://overpass-api.de/api/interpreter"

    query = f"""
    [out:json];
    (
      node(around:{radius},{lat},{lon})[amenity~"^{tag_filters}$"];
      way(around:{radius},{lat},{lon})[amenity~"^{tag_filters}$"];
    );
    out center;
    """

    try:
        response = requests.post(overpass_url, data={"data": query}, timeout=20)
        if response.status_code != 200:
            print("Overpass API error:", response.status_code)
            return {tag: 0 for tag in tags}

        data = response.json()
        counts = {tag: 0 for tag in tags}
        for el in data.get("elements", []):
            tag = el.get("tags", {}).get("amenity")
            if tag in counts:
                counts[tag] += 1
        return counts

    except Exception as e:
        print("Error querying OSM:", e)
        return {tag: 0 for tag in tags}