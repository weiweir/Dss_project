from django.shortcuts import render
from .forms import SearchForm
from .logic.foursquare_api import get_venues
from .logic.geocode import get_coordinates
from .logic.clustering import cluster_venues
from django.utils.safestring import mark_safe
import json

def search_view(request):
    df_result = None
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            addr = form.cleaned_data['address']
            lat, lon = get_coordinates(addr)
            if lat and lon:
                df = get_venues(
                    lat, lon,
                    radius=form.cleaned_data['radius'],
                    category=form.cleaned_data['category'],
                    min_price=form.cleaned_data['min_price'] or None,
                    max_price=form.cleaned_data['max_price'] or None
                )
                if len(df) >= 2:
                    k = form.cleaned_data.get('cluster_k') or 3
                    df, _ = cluster_venues(df, n_clusters=min(k, len(df)))

                df_result = df.to_dict(orient='records')
                return render(request, 'analyzer/search.html', {
                    'form': form,
                    'df': df_result,
                    'df_json': mark_safe(json.dumps(df_result)),
                    'center_lat': lat,
                    'center_lon': lon,
                    'radius': form.cleaned_data['radius'],
                })
    else:
        form = SearchForm()
    return render(request, 'analyzer/search.html', {'form': form})
