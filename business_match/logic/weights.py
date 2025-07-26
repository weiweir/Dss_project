# weights.py

def get_weights():
    """
    Trả về trọng số cho các yếu tố khi tính điểm ngành
    Tổng = 1.0
    """
    return {
        "customer": 0.3,
        "competition": 0.25,
        "safety": 0.15,
        "transport": 0.15,
        "landmark": 0.15
    }
