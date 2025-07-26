# rules.py

def check_rules(business_id, context, threshold=10):
    """
    Kiểm tra xem ngành có vi phạm luật đặc biệt không.

    Args:
        business_id (str): tên ngành
        context (dict): gồm category_counts, osm...

    Returns:
        list[str]: danh sách cảnh báo hoặc cấm mở
    """

    warnings = []

    # 1. Quá nhiều đối thủ → không nên mở
    num_competitors = context["category_counts"].get(business_id, 0)
    if num_competitors >= threshold:
        warnings.append(f"Khu vực có quá nhiều {business_id} (>{threshold})")

    # 2. Khu vực không an toàn
    safety_sources = context["osm"].get("police", 0) + context["osm"].get("hospital", 0)
    if safety_sources <= 0:
        warnings.append("Khu vực không có cơ sở an toàn (công an, bệnh viện)")

    # 3. Giao thông kém
    if context["osm"].get("bus_stop", 0) < 1:
        warnings.append("Khó tiếp cận giao thông (không có trạm xe buýt)")

    return warnings
