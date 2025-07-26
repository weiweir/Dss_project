# customer_profiles.py

# Ma trận đơn giản: ngành → nhóm khách hàng → điểm phù hợp (0.0–1.0)
# Có thể mở rộng thành file JSON cấu hình nếu cần

CUSTOMER_MATCH_MATRIX = {
    "student": {
        "milk_tea": 1.0,
        "fast_food": 0.9,
        "cafe": 0.8,
        "printing": 0.8,
        "gaming": 0.7,
        "bookstore": 0.6,
    },
    "office": {
        "cafe": 1.0,
        "pharmacy": 0.8,
        "laundry": 0.7,
        "bakery": 0.6,
        "spa": 0.6,
    },
    "family": {
        "grocery": 1.0,
        "pharmacy": 0.9,
        "clothing": 0.8,
        "pet_shop": 0.6,
        "flower_shop": 0.6,
    },
    "tourist": {
        "ice_cream": 1.0,
        "gift_shop": 0.9,
        "spa": 0.8,
        "drink_shop": 0.8,
        "tattoo": 0.7,
    },

}
GENERAL_DEFAULTS = {
    "cafe": 0.7,
    "milk_tea": 0.7,
    "fast_food": 0.7,
    "grocery": 0.8,
    "pharmacy": 0.75,
    "drink_shop": 0.7,
    "bakery": 0.7,
    "clothing": 0.65,
    "electronics": 0.6,
    "spa": 0.55,
    "hair_salon": 0.65,
    "nail": 0.6,
    "flower_shop": 0.6,
    "stationery": 0.55,
    "pet_shop": 0.55,
    "barbershop": 0.5,
    "bookstore": 0.5,
    "laundry": 0.5,
    "repair": 0.5,
    "toy_store": 0.5,
    "ice_cream": 0.5,
    "printing": 0.5,
    "tattoo": 0.4,
    "gaming": 0.4,
    "bike_shop": 0.4,
}

def get_customer_match(business_id, customer_target):
    """
    Trả về điểm phù hợp giữa ngành và khách hàng mục tiêu (0.0 – 1.0)
    """
    if customer_target in CUSTOMER_MATCH_MATRIX:
        return CUSTOMER_MATCH_MATRIX[customer_target].get(business_id, 0.4)
    return GENERAL_DEFAULTS.get(business_id, 0.5)
