from django.shortcuts import render
from .forms import CombinedScoreForm
from .logic.geocode import get_coordinates
from .logic.foursquare_api import get_venues
from .logic.clustering import cluster_venues
from .logic.osm import get_osm_counts
from .logic.score_logic import calculate_score, generate_conclusion
from .logic.forecast import get_category_params, generate_synthetic_data, train_forecast_model, forecast_venue, MFDM_cal

from geopy.distance import geodesic
import pandas as pd
import os
from django.conf import settings
import json



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

                    # Lấy thông tin category để tìm doanh thu cơ bản + tốc độ tăng trưởng (không thấy mặc định sẽ là 100 triệu/thấng, tốc độ: 0.6)
                    base_revenue = 100
                    rate = 0.06
                    if form.cleaned_data['use_default_revenue'] == True:
                        cat_path = os.path.join(settings.BASE_DIR, "score", "data", "categories.json")
                        
                        print("Checkbox selected")
                    
                    
                        base_revenue, rate = get_category_params(form.cleaned_data['category'], cat_path)
                        
                        print(base_revenue, rate)
                        base_revenue = 100 if base_revenue == None else base_revenue
                        rate = 0.06 if rate == None else rate
                        
                    else:
                        base_revenue = form.cleaned_data['avg_revenue'] if form.cleaned_data['avg_revenue'] != 0 and form.cleaned_data['avg_revenue'] != None else 100
                    
                    rate = form.cleaned_data['rate'] / 100 if form.cleaned_data['rate'] != None else 0.06
                        
                    
                    # Tìm max_score và min_score trong kết quả tìm kiếm để tạo dữ liệu thử
                    scores = []
                    for index, row in df.iterrows():
                        scores.append(row['score'])
                    
                    min_score = min(scores)
                    max_score = max(scores)
                    print(base_revenue, rate, osm_counts['residential'], min_score, max_score)
                    
                    # Tạo dữ liệu thử
                    test_df = generate_synthetic_data(form.cleaned_data['category'], osm_counts['residential'], min_score, max_score, base_revenue, rate)
                    
                    # Train model
                    model, df_cat = train_forecast_model(test_df, form.cleaned_data['category'])
                    
                    # Dự đoán chi phí tháng sau cho từng venue
                    df['estimated_revenue'] = df.apply(
                        lambda row: round(forecast_venue(model, row['score'], osm_counts['residential']), 2), 
                        axis=1
                    )
                    
                    # for index, row in df.iterrows():
                    #     print(f"🏙️ Venue {index + 1}: {row['name']}, score: {row['score']}, estimated_revenue: {row['estimated_revenue']}, cluster:{row['cluster']}")
                    
                    # Lấy kết quả mức độ quan tâm
                    best_cat = form.cleaned_data['best_choice']
                    second_cat = form.cleaned_data['second_choice']
                    third_cat = form.cleaned_data['third_choice']
                    
                    # Tính giá trị doanh thu hoàn hảo
                    max_rev = base_revenue + base_revenue * (rate + 0.1 + 0.05)
                    
                    
                    # Lấy điểm trung bình từng cụm để dự đoán doanh thu cho từng cụm / điểm mở mới trong cụm
                    cluster_avg = df.groupby("cluster")[["score"]].mean().reset_index()
                    cluster_counts = df.groupby("cluster").size().reset_index(name='venue_count')
                    
                    venue_dict = dict(zip(cluster_counts["cluster"], cluster_counts["venue_count"]))

                
                    cluster_forecasts = []

                    for _, row in cluster_avg.iterrows():
                        avg_score = row["score"]
                        cluster_id = row["cluster"]
                        best = None
                        second = None
                        third = None
                        
                        # Dự đoán doanh thu bằng mô hình đã huấn luyện
                        estimated_revenue = forecast_venue(model, avg_score, osm_counts["residential"])
                        # Lấy số lượng của từng venue
                        venue_count = venue_dict.get(cluster_id, 0)
                        
                        # Tính MFDM
                        if best_cat == 'dt':
                            best = estimated_revenue
                        if best_cat == 'ct':
                            best = venue_count
                        if best_cat == 'dg':
                            best = avg_score
                        
                        if second_cat == 'dt':
                            second = estimated_revenue
                        if second_cat == 'ct':
                            second = venue_count
                        if second_cat == 'dg':
                            second = avg_score
                        
                        if third_cat == 'dt':
                            third = estimated_revenue
                        if third_cat == 'ct':
                            third = venue_count
                        if third_cat == 'dg':
                            third = avg_score
                            
                        
                        cluster_forecasts.append({
                            "cluster": cluster_id,
                            "average_score": round(avg_score, 2),
                            "venue_count": venue_count,
                            "forecasted_revenue": round(estimated_revenue, 2),
                            "MFDM_score": MFDM_cal(best, best_cat, second, second_cat, third, third_cat, max_rev)
                        })  

                    forecast_df = pd.DataFrame(cluster_forecasts)
                    print("📈 Forecasted Revenue for Cluster Averages:")
                    print(forecast_df)
                    
                    
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
                        'cluster_df': forecast_df.to_dict(orient='records')
                    })
        context['form'] = form

    return render(request, 'score/score.html', context)