# seasonal_factors.py
import datetime
from typing import Dict, List, Tuple, Any


def get_seasonal_multiplier(customer_target: str = "general",
                            current_month: int = None) -> float:
    """
    Get seasonal multiplier based on customer target and current month

    Args:
        customer_target: Target customer segment
        current_month: Current month (1-12), defaults to current month

    Returns:
        float: Seasonal multiplier (0.5 - 1.5)
    """

    if current_month is None:
        current_month = datetime.datetime.now().month

    # Vietnam seasonal patterns
    seasonal_patterns = {
        "general": {
            1: 0.9,  # January - post-Tet slow period
            2: 0.8,  # February - Tet holiday impact
            3: 1.1,  # March - recovery
            4: 1.2,  # April - spring season
            5: 1.0,  # May - stable
            6: 0.9,  # June - rainy season starts
            7: 0.9,  # July - summer vacation
            8: 0.9,  # August - continued vacation
            9: 1.1,  # September - back to school/work
            10: 1.2,  # October - peak season
            11: 1.3,  # November - best weather
            12: 1.4  # December - holiday shopping
        },

        "student": {
            1: 0.7,  # January - Tet break
            2: 0.6,  # February - Tet holiday
            3: 1.2,  # March - new semester
            4: 1.3,  # April - active period
            5: 1.4,  # May - exam season (stress buying)
            6: 0.8,  # June - summer break starts
            7: 0.7,  # July - vacation
            8: 0.7,  # August - vacation continues
            9: 1.5,  # September - new school year
            10: 1.3,  # October - active studying
            11: 1.2,  # November - midterm season
            12: 1.0  # December - final exams
        },

        "office": {
            1: 0.9,  # January - slow start
            2: 0.7,  # February - Tet holiday
            3: 1.3,  # March - work resumes
            4: 1.2,  # April - Q1 end activities
            5: 1.1,  # May - stable work
            6: 1.0,  # June - mid-year
            7: 1.1,  # July - Q2 end
            8: 1.0,  # August - summer work
            9: 1.2,  # September - back from vacation
            10: 1.3,  # October - Q3 end busy
            11: 1.2,  # November - year-end prep
            12: 1.4  # December - year-end activities
        },

        "family": {
            1: 0.9,  # January - post-holiday budget tight
            2: 0.8,  # February - Tet expenses
            3: 1.1,  # March - back to normal
            4: 1.2,  # April - spring activities
            5: 1.1,  # May - stable
            6: 1.0,  # June - summer prep
            7: 1.3,  # July - summer vacation spending
            8: 1.2,  # August - continued vacation
            9: 1.4,  # September - back to school shopping
            10: 1.2,  # October - stable
            11: 1.1,  # November - holiday prep
            12: 1.5  # December - holiday/gift season
        },

        "tourist": {
            1: 0.8,  # January - low tourist season
            2: 0.7,  # February - Tet period, mostly domestic
            3: 1.1,  # March - weather improves
            4: 1.4,  # April - peak spring tourism
            5: 1.2,  # May - good weather
            6: 0.9,  # June - rainy season starts
            7: 1.0,  # July - summer tourism
            8: 1.0,  # August - continued summer
            9: 1.1,  # September - weather improves
            10: 1.3,  # October - peak tourism season
            11: 1.4,  # November - best weather
            12: 1.5  # December - holiday tourism
        },

        "elderly": {
            1: 0.9,  # January - cold weather
            2: 0.8,  # February - Tet family time
            3: 1.1,  # March - weather improves
            4: 1.3,  # April - pleasant weather
            5: 1.2,  # May - active period
            6: 0.9,  # June - rainy season
            7: 0.8,  # July - hot weather
            8: 0.8,  # August - continued heat
            9: 1.1,  # September - cooler
            10: 1.3,  # October - pleasant weather
            11: 1.4,  # November - best weather for elderly
            12: 1.2  # December - moderate activity
        },

        "young_professional": {
            1: 0.9,  # January - New Year resolutions
            2: 0.7,  # February - Tet break
            3: 1.2,  # March - back to work energy
            4: 1.3,  # April - spring motivation
            5: 1.2,  # May - active lifestyle
            6: 1.0,  # June - mid-year
            7: 1.1,  # July - summer activities
            8: 1.0,  # August - vacation time
            9: 1.3,  # September - productivity boost
            10: 1.2,  # October - fall activities
            11: 1.1,  # November - year-end push
            12: 1.4  # December - holiday spending
        }
    }

    # Get the pattern for the customer target, default to general
    pattern = seasonal_patterns.get(customer_target, seasonal_patterns["general"])

    # Return the multiplier for the current month
    return pattern.get(current_month, 1.0)


def get_business_seasonal_factors(business_id: str) -> Dict[str, float]:
    """
    Get seasonal factors specific to business types

    Args:
        business_id: ID of the business type

    Returns:
        Dict with seasonal multipliers by month
    """

    business_seasonal_patterns = {
        "ice_cream": {
            1: 0.3, 2: 0.4, 3: 0.7, 4: 1.1, 5: 1.3, 6: 1.2,
            7: 1.5, 8: 1.4, 9: 1.1, 10: 0.9, 11: 0.6, 12: 0.5
        },

        "milk_tea": {
            1: 0.8, 2: 0.6, 3: 1.2, 4: 1.3, 5: 1.4, 6: 1.1,
            7: 1.0, 8: 0.9, 9: 1.5, 10: 1.3, 11: 1.2, 12: 1.1
        },

        "spa": {
            1: 1.1, 2: 0.8, 3: 1.2, 4: 1.3, 5: 1.2, 6: 1.0,
            7: 0.9, 8: 0.9, 9: 1.1, 10: 1.3, 11: 1.4, 12: 1.5
        },

        "pharmacy": {
            1: 1.2, 2: 0.9, 3: 1.1, 4: 1.0, 5: 1.1, 6: 1.3,
            7: 1.2, 8: 1.1, 9: 1.0, 10: 1.1, 11: 1.2, 12: 1.3
        },

        "flower_shop": {
            1: 0.8, 2: 1.5, 3: 1.4, 4: 1.2, 5: 1.1, 6: 0.9,
            7: 0.8, 8: 0.9, 9: 1.0, 10: 1.3, 11: 1.2, 12: 1.4
        },

        "clothing": {
            1: 0.9, 2: 0.8, 3: 1.1, 4: 1.3, 5: 1.2, 6: 1.0,
            7: 1.1, 8: 1.0, 9: 1.4, 10: 1.3, 11: 1.2, 12: 1.5
        },

        "bookstore": {
            1: 0.9, 2: 0.7, 3: 1.2, 4: 1.1, 5: 1.0, 6: 0.8,
            7: 0.7, 8: 0.8, 9: 1.5, 10: 1.2, 11: 1.1, 12: 1.0
        },

        "toy_store": {
            1: 0.8, 2: 0.9, 3: 1.0, 4: 1.1, 5: 1.2, 6: 1.4,
            7: 1.3, 8: 1.2, 9: 1.1, 10: 1.0, 11: 1.2, 12: 1.8
        },

        "cafe": {
            1: 0.9, 2: 0.7, 3: 1.1, 4: 1.2, 5: 1.1, 6: 1.0,
            7: 1.0, 8: 1.0, 9: 1.2, 10: 1.3, 11: 1.2, 12: 1.1
        },

        "gaming": {
            1: 1.1, 2: 0.8, 3: 1.0, 4: 1.0, 5: 1.1, 6: 1.2,
            7: 1.4, 8: 1.3, 9: 0.9, 10: 1.0, 11: 1.1, 12: 1.2
        }
    }

    return business_seasonal_patterns.get(business_id, {
        1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0,
        7: 1.0, 8: 1.0, 9: 1.0, 10: 1.0, 11: 1.0, 12: 1.0
    })


def get_holiday_impacts() -> Dict[str, Dict[str, float]]:
    """
    Get impact of major holidays on different business types

    Returns:
        Dict mapping holidays to business impact multipliers
    """

    return {
        "tet_holiday": {  # Lunar New Year (Jan/Feb)
            "flower_shop": 2.5,
            "grocery": 1.8,
            "clothing": 1.6,
            "pharmacy": 0.6,
            "cafe": 0.4,
            "spa": 0.3,
            "gaming": 0.5,
            "office_related": 0.2
        },

        "valentine": {  # February 14
            "flower_shop": 3.0,
            "cafe": 1.5,
            "spa": 1.4,
            "gift_shop": 2.0,
            "jewelry": 2.5
        },

        "women_day": {  # March 8
            "flower_shop": 2.2,
            "spa": 1.8,
            "clothing": 1.4,
            "cafe": 1.3
        },

        "children_day": {  # June 1
            "toy_store": 2.5,
            "ice_cream": 1.8,
            "bookstore": 1.5,
            "gaming": 1.4
        },

        "ghost_festival": {  # 7th lunar month
            "flower_shop": 1.5,
            "pharmacy": 1.2,
            "religious_items": 2.0
        },

        "mid_autumn": {  # 8th lunar month
            "toy_store": 1.8,
            "bakery": 2.0,
            "gift_shop": 1.6
        },

        "christmas": {  # December 25
            "gift_shop": 2.2,
            "cafe": 1.4,
            "clothing": 1.5,
            "toy_store": 1.8,
            "flower_shop": 1.3
        },

        "new_year": {  # January 1
            "cafe": 1.3,
            "clothing": 1.4,
            "gym": 1.8,  # New Year resolutions
            "bookstore": 1.2
        }
    }


def get_weather_impact_factors() -> Dict[str, Dict[str, float]]:
    """
    Get weather impact on different business types

    Returns:
        Dict mapping weather conditions to business impacts
    """

    return {
        "rainy_season": {  # May - October
            "delivery_services": 1.4,
            "indoor_entertainment": 1.3,
            "gaming": 1.2,
            "cafe": 1.1,
            "pharmacy": 1.2,
            "outdoor_dining": 0.7,
            "ice_cream": 0.6,
            "construction": 0.5
        },

        "dry_season": {  # November - April
            "ice_cream": 1.4,
            "outdoor_dining": 1.3,
            "tourism_related": 1.5,
            "car_wash": 1.2,
            "beverage": 1.3,
            "indoor_entertainment": 0.9
        },

        "hot_weather": {  # March - May, extreme heat
            "ice_cream": 1.8,
            "beverage": 1.5,
            "air_conditioning": 1.6,
            "indoor_activities": 1.3,
            "spa": 1.2,
            "outdoor_activities": 0.6,
            "hot_food": 0.8
        },

        "cool_weather": {  # December - February
            "hot_food": 1.4,
            "coffee": 1.3,
            "clothing": 1.2,
            "heating": 1.5,
            "ice_cream": 0.4,
            "cold_drinks": 0.6
        }
    }


def calculate_seasonal_adjustment(business_id: str, customer_target: str = "general",
                                  current_month: int = None) -> float:
    """
    Calculate comprehensive seasonal adjustment combining multiple factors

    Args:
        business_id: Business type ID
        customer_target: Target customer segment
        current_month: Current month (1-12)

    Returns:
        float: Combined seasonal adjustment factor
    """

    if current_month is None:
        current_month = datetime.datetime.now().month

    # Get base customer seasonal factor
    customer_factor = get_seasonal_multiplier(customer_target, current_month)

    # Get business-specific seasonal factor
    business_factors = get_business_seasonal_factors(business_id)
    business_factor = business_factors.get(current_month, 1.0)

    # Get weather impact
    weather_factors = get_weather_impact_factors()
    weather_factor = 1.0

    # Determine weather condition based on month
    if current_month in [5, 6, 7, 8, 9, 10]:  # Rainy season
        rainy_impact = weather_factors["rainy_season"].get(business_id, 1.0)
        weather_factor *= rainy_impact

    if current_month in [3, 4, 5]:  # Hot weather
        hot_impact = weather_factors["hot_weather"].get(business_id, 1.0)
        weather_factor *= hot_impact

    if current_month in [12, 1, 2]:  # Cool weather
        cool_impact = weather_factors["cool_weather"].get(business_id, 1.0)
        weather_factor *= cool_impact

    # Check for holiday impacts
    holiday_factor = get_holiday_impact_for_month(business_id, current_month)

    # Combine factors with weights
    combined_factor = (
            customer_factor * 0.3 +
            business_factor * 0.4 +
            weather_factor * 0.2 +
            holiday_factor * 0.1
    )

    # Ensure factor stays within reasonable bounds
    return max(0.3, min(2.0, combined_factor))


def get_holiday_impact_for_month(business_id: str, month: int) -> float:
    """
    Get holiday impact for a specific month and business

    Args:
        business_id: Business type ID
        month: Month (1-12)

    Returns:
        float: Holiday impact factor
    """

    holiday_impacts = get_holiday_impacts()
    impact_factor = 1.0

    # Map months to holidays (approximate, as some are lunar calendar)
    month_holidays = {
        1: ["new_year"],
        2: ["tet_holiday", "valentine"],
        3: ["women_day"],
        6: ["children_day"],
        8: ["mid_autumn"],  # Approximate
        12: ["christmas"]
    }

    holidays_in_month = month_holidays.get(month, [])

    for holiday in holidays_in_month:
        if holiday in holiday_impacts:
            holiday_impact = holiday_impacts[holiday].get(business_id, 1.0)
            impact_factor = max(impact_factor, holiday_impact)  # Take the strongest impact

    return impact_factor


def get_yearly_seasonal_profile(business_id: str, customer_target: str = "general") -> Dict[int, float]:
    """
    Get complete yearly seasonal profile for a business

    Args:
        business_id: Business type ID
        customer_target: Target customer segment

    Returns:
        Dict mapping months (1-12) to seasonal factors
    """

    profile = {}

    for month in range(1, 13):
        profile[month] = calculate_seasonal_adjustment(business_id, customer_target, month)

    return profile


def get_peak_months(business_id: str, customer_target: str = "general") -> List[Tuple[int, float]]:
    """
    Get peak months for a business type

    Args:
        business_id: Business type ID
        customer_target: Target customer segment

    Returns:
        List of (month, factor) tuples sorted by factor descending
    """

    yearly_profile = get_yearly_seasonal_profile(business_id, customer_target)

    # Sort months by seasonal factor
    sorted_months = sorted(yearly_profile.items(), key=lambda x: x[1], reverse=True)

    return sorted_months


def get_seasonal_recommendations(business_id: str, customer_target: str = "general") -> Dict[str, Any]:
    """
    Get seasonal business recommendations

    Args:
        business_id: Business type ID
        customer_target: Target customer segment

    Returns:
        Dict with seasonal analysis and recommendations
    """

    yearly_profile = get_yearly_seasonal_profile(business_id, customer_target)
    peak_months = get_peak_months(business_id, customer_target)

    # Identify patterns
    best_months = [month for month, factor in peak_months[:3]]
    worst_months = [month for month, factor in peak_months[-3:]]

    # Calculate seasonality index (variation from mean)
    mean_factor = sum(yearly_profile.values()) / 12
    seasonality_index = max(yearly_profile.values()) / min(yearly_profile.values())

    # Determine seasonality level
    if seasonality_index < 1.3:
        seasonality_level = "low"
    elif seasonality_index < 1.8:
        seasonality_level = "moderate"
    else:
        seasonality_level = "high"

    # Generate recommendations
    recommendations = []

    if seasonality_level == "high":
        recommendations.extend([
            "Chuẩn bị kế hoạch tài chính cho mùa thấp điểm",
            "Đa dạng hóa sản phẩm/dịch vụ để giảm biến động theo mùa",
            "Tận dụng tối đa các tháng cao điểm"
        ])

    # Month-specific recommendations
    month_names = {
        1: "Tháng 1", 2: "Tháng 2", 3: "Tháng 3", 4: "Tháng 4",
        5: "Tháng 5", 6: "Tháng 6", 7: "Tháng 7", 8: "Tháng 8",
        9: "Tháng 9", 10: "Tháng 10", 11: "Tháng 11", 12: "Tháng 12"
    }

    best_month_names = [month_names[m] for m in best_months]
    worst_month_names = [month_names[m] for m in worst_months]

    recommendations.extend([
        f"Tháng cao điểm: {', '.join(best_month_names)} - tăng cường marketing và inventory",
        f"Tháng thấp điểm: {', '.join(worst_month_names)} - giảm chi phí, bảo trì thiết bị"
    ])

    # Current month advice
    current_month = datetime.datetime.now().month
    current_factor = yearly_profile[current_month]

    if current_factor > mean_factor * 1.2:
        current_advice = "Tháng hiện tại là thời điểm tốt - tập trung bán hàng"
    elif current_factor < mean_factor * 0.8:
        current_advice = "Tháng hiện tại là thời điểm khó khăn - tối ưu chi phí"
    else:
        current_advice = "Tháng hiện tại ở mức trung bình - duy trì hoạt động ổn định"

    return {
        "seasonality_level": seasonality_level,
        "seasonality_index": round(seasonality_index, 2),
        "mean_factor": round(mean_factor, 2),
        "best_months": best_months,
        "worst_months": worst_months,
        "yearly_profile": yearly_profile,
        "recommendations": recommendations,
        "current_month_advice": current_advice,
        "peak_season_potential": round(max(yearly_profile.values()), 2),
        "low_season_challenge": round(min(yearly_profile.values()), 2)
    }


def get_competitive_seasonal_analysis(business_id: str, competitors: List[str]) -> Dict[str, Any]:
    """
    Analyze seasonal patterns relative to competitors

    Args:
        business_id: Target business type
        competitors: List of competitor business IDs

    Returns:
        Dict with competitive seasonal analysis
    """

    target_profile = get_yearly_seasonal_profile(business_id)
    competitor_profiles = {comp: get_yearly_seasonal_profile(comp) for comp in competitors}

    # Find months where target business has advantage
    advantage_months = []
    disadvantage_months = []

    for month in range(1, 13):
        target_factor = target_profile[month]
        avg_competitor_factor = sum(prof[month] for prof in competitor_profiles.values()) / len(
            competitor_profiles) if competitor_profiles else 1.0

        if target_factor > avg_competitor_factor * 1.1:
            advantage_months.append(month)
        elif target_factor < avg_competitor_factor * 0.9:
            disadvantage_months.append(month)

    return {
        "advantage_months": advantage_months,
        "disadvantage_months": disadvantage_months,
        "competitive_positioning": "seasonal_leader" if len(advantage_months) > 6 else "seasonal_follower",
        "recommendations": [
            f"Tận dụng lợi thế cạnh tranh trong các tháng: {', '.join(map(str, advantage_months))}",
            f"Cần chiến lược đặc biệt cho các tháng: {', '.join(map(str, disadvantage_months))}"
        ]
    }


def forecast_seasonal_demand(business_id: str, customer_target: str = "general",
                             base_demand: float = 100, months_ahead: int = 12) -> List[Dict[str, Any]]:
    """
    Forecast seasonal demand for upcoming months

    Args:
        business_id: Business type ID
        customer_target: Target customer segment
        base_demand: Base demand level (100 = average)
        months_ahead: Number of months to forecast

    Returns:
        List of monthly forecasts
    """

    current_month = datetime.datetime.now().month
    forecasts = []

    for i in range(months_ahead):
        month = ((current_month + i - 1) % 12) + 1
        year_offset = (current_month + i - 1) // 12

        seasonal_factor = calculate_seasonal_adjustment(business_id, customer_target, month)
        forecasted_demand = base_demand * seasonal_factor

        # Add some trend (simplified - could be more sophisticated)
        trend_factor = 1.0 + (year_offset * 0.02)  # 2% annual growth assumption
        forecasted_demand *= trend_factor

        forecasts.append({
            "month": month,
            "year_offset": year_offset,
            "seasonal_factor": round(seasonal_factor, 3),
            "forecasted_demand": round(forecasted_demand, 1),
            "demand_level": "high" if forecasted_demand > base_demand * 1.2 else
            "low" if forecasted_demand < base_demand * 0.8 else "normal"
        })

    return forecasts