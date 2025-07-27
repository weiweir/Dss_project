# report_generator.py
from typing import Dict, List, Any, Optional
import json
import csv
import io
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate various types of reports from business analysis data"""

    def __init__(self):
        self.report_templates = {
            "executive": self._executive_template,
            "detailed": self._detailed_template,
            "comparison": self._comparison_template,
            "risk_assessment": self._risk_template
        }

    def generate_pdf_report(self, analysis_data: Dict[str, Any],
                            report_type: str = "executive") -> bytes:
        """
        Generate PDF report (simplified implementation)
        In production, you'd use libraries like ReportLab or WeasyPrint
        """
        try:
            # This is a simplified version - in production use proper PDF libraries
            html_content = self.generate_html_report(analysis_data, report_type)

            # Convert HTML to PDF (placeholder)
            # In real implementation:
            # from weasyprint import HTML
            # return HTML(string=html_content).write_pdf()

            # For now, return HTML as bytes
            return html_content.encode('utf-8')

        except Exception as e:
            logger.error(f"PDF generation error: {str(e)}")
            return b"Error generating PDF report"

    def generate_excel_report(self, analysis_data: Dict[str, Any]) -> bytes:
        """
        Generate Excel report with multiple sheets
        """
        try:
            # This requires openpyxl or xlsxwriter
            # For now, return CSV-like data

            output = io.StringIO()

            # Summary sheet
            output.write("BUSINESS ANALYSIS REPORT\n\n")

            # Executive Summary
            exec_summary = analysis_data.get("executive_summary", {})
            output.write("EXECUTIVE SUMMARY\n")
            output.write(f"Market Attractiveness: {exec_summary.get('market_attractiveness', 'N/A')}\n")

            # Top opportunities
            top_opps = exec_summary.get("top_opportunities", [])
            output.write("\nTOP OPPORTUNITIES\n")
            for i, opp in enumerate(top_opps, 1):
                output.write(f"{i}. {opp.get('name', 'N/A')} - {opp.get('score', 0)}%\n")

            # Detailed results
            output.write("\n\nDETAILED RESULTS\n")
            output.write("Business,Score,Risk Level,Key Reason\n")

            detailed_results = analysis_data.get("detailed_results", [])
            for result in detailed_results:
                if result.get("scoring_result"):
                    name = result.get("name", "N/A")
                    score = result["scoring_result"].get("score", 0)
                    risk = result.get("risk_assessment", {}).get("level", "unknown")
                    reason = result["scoring_result"].get("reasons", [""])[0] if result["scoring_result"].get(
                        "reasons") else "N/A"

                    output.write(f'"{name}",{score},"{risk}","{reason}"\n')

            content = output.getvalue()
            output.close()

            return content.encode('utf-8')

        except Exception as e:
            logger.error(f"Excel generation error: {str(e)}")
            return b"Error generating Excel report"

    def generate_html_report(self, analysis_data: Dict[str, Any],
                             report_type: str = "executive") -> str:
        """Generate HTML report"""

        try:
            template_func = self.report_templates.get(report_type, self._executive_template)
            return template_func(analysis_data)

        except Exception as e:
            logger.error(f"HTML report generation error: {str(e)}")
            return f"<html><body><h1>Error generating report: {str(e)}</h1></body></html>"

    def generate_json_report(self, analysis_data: Dict[str, Any]) -> str:
        """Generate JSON report for API consumption"""

        try:
            # Clean and structure data for JSON export
            report_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "report_version": "1.0",
                    "analysis_type": "business_location_analysis"
                },
                "executive_summary": analysis_data.get("executive_summary", {}),
                "market_overview": analysis_data.get("market_overview", {}),
                "top_recommendations": analysis_data.get("top_recommendations", []),
                "risk_matrix": analysis_data.get("risk_matrix", {}),
                "detailed_results": self._format_detailed_results_for_json(
                    analysis_data.get("detailed_results", [])
                ),
                "methodology": analysis_data.get("methodology", {}),
                "data_sources": analysis_data.get("data_sources", {})
            }

            return json.dumps(report_data, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"JSON report generation error: {str(e)}")
            return json.dumps({"error": f"Report generation failed: {str(e)}"})

    def generate_csv_report(self, analysis_data: Dict[str, Any]) -> str:
        """Generate CSV report for data analysis"""

        try:
            output = io.StringIO()
            writer = csv.writer(output)

            # Header
            writer.writerow([
                "Business_ID", "Business_Name", "Score", "Confidence",
                "Risk_Level", "Customer_Match", "Competition_Level",
                "Market_Potential", "Financial_Viability", "Key_Reason"
            ])

            # Data rows
            detailed_results = analysis_data.get("detailed_results", [])
            for result in detailed_results:
                if result.get("scoring_result"):
                    scoring = result["scoring_result"]
                    risk = result.get("risk_assessment", {})

                    row = [
                        result.get("id", ""),
                        result.get("name", ""),
                        scoring.get("score", 0),
                        scoring.get("confidence", 0),
                        risk.get("level", "unknown"),
                        # These would come from detailed scoring breakdown
                        "",  # customer_match
                        "",  # competition_level
                        "",  # market_potential
                        "",  # financial_viability
                        scoring.get("reasons", [""])[0] if scoring.get("reasons") else ""
                    ]
                    writer.writerow(row)

            content = output.getvalue()
            output.close()

            return content

        except Exception as e:
            logger.error(f"CSV report generation error: {str(e)}")
            return f"Error generating CSV report: {str(e)}"

    def _executive_template(self, data: Dict[str, Any]) -> str:
        """Executive summary report template"""

        exec_summary = data.get("executive_summary", {})
        market_overview = data.get("market_overview", {})
        top_recs = data.get("top_recommendations", [])

        html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Báo cáo Phân tích Kinh doanh - Tóm tắt Điều hành</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .header { text-align: center; margin-bottom: 40px; }
        .section { margin-bottom: 30px; }
        .metric { display: inline-block; margin: 10px 20px; padding: 15px; 
                 background: #f5f5f5; border-radius: 8px; text-align: center; }
        .recommendation { padding: 10px; margin: 5px 0; background: #e8f4fd; 
                        border-left: 4px solid #2196F3; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        .score-high { color: #4CAF50; font-weight: bold; }
        .score-medium { color: #FF9800; font-weight: bold; }
        .score-low { color: #F44336; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Báo cáo Phân tích Kinh doanh</h1>
        <h2>Tóm tắt Điều hành</h2>
        <p>Ngày tạo: """ + datetime.now().strftime('%d/%m/%Y %H:%M') + """</p>
    </div>

    <div class="section">
        <h3>Tổng quan Thị trường</h3>
        <div class="metric">
            <h4>Sức hấp dẫn</h4>
            <p>""" + str(exec_summary.get('market_attractiveness', 'N/A')).title() + """</p>
        </div>
        <div class="metric">
            <h4>Cơ hội cao</h4>
            <p>""" + str(exec_summary.get('opportunity_distribution', {}).get('high_potential', 0)) + """</p>
        </div>
        <div class="metric">
            <h4>Điểm hạ tầng</h4>
            <p>""" + f"{market_overview.get('infrastructure_score', 0):.1f}/1.0" + """</p>
        </div>
        <div class="metric">
            <h4>Mật độ cạnh tranh</h4>
            <p>""" + str(market_overview.get('competition_density', 0)) + """ doanh nghiệp</p>
        </div>
    </div>

    <div class="section">
        <h3>Top 3 Cơ hội Tốt nhất</h3>
        <table>
            <thead>
                <tr><th>Ngành</th><th>Điểm số</th><th>Lý do chính</th></tr>
            </thead>
            <tbody>"""

        for opp in exec_summary.get("top_opportunities", []):
            score = opp.get("score", 0)
            score_class = "score-high" if score >= 70 else "score-medium" if score >= 50 else "score-low"

            html += f"""
                <tr>
                    <td>{opp.get('name', 'N/A')}</td>
                    <td class="{score_class}">{score}%</td>
                    <td>{opp.get('key_reason', 'N/A')}</td>
                </tr>"""

        html += """
            </tbody>
        </table>
    </div>

    <div class="section">
        <h3>Khuyến nghị Chính</h3>"""

        for i, rec in enumerate(top_recs[:5], 1):
            html += f"""
        <div class="recommendation">
            <strong>{i}. {rec.get('name', 'N/A')}</strong><br>
            Điểm: {rec.get('score', 0)}% | 
            Rủi ro: {rec.get('risk_level', 'unknown')} | 
            Tin cậy: {rec.get('confidence', 0):.0%}<br>
            <em>{rec.get('top_recommendation', 'Không có khuyến nghị')}</em>
        </div>"""

        html += """
    </div>

    <div class="section">
        <h3>Nhận định Quan trọng</h3>
        <ul>"""

        for insight in exec_summary.get("key_insights", []):
            html += f"<li>{insight}</li>"

        html += """
        </ul>
    </div>

    <div class="section">
        <p><em>Báo cáo được tạo bởi Hệ thống Hỗ trợ Quyết định Kinh doanh (DSS)</em></p>
    </div>
</body>
</html>"""

        return html

    def _detailed_template(self, data: Dict[str, Any]) -> str:
        """Detailed analysis report template"""

        detailed_results = data.get("detailed_results", [])
        methodology = data.get("methodology", {})
        data_sources = data.get("data_sources", {})

        html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Báo cáo Phân tích Kinh doanh - Chi tiết</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        .header { text-align: center; margin-bottom: 30px; }
        .business-card { margin: 20px 0; padding: 20px; border: 1px solid #ddd; 
                       border-radius: 8px; background: #fafafa; }
        .score { font-size: 24px; font-weight: bold; }
        .reasons { margin: 10px 0; }
        .warnings { color: #d32f2f; margin: 10px 0; }
        .recommendations { color: #1976d2; margin: 10px 0; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Báo cáo Phân tích Kinh doanh Chi tiết</h1>
        <p>Ngày tạo: """ + datetime.now().strftime('%d/%m/%Y %H:%M') + """</p>
    </div>

    <div class="section">
        <h2>Kết quả Phân tích Chi tiết</h2>"""

        for result in detailed_results:
            if result.get("scoring_result"):
                scoring = result["scoring_result"]
                risk = result.get("risk_assessment", {})

                html += f"""
        <div class="business-card">
            <h3>{result.get('name', 'N/A')}</h3>
            <div class="score">Điểm: {scoring.get('score', 0)}%</div>
            <p><strong>Độ tin cậy:</strong> {scoring.get('confidence', 0):.0%}</p>
            <p><strong>Mức rủi ro:</strong> {risk.get('level', 'unknown')}</p>

            <div class="reasons">
                <strong>Lý do tích cực:</strong>
                <ul>"""

                for reason in scoring.get("reasons", []):
                    html += f"<li>{reason}</li>"

                html += """
                </ul>
            </div>"""

                if result.get("rule_results"):
                    html += """
            <div class="warnings">
                <strong>Cảnh báo:</strong>
                <ul>"""
                    for rule in result["rule_results"]:
                        html += f"<li>{rule.get('message', 'N/A')}</li>"

                    html += """
                </ul>
            </div>"""

                if scoring.get("recommendations"):
                    html += """
            <div class="recommendations">
                <strong>Khuyến nghị:</strong>
                <ul>"""
                    for rec in scoring["recommendations"]:
                        html += f"<li>{rec}</li>"

                    html += """
                </ul>
            </div>"""

                html += "</div>"

        # Add methodology section
        html += f"""
    </div>

    <div class="section">
        <h2>Phương pháp Phân tích</h2>
        <table>
            <tr><th>Mô hình chấm điểm</th><td>{methodology.get('scoring_model', 'N/A')}</td></tr>
            <tr><th>Nguồn dữ liệu</th><td>{methodology.get('data_sources', 'N/A')}</td></tr>
            <tr><th>Hệ thống luật</th><td>{methodology.get('rules_engine', 'N/A')}</td></tr>
            <tr><th>Tính độ tin cậy</th><td>{methodology.get('confidence_calculation', 'N/A')}</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>Thông tin Dữ liệu</h2>
        <table>
            <tr><th>Dữ liệu địa lý</th><td>{data_sources.get('geographic_data', 'N/A')}</td></tr>
            <tr><th>Dữ liệu doanh nghiệp</th><td>{data_sources.get('business_data', 'N/A')}</td></tr>
            <tr><th>Số địa điểm phân tích</th><td>{data_sources.get('places_analyzed', 'N/A')}</td></tr>
            <tr><th>Tính năng OSM</th><td>{data_sources.get('osm_features', 'N/A')}</td></tr>
            <tr><th>Chất lượng dữ liệu</th><td>{data_sources.get('data_quality', 'N/A')}</td></tr>
        </table>
    </div>
</body>
</html>"""

        return html

    def _comparison_template(self, data: Dict[str, Any]) -> str:
        """Comparison report template"""

        top_recs = data.get("top_recommendations", [])[:5]  # Top 5 for comparison

        html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Báo cáo So sánh Ngành</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        .header { text-align: center; margin-bottom: 30px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: center; border: 1px solid #ddd; }
        th { background-color: #f2f2f2; font-weight: bold; }
        .score-high { background-color: #c8e6c9; }
        .score-medium { background-color: #ffe0b2; }
        .score-low { background-color: #ffcdd2; }
        .business-name { text-align: left; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Báo cáo So sánh Top 5 Ngành</h1>
        <p>Ngày tạo: """ + datetime.now().strftime('%d/%m/%Y %H:%M') + """</p>
    </div>

    <table>
        <thead>
            <tr>
                <th>Ngành</th>
                <th>Điểm tổng</th>
                <th>Độ tin cậy</th>
                <th>Mức rủi ro</th>
                <th>Ranking</th>
            </tr>
        </thead>
        <tbody>"""

        for i, rec in enumerate(top_recs, 1):
            score = rec.get("score", 0)
            confidence = rec.get("confidence", 0)
            risk_level = rec.get("risk_level", "unknown")

            # Determine score class
            if score >= 70:
                score_class = "score-high"
            elif score >= 50:
                score_class = "score-medium"
            else:
                score_class = "score-low"

            html += f"""
            <tr class="{score_class}">
                <td class="business-name">{rec.get('name', 'N/A')}</td>
                <td>{score}%</td>
                <td>{confidence:.0%}</td>
                <td>{risk_level}</td>
                <td>#{i}</td>
            </tr>"""

        html += """
        </tbody>
    </table>

    <div class="section">
        <h3>Phân tích So sánh</h3>
        <p>Bảng trên cho thấy top 5 ngành có tiềm năng nhất dựa trên:</p>
        <ul>
            <li><strong>Điểm tổng:</strong> Tổng hợp từ 8 yếu tố chính</li>
            <li><strong>Độ tin cậy:</strong> Mức độ chắc chắn của dự đoán</li>
            <li><strong>Mức rủi ro:</strong> Đánh giá rủi ro tổng thể</li>
        </ul>
    </div>
</body>
</html>"""

        return html

    def _risk_template(self, data: Dict[str, Any]) -> str:
        """Risk assessment report template"""

        risk_matrix = data.get("risk_matrix", {})

        html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Báo cáo Đánh giá Rủi ro</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        .header { text-align: center; margin-bottom: 30px; }
        .risk-section { margin: 20px 0; padding: 15px; border-radius: 8px; }
        .risk-very-low { background-color: #e8f5e8; border-left: 5px solid #4caf50; }
        .risk-low { background-color: #e3f2fd; border-left: 5px solid #2196f3; }
        .risk-medium { background-color: #fff3e0; border-left: 5px solid #ff9800; }
        .risk-high { background-color: #ffebee; border-left: 5px solid #f44336; }
        .risk-very-high { background-color: #fce4ec; border-left: 5px solid #e91e63; }
        .business-item { margin: 5px 0; padding: 8px; background: rgba(255,255,255,0.7); 
                       border-radius: 4px; display: flex; justify-content: space-between; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Báo cáo Đánh giá Rủi ro</h1>
        <p>Ngày tạo: """ + datetime.now().strftime('%d/%m/%Y %H:%M') + """</p>
    </div>"""

        risk_labels = {
            "very_low": "Rủi ro Rất Thấp",
            "low": "Rủi ro Thấp",
            "medium": "Rủi ro Trung Bình",
            "high": "Rủi ro Cao",
            "very_high": "Rủi ro Rất Cao"
        }

        for risk_level, businesses in risk_matrix.items():
            if businesses:
                html += f"""
    <div class="risk-section risk-{risk_level}">
        <h3>{risk_labels.get(risk_level, risk_level)}</h3>"""

                for business in businesses:
                    html += f"""
        <div class="business-item">
            <span>{business.get('name', 'N/A')}</span>
            <span><strong>{business.get('score', 0)}%</strong></span>
        </div>"""

                html += "</div>"

        html += """
    <div class="section">
        <h3>Hướng dẫn Đánh giá Rủi ro</h3>
        <ul>
            <li><strong>Rủi ro Rất Thấp:</strong> An toàn để đầu tư, ít biến động</li>
            <li><strong>Rủi ro Thấp:</strong> Tương đối an toàn, cần theo dõi</li>
            <li><strong>Rủi ro Trung Bình:</strong> Cần nghiên cứu kỹ trước khi quyết định</li>
            <li><strong>Rủi ro Cao:</strong> Cần cân nhắc cẩn trọng, có kế hoạch dự phòng</li>
            <li><strong>Rủi ro Rất Cao:</strong> Không khuyến khích đầu tư</li>
        </ul>
    </div>
</body>
</html>"""

        return html

    def _format_detailed_results_for_json(self, detailed_results: List[Dict]) -> List[Dict]:
        """Format detailed results for JSON export"""

        formatted = []

        for result in detailed_results:
            if result.get("scoring_result"):
                formatted_result = {
                    "business_id": result.get("id"),
                    "business_name": result.get("name"),
                    "score": result["scoring_result"].get("score"),
                    "confidence": result["scoring_result"].get("confidence"),
                    "risk_assessment": result.get("risk_assessment", {}),
                    "key_reasons": result["scoring_result"].get("reasons", []),
                    "warnings": [r.get("message") for r in result.get("rule_results", [])],
                    "recommendations": result["scoring_result"].get("recommendations", []),
                    "market_fit_score": result.get("market_fit_score")
                }
                formatted.append(formatted_result)

        return formatted

    def generate_dashboard_data(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data formatted for dashboard visualization"""

        try:
            detailed_results = analysis_data.get("detailed_results", [])

            # Prepare chart data
            chart_data = {
                "score_distribution": self._prepare_score_distribution(detailed_results),
                "risk_distribution": self._prepare_risk_distribution(detailed_results),
                "top_businesses": self._prepare_top_businesses_chart(detailed_results),
                "market_metrics": self._prepare_market_metrics(analysis_data)
            }

            return {
                "charts": chart_data,
                "summary_stats": self._calculate_summary_stats(detailed_results),
                "alerts": self._generate_dashboard_alerts(analysis_data)
            }

        except Exception as e:
            logger.error(f"Dashboard data generation error: {str(e)}")
            return {"error": str(e)}

    def _prepare_score_distribution(self, results: List[Dict]) -> Dict[str, Any]:
        """Prepare score distribution data for charts"""

        score_ranges = {
            "0-30": 0, "31-50": 0, "51-70": 0, "71-100": 0
        }

        for result in results:
            if result.get("scoring_result"):
                score = result["scoring_result"].get("score", 0)

                if score <= 30:
                    score_ranges["0-30"] += 1
                elif score <= 50:
                    score_ranges["31-50"] += 1
                elif score <= 70:
                    score_ranges["51-70"] += 1
                else:
                    score_ranges["71-100"] += 1

        return {
            "labels": list(score_ranges.keys()),
            "data": list(score_ranges.values()),
            "chart_type": "bar"
        }

    def _prepare_risk_distribution(self, results: List[Dict]) -> Dict[str, Any]:
        """Prepare risk distribution data for charts"""

        risk_counts = {
            "very_low": 0, "low": 0, "medium": 0, "high": 0, "very_high": 0
        }

        for result in results:
            risk_level = result.get("risk_assessment", {}).get("level", "medium")
            if risk_level in risk_counts:
                risk_counts[risk_level] += 1

        return {
            "labels": ["Rất thấp", "Thấp", "Trung bình", "Cao", "Rất cao"],
            "data": list(risk_counts.values()),
            "chart_type": "pie"
        }

    def _prepare_top_businesses_chart(self, results: List[Dict]) -> Dict[str, Any]:
        """Prepare top businesses chart data"""

        # Sort by score and take top 10
        scored_results = [r for r in results if r.get("scoring_result")]
        scored_results.sort(key=lambda x: x["scoring_result"].get("score", 0), reverse=True)

        top_10 = scored_results[:10]

        return {
            "labels": [r.get("name", "N/A") for r in top_10],
            "data": [r["scoring_result"].get("score", 0) for r in top_10],
            "chart_type": "horizontal_bar"
        }

    def _prepare_market_metrics(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare market metrics for dashboard"""

        market_overview = analysis_data.get("market_overview", {})
        exec_summary = analysis_data.get("executive_summary", {})

        return {
            "infrastructure_score": market_overview.get("infrastructure_score", 0),
            "competition_density": market_overview.get("competition_density", 0),
            "market_attractiveness": exec_summary.get("market_attractiveness", "medium"),
            "high_potential_count": exec_summary.get("opportunity_distribution", {}).get("high_potential", 0)
        }

    def _calculate_summary_stats(self, results: List[Dict]) -> Dict[str, Any]:
        """Calculate summary statistics"""

        scored_results = [r for r in results if r.get("scoring_result")]

        if not scored_results:
            return {}

        scores = [r["scoring_result"].get("score", 0) for r in scored_results]

        return {
            "total_analyzed": len(scored_results),
            "average_score": sum(scores) / len(scores),
            "highest_score": max(scores),
            "lowest_score": min(scores),
            "above_threshold": len([s for s in scores if s >= 60]),
            "recommended_businesses": len([s for s in scores if s >= 70])
        }

    def _generate_dashboard_alerts(self, analysis_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate alerts for dashboard"""

        alerts = []

        # Check data quality
        data_quality = analysis_data.get("data_quality", {})
        if data_quality and data_quality.get("overall_quality", 1) < 0.5:
            alerts.append({
                "type": "warning",
                "message": "Chất lượng dữ liệu thấp - kết quả có thể không chính xác"
            })

        # Check for high-risk opportunities
        detailed_results = analysis_data.get("detailed_results", [])
        high_risk_count = len([r for r in detailed_results
                               if r.get("risk_assessment", {}).get("level") in ["high", "very_high"]])

        if high_risk_count > len(detailed_results) * 0.5:
            alerts.append({
                "type": "error",
                "message": f"Nhiều ngành có rủi ro cao ({high_risk_count} ngành)"
            })

        # Check for excellent opportunities
        excellent_count = len([r for r in detailed_results
                               if r.get("scoring_result", {}).get("score", 0) >= 80])

        if excellent_count > 0:
            alerts.append({
                "type": "success",
                "message": f"Phát hiện {excellent_count} cơ hội xuất sắc"
            })

        return alerts

    def create_presentation_slides(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create presentation slides data"""

        slides = []

        # Title slide
        slides.append({
            "title": "Báo cáo Phân tích Kinh doanh",
            "content": f"Ngày: {datetime.now().strftime('%d/%m/%Y')}",
            "type": "title"
        })

        # Executive summary slide
        exec_summary = analysis_data.get("executive_summary", {})
        slides.append({
            "title": "Tóm tắt Điều hành",
            "content": {
                "market_attractiveness": exec_summary.get("market_attractiveness"),
                "top_opportunities": exec_summary.get("top_opportunities", [])[:3]
            },
            "type": "summary"
        })

        # Market overview slide
        market_overview = analysis_data.get("market_overview", {})
        slides.append({
            "title": "Tổng quan Thị trường",
            "content": market_overview,
            "type": "market"
        })

        # Top recommendations slide
        top_recs = analysis_data.get("top_recommendations", [])[:5]
        slides.append({
            "title": "Khuyến nghị Hàng đầu",
            "content": top_recs,
            "type": "recommendations"
        })

        # Risk analysis slide
        risk_matrix = analysis_data.get("risk_matrix", {})
        slides.append({
            "title": "Phân tích Rủi ro",
            "content": risk_matrix,
            "type": "risk"
        })

        return slides