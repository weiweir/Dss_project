from django.shortcuts import render
from .forms import CombinedScoreForm
from .logic.geocode import get_coordinates
from .logic.foursquare_api import get_venues
from .logic.clustering import cluster_venues
from .logic.osm import get_osm_counts
from .logic.score_logic import calculate_score, generate_conclusion

from geopy.distance import geodesic
import pandas as pd


def score_view(request):
    context = {'form': CombinedScoreForm()}

    if request.method == 'POST':
        form = CombinedScoreForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data['address']
            radius = form.cleaned_data['radius']
            category = form.cleaned_data['category']
            min_price = form.cleaned_data.get('min_price')
            max_price = form.cleaned_data.get('max_price')
            num_clusters = form.cleaned_data.get("num_clusters") or 3

            center_coords = get_coordinates(address)
            if center_coords and center_coords[0] is not None:
                lat, lon = center_coords

                # Gọi Foursquare API
                df = get_venues(lat, lon, radius=radius, category=category, min_price=min_price, max_price=max_price)

                if not df.empty:
                    # Tính số lượng đối thủ
                    competitors = []
                    for index, venue in df.iterrows():
                        count = 0
                        for _, other_venue in df.iterrows():
                            if venue['name'] != other_venue['name']:
                                dist = geodesic((venue['lat'], venue['lon']),
                                                (other_venue['lat'], other_venue['lon'])).meters
                                if dist < 200:
                                    count += 1
                        competitors.append(count)
                    df['competitors'] = competitors

                    # Phân cụm - Sử dụng num_clusters từ form
                    if len(df) >= 2:
                        # Đảm bảo số cụm hợp lý: không vượt quá số địa điểm
                        n_clusters = min(num_clusters, len(df))
                        if n_clusters < 2:
                            n_clusters = 2

                        print(f"🔍 Phân cụm: {len(df)} địa điểm thành {n_clusters} cụm (user chọn: {num_clusters})")

                        df, kmeans_model = cluster_venues(df, n_clusters=n_clusters)

                        # Thông tin debug về phân cụm
                        unique_clusters = df['cluster'].nunique()
                        print(f"✅ Kết quả: {unique_clusters} cụm được tạo")

                    else:
                        df['cluster'] = 0
                        print("⚠️ Chỉ có 1 địa điểm, không thể phân cụm")

                    # Kiểm tra xem có cột cluster không
                    if 'cluster' not in df.columns:
                        print("❌ Lỗi: Không có cột 'cluster' trong DataFrame")
                        df['cluster'] = 0

                    # Lấy dữ liệu OSM
                    osm_counts = get_osm_counts(lat, lon, radius=radius)

                    # Trọng số
                    weights = {key: val for key, val in form.cleaned_data.items() if key.startswith('w_')}

                    # Tính điểm DSS
                    df['score'] = df.apply(
                        lambda row: calculate_score(row.to_dict(), (lat, lon), weights, osm_counts), axis=1
                    )
                    df = df.sort_values('score', ascending=False).reset_index(drop=True)

                    # Debug: In thông tin cụm
                    if 'cluster' in df.columns:
                        cluster_info = df.groupby('cluster').agg({
                            'name': 'count',
                            'score': 'mean'
                        }).round(2)
                        print("📊 Thông tin cụm:")
                        print(cluster_info)

                    # Sinh kết luận
                    conclusion = generate_conclusion(df, osm_counts, radius)

                    # Gợi ý cụm nên mở: cụm có điểm trung bình cao nhất
                    if 'cluster' in df.columns and len(df) > 0:
                        best_cluster_id = df.groupby('cluster')['score'].mean().idxmax()
                        best_cluster_score = df[df['cluster'] == best_cluster_id]['score'].mean()
                        recommended_cluster = {
                            'cluster_id': best_cluster_id,
                            'avg_score': round(best_cluster_score, 2),
                            'num_locations': len(df[df['cluster'] == best_cluster_id])
                        }
                    else:
                        recommended_cluster = None

                    context.update({
                        'df': df.to_dict(orient='records'),
                        'center_lat': lat,
                        'center_lon': lon,
                        'osm_counts': osm_counts,
                        'address': address,
                        'radius': radius,
                        'conclusion': conclusion,
                        'recommended_cluster': recommended_cluster,
                    })
        context['form'] = form

    return render(request, 'score/score.html', context)