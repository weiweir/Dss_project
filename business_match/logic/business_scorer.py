# enhanced_business_scorer.py
import math
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from .customer_profiles import get_customer_match
from .weights import get_weights, get_business_weights
from .market_analyzer import MarketAnalyzer
from .seasonal_factors import get_seasonal_multiplier
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class BusinessType(Enum):
    FOOD_BEVERAGE = "food_beverage"
    RETAIL = "retail"
    SERVICE = "service"
    ENTERTAINMENT = "entertainment"


@dataclass
class ScoringResult:
    score: float
    confidence: float
    reasons: List[str]
    warnings: List[str]
    sensitivity_analysis: Dict[str, float]
    recommendations: List[str]


@dataclass
class MarketContext:
    osm_data: Dict[str, int]
    category_counts: Dict[str, int]
    population_density: float
    income_level: str
    foot_traffic_score: float
    rent_level: int
    seasonal_factor: float


class AdvancedBusinessScorer:
    def __init__(self):
        self.market_analyzer = MarketAnalyzer()
        self.cache_timeout = 3600  # 1 hour

    def score_business(self, business_id: str, inputs: Dict, context: Dict) -> ScoringResult:
        """
        Enhanced scoring with multiple models and sensitivity analysis
        """
        try:
            # Build enhanced market context
            market_context = self._build_market_context(context, inputs)

            # Get business-specific weights
            weights = get_business_weights(business_id)

            # Calculate component scores using advanced algorithms
            scores = self._calculate_component_scores(business_id, inputs, market_context)

            # Apply business type specific logic
            business_type = self._get_business_type(business_id)
            scores = self._apply_business_type_modifiers(scores, business_type, market_context)

            # Calculate final score with confidence interval
            final_score, confidence = self._calculate_weighted_score(scores, weights)

            # Generate explanations and recommendations
            reasons = self._generate_reasons(scores, weights)
            warnings = self._generate_warnings(business_id, market_context, scores)
            recommendations = self._generate_recommendations(business_id, scores, market_context)

            # Sensitivity analysis
            sensitivity = self._run_sensitivity_analysis(business_id, inputs, market_context, weights)

            return ScoringResult(
                score=round(final_score, 1),
                confidence=round(confidence, 2),
                reasons=reasons,
                warnings=warnings,
                sensitivity_analysis=sensitivity,
                recommendations=recommendations
            )

        except Exception as e:
            logger.error(f"Error scoring business {business_id}: {str(e)}")
            return self._create_error_result()

    def _build_market_context(self, context: Dict, inputs: Dict) -> MarketContext:
        """Build enhanced market context with additional data"""

        # Calculate population density from OSM data
        residential_count = context["osm"].get("residential", 0)
        office_count = context["osm"].get("office", 0)
        population_density = self._estimate_population_density(residential_count, office_count)

        # Estimate income level from area characteristics
        income_level = self._estimate_income_level(context["osm"])

        # Calculate foot traffic score
        foot_traffic = self._calculate_foot_traffic_score(context["osm"])

        # Get seasonal factor
        seasonal_factor = get_seasonal_multiplier(inputs.get("customer_target", "general"))

        return MarketContext(
            osm_data=context["osm"],
            category_counts=context["category_counts"],
            population_density=population_density,
            income_level=income_level,
            foot_traffic_score=foot_traffic,
            rent_level=inputs.get("price_level", 2),
            seasonal_factor=seasonal_factor
        )

    def _calculate_component_scores(self, business_id: str, inputs: Dict,
                                    market_context: MarketContext) -> Dict[str, float]:
        """Calculate enhanced component scores"""

        scores = {}

        # Customer match score (enhanced with demographic data)
        base_customer_score = get_customer_match(business_id, inputs["customer_target"])
        demographic_multiplier = self._get_demographic_multiplier(
            business_id, market_context.income_level, market_context.population_density
        )
        scores["customer"] = min(base_customer_score * demographic_multiplier, 1.0)

        # Competition score (enhanced with market saturation analysis)
        scores["competition"] = self._calculate_competition_score(business_id, market_context)

        # Location scores
        scores["safety"] = self._calculate_safety_score(market_context.osm_data)
        scores["transport"] = self._calculate_transport_score(market_context.osm_data)
        scores["landmark"] = self._calculate_landmark_score(market_context.osm_data)

        # New scoring components
        scores["market_potential"] = self._calculate_market_potential(business_id, market_context)
        scores["operational_feasibility"] = self._calculate_operational_feasibility(business_id, market_context)
        scores["financial_viability"] = self._calculate_financial_viability(business_id, market_context)

        # Apply seasonal factor
        for key in scores:
            scores[key] *= market_context.seasonal_factor

        return scores

    def _calculate_competition_score(self, business_id: str, market_context: MarketContext) -> float:
        """Enhanced competition analysis"""

        competitor_count = market_context.category_counts.get(business_id, 0)

        # Market capacity analysis
        market_capacity = self._estimate_market_capacity(business_id, market_context)

        if market_capacity == 0:
            return 0.0

        # Saturation ratio with sigmoid function for smooth transition
        saturation_ratio = competitor_count / market_capacity
        competition_score = 1 / (1 + math.exp(5 * (saturation_ratio - 0.5)))

        # Adjust for business type competition intensity
        business_type = self._get_business_type(business_id)
        intensity_modifier = {
            BusinessType.FOOD_BEVERAGE: 0.8,  # High competition
            BusinessType.RETAIL: 0.9,
            BusinessType.SERVICE: 1.1,  # Lower competition
            BusinessType.ENTERTAINMENT: 0.7
        }.get(business_type, 1.0)

        return min(competition_score * intensity_modifier, 1.0)

    def _estimate_market_capacity(self, business_id: str, market_context: MarketContext) -> float:
        """Estimate market capacity for a business type"""

        # Base capacity per 1000 people
        capacity_ratios = {
            "cafe": 2.5, "milk_tea": 3.0, "fast_food": 2.0,
            "pharmacy": 0.5, "grocery": 1.0, "spa": 0.8,
            "clothing": 1.5, "electronics": 0.3
        }

        base_ratio = capacity_ratios.get(business_id, 1.0)

        # Adjust for population density and income
        density_factor = min(market_context.population_density / 1000, 2.0)

        income_multipliers = {"low": 0.7, "medium": 1.0, "high": 1.3}
        income_factor = income_multipliers.get(market_context.income_level, 1.0)

        return base_ratio * density_factor * income_factor

    def _calculate_market_potential(self, business_id: str, market_context: MarketContext) -> float:
        """Calculate market growth potential"""

        # Factors affecting market potential
        population_growth_factor = min(market_context.population_density / 500, 1.0)

        # Economic indicators
        economic_factor = {
            "low": 0.6, "medium": 0.8, "high": 1.0
        }.get(market_context.income_level, 0.8)

        # Infrastructure development (transport, offices)
        infrastructure_score = min(
            (market_context.osm_data.get("office", 0) +
             market_context.osm_data.get("bus_stop", 0)) / 10, 1.0
        )

        return (population_growth_factor + economic_factor + infrastructure_score) / 3

    def _calculate_operational_feasibility(self, business_id: str, market_context: MarketContext) -> float:
        """Calculate how feasible it is to operate this business"""

        # Labor availability (estimated from residential areas)
        labor_score = min(market_context.osm_data.get("residential", 0) / 20, 1.0)

        # Supply chain accessibility (transport links)
        supply_chain_score = min(
            (market_context.osm_data.get("bus_stop", 0) +
             market_context.osm_data.get("subway", 0) * 2) / 10, 1.0
        )

        # Regulatory environment (presence of similar businesses indicates approval)
        similar_businesses = sum(market_context.category_counts.values())
        regulatory_score = min(similar_businesses / 50, 1.0) if similar_businesses > 0 else 0.5

        return (labor_score + supply_chain_score + regulatory_score) / 3

    def _calculate_financial_viability(self, business_id: str, market_context: MarketContext) -> float:
        """Calculate financial viability based on costs and revenue potential"""

        # Revenue potential (based on foot traffic and income level)
        revenue_potential = market_context.foot_traffic_score * {
            "low": 0.7, "medium": 1.0, "high": 1.4
        }.get(market_context.income_level, 1.0)

        # Cost factors (rent, labor)
        rent_factor = 1.0 - (market_context.rent_level - 1) * 0.15  # Higher rent = lower score

        # Business-specific profit margins
        profit_margins = {
            "cafe": 0.15, "milk_tea": 0.25, "fast_food": 0.12,
            "pharmacy": 0.20, "grocery": 0.08, "spa": 0.30
        }
        margin_factor = profit_margins.get(business_id, 0.15) * 5  # Normalize to 0-1

        return min((revenue_potential + rent_factor + margin_factor) / 3, 1.0)

    def _calculate_weighted_score(self, scores: Dict[str, float],
                                  weights: Dict[str, float]) -> Tuple[float, float]:
        """Calculate weighted final score with confidence interval"""

        total_score = 0
        total_weight = 0
        variance = 0

        for component, weight in weights.items():
            if component in scores:
                score = scores[component]
                total_score += score * weight
                total_weight += weight

                # Simple variance calculation for confidence
                variance += weight * (score - 0.5) ** 2

        final_score = (total_score / total_weight) * 100 if total_weight > 0 else 0

        # Confidence based on variance (lower variance = higher confidence)
        confidence = max(0.5, 1 - variance)

        return final_score, confidence

    def _run_sensitivity_analysis(self, business_id: str, inputs: Dict,
                                  market_context: MarketContext,
                                  weights: Dict[str, float]) -> Dict[str, float]:
        """Run sensitivity analysis by varying key parameters"""

        sensitivity = {}
        base_scores = self._calculate_component_scores(business_id, inputs, market_context)
        base_score = sum(base_scores[k] * weights.get(k, 0) for k in base_scores)

        # Test sensitivity to weight changes
        for component in weights:
            if component in base_scores:
                # Increase weight by 20%
                modified_weights = weights.copy()
                modified_weights[component] *= 1.2

                # Renormalize weights
                total_weight = sum(modified_weights.values())
                modified_weights = {k: v / total_weight for k, v in modified_weights.items()}

                modified_score = sum(base_scores[k] * modified_weights.get(k, 0) for k in base_scores)

                sensitivity[component] = abs(modified_score - base_score) / base_score * 100

        return sensitivity

    def _generate_recommendations(self, business_id: str, scores: Dict[str, float],
                                  market_context: MarketContext) -> List[str]:
        """Generate actionable recommendations"""

        recommendations = []

        if scores.get("competition", 0) < 0.3:
            recommendations.append("Thị trường đã bão hòa - cân nhắc pivot sang ngành liên quan")

        if scores.get("customer", 0) > 0.8:
            recommendations.append("Nhóm khách hàng mục tiêu rất phù hợp - tập trung vào marketing")

        if scores.get("transport", 0) < 0.4:
            recommendations.append("Giao thông không thuận lợi - cân nhắc dịch vụ delivery")

        if scores.get("financial_viability", 0) < 0.5:
            recommendations.append("Khả năng sinh lời thấp - xem xét mô hình chi phí thấp hơn")

        if market_context.foot_traffic_score > 0.7:
            recommendations.append("Lưu lượng khách cao - tận dụng cho upselling")

        return recommendations

    # Helper methods
    def _get_business_type(self, business_id: str) -> BusinessType:
        type_mapping = {
            "cafe": BusinessType.FOOD_BEVERAGE,
            "milk_tea": BusinessType.FOOD_BEVERAGE,
            "fast_food": BusinessType.FOOD_BEVERAGE,
            "clothing": BusinessType.RETAIL,
            "electronics": BusinessType.RETAIL,
            "spa": BusinessType.SERVICE,
            "pharmacy": BusinessType.SERVICE,
            "gaming": BusinessType.ENTERTAINMENT
        }
        return type_mapping.get(business_id, BusinessType.SERVICE)

    def _estimate_population_density(self, residential: int, office: int) -> float:
        return (residential * 50 + office * 100)  # Rough estimate

    def _estimate_income_level(self, osm_data: Dict[str, int]) -> str:
        # Simple heuristic based on infrastructure
        score = (osm_data.get("office", 0) * 2 +
                 osm_data.get("park", 0) +
                 osm_data.get("hospital", 0) * 3)

        if score > 15:
            return "high"
        elif score > 5:
            return "medium"
        else:
            return "low"

    def _calculate_foot_traffic_score(self, osm_data: Dict[str, int]) -> float:
        traffic_sources = (
                osm_data.get("bus_stop", 0) * 0.3 +
                osm_data.get("subway", 0) * 0.5 +
                osm_data.get("office", 0) * 0.2 +
                osm_data.get("school", 0) * 0.4
        )
        return min(traffic_sources / 10, 1.0)

    def _get_demographic_multiplier(self, business_id: str, income_level: str,
                                    population_density: float) -> float:
        # Business-specific demographic preferences
        income_preferences = {
            "spa": {"high": 1.3, "medium": 1.0, "low": 0.6},
            "milk_tea": {"high": 1.1, "medium": 1.2, "low": 0.9},
            "grocery": {"high": 0.9, "medium": 1.0, "low": 1.2}
        }

        return income_preferences.get(business_id, {}).get(income_level, 1.0)

    def _apply_business_type_modifiers(self, scores: Dict[str, float],
                                       business_type: BusinessType,
                                       market_context: MarketContext) -> Dict[str, float]:
        """Apply business type specific modifiers"""

        if business_type == BusinessType.FOOD_BEVERAGE:
            # Food businesses more sensitive to foot traffic
            scores["transport"] *= 1.2
            scores["landmark"] *= 1.1
        elif business_type == BusinessType.SERVICE:
            # Service businesses less dependent on foot traffic
            scores["transport"] *= 0.9
            scores["customer"] *= 1.2

        return scores

    def _calculate_safety_score(self, osm_data: Dict[str, int]) -> float:
        safety_sources = osm_data.get("police", 0) + osm_data.get("hospital", 0)
        return min(safety_sources / 3, 1.0)

    def _calculate_transport_score(self, osm_data: Dict[str, int]) -> float:
        transport_score = (osm_data.get("bus_stop", 0) +
                           osm_data.get("subway", 0) * 2)
        return min(transport_score / 5, 1.0)

    def _calculate_landmark_score(self, osm_data: Dict[str, int]) -> float:
        landmarks = (osm_data.get("school", 0) +
                     osm_data.get("office", 0) +
                     osm_data.get("park", 0))
        return min(landmarks / 10, 1.0)

    def _generate_reasons(self, scores: Dict[str, float],
                          weights: Dict[str, float]) -> List[str]:
        reasons = []

        # Sort by weighted contribution
        weighted_scores = [(k, v * weights.get(k, 0)) for k, v in scores.items()]
        weighted_scores.sort(key=lambda x: x[1], reverse=True)

        reason_templates = {
            "customer": "Phù hợp tốt với nhóm khách hàng mục tiêu",
            "competition": "Mức độ cạnh tranh thuận lợi",
            "market_potential": "Tiềm năng thị trường tích cực",
            "financial_viability": "Khả năng sinh lời khả quan",
            "safety": "Khu vực an toàn",
            "transport": "Giao thông thuận tiện"
        }

        for component, weighted_score in weighted_scores[:3]:
            if weighted_score > 0.1:  # Only include significant factors
                reasons.append(reason_templates.get(component, f"{component} tích cực"))

        return reasons

    def _generate_warnings(self, business_id: str, market_context: MarketContext,
                           scores: Dict[str, float]) -> List[str]:
        warnings = []

        if scores.get("competition", 1) < 0.2:
            warnings.append("Thị trường có dấu hiệu bão hòa")

        if scores.get("financial_viability", 1) < 0.3:
            warnings.append("Rủi ro tài chính cao")

        if market_context.foot_traffic_score < 0.3:
            warnings.append("Lưu lượng khách hàng có thể thấp")

        return warnings

    def _create_error_result(self) -> ScoringResult:
        return ScoringResult(
            score=0.0, confidence=0.0, reasons=["Lỗi trong quá trình tính toán"],
            warnings=["Không thể phân tích dữ liệu"], sensitivity_analysis={},
            recommendations=["Vui lòng thử lại sau"]
        )




def score_business(business_id: str, inputs: Dict, context: Dict) -> Dict[str, Any]:
    """
    Standalone function for backward compatibility
    Wrapper around AdvancedBusinessScorer class
    """
    try:
        scorer = AdvancedBusinessScorer()
        result = scorer.score_business(business_id, inputs, context)

        # Convert ScoringResult to dict for backward compatibility
        return {
            "score": result.score,
            "reason": ", ".join(result.reasons) if result.reasons else "Phân tích hoàn thành"
        }

    except Exception as e:
        logger.error(f"Error in score_business: {str(e)}")

        # Fallback simple scoring
        base_score = 50
        reasons = []

        # Simple customer target bonus
        customer_bonuses = {
            "student": {"milk_tea": 20, "cafe": 10, "fast_food": 15},
            "office": {"cafe": 20, "pharmacy": 10, "grocery": 15},
            "family": {"grocery": 20, "pharmacy": 15, "clothing": 10}
        }

        customer_target = inputs.get("customer_target", "general")
        if customer_target in customer_bonuses:
            bonus = customer_bonuses[customer_target].get(business_id, 0)
            base_score += bonus
            if bonus > 0:
                reasons.append(f"Phù hợp với {customer_target}")

        # Competition penalty
        competitors = context.get("category_counts", {}).get(business_id, 0)
        if competitors > 3:
            penalty = min(competitors * 5, 20)
            base_score -= penalty
            reasons.append("Cạnh tranh cao")
        elif competitors <= 1:
            base_score += 10
            reasons.append("Ít cạnh tranh")

        # Infrastructure bonus
        osm = context.get("osm", {})
        transport_score = osm.get("bus_stop", 0) + osm.get("subway", 0) * 2
        if transport_score >= 5:
            base_score += 10
            reasons.append("Giao thông thuận tiện")

        safety_score = osm.get("police", 0) + osm.get("hospital", 0)
        if safety_score >= 2:
            base_score += 10
            reasons.append("Khu vực an toàn")

        # Ensure score is in valid range
        final_score = max(10, min(95, base_score))

        return {
            "score": float(final_score),
            "reason": ", ".join(reasons) if reasons else "Phân tích cơ bản"
        }