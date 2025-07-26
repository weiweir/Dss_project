from geopy.distance import geodesic
import pandas as pd

def calculate_score(row: dict, center: tuple, weights: dict, osm_counts: dict) -> float:

    lat, lon = row['lat'], row['lon']
    

    distance = geodesic((lat, lon), center).meters
    distance_score = 1 / (1 + distance / 100)  

    
    competitors = row.get('competitors', 0)
    competitor_score = 1 / (1 + competitors)

    rating = row.get('rating', 3) 
    diversity = row.get('diversity', 0.5) 
    
    school_score = osm_counts.get('schools', 0)
    residential_score = osm_counts.get('residential', 0)

   
    score = (
        weights.get('w_distance', 1) * distance_score +
        weights.get('w_competitors', 1) * competitor_score +
        weights.get('w_rating', 1) * (rating / 5) + 
        weights.get('w_diversity', 1) * diversity +
        weights.get('w_schools', 1) * (school_score / (1 + school_score)) + 
        weights.get('w_residential', 1) * (residential_score / (1 + residential_score)) 
    )
    
    
    final_score = min(100, score * (100 / (sum(weights.values()) + 1e-6)))

    return round(final_score, 2)


def generate_conclusion(df: pd.DataFrame, osm_counts: dict, radius: int) -> str:

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
