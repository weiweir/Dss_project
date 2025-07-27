from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class ScenarioPlanner:
    """Simplified scenario planner for sensitivity analysis"""

    def __init__(self):
        pass

    def run_sensitivity_analysis(self, business_id: str, market_context: Dict[str, Any],
                                 parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run basic sensitivity analysis
        """
        try:
            # Get parameters
            if not parameters:
                parameters = {"weight_adjustment": 0.2}

            weight_adjustment = parameters.get("weight_adjustment", 0.2) / 100.0

            # Define factors
            factors = {
                "customer": "Phù hợp khách hàng",
                "competition": "Mức độ cạnh tranh",
                "market_potential": "Tiềm năng thị trường",
                "transport": "Giao thông",
                "safety": "An toàn",
                "financial_viability": "Khả năng sinh lời"
            }

            # Calculate base sensitivities
            sensitivity_results = {}

            for factor_id, factor_name in factors.items():
                # Simulate sensitivity based on business type and factor
                base_sensitivity = self._calculate_factor_sensitivity(business_id, factor_id, market_context)
                sensitivity_results[factor_id] = base_sensitivity

            # Identify most/least sensitive factors
            sorted_factors = sorted(sensitivity_results.items(), key=lambda x: x[1], reverse=True)
            most_sensitive = [factor for factor, value in sorted_factors[:3]]
            least_sensitive = [factor for factor, value in sorted_factors[-2:]]

            return {
                "baseline_score": 50.0,  # Default baseline
                "factor_sensitivities": sensitivity_results,
                "summary": {
                    "most_sensitive": most_sensitive,
                    "least_sensitive": least_sensitive,
                    "average_sensitivity": sum(sensitivity_results.values()) / len(sensitivity_results)
                },
                "most_sensitive_factors": most_sensitive
            }

        except Exception as e:
            logger.error(f"Sensitivity analysis error: {str(e)}")
            return {
                "baseline_score": 50.0,
                "factor_sensitivities": {
                    "customer": 25,
                    "competition": 20,
                    "market_potential": 30,
                    "transport": 15,
                    "safety": 10
                },
                "summary": {
                    "most_sensitive": ["market_potential", "customer"],
                    "least_sensitive": ["safety", "transport"],
                    "average_sensitivity": 20
                },
                "most_sensitive_factors": ["market_potential", "customer"]
            }

    def _calculate_factor_sensitivity(self, business_id: str, factor_id: str,
                                      market_context: Dict[str, Any]) -> float:
        """Calculate sensitivity for a specific factor"""

        # Business-specific sensitivity patterns
        business_sensitivities = {
            "cafe": {
                "customer": 35,
                "transport": 30,
                "competition": 25,
                "market_potential": 20,
                "safety": 15,
                "financial_viability": 25
            },
            "milk_tea": {
                "customer": 40,
                "competition": 35,
                "transport": 25,
                "market_potential": 20,
                "safety": 10,
                "financial_viability": 20
            },
            "spa": {
                "customer": 35,
                "safety": 30,
                "financial_viability": 30,
                "market_potential": 25,
                "transport": 15,
                "competition": 20
            },
            "pharmacy": {
                "safety": 25,
                "transport": 35,
                "market_potential": 20,
                "customer": 15,
                "competition": 20,
                "financial_viability": 25
            }
        }

        # Get base sensitivity for this business and factor
        if business_id in business_sensitivities:
            base_sensitivity = business_sensitivities[business_id].get(factor_id, 20)
        else:
            # Default sensitivities
            default_sensitivities = {
                "customer": 25,
                "competition": 20,
                "market_potential": 30,
                "transport": 15,
                "safety": 10,
                "financial_viability": 20
            }
            base_sensitivity = default_sensitivities.get(factor_id, 20)

        # Adjust based on market context
        osm_data = market_context.get("osm", {})
        category_counts = market_context.get("category_counts", {})

        # Factor-specific adjustments
        if factor_id == "competition":
            competitor_count = category_counts.get(business_id, 0)
            if competitor_count > 5:
                base_sensitivity *= 1.5  # Higher sensitivity in competitive markets
            elif competitor_count == 0:
                base_sensitivity *= 0.5  # Lower sensitivity with no competition

        elif factor_id == "transport":
            transport_score = osm_data.get("bus_stop", 0) + osm_data.get("subway", 0) * 2
            if transport_score < 2:
                base_sensitivity *= 1.3  # More sensitive when transport is poor

        elif factor_id == "safety":
            safety_score = osm_data.get("police", 0) + osm_data.get("hospital", 0)
            if safety_score == 0:
                base_sensitivity *= 1.4  # More sensitive when safety infrastructure is poor

        # Add some randomness for variation
        import random
        variation = random.uniform(0.8, 1.2)
        base_sensitivity *= variation

        # Ensure reasonable bounds
        return max(5, min(45, base_sensitivity))