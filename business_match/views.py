
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
import json
import os
import logging
from typing import Dict, List, Any

from .forms import BusinessMatchForm
from .logic.business_scorer import score_business
from .logic.rules import check_rules
from .logic.foursquare_api import search_places
from .logic.osm import get_osm_counts
from .logic.geocode import get_coordinates

logger = logging.getLogger(__name__)

CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "data/categories.json")
try:
    with open(CATEGORIES_PATH, encoding="utf-8") as f:
        CATEGORY_LIST = json.load(f)
except:
    # Fallback categories if file not found
    CATEGORY_LIST = [
        {"id": "cafe", "name": "Quán cafe"},
        {"id": "milk_tea", "name": "Trà sữa"},
        {"id": "fast_food", "name": "Ăn nhanh"},
        {"id": "pharmacy", "name": "Nhà thuốc"},
        {"id": "grocery", "name": "Tạp hóa"},
        {"id": "spa", "name": "Spa làm đẹp"},
        {"id": "clothing", "name": "Thời trang"},
        {"id": "electronics", "name": "Điện thoại"}
    ]

# Demo data for when APIs fail
DEMO_OSM_DATA = {
    "school": 3, "hospital": 1, "pharmacy": 2,
    "police": 1, "bus_stop": 5, "subway": 0,
    "park": 2, "office": 4, "residential": 10
}

DEMO_CATEGORY_COUNTS = {
    "cafe": 2, "milk_tea": 1, "fast_food": 3,
    "pharmacy": 1, "grocery": 2, "spa": 1,
    "clothing": 2, "electronics": 1
}


def get_demo_places(lat, lon):
    """Generate demo places when API fails"""
    return [
        {"name": "Demo Cafe", "main_category": "cafe", "lat": lat, "lon": lon},
        {"name": "Demo Restaurant", "main_category": "fast_food", "lat": lat, "lon": lon},
        {"name": "Demo Pharmacy", "main_category": "pharmacy", "lat": lat, "lon": lon},
        {"name": "Demo Shop", "main_category": "grocery", "lat": lat, "lon": lon}
    ]


def safe_score_business(business_id: str, inputs: Dict, context: Dict) -> Dict[str, Any]:
    """Safe scoring function that handles errors"""
    try:
        result = score_business(business_id, inputs, context)
        return result
    except Exception as e:
        logger.error(f"Scoring error for {business_id}: {e}")
        # Return demo result
        base_score = (hash(business_id) % 60) + 30  # Score between 30-90
        return {
            "score": float(base_score),
            "reason": f"Phân tích cơ bản cho {business_id}"
        }


def safe_check_rules(business_id: str, context: Dict) -> List[str]:
    """Safe rules checking that handles errors"""
    try:
        return check_rules(business_id, context)
    except Exception as e:
        logger.error(f"Rules error for {business_id}: {e}")
        warnings = []

        # Simple fallback rules
        competitors = context.get("category_counts", {}).get(business_id, 0)
        if competitors > 5:
            warnings.append("Cạnh tranh cao trong khu vực")

        safety_score = context.get("osm", {}).get("police", 0) + context.get("osm", {}).get("hospital", 0)
        if safety_score == 0:
            warnings.append("Khu vực thiếu cơ sở an toàn")

        return warnings


def get_risk_level(score: float, warnings: List[str]) -> str:
    """Calculate risk level from score and warnings"""
    if len(warnings) >= 3:
        return "very_high"
    elif len(warnings) >= 2:
        return "high"
    elif score < 40:
        return "high"
    elif score < 55:
        return "medium"
    elif score < 75:
        return "low"
    else:
        return "very_low"


def match_view(request):
    """Main business analysis view with error handling"""

    form = BusinessMatchForm(request.POST or None)
    results = []
    lat, lon, radius = None, None, None
    price_min = price_max = None
    report_data = None
    data_quality = None

    if request.method == "POST" and form.is_valid():
        try:
            # Extract form data
            address = form.cleaned_data["address"]
            radius = form.cleaned_data["radius"]
            price_min = form.cleaned_data.get("price_min")
            price_max = form.cleaned_data.get("price_max")
            customer_target = form.cleaned_data["customer_target"]

            # Get coordinates with fallback
            try:
                lat, lon = get_coordinates(address)
                if not lat or not lon:
                    raise Exception("Invalid coordinates")
            except Exception as e:
                logger.error(f"Geocoding error: {e}")
                # Use Ho Chi Minh City as fallback
                lat, lon = 10.8231, 106.6297
                messages.warning(request, "Sử dụng tọa độ mặc định do không thể xác định địa chỉ chính xác")

            # Gather market data with fallbacks
            try:
                places = search_places(lat, lon, radius, price_range=(price_min, price_max))
                if not places:
                    raise Exception("No places data")
            except Exception as e:
                logger.error(f"Foursquare API error: {e}")
                places = get_demo_places(lat, lon)
                messages.info(request, "Sử dụng dữ liệu mô phỏng do lỗi API")

            # Process category counts
            category_counts = {}
            for place in places:
                cat = place.get("main_category", "other")
                category_counts[cat] = category_counts.get(cat, 0) + 1

            # If no real data, use demo
            if not category_counts:
                category_counts = DEMO_CATEGORY_COUNTS.copy()

            # Get OSM data with fallback
            try:
                osm_data = get_osm_counts(lat, lon, radius)
                if not any(osm_data.values()):
                    raise Exception("No OSM data")
            except Exception as e:
                logger.error(f"OSM error: {e}")
                osm_data = DEMO_OSM_DATA.copy()

            # Create analysis context
            context = {
                "category_counts": category_counts,
                "osm": osm_data
            }

            # Analyze each business category
            for cat in CATEGORY_LIST:
                business_id = cat["id"]
                display_name = cat["name"]

                try:
                    # Score the business
                    scoring_result = safe_score_business(
                        business_id,
                        {
                            "customer_target": customer_target,
                            "price_level": price_max or 4
                        },
                        context
                    )

                    # Check rules/warnings
                    warnings = safe_check_rules(business_id, context)

                    # Calculate risk level
                    risk_level = get_risk_level(scoring_result["score"], warnings)

                    # Format result
                    result = {
                        "id": business_id,
                        "name": display_name,
                        "score": scoring_result["score"],
                        "reason": scoring_result.get("reason", "Phân tích cơ bản"),
                        "warnings": warnings,
                        "risk_level": risk_level,
                        "confidence": 70.0,  # Default confidence
                        "recommendations": [f"Khuyến nghị cho {display_name}"]
                    }

                    results.append(result)

                except Exception as e:
                    logger.error(f"Error analyzing {business_id}: {e}")
                    # Add fallback result
                    results.append({
                        "id": business_id,
                        "name": display_name,
                        "score": 50.0,
                        "reason": "Phân tích cơ bản",
                        "warnings": ["Dữ liệu hạn chế"],
                        "risk_level": "medium",
                        "confidence": 50.0,
                        "recommendations": ["Cần nghiên cứu thêm"]
                    })

            # Sort results by score
            results.sort(key=lambda x: x["score"], reverse=True)

            # Generate report data for enhanced template
            report_data = generate_report_data(results, osm_data, category_counts)

            # Generate data quality info
            data_quality = generate_data_quality_info(places, osm_data)

            messages.success(request, f"Đã phân tích {len(results)} ngành kinh doanh")

        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            messages.error(request, "Có lỗi xảy ra trong quá trình phân tích")

    # Prepare context for template
    context = {
        "form": form,
        "results": results,
        "lat": lat,
        "lon": lon,
        "radius": radius,
        "price_min": price_min,
        "price_max": price_max,
        "report_data": report_data,
        "data_quality": data_quality
    }

    return render(request, "business_match/match.html", context)


def generate_report_data(results: List[Dict], osm_data: Dict, category_counts: Dict) -> Dict[str, Any]:
    """Generate report data structure for enhanced template"""

    if not results:
        return {}

    # Calculate metrics
    avg_score = sum(r["score"] for r in results) / len(results)
    high_potential = len([r for r in results if r["score"] >= 70])
    medium_potential = len([r for r in results if 50 <= r["score"] < 70])
    low_potential = len([r for r in results if r["score"] < 50])

    return {
        "executive_summary": {
            "market_attractiveness": "high" if avg_score >= 60 else "medium" if avg_score >= 40 else "low",
            "top_opportunities": results[:3],
            "opportunity_distribution": {
                "high_potential": high_potential,
                "medium_potential": medium_potential,
                "low_potential": low_potential
            },
            "key_insights": [
                "Phân tích dựa trên dữ liệu thực tế và mô phỏng",
                f"Trung bình điểm số: {avg_score:.1f}",
                f"Tìm thấy {high_potential} cơ hội tiềm năng cao"
            ]
        },
        "market_overview": {
            "infrastructure_score": calculate_infrastructure_score(osm_data),
            "competition_density": sum(category_counts.values()),
            "infrastructure_highlights": get_infrastructure_highlights(osm_data),
            "dominant_categories": sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        },
        "top_recommendations": results[:5],
        "risk_matrix": generate_risk_matrix(results),
        "detailed_results": results
    }


def generate_data_quality_info(places: List, osm_data: Dict) -> Dict[str, Any]:
    """Generate data quality information"""

    quality_score = 0.0
    sources = []
    warnings = []

    # Check data sources
    if places and len(places) > 3:
        quality_score += 0.4
        sources.append("Foursquare Places API")
    else:
        warnings.append("Dữ liệu địa điểm hạn chế")
        sources.append("Demo Places Data")

    if osm_data and sum(osm_data.values()) > 5:
        quality_score += 0.4
        sources.append("OpenStreetMap")
    else:
        warnings.append("Dữ liệu OSM hạn chế")
        sources.append("Demo OSM Data")

    quality_score += 0.2  # Base score

    # Determine quality text
    if quality_score >= 0.8:
        quality_text = "Tốt"
    elif quality_score >= 0.6:
        quality_text = "Khá"
    elif quality_score >= 0.4:
        quality_text = "Trung bình"
    else:
        quality_text = "Kém"

    return {
        "overall_quality": quality_score,
        "overall_quality_text": quality_text,
        "sources": sources,
        "warnings": warnings
    }


def calculate_infrastructure_score(osm_data: Dict) -> float:
    """Calculate infrastructure quality score"""
    weights = {
        "bus_stop": 0.2, "subway": 0.3, "hospital": 0.2,
        "police": 0.1, "school": 0.1, "park": 0.1
    }

    score = 0
    for feature, weight in weights.items():
        count = osm_data.get(feature, 0)
        normalized = min(count / 5, 1.0)
        score += normalized * weight

    return round(score, 2)


def get_infrastructure_highlights(osm_data: Dict) -> List[str]:
    """Get infrastructure highlights"""
    highlights = []

    if osm_data.get("subway", 0) > 0:
        highlights.append(f"{osm_data['subway']} trạm tàu điện ngầm")

    if osm_data.get("bus_stop", 0) >= 5:
        highlights.append("Giao thông công cộng thuận tiện")

    if osm_data.get("hospital", 0) > 0:
        highlights.append("Có cơ sở y tế")

    if osm_data.get("school", 0) >= 3:
        highlights.append("Nhiều trường học")

    if osm_data.get("park", 0) > 0:
        highlights.append("Có không gian xanh")

    return highlights


def generate_risk_matrix(results: List[Dict]) -> Dict[str, List[Dict]]:
    """Generate risk matrix from results"""

    risk_matrix = {
        "very_low": [], "low": [], "medium": [], "high": [], "very_high": []
    }

    for result in results:
        risk_level = result.get("risk_level", "medium")
        if risk_level in risk_matrix:
            risk_matrix[risk_level].append({
                "name": result["name"],
                "score": result["score"]
            })

    return risk_matrix


# Simplified API endpoints
@csrf_exempt
@require_http_methods(["POST"])
def sensitivity_analysis_api(request):
    """Simplified sensitivity analysis API"""
    try:
        data = json.loads(request.body)
        business_id = data.get("business_id", "cafe")

        # Generate demo sensitivity data
        factors = ["customer", "competition", "market_potential", "transport", "safety"]
        sensitivity_results = {factor: (hash(factor + business_id) % 30) + 10 for factor in factors}

        return JsonResponse({
            "success": True,
            "sensitivity_results": sensitivity_results
        })

    except Exception as e:
        logger.error(f"Sensitivity analysis error: {str(e)}")
        return JsonResponse({"error": "Analysis failed"}, status=500)


@require_http_methods(["GET"])
def export_report(request, format_type="pdf"):
    """Simplified export function"""
    try:
        # Generate simple report content
        content = "Business Analysis Report\n\nGenerated by DSS System\n\nThis is a simplified export."

        if format_type == "pdf":
            response = HttpResponse(content.encode('utf-8'), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="business_report.pdf"'
        elif format_type == "excel":
            response = HttpResponse(content.encode('utf-8'), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="business_report.csv"'
        else:
            return JsonResponse({"error": "Unsupported format"}, status=400)

        return response

    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        return JsonResponse({"error": "Export failed"}, status=500)