# score/utils.py

def normalize_list(lst):
    """Chuẩn hóa danh sách về khoảng [0, 1]"""
    min_v, max_v = min(lst), max(lst)
    return [(v - min_v) / (max_v - min_v + 1e-6) for v in lst]

def compute_scores(data, weights):
    """
    Tính điểm tổng hợp có chuẩn hóa theo trọng số.
    
    data: list of dict, mỗi dict là một địa điểm.
    weights: dict với trọng số từng yếu tố.
    """
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
            weights["distance"] * (1 - norm_distance[i]) +  # gần thì điểm cao
            weights["opponent"] * (1 - norm_opponent[i]) +  # ít đối thủ thì điểm cao
            weights["population"] * norm_population[i]
        )
        scores.append(round(score * 100, 2))
        data[i]["score"] = scores[-1]

    return data
