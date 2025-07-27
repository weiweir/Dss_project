# enhanced_weights.py
from typing import Dict, Optional
from enum import Enum


class BusinessCategory(Enum):
    FOOD_BEVERAGE = "food_beverage"
    RETAIL = "retail"
    SERVICE = "service"
    ENTERTAINMENT = "entertainment"


# Base weights for general scoring
DEFAULT_WEIGHTS = {
    "customer": 0.20,
    "competition": 0.18,
    "market_potential": 0.15,
    "financial_viability": 0.15,
    "safety": 0.08,
    "transport": 0.12,
    "landmark": 0.07,
    "operational_feasibility": 0.05
}

# Business-specific weight configurations
BUSINESS_SPECIFIC_WEIGHTS = {
    # Food & Beverage businesses
    "cafe": {
        "customer": 0.25,  # High importance for target customer fit
        "competition": 0.20,
        "market_potential": 0.12,
        "financial_viability": 0.13,
        "safety": 0.05,
        "transport": 0.15,  # Critical for foot traffic
        "landmark": 0.08,  # Nearby offices/schools important
        "operational_feasibility": 0.02
    },

    "milk_tea": {
        "customer": 0.30,  # Very customer-segment dependent
        "competition": 0.22,  # High competition market
        "market_potential": 0.10,
        "financial_viability": 0.12,
        "safety": 0.03,
        "transport": 0.18,  # Students need easy access
        "landmark": 0.04,
        "operational_feasibility": 0.01
    },

    "fast_food": {
        "customer": 0.15,
        "competition": 0.25,  # Very competitive
        "market_potential": 0.15,
        "financial_viability": 0.18,  # Margins important
        "safety": 0.05,
        "transport": 0.17,  # High foot traffic needed
        "landmark": 0.03,
        "operational_feasibility": 0.02
    },

    # Service businesses
    "spa": {
        "customer": 0.28,  # High-end customer targeting
        "competition": 0.15,
        "market_potential": 0.18,
        "financial_viability": 0.20,  # High setup costs
        "safety": 0.10,  # Important for premium service
        "transport": 0.05,  # Less dependent on foot traffic
        "landmark": 0.02,
        "operational_feasibility": 0.02
    },

    "pharmacy": {
        "customer": 0.12,  # Less customer-specific
        "competition": 0.20,
        "market_potential": 0.15,
        "financial_viability": 0.15,
        "safety": 0.12,  # Important for medical services
        "transport": 0.18,  # Accessibility crucial
        "landmark": 0.06,
        "operational_feasibility": 0.02
    },

    "hair_salon": {
        "customer": 0.22,
        "competition": 0.18,
        "market_potential": 0.13,
        "financial_viability": 0.16,
        "safety": 0.08,
        "transport": 0.10,
        "landmark": 0.05,
        "operational_feasibility": 0.08  # Licensing, equipment
    },

    # Retail businesses
    "grocery": {
        "customer": 0.10,  # Universal need
        "competition": 0.16,
        "market_potential": 0.12,
        "financial_viability": 0.18,
        "safety": 0.08,
        "transport": 0.25,  # Convenience crucial
        "landmark": 0.08,
        "operational_feasibility": 0.03
    },

    "clothing": {
        "customer": 0.30,  # Very fashion/demographic dependent
        "competition": 0.20,
        "market_potential": 0.18,
        "financial_viability": 0.15,
        "safety": 0.05,
        "transport": 0.08,
        "landmark": 0.02,
        "operational_feasibility": 0.02
    },

    "electronics": {
        "customer": 0.18,
        "competition": 0.22,
        "market_potential": 0.20,  # Tech adoption important
        "financial_viability": 0.20,
        "safety": 0.08,
        "transport": 0.08,
        "landmark": 0.02,
        "operational_feasibility": 0.02
    },

    # Entertainment
    "gaming": {
        "customer": 0.35,  # Very target-specific
        "competition": 0.18,
        "market_potential": 0.15,
        "financial_viability": 0.12,
        "safety": 0.05,
        "transport": 0.10,
        "landmark": 0.03,
        "operational_feasibility": 0.02
    }
}

# Market condition modifiers
MARKET_CONDITION_MODIFIERS = {
    "high_growth": {
        "market_potential": 1.3,
        "competition": 0.9,
        "financial_viability": 1.2
    },
    "mature_market": {
        "competition": 1.2,
        "customer": 1.1,
        "operational_feasibility": 1.1
    },
    "declining_market": {
        "market_potential": 0.7,
        "competition": 1.4,
        "financial_viability": 0.8
    }
}

# Location type modifiers
LOCATION_TYPE_MODIFIERS = {
    "city_center": {
        "transport": 1.3,
        "competition": 1.2,
        "financial_viability": 0.8  # Higher rent
    },
    "residential": {
        "customer": 1.2,
        "safety": 1.2,
        "competition": 0.9
    },
    "commercial": {
        "landmark": 1.3,
        "transport": 1.1,
        "competition": 1.1
    },
    "suburban": {
        "safety": 1.2,
        "financial_viability": 1.1,  # Lower rent
        "transport": 0.8
    }
}


def get_weights() -> Dict[str, float]:
    """Get default weights for backward compatibility"""
    return DEFAULT_WEIGHTS.copy()


def get_business_weights(business_id: str,
                         market_condition: Optional[str] = None,
                         location_type: Optional[str] = None) -> Dict[str, float]:
    """
    Get business-specific weights with optional market and location modifiers

    Args:
        business_id: ID of the business type
        market_condition: 'high_growth', 'mature_market', 'declining_market'
        location_type: 'city_center', 'residential', 'commercial', 'suburban'
    """

    # Start with business-specific weights or default
    weights = BUSINESS_SPECIFIC_WEIGHTS.get(business_id, DEFAULT_WEIGHTS.copy())
    weights = weights.copy()  # Don't modify original

    # Apply market condition modifiers
    if market_condition and market_condition in MARKET_CONDITION_MODIFIERS:
        modifiers = MARKET_CONDITION_MODIFIERS[market_condition]
        for factor, modifier in modifiers.items():
            if factor in weights:
                weights[factor] *= modifier

    # Apply location type modifiers
    if location_type and location_type in LOCATION_TYPE_MODIFIERS:
        modifiers = LOCATION_TYPE_MODIFIERS[location_type]
        for factor, modifier in modifiers.items():
            if factor in weights:
                weights[factor] *= modifier

    # Normalize weights to sum to 1.0
    total_weight = sum(weights.values())
    if total_weight > 0:
        weights = {k: v / total_weight for k, v in weights.items()}

    return weights


def get_business_category(business_id: str) -> BusinessCategory:
    """Get the category for a business type"""

    category_mapping = {
        # Food & Beverage
        "cafe": BusinessCategory.FOOD_BEVERAGE,
        "milk_tea": BusinessCategory.FOOD_BEVERAGE,
        "fast_food": BusinessCategory.FOOD_BEVERAGE,
        "bakery": BusinessCategory.FOOD_BEVERAGE,
        "ice_cream": BusinessCategory.FOOD_BEVERAGE,
        "drink_shop": BusinessCategory.FOOD_BEVERAGE,

        # Service
        "spa": BusinessCategory.SERVICE,
        "pharmacy": BusinessCategory.SERVICE,
        "hair_salon": BusinessCategory.SERVICE,
        "nail": BusinessCategory.SERVICE,
        "barbershop": BusinessCategory.SERVICE,
        "laundry": BusinessCategory.SERVICE,
        "repair": BusinessCategory.SERVICE,
        "printing": BusinessCategory.SERVICE,

        # Retail
        "grocery": BusinessCategory.RETAIL,
        "clothing": BusinessCategory.RETAIL,
        "electronics": BusinessCategory.RETAIL,
        "bookstore": BusinessCategory.RETAIL,
        "stationery": BusinessCategory.RETAIL,
        "pet_shop": BusinessCategory.RETAIL,
        "toy_store": BusinessCategory.RETAIL,
        "flower_shop": BusinessCategory.RETAIL,
        "bike_shop": BusinessCategory.RETAIL,

        # Entertainment
        "gaming": BusinessCategory.ENTERTAINMENT,
        "tattoo": BusinessCategory.ENTERTAINMENT
    }

    return category_mapping.get(business_id, BusinessCategory.SERVICE)


def get_category_weights(category: BusinessCategory) -> Dict[str, float]:
    """Get default weights for a business category"""

    category_weights = {
        BusinessCategory.FOOD_BEVERAGE: {
            "customer": 0.22,
            "competition": 0.20,
            "market_potential": 0.12,
            "financial_viability": 0.14,
            "safety": 0.05,
            "transport": 0.17,
            "landmark": 0.08,
            "operational_feasibility": 0.02
        },

        BusinessCategory.SERVICE: {
            "customer": 0.25,
            "competition": 0.17,
            "market_potential": 0.16,
            "financial_viability": 0.18,
            "safety": 0.08,
            "transport": 0.10,
            "landmark": 0.04,
            "operational_feasibility": 0.02
        },

        BusinessCategory.RETAIL: {
            "customer": 0.20,
            "competition": 0.18,
            "market_potential": 0.15,
            "financial_viability": 0.17,
            "safety": 0.07,
            "transport": 0.15,
            "landmark": 0.06,
            "operational_feasibility": 0.02
        },

        BusinessCategory.ENTERTAINMENT: {
            "customer": 0.30,
            "competition": 0.18,
            "market_potential": 0.15,
            "financial_viability": 0.12,
            "safety": 0.08,
            "transport": 0.12,
            "landmark": 0.03,
            "operational_feasibility": 0.02
        }
    }

    return category_weights.get(category, DEFAULT_WEIGHTS.copy())


def analyze_weight_sensitivity(business_id: str, base_weights: Dict[str, float]) -> Dict[str, str]:
    """
    Analyze which factors are most critical for this business type
    Returns sensitivity level for each factor
    """

    sensitivity_analysis = {}

    for factor, weight in base_weights.items():
        if weight >= 0.20:
            sensitivity_analysis[factor] = "critical"
        elif weight >= 0.15:
            sensitivity_analysis[factor] = "high"
        elif weight >= 0.10:
            sensitivity_analysis[factor] = "medium"
        elif weight >= 0.05:
            sensitivity_analysis[factor] = "low"
        else:
            sensitivity_analysis[factor] = "minimal"

    return sensitivity_analysis


def get_weight_explanations(business_id: str) -> Dict[str, str]:
    """Get explanations for why certain factors are weighted differently"""

    explanations = {
        "cafe": {
            "customer": "Khách hàng mục tiêu rất quan trọng - văn phòng vs sinh viên có nhu cầu khác nhau",
            "transport": "Cần giao thông thuận tiện để thu hút khách đi làm và học",
            "competition": "Thị trường cafe rất cạnh tranh, cần đánh giá kỹ"
        },

        "milk_tea": {
            "customer": "Chủ yếu phục vụ giới trẻ, sinh viên - targeting rất quan trọng",
            "competition": "Ngành trà sữa bùng nổ, cạnh tranh gay gắt",
            "transport": "Sinh viên cần tiếp cận dễ dàng"
        },

        "spa": {
            "customer": "Phân khúc khách hàng cao cấp, cần targeting chính xác",
            "financial_viability": "Chi phí đầu tư cao, cần đảm bảo khả năng sinh lời",
            "market_potential": "Thị trường đang phát triển, tiềm năng quan trọng"
        },

        "grocery": {
            "transport": "Khách hàng cần tiện lợi mua sắm hàng ngày",
            "financial_viability": "Lợi nhuận thấp, cần quản lý chi phí tốt"
        },

        "gaming": {
            "customer": "Nhóm khách hàng rất đặc thù - game thủ, học sinh",
            "competition": "Ít đối thủ nhưng cần đúng target"
        }
    }

    return explanations.get(business_id, {})


def get_dynamic_weights(business_id: str, market_data: Dict) -> Dict[str, float]:
    """
    Calculate dynamic weights based on real-time market conditions

    Args:
        business_id: Business type ID
        market_data: Current market conditions and trends
    """

    base_weights = get_business_weights(business_id)

    # Adjust based on market trends
    trends = market_data.get("trends", {})

    # If market is growing rapidly, increase market_potential weight
    if trends.get("growth_rate", 0) > 0.15:
        base_weights["market_potential"] *= 1.2
        base_weights["competition"] *= 0.9

    # If unemployment is high, adjust customer and financial weights
    if market_data.get("unemployment_rate", 0) > 0.08:
        base_weights["customer"] *= 1.1
        base_weights["financial_viability"] *= 1.2

    # If rent prices are rising, increase financial weight
    if market_data.get("rent_trend", 0) > 0.1:
        base_weights["financial_viability"] *= 1.15

    # If infrastructure is improving, boost transport weight
    if market_data.get("infrastructure_investment", 0) > 0:
        base_weights["transport"] *= 1.1

    # Normalize
    total = sum(base_weights.values())
    return {k: v / total for k, v in base_weights.items()}


# Configuration for A/B testing different weight schemes
WEIGHT_SCHEMES = {
    "conservative": {
        "financial_viability": 1.3,
        "competition": 1.2,
        "market_potential": 0.8
    },

    "aggressive": {
        "market_potential": 1.4,
        "customer": 1.2,
        "competition": 0.8
    },

    "balanced": {
        # No modifiers - use base weights
    }
}


def get_experimental_weights(business_id: str, scheme: str = "balanced") -> Dict[str, float]:
    """Get weights for experimental schemes (for A/B testing)"""

    base_weights = get_business_weights(business_id)

    if scheme in WEIGHT_SCHEMES:
        modifiers = WEIGHT_SCHEMES[scheme]
        for factor, modifier in modifiers.items():
            if factor in base_weights:
                base_weights[factor] *= modifier

        # Normalize
        total = sum(base_weights.values())
        base_weights = {k: v / total for k, v in base_weights.items()}

    return base_weights