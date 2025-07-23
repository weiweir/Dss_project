from geopy.distance import geodesic

def calculate_score(row, center, weights):
    lat, lon = row['lat'], row['lon']
    distance = geodesic((lat, lon), center).meters
    competitors = row.get('competitors', 0)
    rating = row.get('rating', 0)
    diversity = row.get('diversity', 0)

    score = 0
    score += weights['w_distance'] * (1 / (1 + distance))
    score += weights['w_competitors'] * (1 / (1 + competitors))
    score += weights['w_rating'] * rating
    score += weights['w_diversity'] * diversity

    return round(score * 100, 2)
