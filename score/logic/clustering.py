import pandas as pd
from sklearn.cluster import KMeans

def cluster_venues(df: pd.DataFrame, n_clusters: int = 4) -> (pd.DataFrame, KMeans):
    """
    Phân cụm các địa điểm dựa trên tọa độ lat/lon sử dụng K-Means.

    Args:
        df: DataFrame chứa thông tin các địa điểm với cột 'lat' và 'lon'.
        n_clusters: Số lượng cụm mong muốn.

    Returns:
        Một tuple chứa:
        - DataFrame đã được thêm cột 'cluster'.
        - Đối tượng mô hình KMeans đã được huấn luyện.
    """
    if df.empty or 'lat' not in df.columns or 'lon' not in df.columns:
        return df, None

    # Chọn các cột để phân cụm
    coords = df[['lat', 'lon']]

    # Khởi tạo và huấn luyện mô hình K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(coords)

    # Gán nhãn cụm cho mỗi địa điểm
    df['cluster'] = kmeans.labels_
    
    return df, kmeans
