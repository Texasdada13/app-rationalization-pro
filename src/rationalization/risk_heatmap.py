"""
Risk Heat Map Engine for Application Rationalization Pro
Visualizes risk across multiple dimensions for portfolio analysis.

Features:
- Multi-Dimensional Risk Scoring
- Heat Map Data Generation
- Risk Correlation Analysis
- Trend Detection
- Threshold Alerting
- Executive Risk Summaries
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from datetime import datetime
from collections import defaultdict
import random
import math


class RiskCategory(Enum):
    """Risk categories for analysis."""
    TECHNICAL = "technical"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    VENDOR = "vendor"
    BUSINESS = "business"
    DATA = "data"


class RiskSeverity(Enum):
    """Risk severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class TrendIndicator(Enum):
    """Risk trend indicators."""
    INCREASING = "increasing"
    STABLE = "stable"
    DECREASING = "decreasing"


@dataclass
class RiskDimension:
    """A risk dimension with score and details."""
    category: RiskCategory
    score: float  # 0-100
    severity: RiskSeverity
    trend: TrendIndicator = TrendIndicator.STABLE

    # Details
    contributing_factors: List[str] = field(default_factory=list)
    mitigation_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "category": self.category.value,
            "score": self.score,
            "severity": self.severity.value,
            "trend": self.trend.value,
            "contributing_factors": self.contributing_factors,
            "mitigation_actions": self.mitigation_actions
        }


@dataclass
class ApplicationRiskProfile:
    """Complete risk profile for an application."""
    app_id: str
    app_name: str

    # Overall risk
    overall_score: float = 0.0
    overall_severity: RiskSeverity = RiskSeverity.MEDIUM

    # Dimension scores
    dimensions: Dict[RiskCategory, RiskDimension] = field(default_factory=dict)

    # Metadata
    category: str = ""
    business_unit: str = ""
    vendor: str = ""
    user_count: int = 0
    annual_cost: float = 0.0

    # Additional context
    last_assessment: Optional[datetime] = None
    assessment_confidence: float = 0.8

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "app_id": self.app_id,
            "app_name": self.app_name,
            "overall_score": self.overall_score,
            "overall_severity": self.overall_severity.value,
            "dimensions": {k.value: v.to_dict() for k, v in self.dimensions.items()},
            "category": self.category,
            "business_unit": self.business_unit,
            "vendor": self.vendor,
            "user_count": self.user_count,
            "annual_cost": self.annual_cost,
            "last_assessment": self.last_assessment.isoformat() if self.last_assessment else None,
            "assessment_confidence": self.assessment_confidence
        }


@dataclass
class HeatMapCell:
    """A cell in the heat map grid."""
    x_value: str  # X-axis category
    y_value: str  # Y-axis category
    risk_score: float
    severity: RiskSeverity
    application_count: int
    applications: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "x_value": self.x_value,
            "y_value": self.y_value,
            "risk_score": self.risk_score,
            "severity": self.severity.value,
            "application_count": self.application_count,
            "applications": self.applications
        }


@dataclass
class HeatMapData:
    """Complete heat map data for visualization."""
    title: str
    x_axis_label: str
    y_axis_label: str
    x_categories: List[str] = field(default_factory=list)
    y_categories: List[str] = field(default_factory=list)
    cells: List[HeatMapCell] = field(default_factory=list)

    # Summary
    max_risk: float = 0.0
    avg_risk: float = 0.0
    hotspots: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "x_axis_label": self.x_axis_label,
            "y_axis_label": self.y_axis_label,
            "x_categories": self.x_categories,
            "y_categories": self.y_categories,
            "cells": [c.to_dict() for c in self.cells],
            "max_risk": self.max_risk,
            "avg_risk": self.avg_risk,
            "hotspots": self.hotspots
        }


@dataclass
class RiskCorrelation:
    """Correlation between risk dimensions."""
    dimension_1: RiskCategory
    dimension_2: RiskCategory
    correlation: float  # -1 to 1
    strength: str  # weak, moderate, strong
    insight: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "dimension_1": self.dimension_1.value,
            "dimension_2": self.dimension_2.value,
            "correlation": self.correlation,
            "strength": self.strength,
            "insight": self.insight
        }


@dataclass
class RiskAlert:
    """A risk alert or threshold breach."""
    alert_id: str
    severity: RiskSeverity
    category: RiskCategory
    title: str
    description: str
    affected_apps: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "severity": self.severity.value,
            "category": self.category.value,
            "title": self.title,
            "description": self.description,
            "affected_apps": self.affected_apps,
            "recommended_actions": self.recommended_actions,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class RiskSummary:
    """Executive risk summary."""
    total_applications: int = 0
    assessed_applications: int = 0

    # Severity distribution
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0

    # Average scores by dimension
    dimension_averages: Dict[str, float] = field(default_factory=dict)

    # Top risks
    top_risks: List[Dict] = field(default_factory=list)

    # Trends
    overall_trend: TrendIndicator = TrendIndicator.STABLE
    improving_dimensions: List[str] = field(default_factory=list)
    worsening_dimensions: List[str] = field(default_factory=list)

    # Alerts
    active_alerts: int = 0
    critical_alerts: int = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "total_applications": self.total_applications,
            "assessed_applications": self.assessed_applications,
            "critical_count": self.critical_count,
            "high_count": self.high_count,
            "medium_count": self.medium_count,
            "low_count": self.low_count,
            "dimension_averages": self.dimension_averages,
            "top_risks": self.top_risks,
            "overall_trend": self.overall_trend.value,
            "improving_dimensions": self.improving_dimensions,
            "worsening_dimensions": self.worsening_dimensions,
            "active_alerts": self.active_alerts,
            "critical_alerts": self.critical_alerts
        }


@dataclass
class RiskHeatMapResult:
    """Complete risk heat map analysis result."""
    summary: RiskSummary
    heat_maps: Dict[str, HeatMapData] = field(default_factory=dict)
    correlations: List[RiskCorrelation] = field(default_factory=list)
    alerts: List[RiskAlert] = field(default_factory=list)
    application_profiles: List[ApplicationRiskProfile] = field(default_factory=list)

    # Metadata
    generated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "summary": self.summary.to_dict(),
            "heat_maps": {k: v.to_dict() for k, v in self.heat_maps.items()},
            "correlations": [c.to_dict() for c in self.correlations],
            "alerts": [a.to_dict() for a in self.alerts],
            "application_profiles": [p.to_dict() for p in self.application_profiles],
            "generated_at": self.generated_at.isoformat()
        }


class RiskHeatMapEngine:
    """
    Risk Heat Map Engine for portfolio risk visualization.
    """

    # Severity thresholds
    SEVERITY_THRESHOLDS = {
        RiskSeverity.CRITICAL: 80,
        RiskSeverity.HIGH: 60,
        RiskSeverity.MEDIUM: 40,
        RiskSeverity.LOW: 20,
        RiskSeverity.MINIMAL: 0
    }

    # Risk dimension weights
    DIMENSION_WEIGHTS = {
        RiskCategory.SECURITY: 1.2,
        RiskCategory.COMPLIANCE: 1.1,
        RiskCategory.TECHNICAL: 1.0,
        RiskCategory.OPERATIONAL: 0.9,
        RiskCategory.VENDOR: 0.9,
        RiskCategory.FINANCIAL: 0.8,
        RiskCategory.BUSINESS: 0.8,
        RiskCategory.DATA: 1.0,
    }

    # Contributing factors by category
    RISK_FACTORS = {
        RiskCategory.TECHNICAL: [
            "Outdated technology stack",
            "Unsupported platform version",
            "Complex integration dependencies",
            "Poor code quality metrics",
            "Lack of automated testing",
            "Single point of failure",
        ],
        RiskCategory.SECURITY: [
            "Known vulnerabilities unpatched",
            "Missing encryption",
            "Weak authentication",
            "Insufficient access controls",
            "Lack of security monitoring",
            "Exposed sensitive data",
        ],
        RiskCategory.COMPLIANCE: [
            "Missing audit logs",
            "Data retention violations",
            "Certification gaps",
            "Policy non-compliance",
            "Documentation deficiencies",
            "Control weaknesses",
        ],
        RiskCategory.OPERATIONAL: [
            "Insufficient monitoring",
            "Missing disaster recovery",
            "Inadequate backup procedures",
            "Manual processes",
            "Knowledge concentration",
            "Poor incident response",
        ],
        RiskCategory.VENDOR: [
            "Vendor financial instability",
            "Contract expiration approaching",
            "Limited support options",
            "Lock-in concerns",
            "Integration limitations",
            "Roadmap misalignment",
        ],
        RiskCategory.FINANCIAL: [
            "Unexpected cost increases",
            "Budget overruns",
            "Hidden costs identified",
            "Poor cost visibility",
            "Unsustainable licensing",
            "Maintenance cost growth",
        ],
        RiskCategory.BUSINESS: [
            "Low user adoption",
            "Declining business value",
            "Strategic misalignment",
            "Functionality gaps",
            "User satisfaction issues",
            "Competitive disadvantage",
        ],
        RiskCategory.DATA: [
            "Data quality issues",
            "Integration data gaps",
            "Master data conflicts",
            "Orphaned data concerns",
            "Migration complexity",
            "Privacy concerns",
        ],
    }

    # Mitigation actions by category
    MITIGATION_ACTIONS = {
        RiskCategory.TECHNICAL: [
            "Plan technology upgrade",
            "Implement automated testing",
            "Address technical debt",
            "Improve code quality",
        ],
        RiskCategory.SECURITY: [
            "Apply security patches",
            "Implement encryption",
            "Strengthen authentication",
            "Conduct security audit",
        ],
        RiskCategory.COMPLIANCE: [
            "Complete compliance assessment",
            "Update documentation",
            "Implement required controls",
            "Schedule certification renewal",
        ],
        RiskCategory.OPERATIONAL: [
            "Implement monitoring",
            "Create DR plan",
            "Document procedures",
            "Cross-train team members",
        ],
        RiskCategory.VENDOR: [
            "Evaluate alternatives",
            "Negotiate contract terms",
            "Plan migration strategy",
            "Reduce dependencies",
        ],
        RiskCategory.FINANCIAL: [
            "Conduct cost analysis",
            "Optimize licensing",
            "Reduce infrastructure costs",
            "Improve cost tracking",
        ],
        RiskCategory.BUSINESS: [
            "Increase user training",
            "Gather user feedback",
            "Align with business strategy",
            "Evaluate alternatives",
        ],
        RiskCategory.DATA: [
            "Implement data quality program",
            "Create data governance",
            "Plan data migration",
            "Address privacy gaps",
        ],
    }

    def __init__(self):
        """Initialize heat map engine."""
        self._applications: List[ApplicationRiskProfile] = []
        self._alerts: List[RiskAlert] = []
        self._alert_counter = 0

    def add_application(self, app: ApplicationRiskProfile) -> None:
        """Add an application risk profile."""
        self._applications.append(app)

    def add_applications(self, apps: List[ApplicationRiskProfile]) -> None:
        """Add multiple application risk profiles."""
        self._applications.extend(apps)

    def clear_applications(self) -> None:
        """Clear all applications."""
        self._applications = []
        self._alerts = []

    def _score_to_severity(self, score: float) -> RiskSeverity:
        """Convert risk score to severity level."""
        if score >= self.SEVERITY_THRESHOLDS[RiskSeverity.CRITICAL]:
            return RiskSeverity.CRITICAL
        elif score >= self.SEVERITY_THRESHOLDS[RiskSeverity.HIGH]:
            return RiskSeverity.HIGH
        elif score >= self.SEVERITY_THRESHOLDS[RiskSeverity.MEDIUM]:
            return RiskSeverity.MEDIUM
        elif score >= self.SEVERITY_THRESHOLDS[RiskSeverity.LOW]:
            return RiskSeverity.LOW
        else:
            return RiskSeverity.MINIMAL

    def _calculate_overall_score(self, dimensions: Dict[RiskCategory, RiskDimension]) -> float:
        """Calculate weighted overall risk score."""
        if not dimensions:
            return 0.0

        total_weight = 0.0
        weighted_sum = 0.0

        for category, dimension in dimensions.items():
            weight = self.DIMENSION_WEIGHTS.get(category, 1.0)
            weighted_sum += dimension.score * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _generate_contributing_factors(
        self,
        category: RiskCategory,
        score: float
    ) -> List[str]:
        """Generate contributing factors based on score."""
        all_factors = self.RISK_FACTORS.get(category, [])
        if not all_factors:
            return []

        # Higher scores = more factors
        factor_count = min(len(all_factors), max(1, int(score / 25)))
        return random.sample(all_factors, factor_count)

    def _generate_mitigation_actions(
        self,
        category: RiskCategory,
        score: float
    ) -> List[str]:
        """Generate mitigation actions based on category and score."""
        all_actions = self.MITIGATION_ACTIONS.get(category, [])
        if not all_actions:
            return []

        action_count = min(len(all_actions), max(1, int(score / 30)))
        return random.sample(all_actions, action_count)

    def _check_thresholds_and_create_alerts(self) -> List[RiskAlert]:
        """Check for threshold breaches and create alerts."""
        alerts = []

        # Check each application
        for app in self._applications:
            # Critical overall risk
            if app.overall_severity == RiskSeverity.CRITICAL:
                self._alert_counter += 1
                alerts.append(RiskAlert(
                    alert_id=f"ALERT-{self._alert_counter:05d}",
                    severity=RiskSeverity.CRITICAL,
                    category=RiskCategory.BUSINESS,
                    title=f"Critical Risk: {app.app_name}",
                    description=f"Application has critical overall risk score of {app.overall_score:.0f}",
                    affected_apps=[app.app_name],
                    recommended_actions=["Immediate risk assessment required", "Executive review recommended"]
                ))

            # Check dimension-specific thresholds
            for category, dimension in app.dimensions.items():
                if dimension.severity == RiskSeverity.CRITICAL:
                    self._alert_counter += 1
                    alerts.append(RiskAlert(
                        alert_id=f"ALERT-{self._alert_counter:05d}",
                        severity=RiskSeverity.CRITICAL,
                        category=category,
                        title=f"Critical {category.value.title()} Risk: {app.app_name}",
                        description=f"{category.value.title()} risk score of {dimension.score:.0f} exceeds critical threshold",
                        affected_apps=[app.app_name],
                        recommended_actions=dimension.mitigation_actions[:2]
                    ))

        return alerts

    def _generate_heat_map(
        self,
        x_field: str,
        y_field: str,
        title: str
    ) -> HeatMapData:
        """Generate heat map data for given dimensions."""
        # Get unique categories
        x_values = set()
        y_values = set()

        for app in self._applications:
            x_val = getattr(app, x_field, "Unknown") or "Unknown"
            y_val = getattr(app, y_field, "Unknown") or "Unknown"
            x_values.add(x_val)
            y_values.add(y_val)

        x_categories = sorted(list(x_values))
        y_categories = sorted(list(y_values))

        # Build cell data
        cells = []
        cell_data = defaultdict(lambda: {"score_sum": 0, "count": 0, "apps": []})

        for app in self._applications:
            x_val = getattr(app, x_field, "Unknown") or "Unknown"
            y_val = getattr(app, y_field, "Unknown") or "Unknown"
            key = (x_val, y_val)

            cell_data[key]["score_sum"] += app.overall_score
            cell_data[key]["count"] += 1
            cell_data[key]["apps"].append(app.app_name)

        max_risk = 0
        total_risk = 0
        cell_count = 0

        for x_val in x_categories:
            for y_val in y_categories:
                key = (x_val, y_val)
                data = cell_data[key]

                if data["count"] > 0:
                    avg_score = data["score_sum"] / data["count"]
                    max_risk = max(max_risk, avg_score)
                    total_risk += avg_score
                    cell_count += 1
                else:
                    avg_score = 0

                cells.append(HeatMapCell(
                    x_value=x_val,
                    y_value=y_val,
                    risk_score=round(avg_score, 1),
                    severity=self._score_to_severity(avg_score),
                    application_count=data["count"],
                    applications=data["apps"]
                ))

        # Identify hotspots
        hotspots = [
            {"x": c.x_value, "y": c.y_value, "score": c.risk_score, "apps": c.application_count}
            for c in cells if c.severity in [RiskSeverity.CRITICAL, RiskSeverity.HIGH]
        ]
        hotspots.sort(key=lambda x: x["score"], reverse=True)

        return HeatMapData(
            title=title,
            x_axis_label=x_field.replace("_", " ").title(),
            y_axis_label=y_field.replace("_", " ").title(),
            x_categories=x_categories,
            y_categories=y_categories,
            cells=cells,
            max_risk=round(max_risk, 1),
            avg_risk=round(total_risk / cell_count, 1) if cell_count > 0 else 0,
            hotspots=hotspots[:5]
        )

    def _calculate_correlations(self) -> List[RiskCorrelation]:
        """Calculate correlations between risk dimensions."""
        if len(self._applications) < 3:
            return []

        correlations = []
        categories = list(RiskCategory)

        for i, cat1 in enumerate(categories):
            for cat2 in categories[i+1:]:
                # Get scores for both dimensions
                scores1 = []
                scores2 = []

                for app in self._applications:
                    if cat1 in app.dimensions and cat2 in app.dimensions:
                        scores1.append(app.dimensions[cat1].score)
                        scores2.append(app.dimensions[cat2].score)

                if len(scores1) < 3:
                    continue

                # Calculate Pearson correlation
                n = len(scores1)
                sum1 = sum(scores1)
                sum2 = sum(scores2)
                sum1_sq = sum(x**2 for x in scores1)
                sum2_sq = sum(x**2 for x in scores2)
                sum_prod = sum(x*y for x, y in zip(scores1, scores2))

                num = n * sum_prod - sum1 * sum2
                den = math.sqrt((n * sum1_sq - sum1**2) * (n * sum2_sq - sum2**2))

                if den == 0:
                    corr = 0
                else:
                    corr = num / den

                # Determine strength
                abs_corr = abs(corr)
                if abs_corr >= 0.7:
                    strength = "strong"
                elif abs_corr >= 0.4:
                    strength = "moderate"
                else:
                    strength = "weak"

                # Generate insight
                if corr > 0.5:
                    insight = f"High {cat1.value} risk often accompanies high {cat2.value} risk"
                elif corr < -0.5:
                    insight = f"{cat1.value} and {cat2.value} risks show inverse relationship"
                else:
                    insight = f"{cat1.value} and {cat2.value} risks are relatively independent"

                correlations.append(RiskCorrelation(
                    dimension_1=cat1,
                    dimension_2=cat2,
                    correlation=round(corr, 2),
                    strength=strength,
                    insight=insight
                ))

        # Sort by absolute correlation
        correlations.sort(key=lambda x: abs(x.correlation), reverse=True)
        return correlations[:10]  # Top 10

    def _generate_summary(self) -> RiskSummary:
        """Generate executive risk summary."""
        if not self._applications:
            return RiskSummary()

        # Count by severity
        critical = sum(1 for a in self._applications if a.overall_severity == RiskSeverity.CRITICAL)
        high = sum(1 for a in self._applications if a.overall_severity == RiskSeverity.HIGH)
        medium = sum(1 for a in self._applications if a.overall_severity == RiskSeverity.MEDIUM)
        low = sum(1 for a in self._applications if a.overall_severity == RiskSeverity.LOW)

        # Dimension averages
        dim_totals = defaultdict(lambda: {"sum": 0, "count": 0})
        for app in self._applications:
            for category, dimension in app.dimensions.items():
                dim_totals[category.value]["sum"] += dimension.score
                dim_totals[category.value]["count"] += 1

        dim_averages = {
            k: round(v["sum"] / v["count"], 1) if v["count"] > 0 else 0
            for k, v in dim_totals.items()
        }

        # Top risks
        sorted_apps = sorted(self._applications, key=lambda x: x.overall_score, reverse=True)
        top_risks = [
            {"app_name": a.app_name, "score": a.overall_score, "severity": a.overall_severity.value}
            for a in sorted_apps[:5]
        ]

        # Count alerts
        active_alerts = len(self._alerts)
        critical_alerts = sum(1 for a in self._alerts if a.severity == RiskSeverity.CRITICAL)

        return RiskSummary(
            total_applications=len(self._applications),
            assessed_applications=len(self._applications),
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
            dimension_averages=dim_averages,
            top_risks=top_risks,
            overall_trend=TrendIndicator.STABLE,
            active_alerts=active_alerts,
            critical_alerts=critical_alerts
        )

    def generate_analysis(self) -> RiskHeatMapResult:
        """Generate complete risk heat map analysis."""
        # Check thresholds and create alerts
        self._alerts = self._check_thresholds_and_create_alerts()

        # Generate heat maps
        heat_maps = {
            "category_vs_vendor": self._generate_heat_map(
                "category", "vendor",
                "Risk by Category and Vendor"
            ),
            "category_vs_unit": self._generate_heat_map(
                "category", "business_unit",
                "Risk by Category and Business Unit"
            ),
            "vendor_vs_unit": self._generate_heat_map(
                "vendor", "business_unit",
                "Risk by Vendor and Business Unit"
            ),
        }

        # Calculate correlations
        correlations = self._calculate_correlations()

        # Generate summary
        summary = self._generate_summary()

        return RiskHeatMapResult(
            summary=summary,
            heat_maps=heat_maps,
            correlations=correlations,
            alerts=self._alerts,
            application_profiles=self._applications
        )

    def get_dimension_breakdown(self) -> Dict[str, Dict]:
        """Get breakdown of risk by dimension across portfolio."""
        if not self._applications:
            return {}

        breakdown = {}
        for category in RiskCategory:
            scores = []
            for app in self._applications:
                if category in app.dimensions:
                    scores.append(app.dimensions[category].score)

            if scores:
                breakdown[category.value] = {
                    "average": round(sum(scores) / len(scores), 1),
                    "max": max(scores),
                    "min": min(scores),
                    "count": len(scores),
                    "critical_count": sum(1 for s in scores if s >= 80),
                    "high_count": sum(1 for s in scores if 60 <= s < 80)
                }

        return breakdown


def create_risk_heatmap_engine() -> RiskHeatMapEngine:
    """Factory function to create a risk heat map engine."""
    return RiskHeatMapEngine()


def create_demo_risk_profiles(count: int = 25) -> List[ApplicationRiskProfile]:
    """Create demo risk profiles for testing."""
    categories = ["CRM", "ERP", "HRM", "Finance", "Marketing", "Analytics", "Security", "Operations"]
    vendors = ["Salesforce", "Microsoft", "SAP", "Oracle", "Workday", "Custom", "Open Source"]
    units = ["Sales", "Finance", "HR", "IT", "Operations", "Marketing", "Legal"]

    profiles = []
    for i in range(count):
        # Generate dimension scores
        dimensions = {}
        for category in RiskCategory:
            score = random.uniform(10, 90)
            trend = random.choice(list(TrendIndicator))

            dim = RiskDimension(
                category=category,
                score=round(score, 1),
                severity=RiskHeatMapEngine()._score_to_severity(score),
                trend=trend
            )

            # Add factors and actions based on score
            engine = RiskHeatMapEngine()
            dim.contributing_factors = engine._generate_contributing_factors(category, score)
            dim.mitigation_actions = engine._generate_mitigation_actions(category, score)

            dimensions[category] = dim

        # Calculate overall score
        overall = RiskHeatMapEngine()._calculate_overall_score(dimensions)

        profile = ApplicationRiskProfile(
            app_id=f"APP-{i+1:04d}",
            app_name=f"{random.choice(categories)} System {i+1}",
            overall_score=round(overall, 1),
            overall_severity=RiskHeatMapEngine()._score_to_severity(overall),
            dimensions=dimensions,
            category=random.choice(categories),
            business_unit=random.choice(units),
            vendor=random.choice(vendors),
            user_count=random.randint(50, 5000),
            annual_cost=random.uniform(20000, 500000),
            last_assessment=datetime.now(),
            assessment_confidence=random.uniform(0.6, 1.0)
        )
        profiles.append(profile)

    return profiles
