# market_analyzer.py
import math
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MarketInsight:
    metric_name: str
    value: float
    description: str
    trend: str  # "up", "down", "stable"
    confidence: float


class MarketAnalyzer:
    """Advanced market analysis and insights generation"""

    def __init__(self):
        self.population_density_threshold = {
            "low": 500,
            "medium": 1500,
            "high": 3000
        }

        self.competition_thresholds = {
            "low": 5,
            "medium": 15,
            "high": 30
        }

    def analyze_market_conditions(self, lat: float, lon: float, radius: int,
                                  category_counts: Dict[str, int],
                                  osm_data: Dict[str, int]) -> Dict[str, Any]:
        """
        Comprehensive market condition analysis
        """
        try:
            insights = {
                "maturity_level": self._calculate_market_maturity(category_counts, osm_data),
                "growth_potential": self._calculate_growth_potential(osm_data),
                "competition_intensity": self._analyze_competition_intensity(category_counts),
                "infrastructure_quality": self._assess_infrastructure_quality(osm_data),
                "demographic_profile": self._analyze_demographics(osm_data),
                "economic_indicators": self._analyze_economic_indicators(osm_data),
                "accessibility_score": self._calculate_accessibility_score(osm_data),
                "market_gaps": self._identify_market_gaps(category_counts, osm_data),
                "seasonal_factors": self._analyze_seasonal_factors(lat, lon),
                "risk_factors": self._identify_risk_factors(category_counts, osm_data)
            }

            # Generate summary insights
            insights["summary"] = self._generate_market_summary(insights)
            insights["recommendations"] = self._generate_market_recommendations(insights)

            return insights

        except Exception as e:
            logger.error(f"Market analysis error: {str(e)}")
            return self._get_fallback_insights()

    def _calculate_market_maturity(self, category_counts: Dict[str, int],
                                   osm_data: Dict[str, int]) -> float:
        """Calculate market maturity level (0-1)"""

        # Total business density
        total_businesses = sum(category_counts.values())
        business_density = min(total_businesses / 50, 1.0)  # Normalize to 0-1

        # Infrastructure development
        infrastructure_items = ["office", "hospital", "school", "bank"]
        infrastructure_score = sum(osm_data.get(item, 0) for item in infrastructure_items)
        infrastructure_maturity = min(infrastructure_score / 20, 1.0)

        # Diversity of businesses
        business_diversity = len(category_counts) / 25 if category_counts else 0
        diversity_score = min(business_diversity, 1.0)

        # Weighted average
        maturity = (business_density * 0.4 +
                    infrastructure_maturity * 0.4 +
                    diversity_score * 0.2)

        return round(maturity, 3)

    def _calculate_growth_potential(self, osm_data: Dict[str, int]) -> float:
        """Calculate market growth potential (0-1)"""

        # Development indicators
        development_indicators = {
            "residential": 0.3,  # New residential areas indicate growth
            "office": 0.3,  # Office development
            "subway": 0.2,  # Transport infrastructure
            "hospital": 0.1,  # Healthcare infrastructure
            "school": 0.1  # Educational infrastructure
        }

        growth_score = 0
        for indicator, weight in development_indicators.items():
            count = osm_data.get(indicator, 0)
            normalized_count = min(count / 10, 1.0)  # Normalize
            growth_score += normalized_count * weight

        # Boost for transportation hubs
        if osm_data.get("subway", 0) > 0:
            growth_score *= 1.2

        return min(growth_score, 1.0)

    def _analyze_competition_intensity(self, category_counts: Dict[str, int]) -> Dict[str, Any]:
        """Analyze competition intensity across categories"""

        total_businesses = sum(category_counts.values())

        if total_businesses == 0:
            return {
                "level": "very_low",
                "score": 0.0,
                "dominant_categories": [],
                "market_concentration": 0.0
            }

        # Calculate Herfindahl-Hirschman Index for market concentration
        market_shares = [count / total_businesses for count in category_counts.values()]
        hhi = sum(share ** 2 for share in market_shares)

        # Identify dominant categories
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        dominant_categories = sorted_categories[:3]

        # Competition level
        if total_businesses < self.competition_thresholds["low"]:
            level = "very_low"
        elif total_businesses < self.competition_thresholds["medium"]:
            level = "low"
        elif total_businesses < self.competition_thresholds["high"]:
            level = "medium"
        else:
            level = "high"

        competition_score = min(total_businesses / self.competition_thresholds["high"], 1.0)

        return {
            "level": level,
            "score": competition_score,
            "total_businesses": total_businesses,
            "dominant_categories": dominant_categories,
            "market_concentration": hhi,
            "diversity_index": 1 - hhi  # Higher = more diverse
        }

    def _assess_infrastructure_quality(self, osm_data: Dict[str, int]) -> Dict[str, Any]:
        """Assess infrastructure quality and completeness"""

        infrastructure_components = {
            "transport": {
                "items": ["bus_stop", "subway"],
                "weights": [0.6, 0.4],
                "weight": 0.3
            },
            "healthcare": {
                "items": ["hospital", "pharmacy"],
                "weights": [0.7, 0.3],
                "weight": 0.2
            },
            "education": {
                "items": ["school"],
                "weights": [1.0],
                "weight": 0.2
            },
            "safety": {
                "items": ["police"],
                "weights": [1.0],
                "weight": 0.15
            },
            "recreation": {
                "items": ["park"],
                "weights": [1.0],
                "weight": 0.15
            }
        }

        component_scores = {}
        total_score = 0

        for component, config in infrastructure_components.items():
            component_score = 0
            for item, weight in zip(config["items"], config["weights"]):
                count = osm_data.get(item, 0)
                normalized = min(count / 5, 1.0)  # Normalize to 0-1
                component_score += normalized * weight

            component_scores[component] = component_score
            total_score += component_score * config["weight"]

        # Quality rating
        if total_score >= 0.8:
            quality_rating = "excellent"
        elif total_score >= 0.6:
            quality_rating = "good"
        elif total_score >= 0.4:
            quality_rating = "fair"
        else:
            quality_rating = "poor"

        return {
            "overall_score": total_score,
            "quality_rating": quality_rating,
            "component_scores": component_scores,
            "strengths": [k for k, v in component_scores.items() if v > 0.7],
            "weaknesses": [k for k, v in component_scores.items() if v < 0.3]
        }

    def _analyze_demographics(self, osm_data: Dict[str, int]) -> Dict[str, Any]:
        """Analyze demographic composition"""

        # Estimate population density
        residential_units = osm_data.get("residential", 0)
        estimated_population = residential_units * 50  # Rough estimate

        # Estimate demographic composition
        schools = osm_data.get("school", 0)
        offices = osm_data.get("office", 0)
        hospitals = osm_data.get("hospital", 0)

        # Age composition estimates
        young_families_indicator = schools / max(residential_units, 1)
        working_age_indicator = offices / max(residential_units, 1)
        elderly_indicator = hospitals / max(residential_units, 1)

        # Income level estimation
        office_density = offices / max(residential_units, 1)
        if office_density > 0.3:
            income_level = "high"
        elif office_density > 0.1:
            income_level = "medium"
        else:
            income_level = "low"

        return {
            "estimated_population": estimated_population,
            "population_density_level": self._categorize_population_density(estimated_population),
            "income_level": income_level,
            "demographic_indicators": {
                "young_families": young_families_indicator,
                "working_age": working_age_indicator,
                "elderly": elderly_indicator
            },
            "lifestyle_indicators": {
                "urban_professional": office_density > 0.2,
                "family_oriented": young_families_indicator > 0.1,
                "health_conscious": hospitals > 0
            }
        }

    def _analyze_economic_indicators(self, osm_data: Dict[str, int]) -> Dict[str, Any]:
        """Analyze economic health indicators"""

        # Economic activity indicators
        offices = osm_data.get("office", 0)
        banks = osm_data.get("bank", 0)
        commercial_activity = offices + banks

        # Employment indicators
        employment_hubs = offices + osm_data.get("hospital", 0) + osm_data.get("school", 0)

        # Economic health score
        economic_score = min((commercial_activity + employment_hubs) / 20, 1.0)

        # Economic level categorization
        if economic_score >= 0.7:
            economic_level = "strong"
        elif economic_score >= 0.4:
            economic_level = "moderate"
        else:
            economic_level = "developing"

        return {
            "economic_level": economic_level,
            "economic_score": economic_score,
            "commercial_activity": commercial_activity,
            "employment_hubs": employment_hubs,
            "indicators": {
                "business_density": offices,
                "financial_services": banks,
                "public_sector": osm_data.get("hospital", 0) + osm_data.get("school", 0)
            }
        }

    def _calculate_accessibility_score(self, osm_data: Dict[str, int]) -> Dict[str, Any]:
        """Calculate accessibility and connectivity score"""

        # Transport connectivity
        bus_stops = osm_data.get("bus_stop", 0)
        subway_stations = osm_data.get("subway", 0)

        # Weighted transport score
        transport_score = min((bus_stops * 0.3 + subway_stations * 0.7) / 5, 1.0)

        # Walkability indicators
        pedestrian_infrastructure = osm_data.get("park", 0) + osm_data.get("school", 0)
        walkability_score = min(pedestrian_infrastructure / 5, 1.0)

        # Overall accessibility
        accessibility_score = (transport_score * 0.7 + walkability_score * 0.3)

        # Accessibility rating
        if accessibility_score >= 0.8:
            rating = "excellent"
        elif accessibility_score >= 0.6:
            rating = "good"
        elif accessibility_score >= 0.4:
            rating = "fair"
        else:
            rating = "poor"

        return {
            "overall_score": accessibility_score,
            "rating": rating,
            "transport_score": transport_score,
            "walkability_score": walkability_score,
            "connectivity_features": {
                "bus_connectivity": bus_stops > 0,
                "subway_access": subway_stations > 0,
                "pedestrian_friendly": pedestrian_infrastructure > 2
            }
        }

    def _identify_market_gaps(self, category_counts: Dict[str, int],
                              osm_data: Dict[str, int]) -> List[Dict[str, Any]]:
        """Identify potential market gaps and opportunities"""

        gaps = []

        # Essential services gaps
        if osm_data.get("hospital", 0) == 0:
            gaps.append({
                "type": "healthcare",
                "description": "Thiếu cơ sở y tế",
                "opportunity": "pharmacy",
                "priority": "high"
            })

        if osm_data.get("school", 0) > 2 and category_counts.get("stationery", 0) == 0:
            gaps.append({
                "type": "education_support",
                "description": "Nhiều trường học nhưng thiếu cửa hàng văn phòng phẩm",
                "opportunity": "stationery",
                "priority": "medium"
            })

        # Office area gaps
        if osm_data.get("office", 0) > 3:
            if category_counts.get("cafe", 0) < 2:
                gaps.append({
                    "type": "food_service",
                    "description": "Khu văn phòng thiếu quán cafe",
                    "opportunity": "cafe",
                    "priority": "high"
                })

            if category_counts.get("laundry", 0) == 0:
                gaps.append({
                    "type": "convenience",
                    "description": "Dân văn phòng cần dịch vụ giặt ủi",
                    "opportunity": "laundry",
                    "priority": "medium"
                })

        # Residential area gaps
        residential_density = osm_data.get("residential", 0)
        if residential_density > 5:
            if category_counts.get("grocery", 0) == 0:
                gaps.append({
                    "type": "daily_needs",
                    "description": "Khu dân cư thiếu cửa hàng tạp hóa",
                    "opportunity": "grocery",
                    "priority": "high"
                })

        return gaps

    def _analyze_seasonal_factors(self, lat: float, lon: float) -> Dict[str, Any]:
        """Analyze seasonal business factors for the location"""

        # Vietnam is in tropical zone, seasonal variations are mainly about rain/dry
        # This is a simplified analysis

        seasonal_factors = {
            "climate_zone": "tropical",
            "seasonal_variation": "moderate",
            "peak_seasons": {
                "dry_season": {
                    "months": "Dec-Apr",
                    "businesses_favored": ["ice_cream", "cafe", "tourism_related"],
                    "impact": "positive"
                },
                "rainy_season": {
                    "months": "May-Nov",
                    "businesses_favored": ["indoor_entertainment", "delivery_services"],
                    "impact": "mixed"
                }
            },
            "holiday_impacts": {
                "tet_holiday": {
                    "duration": "1-2 weeks",
                    "impact": "significant_closure",
                    "recovery_time": "1-2 weeks"
                },
                "summer_vacation": {
                    "duration": "2-3 months",
                    "impact": "student_businesses_affected"
                }
            }
        }

        return seasonal_factors

    def _identify_risk_factors(self, category_counts: Dict[str, int],
                               osm_data: Dict[str, int]) -> List[Dict[str, str]]:
        """Identify potential risk factors for business"""

        risks = []

        # Market saturation risks
        total_businesses = sum(category_counts.values())
        if total_businesses > 30:
            risks.append({
                "type": "market_saturation",
                "level": "high",
                "description": "Thị trường có dấu hiệu bão hòa"
            })

        # Infrastructure risks
        if osm_data.get("police", 0) == 0:
            risks.append({
                "type": "security",
                "level": "medium",
                "description": "Thiếu cơ sở an ninh công cộng"
            })

        if osm_data.get("hospital", 0) == 0:
            risks.append({
                "type": "emergency_services",
                "level": "medium",
                "description": "Thiếu cơ sở y tế khẩn cấp"
            })

        # Transport risks
        if osm_data.get("bus_stop", 0) == 0 and osm_data.get("subway", 0) == 0:
            risks.append({
                "type": "accessibility",
                "level": "high",
                "description": "Giao thông công cộng kém"
            })

        return risks

    def _generate_market_summary(self, insights: Dict[str, Any]) -> str:
        """Generate a concise market summary"""

        maturity = insights.get("maturity_level", 0)
        growth = insights.get("growth_potential", 0)
        competition = insights.get("competition_intensity", {}).get("level", "unknown")

        if maturity > 0.7 and growth > 0.6:
            summary = "Thị trường trưởng thành với tiềm năng phát triển tốt"
        elif maturity > 0.5 and competition in ["low", "medium"]:
            summary = "Thị trường ổn định với cơ hội cạnh tranh vừa phải"
        elif growth > 0.7:
            summary = "Thị trường mới nổi với tiềm năng cao"
        elif maturity < 0.3:
            summary = "Thị trường non trẻ, cần thận trọng"
        else:
            summary = "Thị trường cân bằng với cơ hội hỗn hợp"

        return summary

    def _generate_market_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """Generate market-level recommendations"""

        recommendations = []

        # Based on infrastructure
        infra = insights.get("infrastructure_quality", {})
        if infra.get("overall_score", 0) < 0.4:
            recommendations.append("Đầu tư vào các dịch vụ bổ sung hạ tầng thiếu hụt")

        # Based on competition
        competition = insights.get("competition_intensity", {})
        if competition.get("level") == "low":
            recommendations.append("Cơ hội tốt để vào thị trường với ít đối thủ")
        elif competition.get("level") == "high":
            recommendations.append("Cần chiến lược khác biệt hóa mạnh mẽ")

        # Based on market gaps
        gaps = insights.get("market_gaps", [])
        if gaps:
            high_priority_gaps = [g for g in gaps if g.get("priority") == "high"]
            if high_priority_gaps:
                recommendations.append(
                    f"Ưu tiên các ngành: {', '.join([g['opportunity'] for g in high_priority_gaps])}")

        # Based on demographics
        demographics = insights.get("demographic_profile", {})
        if demographics.get("income_level") == "high":
            recommendations.append("Thị trường phù hợp với dịch vụ cao cấp")
        elif demographics.get("income_level") == "low":
            recommendations.append("Tập trung vào dịch vụ giá rẻ, tiện lợi")

        return recommendations

    # Helper methods
    def _categorize_population_density(self, population: int) -> str:
        """Categorize population density level"""
        if population >= self.population_density_threshold["high"]:
            return "high"
        elif population >= self.population_density_threshold["medium"]:
            return "medium"
        else:
            return "low"

    def _get_fallback_insights(self) -> Dict[str, Any]:
        """Return basic insights when analysis fails"""
        return {
            "maturity_level": 0.5,
            "growth_potential": 0.5,
            "competition_intensity": {"level": "medium", "score": 0.5},
            "infrastructure_quality": {"overall_score": 0.5, "quality_rating": "fair"},
            "demographic_profile": {"income_level": "medium"},
            "economic_indicators": {"economic_level": "moderate"},
            "accessibility_score": {"overall_score": 0.5, "rating": "fair"},
            "market_gaps": [],
            "seasonal_factors": {"seasonal_variation": "moderate"},
            "risk_factors": [],
            "summary": "Dữ liệu không đầy đủ để phân tích chi tiết",
            "recommendations": ["Cần thu thập thêm dữ liệu thị trường"]
        }