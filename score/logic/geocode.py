from geopy.geocoders import Nominatim

def get_coordinates(address):
    geolocator = Nominatim(user_agent="dss_app")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    return None, None
