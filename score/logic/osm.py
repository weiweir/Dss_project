import requests

def get_osm_counts(lat, lon):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node["amenity"="school"](around:1000, {lat}, {lon});
      node["landuse"="residential"](around:1000, {lat}, {lon});
    );
    out count;
    """
    r = requests.get(overpass_url, params={'data': query})
    if r.status_code == 200:
        return r.json()
    return {}
