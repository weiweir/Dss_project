from geopy.distance import geodesic
import pandas as pd

def calculate_score(row: dict, center: tuple, weights: dict, osm_counts: dict) -> float:
    """
    Tính toán điểm cho một địa điểm dựa trên nhiều yếu tố.

    Args:
        row: Một hàng dữ liệu (dictionary) của địa điểm.
        center: Tuple (lat, lon) của điểm trung tâm.
        weights: Dictionary chứa các trọng số.
        osm_counts: Dictionary chứa số lượng tiện ích từ OSM.

    Returns:
        Điểm số cuối cùng (0-100).
    """
    lat, lon = row['lat'], row['lon']
    
    # Yếu tố khoảng cách: Càng gần trung tâm điểm càng cao
    distance = geodesic((lat, lon), center).meters
    distance_score = 1 / (1 + distance / 100)  # Chuẩn hóa khoảng cách

    # Yếu tố đối thủ: Càng ít đối thủ gần đó điểm càng cao
    competitors = row.get('competitors', 0)
    competitor_score = 1 / (1 + competitors)

    # Yếu tố rating và đa dạng (giả định, cần dữ liệu thực tế từ API)
    # Hiện tại, các giá trị này được truyền vào nhưng chưa có nguồn dữ liệu
    rating = row.get('rating', 3) # Giả sử điểm rating trung bình là 3
    diversity = row.get('diversity', 0.5) # Giả sử độ đa dạng trung bình
    
    # Yếu tố môi trường xung quanh từ OSM
    # Càng nhiều trường học/khu dân cư thì càng tiềm năng
    school_score = osm_counts.get('schools', 0)
    residential_score = osm_counts.get('residential', 0)

    # Tính điểm tổng hợp dựa trên trọng số
    score = (
        weights.get('w_distance', 1) * distance_score +
        weights.get('w_competitors', 1) * competitor_score +
        weights.get('w_rating', 1) * (rating / 5) + # Chuẩn hóa rating về 0-1
        weights.get('w_diversity', 1) * diversity +
        weights.get('w_schools', 1) * (school_score / (1 + school_score)) + # Chuẩn hóa
        weights.get('w_residential', 1) * (residential_score / (1 + residential_score)) # Chuẩn hóa
    )
    
    # Chuẩn hóa điểm cuối cùng về thang 100
    # Tổng các trọng số tối đa có thể là 5*6=30, điểm tối đa ~30
    # Nhân với một hệ số để thang điểm đẹp hơn
    final_score = min(100, score * (100 / (sum(weights.values()) + 1e-6)))

    return round(final_score, 2)

# (Giữ nguyên hàm calculate_score ở trên)

def generate_conclusion(df: pd.DataFrame, osm_counts: dict, radius: int) -> str:
    """
    Tạo kết luận và gợi ý từ kết quả phân tích địa điểm.

    Args:
        df: DataFrame đã sắp xếp chứa các địa điểm và điểm số.
        osm_counts: Dictionary chứa dữ liệu môi trường từ OSM.
        radius: Bán kính tìm kiếm (đơn vị: mét).

    Returns:
        Một đoạn văn bản tổng kết.
    """
    if df.empty:
        return "⚠️ Không có đủ dữ liệu để đưa ra kết luận. Vui lòng thử một khu vực khác."

    conclusion_parts = []
    top_venue = df.iloc[0]
    top_name = top_venue['name']
    top_score = top_venue['score']

    # 1. Địa điểm đứng đầu
    conclusion_parts.append(
        f"🏆 **Địa điểm tiềm năng nhất:** **{top_name}** đạt số điểm cao nhất là **{top_score:.2f}**. "
        f"Đây là vị trí nổi bật nhờ khoảng cách thuận lợi đến trung tâm, mức độ cạnh tranh thấp và nhiều tiện ích xung quanh."
    )

    # 2. Phân tích cụm (nếu có)
    if 'cluster' in df.columns and 'cluster' in top_venue:
        top_cluster_id = top_venue['cluster']
        top_cluster_df = df[df['cluster'] == top_cluster_id]
        avg_score = top_cluster_df['score'].mean()

        conclusion_parts.append(
            f"📊 **Phân tích cụm:** Vị trí trên thuộc **Cụm {top_cluster_id}**, có điểm trung bình là **{avg_score:.2f}**. "
            f"Cụm này đại diện cho khu vực tập trung nhiều địa điểm tiềm năng — rất đáng để khảo sát thêm."
        )

    # 3. Môi trường xung quanh
    residential_count = osm_counts.get('residential', 0)
    school_count = osm_counts.get('schools', 0)

    conclusion_parts.append(
        f"🌆 **Môi trường xung quanh:** Trong bán kính **{radius}m**, có **{residential_count} khu dân cư** "
        f"và **{school_count} trường học**. Đây là lợi thế quan trọng, thể hiện tiềm năng về nguồn khách hàng tại chỗ và vãng lai."
    )

    # 4. Khuyến nghị
    recommendation = (
        f"💡 **Khuyến nghị:** Nên ưu tiên khảo sát thực địa tại **{top_name}**"
    )
    if 'cluster' in df.columns and 'cluster' in top_venue:
        recommendation += f" và các địa điểm khác trong **Cụm {top_cluster_id}**"

    recommendation += (
        ". Cần xem xét thêm các yếu tố thực tế như: giao thông, lưu lượng người qua lại, mặt bằng và mức độ phù hợp với mô hình kinh doanh."
    )
    conclusion_parts.append(recommendation)

    return "\n\n".join(conclusion_parts)
