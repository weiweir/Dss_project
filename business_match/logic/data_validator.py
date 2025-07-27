# data_validator.py
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class DataQualityIssue:
    category: str
    severity: str  # "low", "medium", "high", "critical"
    message: str
    impact: str
    recommendation: str


@dataclass
class DataQualityReport:
    overall_quality: float  # 0-1 score
    overall_quality_text: str
    completeness_score: float
    accuracy_score: float
    consistency_score: float
    timeliness_score: float
    issues: List[DataQualityIssue]
    sources: List[str]
    warnings: List[str]
    data_coverage: Dict[str, bool]


class DataValidator:
    """Validates and assesses quality of market data from various sources"""

    def __init__(self):
        self.required_osm_fields = [
            "school", "hospital", "pharmacy", "police",
            "bus_stop", "subway", "park", "office", "residential"
        ]

        self.data_quality_thresholds = {
            "excellent": 0.9,
            "good": 0.7,
            "fair": 0.5,
            "poor": 0.3
        }

    def validate_market_data(self, market_context: Dict[str, Any]) -> DataQualityReport:
        """
        Comprehensive validation of market data quality
        """
        try:
            issues = []
            sources = []
            warnings = []

            # Validate OSM data
            osm_quality, osm_issues, osm_coverage = self._validate_osm_data(
                market_context.get("osm", {})
            )
            issues.extend(osm_issues)
            if market_context.get("osm"):
                sources.append("OpenStreetMap")

            # Validate business data
            business_quality, business_issues = self._validate_business_data(
                market_context.get("category_counts", {}),
                market_context.get("places", [])
            )
            issues.extend(business_issues)
            if market_context.get("places"):
                sources.append("Foursquare Places API")

            # Validate geographic data
            geo_quality, geo_issues = self._validate_geographic_data(
                market_context.get("coordinates", {})
            )
            issues.extend(geo_issues)
            if market_context.get("coordinates"):
                sources.append("Geocoding Service")

            # Calculate component scores
            completeness_score = self._calculate_completeness_score(market_context)
            accuracy_score = self._estimate_accuracy_score(market_context, issues)
            consistency_score = self._check_data_consistency(market_context)
            timeliness_score = self._assess_data_timeliness(market_context)

            # Calculate overall quality
            component_weights = {
                "completeness": 0.3,
                "accuracy": 0.3,
                "consistency": 0.2,
                "timeliness": 0.2
            }

            overall_quality = (
                    completeness_score * component_weights["completeness"] +
                    accuracy_score * component_weights["accuracy"] +
                    consistency_score * component_weights["consistency"] +
                    timeliness_score * component_weights["timeliness"]
            )

            # Generate warnings
            warnings = self._generate_warnings(overall_quality, issues)

            # Create quality text description
            quality_text = self._get_quality_description(overall_quality)

            return DataQualityReport(
                overall_quality=overall_quality,
                overall_quality_text=quality_text,
                completeness_score=completeness_score,
                accuracy_score=accuracy_score,
                consistency_score=consistency_score,
                timeliness_score=timeliness_score,
                issues=issues,
                sources=sources,
                warnings=warnings,
                data_coverage=osm_coverage
            )

        except Exception as e:
            logger.error(f"Data validation error: {str(e)}")
            return self._create_fallback_report()

    def _validate_osm_data(self, osm_data: Dict[str, int]) -> Tuple[float, List[DataQualityIssue], Dict[str, bool]]:
        """Validate OpenStreetMap data quality"""

        issues = []
        coverage = {}

        # Check completeness
        missing_fields = []
        for field in self.required_osm_fields:
            has_data = field in osm_data and osm_data[field] > 0
            coverage[field] = has_data

            if not has_data:
                missing_fields.append(field)

        # Add issues for missing critical data
        if "hospital" not in osm_data or osm_data["hospital"] == 0:
            issues.append(DataQualityIssue(
                category="completeness",
                severity="medium",
                message="Không có dữ liệu bệnh viện",
                impact="Ảnh hưởng đến đánh giá an toàn và dịch vụ y tế",
                recommendation="Kiểm tra thủ công các cơ sở y tế trong khu vực"
            ))

        if "police" not in osm_data or osm_data["police"] == 0:
            issues.append(DataQualityIssue(
                category="completeness",
                severity="medium",
                message="Không có dữ liệu đồn công an",
                impact="Ảnh hưởng đến đánh giá an ninh",
                recommendation="Xác minh tình hình an ninh khu vực"
            ))

        # Check for suspiciously high values
        for field, value in osm_data.items():
            if value > 50:  # Threshold for suspicious data
                issues.append(DataQualityIssue(
                    category="accuracy",
                    severity="low",
                    message=f"Giá trị {field} có vẻ cao bất thường: {value}",
                    impact="Có thể làm sai lệch kết quả phân tích",
                    recommendation="Kiểm tra lại dữ liệu từ nguồn khác"
                ))

        # Calculate quality score
        completeness_ratio = len([f for f in self.required_osm_fields if coverage.get(f, False)]) / len(
            self.required_osm_fields)
        accuracy_penalty = min(len([i for i in issues if i.category == "accuracy"]) * 0.1, 0.3)

        quality_score = max(completeness_ratio - accuracy_penalty, 0)

        return quality_score, issues, coverage

    def _validate_business_data(self, category_counts: Dict[str, int],
                                places: List[Dict]) -> Tuple[float, List[DataQualityIssue]]:
        """Validate business data from Foursquare API"""

        issues = []

        if not places:
            issues.append(DataQualityIssue(
                category="completeness",
                severity="critical",
                message="Không có dữ liệu doanh nghiệp từ Foursquare",
                impact="Không thể phân tích cạnh tranh chính xác",
                recommendation="Kiểm tra kết nối API hoặc mở rộng bán kính tìm kiếm"
            ))
            return 0.0, issues

        # Check data completeness
        complete_places = 0
        for place in places:
            if (place.get("name") and
                    place.get("main_category") and
                    place.get("lat") and
                    place.get("lon")):
                complete_places += 1

        completeness_ratio = complete_places / len(places) if places else 0

        if completeness_ratio < 0.8:
            issues.append(DataQualityIssue(
                category="completeness",
                severity="medium",
                message=f"Chỉ {completeness_ratio:.1%} dữ liệu doanh nghiệp đầy đủ",
                impact="Có thể thiếu sót một số đối thủ cạnh tranh",
                recommendation="Bổ sung thêm nguồn dữ liệu hoặc khảo sát thực địa"
            ))

        # Check for data consistency
        total_from_places = len(places)
        total_from_counts = sum(category_counts.values())

        if abs(total_from_places - total_from_counts) > total_from_places * 0.2:
            issues.append(DataQualityIssue(
                category="consistency",
                severity="medium",
                message="Không nhất quán giữa số lượng địa điểm và phân loại",
                impact="Có thể ảnh hưởng đến độ chính xác phân tích cạnh tranh",
                recommendation="Kiểm tra lại logic phân loại doanh nghiệp"
            ))

        # Check for suspicious patterns
        if len(places) < 5:
            issues.append(DataQualityIssue(
                category="completeness",
                severity="high",
                message="Quá ít dữ liệu doanh nghiệp để phân tích đáng tin cậy",
                impact="Kết quả phân tích có thể không chính xác",
                recommendation="Mở rộng bán kính tìm kiếm hoặc chọn khu vực khác"
            ))

        # Calculate quality score
        base_score = completeness_ratio
        penalty = len([i for i in issues if i.severity in ["high", "critical"]]) * 0.2
        quality_score = max(base_score - penalty, 0)

        return quality_score, issues

    def _validate_geographic_data(self, coordinates: Dict[str, Any]) -> Tuple[float, List[DataQualityIssue]]:
        """Validate geographic coordinates and radius"""

        issues = []

        if not coordinates:
            issues.append(DataQualityIssue(
                category="completeness",
                severity="critical",
                message="Thiếu thông tin tọa độ địa lý",
                impact="Không thể thực hiện phân tích không gian",
                recommendation="Kiểm tra dịch vụ geocoding"
            ))
            return 0.0, issues

        lat = coordinates.get("lat")
        lon = coordinates.get("lon")
        radius = coordinates.get("radius")

        # Validate coordinates
        if not lat or not lon:
            issues.append(DataQualityIssue(
                category="completeness",
                severity="critical",
                message="Tọa độ không hợp lệ",
                impact="Không thể xác định vị trí chính xác",
                recommendation="Nhập lại địa chỉ chính xác hơn"
            ))
            return 0.0, issues

        # Check coordinate ranges (Vietnam bounds approximately)
        if not (8.0 <= lat <= 23.5 and 102.0 <= lon <= 110.0):
            issues.append(DataQualityIssue(
                category="accuracy",
                severity="high",
                message="Tọa độ nằm ngoài phạm vi Việt Nam",
                impact="Có thể đang phân tích sai vị trí",
                recommendation="Kiểm tra lại địa chỉ đầu vào"
            ))

        # Validate radius
        if radius and (radius < 100 or radius > 10000):
            issues.append(DataQualityIssue(
                category="accuracy",
                severity="medium",
                message=f"Bán kính {radius}m có vẻ không hợp lý",
                impact="Có thể thu thập quá ít hoặc quá nhiều dữ liệu",
                recommendation="Điều chỉnh bán kính phù hợp (500-3000m)"
            ))

        # Calculate quality score
        quality_score = 1.0
        for issue in issues:
            if issue.severity == "critical":
                quality_score -= 0.5
            elif issue.severity == "high":
                quality_score -= 0.3
            elif issue.severity == "medium":
                quality_score -= 0.1

        return max(quality_score, 0), issues

    def _calculate_completeness_score(self, market_context: Dict[str, Any]) -> float:
        """Calculate data completeness score"""

        expected_components = [
            "osm", "category_counts", "places", "coordinates"
        ]

        present_components = 0
        for component in expected_components:
            if component in market_context and market_context[component]:
                present_components += 1

        base_completeness = present_components / len(expected_components)

        # Detailed completeness for OSM data
        osm_data = market_context.get("osm", {})
        osm_completeness = 0
        if osm_data:
            present_fields = len([f for f in self.required_osm_fields
                                  if f in osm_data and osm_data[f] > 0])
            osm_completeness = present_fields / len(self.required_osm_fields)

        # Weighted completeness
        overall_completeness = (base_completeness * 0.6 + osm_completeness * 0.4)

        return overall_completeness

    def _estimate_accuracy_score(self, market_context: Dict[str, Any],
                                 issues: List[DataQualityIssue]) -> float:
        """Estimate data accuracy based on cross-validation and patterns"""

        base_accuracy = 0.8  # Assume decent accuracy by default

        # Penalize based on accuracy issues
        accuracy_issues = [i for i in issues if i.category == "accuracy"]

        for issue in accuracy_issues:
            if issue.severity == "critical":
                base_accuracy -= 0.3
            elif issue.severity == "high":
                base_accuracy -= 0.2
            elif issue.severity == "medium":
                base_accuracy -= 0.1
            else:
                base_accuracy -= 0.05

        # Cross-validation checks
        osm_data = market_context.get("osm", {})
        places = market_context.get("places", [])

        # Check for reasonable ratios
        if osm_data and places:
            schools = osm_data.get("school", 0)
            offices = osm_data.get("office", 0)
            total_businesses = len(places)

            # If many offices but very few businesses, something might be wrong
            if offices > 10 and total_businesses < 5:
                base_accuracy -= 0.1

            # If many schools but no education-related businesses
            education_businesses = len([p for p in places
                                        if p.get("main_category") in ["bookstore", "stationery"]])
            if schools > 3 and education_businesses == 0:
                base_accuracy -= 0.05

        return max(base_accuracy, 0)

    def _check_data_consistency(self, market_context: Dict[str, Any]) -> float:
        """Check consistency between different data sources"""

        consistency_score = 1.0

        osm_data = market_context.get("osm", {})
        category_counts = market_context.get("category_counts", {})
        places = market_context.get("places", [])

        # Check business count consistency
        if places and category_counts:
            places_count = len(places)
            categories_count = sum(category_counts.values())

            if places_count > 0:
                ratio = abs(places_count - categories_count) / places_count
                if ratio > 0.3:  # More than 30% difference
                    consistency_score -= 0.2

        # Check geographic consistency
        coordinates = market_context.get("coordinates", {})
        if coordinates and places:
            # All places should be within reasonable distance of center
            center_lat = coordinates.get("lat")
            center_lon = coordinates.get("lon")
            radius = coordinates.get("radius", 2000)

            if center_lat and center_lon:
                outliers = 0
                for place in places:
                    place_lat = place.get("lat")
                    place_lon = place.get("lon")

                    if place_lat and place_lon:
                        # Rough distance calculation (not precise but good enough)
                        lat_diff = abs(center_lat - place_lat)
                        lon_diff = abs(center_lon - place_lon)

                        # Very rough: 1 degree ≈ 111km
                        estimated_distance = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111000

                        if estimated_distance > radius * 1.5:  # 50% tolerance
                            outliers += 1

                if places and outliers / len(places) > 0.2:  # More than 20% outliers
                    consistency_score -= 0.3

        return max(consistency_score, 0)

    def _assess_data_timeliness(self, market_context: Dict[str, Any]) -> float:
        """Assess how recent/fresh the data is"""

        # Since we don't have timestamp info, we make reasonable assumptions
        # OSM data is generally current, API data is real-time

        timeliness_score = 0.8  # Base assumption of reasonably fresh data

        # Check if we have minimal data (might indicate stale/cached data)
        places = market_context.get("places", [])
        osm_data = market_context.get("osm", {})

        if not places:
            timeliness_score -= 0.3  # No business data might indicate old/cached results

        if not osm_data or sum(osm_data.values()) == 0:
            timeliness_score -= 0.2  # No OSM data might indicate issues

        return max(timeliness_score, 0)

    def _generate_warnings(self, overall_quality: float,
                           issues: List[DataQualityIssue]) -> List[str]:
        """Generate user-friendly warnings about data quality"""

        warnings = []

        if overall_quality < 0.3:
            warnings.append("Chất lượng dữ liệu rất thấp - kết quả có thể không đáng tin cậy")
        elif overall_quality < 0.5:
            warnings.append("Chất lượng dữ liệu hạn chế - nên thu thập thêm thông tin")
        elif overall_quality < 0.7:
            warnings.append("Chất lượng dữ liệu tương đối tốt nhưng có thể cải thiện")

        # Critical issues warnings
        critical_issues = [i for i in issues if i.severity == "critical"]
        if critical_issues:
            warnings.append("Có vấn đề nghiêm trọng với dữ liệu - cần kiểm tra lại")

        # High severity issues
        high_issues = [i for i in issues if i.severity == "high"]
        if len(high_issues) > 2:
            warnings.append("Nhiều vấn đề quan trọng được phát hiện")

        return warnings

    def _get_quality_description(self, quality_score: float) -> str:
        """Get text description of quality score"""

        if quality_score >= self.data_quality_thresholds["excellent"]:
            return "Xuất sắc"
        elif quality_score >= self.data_quality_thresholds["good"]:
            return "Tốt"
        elif quality_score >= self.data_quality_thresholds["fair"]:
            return "Tương đối"
        elif quality_score >= self.data_quality_thresholds["poor"]:
            return "Kém"
        else:
            return "Rất kém"

    def _create_fallback_report(self) -> DataQualityReport:
        """Create a fallback report when validation fails"""

        return DataQualityReport(
            overall_quality=0.3,
            overall_quality_text="Không xác định",
            completeness_score=0.3,
            accuracy_score=0.3,
            consistency_score=0.3,
            timeliness_score=0.3,
            issues=[
                DataQualityIssue(
                    category="system",
                    severity="critical",
                    message="Lỗi hệ thống trong quá trình validation",
                    impact="Không thể đánh giá chất lượng dữ liệu",
                    recommendation="Thử lại hoặc liên hệ hỗ trợ kỹ thuật"
                )
            ],
            sources=[],
            warnings=["Không thể đánh giá chất lượng dữ liệu"],
            data_coverage={}
        )

    def validate_user_inputs(self, inputs: Dict[str, Any]) -> List[DataQualityIssue]:
        """Validate user input parameters"""

        issues = []

        # Validate address
        address = inputs.get("address", "").strip()
        if not address:
            issues.append(DataQualityIssue(
                category="input",
                severity="critical",
                message="Địa chỉ không được để trống",
                impact="Không thể thực hiện phân tích",
                recommendation="Nhập địa chỉ cụ thể"
            ))
        elif len(address) < 10:
            issues.append(DataQualityIssue(
                category="input",
                severity="medium",
                message="Địa chỉ có vẻ quá ngắn",
                impact="Có thể không xác định được vị trí chính xác",
                recommendation="Nhập địa chỉ chi tiết hơn"
            ))

        # Validate radius
        radius = inputs.get("radius")
        if radius:
            if radius < 100:
                issues.append(DataQualityIssue(
                    category="input",
                    severity="medium",
                    message="Bán kính quá nhỏ",
                    impact="Có thể thu thập quá ít dữ liệu",
                    recommendation="Tăng bán kính lên ít nhất 500m"
                ))
            elif radius > 5000:
                issues.append(DataQualityIssue(
                    category="input",
                    severity="medium",
                    message="Bán kính quá lớn",
                    impact="Có thể thu thập dữ liệu không liên quan",
                    recommendation="Giảm bán kính xuống dưới 3000m"
                ))

        # Validate price range
        price_min = inputs.get("price_min")
        price_max = inputs.get("price_max")

        if price_min and price_max and price_min > price_max:
            issues.append(DataQualityIssue(
                category="input",
                severity="medium",
                message="Giá tối thiểu lớn hơn giá tối đa",
                impact="Có thể lọc sai dữ liệu",
                recommendation="Kiểm tra lại khoảng giá"
            ))

        return issues

    def get_data_quality_recommendations(self, report: DataQualityReport) -> List[str]:
        """Get recommendations to improve data quality"""

        recommendations = []

        if report.completeness_score < 0.7:
            recommendations.append("Thu thập thêm dữ liệu từ các nguồn khác")
            recommendations.append("Mở rộng bán kính tìm kiếm")
            recommendations.append("Khảo sát thực địa để bổ sung thông tin")

        if report.accuracy_score < 0.7:
            recommendations.append("Xác minh dữ liệu bằng nguồn thứ hai")
            recommendations.append("Kiểm tra thủ công các thông tin quan trọng")

        if report.consistency_score < 0.7:
            recommendations.append("Đối chiếu dữ liệu giữa các nguồn")
            recommendations.append("Kiểm tra lại logic phân loại dữ liệu")

        # High-severity issue recommendations
        critical_issues = [i for i in report.issues if i.severity == "critical"]
        for issue in critical_issues:
            if issue.recommendation not in recommendations:
                recommendations.append(issue.recommendation)

        return recommendations[:5]  # Top 5 recommendations