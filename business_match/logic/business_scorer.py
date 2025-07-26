# business_scorer.py
from .customer_profiles import get_customer_match
from .weights import get_weights

def score_business(business_id, inputs, context):
    """
    Trả về điểm phù hợp (0–100) và giải thích cho một ngành

    Args:
        business_id (str): ID ngành (vd: 'cafe', 'spa', ...)
        inputs (dict): dữ liệu người dùng: {
            "customer_target": "student",
            "price_level": 2
        }
        context (dict): dữ liệu khu vực: {
            "osm": {...},              # kết quả từ OSM (trường học, công an, bus...)
            "category_counts": {...},  # số lượng các ngành hiện có
        }

    Returns:
        dict: {
            "score": float,
            "reason": str
        }
    """

    # Lấy trọng số
    w = get_weights()

    # Tính điểm từng thành phần
    customer_score = get_customer_match(business_id, inputs["customer_target"])  # 0–1
    competition_score = max(1 - context["category_counts"].get(business_id, 0) / 10, 0)  # ít đối thủ = điểm cao
    safety_score = min(context["osm"].get("police", 0) + context["osm"].get("hospital", 0), 5) / 5
    transport_score = min(context["osm"].get("bus_stop", 0), 5) / 5
    landmark_score = min(
        context["osm"].get("school", 0)
        + context["osm"].get("office", 0)
        + context["osm"].get("park", 0), 10
    ) / 10

    # Tổng hợp điểm
    total = (
        customer_score * w["customer"]
        + competition_score * w["competition"]
        + safety_score * w["safety"]
        + transport_score * w["transport"]
        + landmark_score * w["landmark"]
    )

    score = round(total * 100, 1)

    # Giải thích gợi ý (tùy biến nâng cao sau)
    reason = []
    if competition_score > 0.7:
        reason.append("Ít đối thủ trong khu vực")
    if safety_score > 0.6:
        reason.append("Khu vực an toàn (gần công an, bệnh viện)")
    if customer_score > 0.5:
        reason.append("Phù hợp với nhóm khách hàng mục tiêu")
    if transport_score > 0.5:
        reason.append("Giao thông dễ tiếp cận")
    if landmark_score > 0.5:
        reason.append("Gần địa điểm nổi bật (trường học, văn phòng...)")

    return {
        "score": score,
        "reason": ", ".join(reason) or "Không có đặc điểm nổi bật"
    }
