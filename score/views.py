from django.shortcuts import render
from .forms import ScoreForm
from analyzer.logic.geocode import get_coordinates
from analyzer.logic.foursquare_api import get_venues
from analyzer.logic.clustering import cluster_venues
from .logic.score_logic import calculate_score

def score_view(request):
    context = {'form': ScoreForm()}
    if request.method == 'POST':
        form = ScoreForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data['address']
            center = get_coordinates(address)
            if center:
                lat, lon = center
                df = get_venues(lat, lon, radius=1000)
                if len(df) >= 2:
                    df, _ = cluster_venues(df, n_clusters=min(4, len(df)))

                weights = {
                    'w_distance': form.cleaned_data['w_distance'],
                    'w_competitors': form.cleaned_data['w_competitors'],
                    'w_rating': form.cleaned_data['w_rating'],
                    'w_diversity': form.cleaned_data['w_diversity'],
                }
                df['score'] = df.apply(lambda row: calculate_score(row, (lat, lon), weights), axis=1)
                context.update({
                    'form': form,
                    'df': df.to_dict(orient='records'),
                    'center_lat': lat,
                    'center_lon': lon,
                })
    return render(request, 'score/score.html', context)
