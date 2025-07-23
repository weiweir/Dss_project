from django.shortcuts import render
from .forms import ScoreForm
from .logic.geocode import get_coordinates
from .logic.foursquare_api import get_venues
from .logic.clustering import cluster_venues
from .logic.osm import get_osm_counts
# Import thêm hàm generate_conclusion
from .logic.score_logic import calculate_score, generate_conclusion
from geopy.distance import geodesic
import pandas as pd

def score_view(request):
    context = {'form': ScoreForm()}
    
    if request.method == 'POST':
        form = ScoreForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data['address']
            radius = form.cleaned_data['radius']
            category = form.cleaned_data['category']
            
            center_coords = get_coordinates(address)

            if center_coords and center_coords[0] is not None:
                lat, lon = center_coords
                
                df = get_venues(lat, lon, radius=radius, category=category)

                if not df.empty:
                    # ... (Toàn bộ logic tính toán điểm số giữ nguyên)
                    competitors = []
                    for index, venue in df.iterrows():
                        count = 0
                        for _, other_venue in df.iterrows():
                            if venue['name'] != other_venue['name']:
                                dist = geodesic((venue['lat'], venue['lon']), (other_venue['lat'], other_venue['lon'])).meters
                                if dist < 200:
                                    count += 1
                        competitors.append(count)
                    df['competitors'] = competitors

                    if len(df) >= 2:
                        n_clusters = min(5, len(df) // 4 + 1)
                        if n_clusters > 1:
                           df, _ = cluster_venues(df, n_clusters=n_clusters)
                        else:
                           df['cluster'] = 0

                    osm_counts = get_osm_counts(lat, lon, radius=radius)
                    weights = {key: val for key, val in form.cleaned_data.items() if key.startswith('w_')}
                    
                    df['score'] = df.apply(
                        lambda row: calculate_score(row.to_dict(), (lat, lon), weights, osm_counts), 
                        axis=1
                    )
                    
                    df = df.sort_values('score', ascending=False).reset_index(drop=True)

                    # --- GỌI HÀM SINH KẾT LUẬN ---
                    conclusion = generate_conclusion(df, osm_counts, radius)
                    # --- HẾT PHẦN GỌI HÀM ---

                    context.update({
                        'df': df.to_dict(orient='records'),
                        'center_lat': lat,
                        'center_lon': lon,
                        'osm_counts': osm_counts,
                        'address': address,
                        'radius': radius,
                        'conclusion': conclusion, # Truyền kết luận sang template
                    })

        context['form'] = form 
            
    return render(request, 'score/score.html', context)