from django.shortcuts import render
from .forms import BusinessMatchForm
from .logic.business_scorer import score_business
from .logic.rules import check_rules
from .logic.foursquare_api import search_places
from .logic.osm import get_osm_counts
from .logic.geocode import get_coordinates
import json
import os

CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "data/categories.json")
with open(CATEGORIES_PATH, encoding="utf-8") as f:
    CATEGORY_LIST = json.load(f)

def match_view(request):
    form = BusinessMatchForm(request.POST or None)
    results = []
    lat, lon, radius = None, None, None
    price_min = price_max = None

    if request.method == "POST" and form.is_valid():
        address = form.cleaned_data["address"]
        radius = form.cleaned_data["radius"]
        price_min = form.cleaned_data.get("price_min")
        price_max = form.cleaned_data.get("price_max")
        customer_target = form.cleaned_data["customer_target"]

        lat, lon = get_coordinates(address)
        places = search_places(lat, lon, radius, price_range=(price_min, price_max))

        # Đếm số lượng theo loại
        category_counts = {}
        for p in places:
            cat = p.get("main_category", "other")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        osm = get_osm_counts(lat, lon, radius)

        context = {
            "category_counts": category_counts,
            "osm": osm
        }

        for cat in CATEGORY_LIST:
            business_id = cat["id"]
            display_name = cat["name"]

            result = score_business(
                business_id,
                inputs={
                    "customer_target": customer_target,
                    "price_level": price_max or 4  # fallback nếu không nhập
                },
                context=context
            )

            warnings = check_rules(business_id, context)

            results.append({
                "id": business_id,
                "name": display_name,
                "score": result["score"],
                "reason": result["reason"],
                "warnings": warnings
            })

        results.sort(key=lambda x: x["score"], reverse=True)

    return render(request, "business_match/match.html", {
        "form": form,
        "results": results,
        "lat": lat,
        "lon": lon,
        "radius": radius,
        "price_min": price_min,
        "price_max": price_max
    })
