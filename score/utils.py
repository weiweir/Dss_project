
def normalize_list(lst):
    min_v, max_v = min(lst), max(lst)
    return [(v - min_v) / (max_v - min_v + 1e-6) for v in lst]

def compute_scores(data, weights):
    ratings = [d.get("rating", 0) for d in data]
    checkins = [d.get("checkin_count", 0) for d in data]
    distances = [d.get("distance_to_center", 0) for d in data]
    opponents = [d.get("opponent_count", 0) for d in data]
    populations = [d.get("population_density", 0) for d in data]

    norm_rating = normalize_list(ratings)
    norm_checkin = normalize_list(checkins)
    norm_distance = normalize_list(distances)
    norm_opponent = normalize_list(opponents)
    norm_population = normalize_list(populations)

    scores = []
    for i in range(len(data)):
        score = (
            weights["rating"] * norm_rating[i] +
            weights["checkin"] * norm_checkin[i] +
            weights["distance"] * (1 - norm_distance[i]) +
            weights["opponent"] * (1 - norm_opponent[i]) +
            weights["population"] * norm_population[i]
        )
        scores.append(round(score * 100, 2))
        data[i]["score"] = scores[-1]

    return data
