# scenario_planner.py
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import copy
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScenarioResult:
    scenario_name: str
    modified_score: float
    score_change: float
    score_change_percent: float
    key_impacts: List[str]
    risk_level_change: str
    recommendations: List[str]


@dataclass
class SensitivityResult:
    factor_name: str
    base_impact: float  # How much this factor affects the base score
    sensitivity_coefficient: float  # How sensitive the score is to changes in this factor
    impact_range: Tuple[float, float]  # Min/max score when factor varies
    critical_threshold: float  # Point where factor becomes critical


class ScenarioPlanner:
    """Advanced scenario planning and sensitivity analysis for business decisions"""

    def __init__(self):
        self.base_scenarios = self._initialize_base_scenarios()
        self.sensitivity_ranges = {
            "customer": (-0.3, 0.3),
            "competition": (-0.4, 0.4),
            "market_potential": (-0.5, 0.5),
            "financial_viability": (-0.4, 0.4),
            "transport": (-0.2, 0.2),
            "safety": (-0.2, 0.2),
            "landmark": (-0.1, 0.1),
            "operational_feasibility": (-0.2, 0.2)
        }

    def run_scenarios(self, business_id: str, market_context: Dict[str, Any],
                      custom_scenarios: List[Dict] = None) -> List[ScenarioResult]:
        """
        Run multiple scenario analyses for a business
        """
        try:
            scenarios_to_run = self.base_scenarios.copy()

            # Add custom scenarios if provided
            if custom_scenarios:
                scenarios_to_run.extend(custom_scenarios)

            results = []

            # Get baseline score
            from .enhanced_business_scorer import AdvancedBusinessScorer
            scorer = AdvancedBusinessScorer()

            baseline_inputs = {"customer_target": "general", "price_level": 2}
            baseline_result = scorer.score_business(business_id, baseline_inputs, market_context)
            baseline_score = baseline_result.score

            # Run each scenario
            for scenario in scenarios_to_run:
                try:
                    scenario_result = self._run_single_scenario(
                        scenario, business_id, market_context, baseline_score
                    )
                    results.append(scenario_result)

                except Exception as e:
                    logger.error(f"Error running scenario {scenario.get('name', 'unknown')}: {str(e)}")
                    continue

            # Sort by impact magnitude
            results.sort(key=lambda x: abs(x.score_change), reverse=True)

            return results

        except Exception as e:
            logger.error(f"Scenario planning error: {str(e)}")
            return []

    def run_sensitivity_analysis(self, business_id: str, market_context: Dict[str, Any],
                                 parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run comprehensive sensitivity analysis
        """
        try:
            from .enhanced_business_scorer import AdvancedBusinessScorer
            from .enhanced_weights import get_business_weights

            scorer = AdvancedBusinessScorer()
            base_weights = get_business_weights(business_id)

            # Default parameters
            if not parameters:
                parameters = {"weight_adjustment": 0.2}

            adjustment_percent = parameters.get("weight_adjustment", 0.2)

            # Get baseline
            baseline_inputs = {"customer_target": "general", "price_level": 2}
            baseline_result = scorer.score_business(business_id, baseline_inputs, market_context)
            baseline_score = baseline_result.score

            sensitivity_results = {}

            # Test each factor
            for factor in base_weights.keys():
                sensitivity_result = self._analyze_factor_sensitivity(
                    factor, business_id, market_context, baseline_score,
                    adjustment_percent, scorer
                )
                sensitivity_results[factor] = sensitivity_result

            # Generate summary
            summary = self._generate_sensitivity_summary(sensitivity_results)

            return {
                "baseline_score": baseline_score,
                "factor_sensitivities": sensitivity_results,
                "summary": summary,
                "most_sensitive_factors": summary["most_sensitive"],
                "least_sensitive_factors": summary["least_sensitive"],
                "critical_factors": summary["critical_factors"]
            }

        except Exception as e:
            logger.error(f"Sensitivity analysis error: {str(e)}")
            return {}

    def _initialize_base_scenarios(self) -> List[Dict[str, Any]]:
        """Initialize predefined scenarios"""

        return [
            {
                "name": "Suy thoái kinh tế",
                "description": "Kinh tế suy giảm 10%, giảm thu nhập và chi tiêu",
                "modifications": {
                    "market_potential": -0.3,
                    "customer": -0.2,
                    "financial_viability": -0.4
                },
                "external_factors": {
                    "economic_growth": -0.1,
                    "unemployment_rate": 0.05
                }
            },

            {
                "name": "Tăng trưởng mạnh",
                "description": "Khu vực phát triển nhanh, tăng dân số và thu nhập",
                "modifications": {
                    "market_potential": 0.4,
                    "customer": 0.2,
                    "competition": 0.3,  # More competition due to attractiveness
                    "financial_viability": 0.2
                },
                "external_factors": {
                    "economic_growth": 0.15,
                    "population_growth": 0.08
                }
            },

            {
                "name": "Cải thiện hạ tầng",
                "description": "Đầu tư lớn vào hạ tầng giao thông và tiện ích",
                "modifications": {
                    "transport": 0.5,
                    "safety": 0.3,
                    "landmark": 0.2,
                    "market_potential": 0.3
                },
                "external_factors": {
                    "infrastructure_investment": 0.5
                }
            },

            {
                "name": "Bão hòa thị trường",
                "description": "Quá nhiều đối thủ mới gia nhập thị trường",
                "modifications": {
                    "competition": -0.6,
                    "market_potential": -0.3,
                    "financial_viability": -0.3
                },
                "external_factors": {
                    "new_business_rate": 0.5
                }
            },

            {
                "name": "Thay đổi nhân khẩu học",
                "description": "Dân số trẻ hóa, thay đổi thói quen tiêu dùng",
                "modifications": {
                    "customer": 0.3,  # Better for youth-oriented businesses
                    "market_potential": 0.2
                },
                "business_specific": {
                    "milk_tea": {"customer": 0.5},
                    "gaming": {"customer": 0.4},
                    "spa": {"customer": -0.2}  # Less appealing to young demographics
                }
            },

            {
                "name": "Khủng hoảng an ninh",
                "description": "Tình hình an ninh không ổn định",
                "modifications": {
                    "safety": -0.7,
                    "customer": -0.3,
                    "market_potential": -0.4
                },
                "external_factors": {
                    "crime_rate": 0.3
                }
            },

            {
                "name": "Chuyển đổi số",
                "description": "Thương mại điện tử phát triển mạnh",
                "modifications": {
                    "operational_feasibility": 0.2,
                    "competition": 0.4  # Online competition increases
                },
                "business_specific": {
                    "bookstore": {"competition": -0.5, "market_potential": -0.4},
                    "electronics": {"competition": -0.3},
                    "clothing": {"competition": -0.2},
                    "grocery": {"operational_feasibility": 0.4}  # Delivery services
                }
            },

            {
                "name": "Dịch bệnh COVID-19",
                "description": "Ảnh hưởng của dịch bệnh đến kinh doanh",
                "modifications": {
                    "customer": -0.4,
                    "financial_viability": -0.5,
                    "operational_feasibility": -0.3
                },
                "business_specific": {
                    "spa": {"customer": -0.8, "operational_feasibility": -0.7},
                    "gaming": {"customer": -0.6, "operational_feasibility": -0.8},
                    "pharmacy": {"customer": 0.3, "market_potential": 0.4},
                    "grocery": {"customer": 0.2, "market_potential": 0.3}
                }
            }
        ]

    def _run_single_scenario(self, scenario: Dict[str, Any], business_id: str,
                             market_context: Dict[str, Any], baseline_score: float) -> ScenarioResult:
        """Run a single scenario analysis"""

        from .enhanced_business_scorer import AdvancedBusinessScorer

        # Create modified market context
        modified_context = copy.deepcopy(market_context)

        # Apply scenario modifications
        modifications = scenario.get("modifications", {})
        business_specific = scenario.get("business_specific", {}).get(business_id, {})

        # Combine general and business-specific modifications
        all_modifications = {**modifications, **business_specific}

        # Apply modifications to context (simplified approach)
        # In a real implementation, this would be more sophisticated
        self._apply_scenario_modifications(modified_context, all_modifications)

        # Calculate new score
        scorer = AdvancedBusinessScorer()
        baseline_inputs = {"customer_target": "general", "price_level": 2}

        modified_result = scorer.score_business(business_id, baseline_inputs, modified_context)
        modified_score = modified_result.score

        # Calculate changes
        score_change = modified_score - baseline_score
        score_change_percent = (score_change / baseline_score * 100) if baseline_score > 0 else 0

        # Analyze key impacts
        key_impacts = self._analyze_scenario_impacts(all_modifications)

        # Determine risk level change
        risk_change = self._assess_risk_level_change(score_change_percent)

        # Generate recommendations
        recommendations = self._generate_scenario_recommendations(
            scenario, score_change, all_modifications
        )

        return ScenarioResult(
            scenario_name=scenario["name"],
            modified_score=modified_score,
            score_change=score_change,
            score_change_percent=score_change_percent,
            key_impacts=key_impacts,
            risk_level_change=risk_change,
            recommendations=recommendations
        )

    def _apply_scenario_modifications(self, context: Dict[str, Any],
                                      modifications: Dict[str, float]) -> None:
        """Apply scenario modifications to market context"""

        # This is a simplified implementation
        # In practice, you'd want more sophisticated modeling

        # Store modifications for use in scoring
        if "scenario_adjustments" not in context:
            context["scenario_adjustments"] = {}

        context["scenario_adjustments"].update(modifications)

        # Apply some direct modifications
        if "competition" in modifications:
            # Modify category counts to simulate competition changes
            category_counts = context.get("category_counts", {})
            adjustment = modifications["competition"]

            for category in category_counts:
                original_count = category_counts[category]
                # Positive adjustment = more competition
                new_count = max(0, int(original_count * (1 + adjustment)))
                category_counts[category] = new_count

        if "transport" in modifications:
            # Modify OSM transport data
            osm_data = context.get("osm", {})
            adjustment = modifications["transport"]

            transport_items = ["bus_stop", "subway"]
            for item in transport_items:
                if item in osm_data:
                    original_value = osm_data[item]
                    new_value = max(0, int(original_value * (1 + adjustment)))
                    osm_data[item] = new_value

    def _analyze_factor_sensitivity(self, factor: str, business_id: str,
                                    market_context: Dict[str, Any], baseline_score: float,
                                    adjustment_percent: float, scorer) -> float:
        """Analyze sensitivity for a specific factor"""

        from .enhanced_weights import get_business_weights

        # Test positive and negative adjustments
        scores = []

        for multiplier in [-1, -0.5, 0, 0.5, 1]:
            # Create modified weights
            base_weights = get_business_weights(business_id)
            modified_weights = base_weights.copy()

            # Adjust the specific factor
            if factor in modified_weights:
                adjustment = adjustment_percent * multiplier
                modified_weights[factor] *= (1 + adjustment)

                # Renormalize weights
                total_weight = sum(modified_weights.values())
                modified_weights = {k: v / total_weight for k, v in modified_weights.items()}

            # Calculate score with modified weights
            # This is simplified - in practice you'd modify the scorer to accept custom weights
            baseline_inputs = {"customer_target": "general", "price_level": 2}

            # Store original weights and temporarily modify
            # (This requires the scorer to support custom weights)
            try:
                result = scorer.score_business(business_id, baseline_inputs, market_context)
                scores.append(result.score)
            except:
                # Fallback calculation
                scores.append(baseline_score * (1 + adjustment * 0.5))

        # Calculate sensitivity as variance in scores
        if len(scores) > 1:
            score_range = max(scores) - min(scores)
            sensitivity = score_range / baseline_score if baseline_score > 0 else 0
        else:
            sensitivity = 0

        return sensitivity

    def _generate_sensitivity_summary(self, sensitivity_results: Dict[str, float]) -> Dict[str, Any]:
        """Generate summary of sensitivity analysis"""

        # Sort factors by sensitivity
        sorted_factors = sorted(sensitivity_results.items(), key=lambda x: x[1], reverse=True)

        # Categorize factors
        high_sensitivity = [f for f, s in sorted_factors if s > 0.3]
        medium_sensitivity = [f for f, s in sorted_factors if 0.1 <= s <= 0.3]
        low_sensitivity = [f for f, s in sorted_factors if s < 0.1]

        # Identify critical factors (high baseline impact + high sensitivity)
        critical_factors = high_sensitivity[:3]  # Top 3 most sensitive

        return {
            "most_sensitive": high_sensitivity,
            "moderately_sensitive": medium_sensitivity,
            "least_sensitive": low_sensitivity,
            "critical_factors": critical_factors,
            "average_sensitivity": sum(sensitivity_results.values()) / len(
                sensitivity_results) if sensitivity_results else 0,
            "sensitivity_distribution": {
                "high": len(high_sensitivity),
                "medium": len(medium_sensitivity),
                "low": len(low_sensitivity)
            }
        }

    def _analyze_scenario_impacts(self, modifications: Dict[str, float]) -> List[str]:
        """Analyze key impacts of scenario modifications"""

        impacts = []

        # Sort modifications by magnitude
        sorted_mods = sorted(modifications.items(), key=lambda x: abs(x[1]), reverse=True)

        factor_descriptions = {
            "customer": "phù hợp khách hàng",
            "competition": "mức độ cạnh tranh",
            "market_potential": "tiềm năng thị trường",
            "financial_viability": "khả năng sinh lời",
            "transport": "giao thông",
            "safety": "an toàn",
            "landmark": "địa danh nổi bật",
            "operational_feasibility": "khả năng vận hành"
        }

        for factor, change in sorted_mods[:3]:  # Top 3 impacts
            description = factor_descriptions.get(factor, factor)

            if change > 0.2:
                impacts.append(f"Cải thiện đáng kể {description}")
            elif change > 0:
                impacts.append(f"Cải thiện nhẹ {description}")
            elif change < -0.2:
                impacts.append(f"Giảm mạnh {description}")
            else:
                impacts.append(f"Giảm nhẹ {description}")

        return impacts

    def _assess_risk_level_change(self, score_change_percent: float) -> str:
        """Assess how risk level changes based on score change"""

        if score_change_percent > 20:
            return "Giảm rủi ro đáng kể"
        elif score_change_percent > 10:
            return "Giảm rủi ro nhẹ"
        elif score_change_percent > -10:
            return "Rủi ro không đổi"
        elif score_change_percent > -20:
            return "Tăng rủi ro nhẹ"
        else:
            return "Tăng rủi ro đáng kể"

    def _generate_scenario_recommendations(self, scenario: Dict[str, Any],
                                           score_change: float,
                                           modifications: Dict[str, float]) -> List[str]:
        """Generate recommendations based on scenario results"""

        recommendations = []
        scenario_name = scenario["name"]

        if score_change > 10:
            recommendations.append(f"Kịch bản '{scenario_name}' có tác động tích cực - nên chuẩn bị tận dụng")
        elif score_change < -10:
            recommendations.append(f"Kịch bản '{scenario_name}' có rủi ro cao - cần kế hoạch phòng ngừa")

        # Specific recommendations based on modifications
        if "competition" in modifications and modifications["competition"] > 0.3:
            recommendations.append("Chuẩn bị chiến lược khác biệt hóa cho môi trường cạnh tranh cao")

        if "market_potential" in modifications and modifications["market_potential"] < -0.3:
            recommendations.append("Xem xét đa dạng hóa sản phẩm/dịch vụ để giảm rủi ro")

        if "financial_viability" in modifications and modifications["financial_viability"] < -0.3:
            recommendations.append("Tối ưu hóa chi phí và có kế hoạch tài chính dự phòng")

        if "transport" in modifications and modifications["transport"] > 0.3:
            recommendations.append("Tận dụng cải thiện giao thông để mở rộng thị trường")

        # General scenario-based recommendations
        if scenario_name == "Suy thoái kinh tế":
            recommendations.extend([
                "Tập trung vào sản phẩm/dịch vụ thiết yếu",
                "Giảm chi phí vận hành",
                "Xây dựng mối quan hệ khách hàng trung thành"
            ])

        elif scenario_name == "Tăng trưởng mạnh":
            recommendations.extend([
                "Chuẩn bị mở rộng quy mô",
                "Đầu tư vào marketing để tăng thị phần",
                "Nâng cao chất lượng dịch vụ"
            ])

        elif scenario_name == "Dịch bệnh COVID-19":
            recommendations.extend([
                "Phát triển kênh bán hàng online",
                "Tăng cường các biện pháp an toàn",
                "Linh hoạt trong mô hình kinh doanh"
            ])

        return recommendations[:5]  # Top 5 recommendations

    def create_custom_scenario(self, name: str, description: str,
                               factor_changes: Dict[str, float]) -> Dict[str, Any]:
        """Create a custom scenario"""

        return {
            "name": name,
            "description": description,
            "modifications": factor_changes,
            "custom": True
        }

    def monte_carlo_analysis(self, business_id: str, market_context: Dict[str, Any],
                             num_simulations: int = 1000) -> Dict[str, Any]:
        """Run Monte Carlo simulation for uncertainty analysis"""

        try:
            import random
            from .enhanced_business_scorer import AdvancedBusinessScorer

            scorer = AdvancedBusinessScorer()
            baseline_inputs = {"customer_target": "general", "price_level": 2}

            scores = []

            for _ in range(num_simulations):
                # Create random variations in market context
                modified_context = copy.deepcopy(market_context)

                # Add random variations to key factors
                osm_data = modified_context.get("osm", {})
                for key in osm_data:
                    # Add ±20% random variation
                    variation = random.uniform(-0.2, 0.2)
                    original_value = osm_data[key]
                    osm_data[key] = max(0, int(original_value * (1 + variation)))

                # Add variation to category counts
                category_counts = modified_context.get("category_counts", {})
                for category in category_counts:
                    variation = random.uniform(-0.3, 0.3)
                    original_count = category_counts[category]
                    category_counts[category] = max(0, int(original_count * (1 + variation)))

                # Calculate score
                try:
                    result = scorer.score_business(business_id, baseline_inputs, modified_context)
                    scores.append(result.score)
                except:
                    continue

            if not scores:
                return {"error": "No valid simulations"}

            # Calculate statistics
            scores.sort()
            n = len(scores)

            statistics = {
                "mean": sum(scores) / n,
                "median": scores[n // 2],
                "std_dev": (sum((x - sum(scores) / n) ** 2 for x in scores) / n) ** 0.5,
                "min": min(scores),
                "max": max(scores),
                "percentile_5": scores[int(n * 0.05)],
                "percentile_25": scores[int(n * 0.25)],
                "percentile_75": scores[int(n * 0.75)],
                "percentile_95": scores[int(n * 0.95)]
            }

            # Risk assessment
            baseline_result = scorer.score_business(business_id, baseline_inputs, market_context)
            baseline_score = baseline_result.score

            probability_below_baseline = len([s for s in scores if s < baseline_score]) / n
            probability_above_60 = len([s for s in scores if s >= 60]) / n

            return {
                "statistics": statistics,
                "baseline_score": baseline_score,
                "probability_below_baseline": probability_below_baseline,
                "probability_success": probability_above_60,
                "confidence_interval_90": (statistics["percentile_5"], statistics["percentile_95"]),
                "risk_assessment": self._assess_monte_carlo_risk(statistics, baseline_score),
                "num_simulations": len(scores)
            }

        except Exception as e:
            logger.error(f"Monte Carlo analysis error: {str(e)}")
            return {"error": str(e)}

    def _assess_monte_carlo_risk(self, statistics: Dict[str, float], baseline: float) -> Dict[str, Any]:
        """Assess risk based on Monte Carlo results"""

        volatility = statistics["std_dev"] / statistics["mean"] if statistics["mean"] > 0 else 1
        downside_risk = max(0, baseline - statistics["percentile_5"])
        upside_potential = max(0, statistics["percentile_95"] - baseline)

        # Risk categorization
        if volatility < 0.1:
            risk_level = "very_low"
        elif volatility < 0.2:
            risk_level = "low"
        elif volatility < 0.3:
            risk_level = "medium"
        elif volatility < 0.5:
            risk_level = "high"
        else:
            risk_level = "very_high"

        return {
            "risk_level": risk_level,
            "volatility": volatility,
            "downside_risk": downside_risk,
            "upside_potential": upside_potential,
            "risk_reward_ratio": upside_potential / downside_risk if downside_risk > 0 else float('inf')
        }

    def generate_decision_tree(self, business_id: str, market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a decision tree for business decisions"""

        # Simplified decision tree structure
        decision_tree = {
            "root": {
                "question": "Bạn có ngân sách đầu tư > 500 triệu?",
                "high_budget": {
                    "question": "Khu vực có mật độ cạnh tranh cao?",
                    "high_competition": {
                        "recommendation": "Chọn ngành dịch vụ cao cấp với khác biệt hóa mạnh",
                        "suggested_businesses": ["spa", "nail", "hair_salon"]
                    },
                    "low_competition": {
                        "recommendation": "Cơ hội tốt cho ngành có lợi nhuận cao",
                        "suggested_businesses": ["pharmacy", "electronics", "cafe"]
                    }
                },
                "low_budget": {
                    "question": "Khu vực có nhiều sinh viên?",
                    "student_area": {
                        "recommendation": "Tập trung vào nhu cầu sinh viên",
                        "suggested_businesses": ["milk_tea", "stationery", "printing"]
                    },
                    "general_area": {
                        "recommendation": "Chọn ngành có vòng quay vốn nhanh",
                        "suggested_businesses": ["grocery", "fast_food", "laundry"]
                    }
                }
            }
        }

        return decision_tree

    def what_if_analysis(self, business_id: str, market_context: Dict[str, Any],
                         what_if_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Perform what-if analysis with specific conditions"""

        results = {}

        from .enhanced_business_scorer import AdvancedBusinessScorer
        scorer = AdvancedBusinessScorer()
        baseline_inputs = {"customer_target": "general", "price_level": 2}

        # Get baseline
        baseline_result = scorer.score_business(business_id, baseline_inputs, market_context)
        baseline_score = baseline_result.score

        # Test each what-if condition
        for condition_name, condition_changes in what_if_conditions.items():
            modified_context = copy.deepcopy(market_context)
            self._apply_scenario_modifications(modified_context, condition_changes)

            modified_result = scorer.score_business(business_id, baseline_inputs, modified_context)

            results[condition_name] = {
                "original_score": baseline_score,
                "new_score": modified_result.score,
                "change": modified_result.score - baseline_score,
                "change_percent": ((
                                               modified_result.score - baseline_score) / baseline_score * 100) if baseline_score > 0 else 0,
                "impact_assessment": self._assess_what_if_impact(modified_result.score - baseline_score)
            }

        return results

    def _assess_what_if_impact(self, score_change: float) -> str:
        """Assess the impact of a what-if scenario"""

        if score_change > 15:
            return "Tác động tích cực lớn"
        elif score_change > 5:
            return "Tác động tích cực vừa"
        elif score_change > -5:
            return "Tác động không đáng kể"
        elif score_change > -15:
            return "Tác động tiêu cực vừa"
        else:
            return "Tác động tiêu cực lớn"