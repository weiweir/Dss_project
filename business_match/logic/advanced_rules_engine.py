# advanced_rules_engine.py
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RuleSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    BLOCKING = "blocking"


class RuleCategory(Enum):
    MARKET = "market"
    LEGAL = "legal"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"


@dataclass
class BusinessRule:
    id: str
    name: str
    category: RuleCategory
    severity: RuleSeverity
    condition: callable
    message: str
    recommendation: str
    priority: int = 1  # 1-10, higher = more important


@dataclass
class RuleResult:
    rule_id: str
    triggered: bool
    severity: RuleSeverity
    category: RuleCategory
    message: str
    recommendation: str
    confidence: float
    supporting_data: Dict[str, Any]


class AdvancedRulesEngine:
    def __init__(self):
        self.rules = self._initialize_rules()
        self.business_specific_rules = self._initialize_business_specific_rules()
        self.contextual_rules = self._initialize_contextual_rules()

    def evaluate_business(self, business_id: str, context: Dict,
                          scores: Dict[str, float]) -> List[RuleResult]:
        """
        Evaluate all applicable rules for a business
        """
        results = []

        # Combine all applicable rules
        applicable_rules = self._get_applicable_rules(business_id, context)

        for rule in applicable_rules:
            try:
                result = self._evaluate_rule(rule, business_id, context, scores)
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.id}: {str(e)}")

        # Sort by severity and priority
        results.sort(key=lambda x: (
            list(RuleSeverity).index(x.severity),
            -self._get_rule_priority(x.rule_id)
        ))

        return results

    def _initialize_rules(self) -> List[BusinessRule]:
        """Initialize general business rules"""

        rules = [
            # Market saturation rules
            BusinessRule(
                id="market_oversaturated",
                name="Market Oversaturation",
                category=RuleCategory.MARKET,
                severity=RuleSeverity.CRITICAL,
                condition=lambda bid, ctx, scores: self._check_market_saturation(bid, ctx, scores),
                message="Thị trường đã bão hòa với loại hình kinh doanh này",
                recommendation="Xem xét pivot sang ngành liên quan hoặc tìm khu vực khác",
                priority=9
            ),

            BusinessRule(
                id="high_competition",
                name="High Competition",
                category=RuleCategory.MARKET,
                severity=RuleSeverity.WARNING,
                condition=lambda bid, ctx, scores: self._check_high_competition(bid, ctx, scores),
                message="Mức độ cạnh tranh cao trong khu vực",
                recommendation="Cần chiến lược khác biệt hóa mạnh mẽ",
                priority=7
            ),

            # Financial viability rules
            BusinessRule(
                id="low_profit_potential",
                name="Low Profit Potential",
                category=RuleCategory.FINANCIAL,
                severity=RuleSeverity.WARNING,
                condition=lambda bid, ctx, scores: scores.get("financial_viability", 0) < 0.3,
                message="Khả năng sinh lời thấp",
                recommendation="Xem xét mô hình kinh doanh với chi phí thấp hơn",
                priority=8
            ),

            BusinessRule(
                id="high_rent_area",
                name="High Rent Area",
                category=RuleCategory.FINANCIAL,
                severity=RuleSeverity.WARNING,
                condition=lambda bid, ctx, scores: self._check_high_rent(bid, ctx, scores),
                message="Khu vực có mức thuê mặt bằng cao",
                recommendation="Cân nhắc mô hình online hoặc tìm vị trí khác",
                priority=6
            ),

            # Safety and infrastructure rules
            BusinessRule(
                id="poor_safety",
                name="Poor Safety Infrastructure",
                category=RuleCategory.OPERATIONAL,
                severity=RuleSeverity.WARNING,
                condition=lambda bid, ctx, scores: self._check_poor_safety(bid, ctx, scores),
                message="Cơ sở hạ tầng an ninh kém",
                recommendation="Đầu tư thêm vào bảo mật hoặc chọn vị trí khác",
                priority=5
            ),

            BusinessRule(
                id="poor_transport",
                name="Poor Transportation",
                category=RuleCategory.OPERATIONAL,
                severity=RuleSeverity.INFO,
                condition=lambda bid, ctx, scores: scores.get("transport", 0) < 0.3,
                message="Giao thông không thuận tiện",
                recommendation="Cân nhắc dịch vụ giao hàng hoặc marketing online",
                priority=4
            ),

            # Market potential rules
            BusinessRule(
                id="declining_market",
                name="Declining Market",
                category=RuleCategory.STRATEGIC,
                severity=RuleSeverity.WARNING,
                condition=lambda bid, ctx, scores: self._check_declining_market(bid, ctx, scores),
                message="Thị trường có dấu hiệu suy giảm",
                recommendation="Cần nghiên cứu xu hướng dài hạn",
                priority=7
            ),

            # Customer mismatch rules
            BusinessRule(
                id="customer_mismatch",
                name="Customer Target Mismatch",
                category=RuleCategory.STRATEGIC,
                severity=RuleSeverity.WARNING,
                condition=lambda bid, ctx, scores: scores.get("customer", 0) < 0.4,
                message="Không phù hợp với nhóm khách hàng mục tiêu",
                recommendation="Xem xét thay đổi target hoặc chọn ngành khác",
                priority=8
            )
        ]

        return rules

    def _initialize_business_specific_rules(self) -> Dict[str, List[BusinessRule]]:
        """Initialize rules specific to business types"""

        business_rules = {
            "cafe": [
                BusinessRule(
                    id="cafe_no_office_nearby",
                    name="No Office Buildings Nearby",
                    category=RuleCategory.MARKET,
                    severity=RuleSeverity.WARNING,
                    condition=lambda bid, ctx, scores: ctx["osm"].get("office", 0) < 2,
                    message="Ít tòa nhà văn phòng xung quanh",
                    recommendation="Tập trung vào khách hàng sinh viên hoặc dân cư",
                    priority=6
                ),

                BusinessRule(
                    id="cafe_too_many_competitors",
                    name="Too Many Coffee Shops",
                    category=RuleCategory.MARKET,
                    severity=RuleSeverity.CRITICAL,
                    condition=lambda bid, ctx, scores: ctx["category_counts"].get("cafe", 0) > 5,
                    message="Quá nhiều quán cafe trong bán kính",
                    recommendation="Chọn vị trí khác hoặc concept khác biệt",
                    priority=9
                )
            ],

            "milk_tea": [
                BusinessRule(
                    id="milk_tea_no_students",
                    name="No Educational Institutions",
                    category=RuleCategory.MARKET,
                    severity=RuleSeverity.WARNING,
                    condition=lambda bid, ctx, scores: ctx["osm"].get("school", 0) < 1,
                    message="Không có trường học gần đó",
                    recommendation="Xem xét target khách hàng khác hoặc đổi vị trí",
                    priority=7
                ),

                BusinessRule(
                    id="milk_tea_oversaturated",
                    name="Milk Tea Market Oversaturated",
                    category=RuleCategory.MARKET,
                    severity=RuleSeverity.BLOCKING,
                    condition=lambda bid, ctx, scores: ctx["category_counts"].get("milk_tea", 0) > 8,
                    message="Thị trường trà sữa đã quá bão hòa",
                    recommendation="Không nên mở thêm - tìm ngành khác",
                    priority=10
                )
            ],

            "pharmacy": [
                BusinessRule(
                    id="pharmacy_hospital_required",
                    name="Hospital Proximity Required",
                    category=RuleCategory.LEGAL,
                    severity=RuleSeverity.CRITICAL,
                    condition=lambda bid, ctx, scores: ctx["osm"].get("hospital", 0) < 1,
                    message="Cần gần bệnh viện hoặc cơ sở y tế",
                    recommendation="Tìm vị trí gần bệnh viện/phòng khám",
                    priority=9
                ),

                BusinessRule(
                    id="pharmacy_license_complex",
                    name="Complex Licensing Requirements",
                    category=RuleCategory.LEGAL,
                    severity=RuleSeverity.INFO,
                    condition=lambda bid, ctx, scores: True,  # Always applies
                    message="Ngành dược phẩm có quy định phức tạp",
                    recommendation="Chuẩn bị đầy đủ giấy phép và nhân sự có chứng chỉ",
                    priority=8
                )
            ],

            "spa": [
                BusinessRule(
                    id="spa_high_income_area",
                    name="Requires High Income Area",
                    category=RuleCategory.MARKET,
                    severity=RuleSeverity.WARNING,
                    condition=lambda bid, ctx, scores: self._check_income_level(ctx) == "low",
                    message="Spa cần khu vực có thu nhập cao",
                    recommendation="Tìm khu vực khác hoặc điều chỉnh mức giá",
                    priority=7
                ),

                BusinessRule(
                    id="spa_parking_needed",
                    name="Parking Infrastructure Needed",
                    category=RuleCategory.OPERATIONAL,
                    severity=RuleSeverity.INFO,
                    condition=lambda bid, ctx, scores: True,
                    message="Khách hàng spa thường cần chỗ đậu xe",
                    recommendation="Đảm bảo có chỗ đậu xe hoặc gần bãi xe",
                    priority=5
                )
            ],

            "gaming": [
                BusinessRule(
                    id="gaming_student_area",
                    name="Student Population Required",
                    category=RuleCategory.MARKET,
                    severity=RuleSeverity.CRITICAL,
                    condition=lambda bid, ctx, scores: self._check_student_population(ctx) < 0.3,
                    message="Cần khu vực có đông học sinh/sinh viên",
                    recommendation="Tìm vị trí gần trường học hoặc khu dân cư trẻ",
                    priority=8
                ),

                BusinessRule(
                    id="gaming_noise_regulations",
                    name="Noise Regulation Concerns",
                    category=RuleCategory.LEGAL,
                    severity=RuleSeverity.WARNING,
                    condition=lambda bid, ctx, scores: ctx["osm"].get("residential", 0) > 10,
                    message="Khu dân cư đông có thể có vấn đề tiếng ồn",
                    recommendation="Kiểm tra quy định và đầu tư cách âm",
                    priority=6
                )
            ]
        }

        return business_rules

    def _initialize_contextual_rules(self) -> List[BusinessRule]:
        """Initialize rules that depend on broader context"""

        return [
            BusinessRule(
                id="covid_impact_assessment",
                name="COVID-19 Impact Assessment",
                category=RuleCategory.STRATEGIC,
                severity=RuleSeverity.INFO,
                condition=lambda bid, ctx, scores: self._assess_covid_impact(bid),
                message="Ngành này bị ảnh hưởng bởi COVID-19",
                recommendation="Chuẩn bị kế hoạch đối phó với dịch bệnh",
                priority=6
            ),

            BusinessRule(
                id="seasonal_business",
                name="Seasonal Business Pattern",
                category=RuleCategory.STRATEGIC,
                severity=RuleSeverity.INFO,
                condition=lambda bid, ctx, scores: self._check_seasonal_pattern(bid),
                message="Ngành có tính thời vụ cao",
                recommendation="Chuẩn bị kế hoạch cho các mùa khác nhau",
                priority=4
            ),

            BusinessRule(
                id="digital_transformation",
                name="Digital Transformation Required",
                category=RuleCategory.STRATEGIC,
                severity=RuleSeverity.INFO,
                condition=lambda bid, ctx, scores: self._needs_digital_transformation(bid),
                message="Ngành này cần chuyển đổi số",
                recommendation="Đầu tư vào technology và online presence",
                priority=5
            )
        ]

    def _get_applicable_rules(self, business_id: str, context: Dict) -> List[BusinessRule]:
        """Get all rules applicable to this business and context"""

        applicable_rules = self.rules.copy()  # General rules

        # Add business-specific rules
        if business_id in self.business_specific_rules:
            applicable_rules.extend(self.business_specific_rules[business_id])

        # Add contextual rules
        applicable_rules.extend(self.contextual_rules)

        return applicable_rules

    def _evaluate_rule(self, rule: BusinessRule, business_id: str,
                       context: Dict, scores: Dict[str, float]) -> Optional[RuleResult]:
        """Evaluate a single rule"""

        try:
            triggered = rule.condition(business_id, context, scores)

            if triggered:
                # Calculate confidence based on data quality
                confidence = self._calculate_rule_confidence(rule, context, scores)

                # Get supporting data
                supporting_data = self._get_supporting_data(rule, context, scores)

                return RuleResult(
                    rule_id=rule.id,
                    triggered=True,
                    severity=rule.severity,
                    category=rule.category,
                    message=rule.message,
                    recommendation=rule.recommendation,
                    confidence=confidence,
                    supporting_data=supporting_data
                )

            return None

        except Exception as e:
            logger.error(f"Error evaluating rule {rule.id}: {str(e)}")
            return None

    # Rule condition methods
    def _check_market_saturation(self, business_id: str, context: Dict, scores: Dict) -> bool:
        """Check if market is oversaturated"""
        competitors = context["category_counts"].get(business_id, 0)

        # Define saturation thresholds by business type
        saturation_thresholds = {
            "milk_tea": 6, "cafe": 8, "pharmacy": 3,
            "spa": 4, "gaming": 2, "fast_food": 10
        }

        threshold = saturation_thresholds.get(business_id, 5)
        return competitors >= threshold

    def _check_high_competition(self, business_id: str, context: Dict, scores: Dict) -> bool:
        """Check for high competition"""
        return scores.get("competition", 1) < 0.4

    def _check_high_rent(self, business_id: str, context: Dict, scores: Dict) -> bool:
        """Check if area has high rent"""
        # Estimate rent based on office and commercial activity
        commercial_activity = (context["osm"].get("office", 0) +
                               context["osm"].get("subway", 0) * 2)
        return commercial_activity > 15

    def _check_poor_safety(self, business_id: str, context: Dict, scores: Dict) -> bool:
        """Check for poor safety infrastructure"""
        safety_infrastructure = (context["osm"].get("police", 0) +
                                 context["osm"].get("hospital", 0))
        return safety_infrastructure == 0

    def _check_declining_market(self, business_id: str, context: Dict, scores: Dict) -> bool:
        """Check if market is declining"""
        return scores.get("market_potential", 0) < 0.3

    def _check_income_level(self, context: Dict) -> str:
        """Estimate income level of area"""
        office_count = context["osm"].get("office", 0)
        hospital_count = context["osm"].get("hospital", 0)
        park_count = context["osm"].get("park", 0)

        score = office_count * 2 + hospital_count * 3 + park_count

        if score > 15:
            return "high"
        elif score > 5:
            return "medium"
        else:
            return "low"

    def _check_student_population(self, context: Dict) -> float:
        """Estimate student population ratio"""
        schools = context["osm"].get("school", 0)
        total_population_indicators = (context["osm"].get("residential", 0) +
                                       context["osm"].get("office", 0))

        if total_population_indicators == 0:
            return 0.0

        return min(schools / total_population_indicators, 1.0)

    def _assess_covid_impact(self, business_id: str) -> bool:
        """Assess if business is impacted by COVID-19"""
        high_impact_businesses = ["spa", "gaming", "nail", "barbershop", "tattoo"]
        return business_id in high_impact_businesses

    def _check_seasonal_pattern(self, business_id: str) -> bool:
        """Check if business has strong seasonal patterns"""
        seasonal_businesses = ["ice_cream", "flower_shop", "toy_store"]
        return business_id in seasonal_businesses

    def _needs_digital_transformation(self, business_id: str) -> bool:
        """Check if business needs digital transformation"""
        digital_important = ["bookstore", "electronics", "clothing", "pharmacy"]
        return business_id in digital_important

    def _calculate_rule_confidence(self, rule: BusinessRule, context: Dict,
                                   scores: Dict) -> float:
        """Calculate confidence level for rule result"""

        # Base confidence on data completeness
        data_completeness = len([v for v in context["osm"].values() if v > 0]) / len(context["osm"])

        # Adjust based on rule category
        category_confidence = {
            RuleCategory.MARKET: 0.8,
            RuleCategory.FINANCIAL: 0.7,
            RuleCategory.OPERATIONAL: 0.9,
            RuleCategory.LEGAL: 0.95,
            RuleCategory.STRATEGIC: 0.6
        }

        base_confidence = category_confidence.get(rule.category, 0.7)

        return min(base_confidence * data_completeness + 0.1, 1.0)

    def _get_supporting_data(self, rule: BusinessRule, context: Dict,
                             scores: Dict) -> Dict[str, Any]:
        """Get supporting data for rule result"""

        supporting_data = {
            "rule_category": rule.category.value,
            "data_sources": list(context.keys())
        }

        # Add relevant context data based on rule
        if "competition" in rule.id:
            supporting_data["competitor_count"] = context["category_counts"]

        if "safety" in rule.id:
            supporting_data["safety_infrastructure"] = {
                "police": context["osm"].get("police", 0),
                "hospital": context["osm"].get("hospital", 0)
            }

        if "transport" in rule.id:
            supporting_data["transport_options"] = {
                "bus_stops": context["osm"].get("bus_stop", 0),
                "subway": context["osm"].get("subway", 0)
            }

        return supporting_data

    def _get_rule_priority(self, rule_id: str) -> int:
        """Get priority for a rule ID"""
        for rule in self.rules + sum(self.business_specific_rules.values(), []) + self.contextual_rules:
            if rule.id == rule_id:
                return rule.priority
        return 1

    def get_rule_summary(self, results: List[RuleResult]) -> Dict[str, Any]:
        """Generate summary of rule evaluation results"""

        summary = {
            "total_rules_triggered": len(results),
            "blocking_issues": len([r for r in results if r.severity == RuleSeverity.BLOCKING]),
            "critical_issues": len([r for r in results if r.severity == RuleSeverity.CRITICAL]),
            "warnings": len([r for r in results if r.severity == RuleSeverity.WARNING]),
            "info_items": len([r for r in results if r.severity == RuleSeverity.INFO]),
            "categories": {}
        }

        # Count by category
        for category in RuleCategory:
            summary["categories"][category.value] = len([
                r for r in results if r.category == category
            ])

        # Overall risk assessment
        if summary["blocking_issues"] > 0:
            summary["overall_risk"] = "very_high"
        elif summary["critical_issues"] > 2:
            summary["overall_risk"] = "high"
        elif summary["critical_issues"] > 0 or summary["warnings"] > 3:
            summary["overall_risk"] = "medium"
        elif summary["warnings"] > 0:
            summary["overall_risk"] = "low"
        else:
            summary["overall_risk"] = "very_low"

        return summary