"""
Portfolio Dashboard Engine for Application Rationalization Pro
Executive-level visualizations and portfolio analytics.

Features:
- Portfolio Health Scorecard
- Executive Summary Metrics
- Trend Analysis and Forecasting
- Benchmark Comparisons
- Investment Allocation Views
- Strategic Recommendations
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
import random
import math


class HealthStatus(Enum):
    """Portfolio health status levels."""
    CRITICAL = "critical"
    AT_RISK = "at_risk"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


class TrendDirection(Enum):
    """Trend directions."""
    DECLINING = "declining"
    STABLE = "stable"
    IMPROVING = "improving"
    RAPID_IMPROVEMENT = "rapid_improvement"


class InvestmentCategory(Enum):
    """Investment allocation categories."""
    RUN = "run"  # Maintenance/operations
    GROW = "grow"  # Enhancements
    TRANSFORM = "transform"  # Innovation/modernization


class MetricType(Enum):
    """Types of portfolio metrics."""
    COST = "cost"
    RISK = "risk"
    VALUE = "value"
    HEALTH = "health"
    EFFICIENCY = "efficiency"


@dataclass
class PortfolioMetric:
    """A single portfolio metric."""
    name: str
    value: float
    unit: str = ""
    trend: TrendDirection = TrendDirection.STABLE
    change_percentage: float = 0.0
    benchmark_value: Optional[float] = None
    benchmark_comparison: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "trend": self.trend.value,
            "change_percentage": self.change_percentage,
            "benchmark_value": self.benchmark_value,
            "benchmark_comparison": self.benchmark_comparison
        }


@dataclass
class HealthScorecard:
    """Portfolio health scorecard."""
    overall_score: float = 0.0
    overall_status: HealthStatus = HealthStatus.FAIR

    # Dimension scores (0-100)
    cost_efficiency: float = 0.0
    technical_health: float = 0.0
    business_alignment: float = 0.0
    security_posture: float = 0.0
    operational_stability: float = 0.0
    innovation_readiness: float = 0.0

    # Trends
    cost_trend: TrendDirection = TrendDirection.STABLE
    health_trend: TrendDirection = TrendDirection.STABLE
    risk_trend: TrendDirection = TrendDirection.STABLE

    # Comparisons
    industry_benchmark: float = 0.0
    previous_period: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "overall_score": self.overall_score,
            "overall_status": self.overall_status.value,
            "cost_efficiency": self.cost_efficiency,
            "technical_health": self.technical_health,
            "business_alignment": self.business_alignment,
            "security_posture": self.security_posture,
            "operational_stability": self.operational_stability,
            "innovation_readiness": self.innovation_readiness,
            "cost_trend": self.cost_trend.value,
            "health_trend": self.health_trend.value,
            "risk_trend": self.risk_trend.value,
            "industry_benchmark": self.industry_benchmark,
            "previous_period": self.previous_period
        }


@dataclass
class ExecutiveSummary:
    """Executive summary for portfolio."""
    total_applications: int = 0
    total_annual_cost: float = 0.0
    total_users: int = 0

    # Categorization
    apps_by_health: Dict[str, int] = field(default_factory=dict)
    apps_by_strategy: Dict[str, int] = field(default_factory=dict)
    apps_by_lifecycle: Dict[str, int] = field(default_factory=dict)

    # Key metrics
    average_age_years: float = 0.0
    technical_debt_ratio: float = 0.0
    cloud_adoption_percentage: float = 0.0
    redundancy_percentage: float = 0.0

    # Top insights
    top_cost_apps: List[Dict] = field(default_factory=list)
    top_risk_apps: List[Dict] = field(default_factory=list)
    top_opportunities: List[Dict] = field(default_factory=list)

    # Financial summary
    potential_savings: float = 0.0
    required_investment: float = 0.0
    projected_roi: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "total_applications": self.total_applications,
            "total_annual_cost": self.total_annual_cost,
            "total_users": self.total_users,
            "apps_by_health": self.apps_by_health,
            "apps_by_strategy": self.apps_by_strategy,
            "apps_by_lifecycle": self.apps_by_lifecycle,
            "average_age_years": self.average_age_years,
            "technical_debt_ratio": self.technical_debt_ratio,
            "cloud_adoption_percentage": self.cloud_adoption_percentage,
            "redundancy_percentage": self.redundancy_percentage,
            "top_cost_apps": self.top_cost_apps,
            "top_risk_apps": self.top_risk_apps,
            "top_opportunities": self.top_opportunities,
            "potential_savings": self.potential_savings,
            "required_investment": self.required_investment,
            "projected_roi": self.projected_roi
        }


@dataclass
class TrendDataPoint:
    """A point in trend data."""
    period: str
    value: float
    forecast: bool = False


@dataclass
class TrendAnalysis:
    """Trend analysis for a metric."""
    metric_name: str
    current_value: float
    period_change: float
    trend_direction: TrendDirection = TrendDirection.STABLE

    # Historical data
    historical_data: List[TrendDataPoint] = field(default_factory=list)

    # Forecast
    forecast_data: List[TrendDataPoint] = field(default_factory=list)
    forecast_confidence: float = 0.0

    # Insights
    key_drivers: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "period_change": self.period_change,
            "trend_direction": self.trend_direction.value,
            "historical_data": [{"period": d.period, "value": d.value, "forecast": d.forecast}
                               for d in self.historical_data],
            "forecast_data": [{"period": d.period, "value": d.value, "forecast": d.forecast}
                             for d in self.forecast_data],
            "forecast_confidence": self.forecast_confidence,
            "key_drivers": self.key_drivers,
            "recommendations": self.recommendations
        }


@dataclass
class InvestmentAllocation:
    """Investment allocation analysis."""
    total_budget: float = 0.0

    # Category allocations
    run_budget: float = 0.0
    grow_budget: float = 0.0
    transform_budget: float = 0.0

    # Percentages
    run_percentage: float = 0.0
    grow_percentage: float = 0.0
    transform_percentage: float = 0.0

    # Benchmarks
    recommended_run: float = 60.0
    recommended_grow: float = 25.0
    recommended_transform: float = 15.0

    # Analysis
    is_balanced: bool = False
    rebalancing_needed: str = ""
    optimization_opportunities: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "total_budget": self.total_budget,
            "run_budget": self.run_budget,
            "grow_budget": self.grow_budget,
            "transform_budget": self.transform_budget,
            "run_percentage": self.run_percentage,
            "grow_percentage": self.grow_percentage,
            "transform_percentage": self.transform_percentage,
            "recommended_run": self.recommended_run,
            "recommended_grow": self.recommended_grow,
            "recommended_transform": self.recommended_transform,
            "is_balanced": self.is_balanced,
            "rebalancing_needed": self.rebalancing_needed,
            "optimization_opportunities": self.optimization_opportunities
        }


@dataclass
class StrategicRecommendation:
    """A strategic recommendation for the portfolio."""
    priority: int
    title: str
    description: str
    impact: str
    effort: str
    timeline: str
    estimated_savings: float = 0.0
    estimated_cost: float = 0.0
    affected_apps: int = 0
    category: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "priority": self.priority,
            "title": self.title,
            "description": self.description,
            "impact": self.impact,
            "effort": self.effort,
            "timeline": self.timeline,
            "estimated_savings": self.estimated_savings,
            "estimated_cost": self.estimated_cost,
            "affected_apps": self.affected_apps,
            "category": self.category
        }


@dataclass
class ApplicationData:
    """Application data for portfolio analysis."""
    app_id: str
    app_name: str

    # Core metrics
    annual_cost: float = 0.0
    user_count: int = 0
    age_years: float = 0.0

    # Scores (0-1)
    business_value: float = 0.5
    technical_health: float = 0.5
    risk_score: float = 0.3
    cost_efficiency: float = 0.5

    # Classifications
    lifecycle_stage: str = "maturity"
    time_recommendation: str = "tolerate"
    is_cloud_hosted: bool = False
    has_redundancy: bool = False

    # Categories
    category: str = ""
    vendor: str = ""
    business_unit: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "app_id": self.app_id,
            "app_name": self.app_name,
            "annual_cost": self.annual_cost,
            "user_count": self.user_count,
            "age_years": self.age_years,
            "business_value": self.business_value,
            "technical_health": self.technical_health,
            "risk_score": self.risk_score,
            "cost_efficiency": self.cost_efficiency,
            "lifecycle_stage": self.lifecycle_stage,
            "time_recommendation": self.time_recommendation,
            "is_cloud_hosted": self.is_cloud_hosted,
            "has_redundancy": self.has_redundancy,
            "category": self.category,
            "vendor": self.vendor,
            "business_unit": self.business_unit
        }


@dataclass
class PortfolioDashboard:
    """Complete portfolio dashboard data."""
    portfolio_id: str
    portfolio_name: str

    # Components
    scorecard: HealthScorecard = field(default_factory=HealthScorecard)
    summary: ExecutiveSummary = field(default_factory=ExecutiveSummary)
    investment: InvestmentAllocation = field(default_factory=InvestmentAllocation)
    recommendations: List[StrategicRecommendation] = field(default_factory=list)

    # Trend analyses
    cost_trend: Optional[TrendAnalysis] = None
    health_trend: Optional[TrendAnalysis] = None
    risk_trend: Optional[TrendAnalysis] = None

    # Key metrics
    key_metrics: List[PortfolioMetric] = field(default_factory=list)

    # Charts data
    cost_by_category: Dict[str, float] = field(default_factory=dict)
    cost_by_vendor: Dict[str, float] = field(default_factory=dict)
    apps_by_quadrant: Dict[str, List[str]] = field(default_factory=dict)

    # Metadata
    generated_at: datetime = field(default_factory=datetime.now)
    data_freshness: str = "current"

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "portfolio_id": self.portfolio_id,
            "portfolio_name": self.portfolio_name,
            "scorecard": self.scorecard.to_dict(),
            "summary": self.summary.to_dict(),
            "investment": self.investment.to_dict(),
            "recommendations": [r.to_dict() for r in self.recommendations],
            "cost_trend": self.cost_trend.to_dict() if self.cost_trend else None,
            "health_trend": self.health_trend.to_dict() if self.health_trend else None,
            "risk_trend": self.risk_trend.to_dict() if self.risk_trend else None,
            "key_metrics": [m.to_dict() for m in self.key_metrics],
            "cost_by_category": self.cost_by_category,
            "cost_by_vendor": self.cost_by_vendor,
            "apps_by_quadrant": self.apps_by_quadrant,
            "generated_at": self.generated_at.isoformat(),
            "data_freshness": self.data_freshness
        }


class PortfolioDashboardEngine:
    """
    Portfolio Dashboard Engine for executive-level analytics.
    """

    # Industry benchmarks
    BENCHMARKS = {
        "cost_per_user": 500,  # Annual cost per user
        "technical_health": 70,  # Average health score
        "cloud_adoption": 60,  # Percentage in cloud
        "technical_debt_ratio": 0.25,  # Debt to value ratio
        "run_grow_transform": (60, 25, 15),  # Budget split
    }

    def __init__(self):
        """Initialize dashboard engine."""
        self._applications: List[ApplicationData] = []
        self._historical_data: Dict[str, List[Dict]] = {}

    def add_application(self, app: ApplicationData) -> None:
        """Add an application for analysis."""
        self._applications.append(app)

    def add_applications(self, apps: List[ApplicationData]) -> None:
        """Add multiple applications."""
        self._applications.extend(apps)

    def clear_applications(self) -> None:
        """Clear all applications."""
        self._applications = []

    def set_historical_data(self, metric: str, data: List[Dict]) -> None:
        """Set historical data for trend analysis."""
        self._historical_data[metric] = data

    def _calculate_scorecard(self) -> HealthScorecard:
        """Calculate portfolio health scorecard."""
        if not self._applications:
            return HealthScorecard()

        n = len(self._applications)

        # Calculate dimension scores
        cost_efficiency = sum(app.cost_efficiency for app in self._applications) / n * 100
        technical_health = sum(app.technical_health for app in self._applications) / n * 100
        business_alignment = sum(app.business_value for app in self._applications) / n * 100
        security_posture = 100 - (sum(app.risk_score for app in self._applications) / n * 100)
        operational_stability = (cost_efficiency + technical_health) / 2
        innovation_readiness = sum(1 for app in self._applications if app.is_cloud_hosted) / n * 100

        # Overall score (weighted average)
        weights = {
            "cost_efficiency": 0.2,
            "technical_health": 0.2,
            "business_alignment": 0.2,
            "security_posture": 0.15,
            "operational_stability": 0.15,
            "innovation_readiness": 0.1
        }

        overall = (
            cost_efficiency * weights["cost_efficiency"] +
            technical_health * weights["technical_health"] +
            business_alignment * weights["business_alignment"] +
            security_posture * weights["security_posture"] +
            operational_stability * weights["operational_stability"] +
            innovation_readiness * weights["innovation_readiness"]
        )

        # Determine status
        if overall >= 80:
            status = HealthStatus.EXCELLENT
        elif overall >= 65:
            status = HealthStatus.GOOD
        elif overall >= 50:
            status = HealthStatus.FAIR
        elif overall >= 35:
            status = HealthStatus.AT_RISK
        else:
            status = HealthStatus.CRITICAL

        return HealthScorecard(
            overall_score=round(overall, 1),
            overall_status=status,
            cost_efficiency=round(cost_efficiency, 1),
            technical_health=round(technical_health, 1),
            business_alignment=round(business_alignment, 1),
            security_posture=round(security_posture, 1),
            operational_stability=round(operational_stability, 1),
            innovation_readiness=round(innovation_readiness, 1),
            industry_benchmark=self.BENCHMARKS["technical_health"]
        )

    def _calculate_summary(self) -> ExecutiveSummary:
        """Calculate executive summary."""
        if not self._applications:
            return ExecutiveSummary()

        n = len(self._applications)

        # Basic metrics
        total_cost = sum(app.annual_cost for app in self._applications)
        total_users = sum(app.user_count for app in self._applications)
        avg_age = sum(app.age_years for app in self._applications) / n

        # Health distribution
        health_dist = {"excellent": 0, "good": 0, "fair": 0, "poor": 0, "critical": 0}
        for app in self._applications:
            if app.technical_health >= 0.8:
                health_dist["excellent"] += 1
            elif app.technical_health >= 0.6:
                health_dist["good"] += 1
            elif app.technical_health >= 0.4:
                health_dist["fair"] += 1
            elif app.technical_health >= 0.2:
                health_dist["poor"] += 1
            else:
                health_dist["critical"] += 1

        # Strategy distribution
        strategy_dist = defaultdict(int)
        for app in self._applications:
            strategy_dist[app.time_recommendation] += 1

        # Lifecycle distribution
        lifecycle_dist = defaultdict(int)
        for app in self._applications:
            lifecycle_dist[app.lifecycle_stage] += 1

        # Cloud adoption
        cloud_count = sum(1 for app in self._applications if app.is_cloud_hosted)
        cloud_percentage = (cloud_count / n) * 100

        # Redundancy
        redundant_count = sum(1 for app in self._applications if app.has_redundancy)
        redundancy_percentage = (redundant_count / n) * 100

        # Technical debt ratio (inverse of health)
        debt_ratio = 1 - (sum(app.technical_health for app in self._applications) / n)

        # Top cost applications
        sorted_by_cost = sorted(self._applications, key=lambda x: x.annual_cost, reverse=True)
        top_cost = [
            {"app_id": app.app_id, "app_name": app.app_name, "annual_cost": app.annual_cost}
            for app in sorted_by_cost[:5]
        ]

        # Top risk applications
        sorted_by_risk = sorted(self._applications, key=lambda x: x.risk_score, reverse=True)
        top_risk = [
            {"app_id": app.app_id, "app_name": app.app_name, "risk_score": app.risk_score}
            for app in sorted_by_risk[:5]
        ]

        # Opportunities (low value, high cost)
        opportunities = []
        for app in self._applications:
            if app.cost_efficiency < 0.4 and app.business_value < 0.5:
                potential = app.annual_cost * 0.3
                opportunities.append({
                    "app_id": app.app_id,
                    "app_name": app.app_name,
                    "potential_savings": potential,
                    "action": "Retire or replace"
                })
        opportunities.sort(key=lambda x: x["potential_savings"], reverse=True)

        # Financial projections
        potential_savings = sum(o["potential_savings"] for o in opportunities[:10])
        required_investment = potential_savings * 0.5  # Rough estimate
        roi = ((potential_savings - required_investment) / required_investment * 100) if required_investment > 0 else 0

        return ExecutiveSummary(
            total_applications=n,
            total_annual_cost=total_cost,
            total_users=total_users,
            apps_by_health=health_dist,
            apps_by_strategy=dict(strategy_dist),
            apps_by_lifecycle=dict(lifecycle_dist),
            average_age_years=round(avg_age, 1),
            technical_debt_ratio=round(debt_ratio, 2),
            cloud_adoption_percentage=round(cloud_percentage, 1),
            redundancy_percentage=round(redundancy_percentage, 1),
            top_cost_apps=top_cost,
            top_risk_apps=top_risk,
            top_opportunities=opportunities[:5],
            potential_savings=round(potential_savings, 2),
            required_investment=round(required_investment, 2),
            projected_roi=round(roi, 1)
        )

    def _calculate_investment(self) -> InvestmentAllocation:
        """Calculate investment allocation analysis."""
        if not self._applications:
            return InvestmentAllocation()

        total_budget = sum(app.annual_cost for app in self._applications)

        # Categorize applications
        run_apps = [app for app in self._applications if app.time_recommendation in ["tolerate", "maintain"]]
        grow_apps = [app for app in self._applications if app.time_recommendation in ["invest", "enhance"]]
        transform_apps = [app for app in self._applications if app.time_recommendation in ["migrate", "modernize", "eliminate"]]

        run_budget = sum(app.annual_cost for app in run_apps)
        grow_budget = sum(app.annual_cost for app in grow_apps)
        transform_budget = sum(app.annual_cost for app in transform_apps)

        run_pct = (run_budget / total_budget * 100) if total_budget > 0 else 0
        grow_pct = (grow_budget / total_budget * 100) if total_budget > 0 else 0
        transform_pct = (transform_budget / total_budget * 100) if total_budget > 0 else 0

        # Check balance
        rec_run, rec_grow, rec_transform = self.BENCHMARKS["run_grow_transform"]
        is_balanced = abs(run_pct - rec_run) < 10 and abs(grow_pct - rec_grow) < 10

        # Rebalancing advice
        rebalancing = ""
        if run_pct > rec_run + 10:
            rebalancing = f"Over-invested in Run ({run_pct:.0f}% vs {rec_run}% target). Consider modernization."
        elif grow_pct < rec_grow - 10:
            rebalancing = f"Under-invested in Growth ({grow_pct:.0f}% vs {rec_grow}% target). Increase innovation budget."
        elif transform_pct < rec_transform - 5:
            rebalancing = f"Under-invested in Transform ({transform_pct:.0f}% vs {rec_transform}% target). Accelerate modernization."

        # Opportunities
        opportunities = []
        if run_pct > rec_run:
            opportunities.append("Identify Run applications for retirement to free up budget")
        if transform_pct < rec_transform:
            opportunities.append("Increase investment in cloud migration and modernization")
        if grow_pct < rec_grow:
            opportunities.append("Allocate more resources to enhancing high-value applications")

        return InvestmentAllocation(
            total_budget=total_budget,
            run_budget=run_budget,
            grow_budget=grow_budget,
            transform_budget=transform_budget,
            run_percentage=round(run_pct, 1),
            grow_percentage=round(grow_pct, 1),
            transform_percentage=round(transform_pct, 1),
            is_balanced=is_balanced,
            rebalancing_needed=rebalancing,
            optimization_opportunities=opportunities
        )

    def _calculate_trend(
        self,
        metric_name: str,
        current_value: float,
        historical: Optional[List[Dict]] = None
    ) -> TrendAnalysis:
        """Calculate trend analysis for a metric."""
        if historical is None:
            historical = self._historical_data.get(metric_name, [])

        # Generate mock historical if none provided
        if not historical:
            base_value = current_value
            historical = []
            for i in range(6):
                month = datetime.now() - timedelta(days=30 * (6 - i))
                variance = random.uniform(-0.1, 0.15)
                value = base_value * (0.9 + variance)
                historical.append({"period": month.strftime("%Y-%m"), "value": value})

        # Build historical data points
        hist_points = [
            TrendDataPoint(period=d["period"], value=d["value"], forecast=False)
            for d in historical
        ]

        # Calculate period change
        if len(historical) >= 2:
            old_value = historical[0]["value"]
            period_change = ((current_value - old_value) / old_value * 100) if old_value > 0 else 0
        else:
            period_change = 0

        # Determine trend direction
        if period_change > 10:
            direction = TrendDirection.RAPID_IMPROVEMENT
        elif period_change > 3:
            direction = TrendDirection.IMPROVING
        elif period_change < -3:
            direction = TrendDirection.DECLINING
        else:
            direction = TrendDirection.STABLE

        # Simple linear forecast
        forecast_points = []
        if len(historical) >= 2:
            avg_change = sum(
                historical[i+1]["value"] - historical[i]["value"]
                for i in range(len(historical)-1)
            ) / (len(historical) - 1)

            forecast_value = current_value
            for i in range(3):
                month = datetime.now() + timedelta(days=30 * (i + 1))
                forecast_value += avg_change
                forecast_points.append(
                    TrendDataPoint(period=month.strftime("%Y-%m"), value=forecast_value, forecast=True)
                )

        return TrendAnalysis(
            metric_name=metric_name,
            current_value=current_value,
            period_change=round(period_change, 1),
            trend_direction=direction,
            historical_data=hist_points,
            forecast_data=forecast_points,
            forecast_confidence=0.75 if len(historical) >= 4 else 0.5
        )

    def _generate_recommendations(self) -> List[StrategicRecommendation]:
        """Generate strategic recommendations."""
        recommendations = []
        priority = 1

        if not self._applications:
            return recommendations

        # Analyze portfolio for recommendations
        high_cost_low_value = [
            app for app in self._applications
            if app.cost_efficiency < 0.4 and app.business_value < 0.5
        ]
        if high_cost_low_value:
            total_savings = sum(app.annual_cost * 0.4 for app in high_cost_low_value)
            recommendations.append(StrategicRecommendation(
                priority=priority,
                title="Retire Low-Value Applications",
                description=f"Identify and retire {len(high_cost_low_value)} applications with low business value",
                impact="High",
                effort="Medium",
                timeline="6-12 months",
                estimated_savings=total_savings,
                affected_apps=len(high_cost_low_value),
                category="cost_optimization"
            ))
            priority += 1

        # Cloud migration
        non_cloud = [app for app in self._applications if not app.is_cloud_hosted]
        if len(non_cloud) > len(self._applications) * 0.5:
            recommendations.append(StrategicRecommendation(
                priority=priority,
                title="Accelerate Cloud Migration",
                description=f"Migrate {len(non_cloud)} on-premises applications to cloud infrastructure",
                impact="High",
                effort="High",
                timeline="12-24 months",
                estimated_savings=sum(app.annual_cost * 0.25 for app in non_cloud),
                estimated_cost=sum(app.annual_cost * 0.15 for app in non_cloud),
                affected_apps=len(non_cloud),
                category="modernization"
            ))
            priority += 1

        # Technical debt
        high_debt = [app for app in self._applications if app.technical_health < 0.4]
        if high_debt:
            recommendations.append(StrategicRecommendation(
                priority=priority,
                title="Address Technical Debt",
                description=f"Remediate technical debt in {len(high_debt)} applications with poor health scores",
                impact="Medium",
                effort="High",
                timeline="12-18 months",
                estimated_cost=len(high_debt) * 50000,
                affected_apps=len(high_debt),
                category="technical_health"
            ))
            priority += 1

        # Consolidation
        redundant = [app for app in self._applications if app.has_redundancy]
        if redundant:
            recommendations.append(StrategicRecommendation(
                priority=priority,
                title="Consolidate Redundant Applications",
                description=f"Evaluate {len(redundant)} applications with overlapping functionality",
                impact="Medium",
                effort="Medium",
                timeline="6-12 months",
                estimated_savings=sum(app.annual_cost * 0.5 for app in redundant[:5]),
                affected_apps=len(redundant),
                category="consolidation"
            ))
            priority += 1

        # Security improvements
        high_risk = [app for app in self._applications if app.risk_score > 0.7]
        if high_risk:
            recommendations.append(StrategicRecommendation(
                priority=priority,
                title="Reduce Security Risk Exposure",
                description=f"Address security vulnerabilities in {len(high_risk)} high-risk applications",
                impact="Critical",
                effort="High",
                timeline="3-6 months",
                estimated_cost=len(high_risk) * 25000,
                affected_apps=len(high_risk),
                category="security"
            ))
            priority += 1

        return recommendations

    def _calculate_key_metrics(self) -> List[PortfolioMetric]:
        """Calculate key portfolio metrics."""
        if not self._applications:
            return []

        n = len(self._applications)
        total_cost = sum(app.annual_cost for app in self._applications)
        total_users = sum(app.user_count for app in self._applications)

        metrics = [
            PortfolioMetric(
                name="Total Annual Cost",
                value=total_cost,
                unit="USD",
                benchmark_value=n * 100000,
                benchmark_comparison="industry average"
            ),
            PortfolioMetric(
                name="Cost per User",
                value=total_cost / total_users if total_users > 0 else 0,
                unit="USD/user",
                benchmark_value=self.BENCHMARKS["cost_per_user"],
                benchmark_comparison="industry benchmark"
            ),
            PortfolioMetric(
                name="Average Technical Health",
                value=sum(app.technical_health for app in self._applications) / n * 100,
                unit="%",
                benchmark_value=self.BENCHMARKS["technical_health"],
                benchmark_comparison="industry average"
            ),
            PortfolioMetric(
                name="Cloud Adoption",
                value=sum(1 for app in self._applications if app.is_cloud_hosted) / n * 100,
                unit="%",
                benchmark_value=self.BENCHMARKS["cloud_adoption"],
                benchmark_comparison="industry average"
            ),
            PortfolioMetric(
                name="Average Risk Score",
                value=sum(app.risk_score for app in self._applications) / n * 100,
                unit="%"
            ),
            PortfolioMetric(
                name="Application Count",
                value=n,
                unit="apps"
            ),
        ]

        return metrics

    def _calculate_distribution_charts(self) -> Tuple[Dict[str, float], Dict[str, float], Dict[str, List[str]]]:
        """Calculate data for distribution charts."""
        cost_by_category = defaultdict(float)
        cost_by_vendor = defaultdict(float)
        apps_by_quadrant = {
            "stars": [],  # High value, high health
            "cash_cows": [],  # High value, low health
            "question_marks": [],  # Low value, high health
            "dogs": []  # Low value, low health
        }

        for app in self._applications:
            cost_by_category[app.category or "Uncategorized"] += app.annual_cost
            cost_by_vendor[app.vendor or "Unknown"] += app.annual_cost

            # Quadrant assignment
            if app.business_value >= 0.5 and app.technical_health >= 0.5:
                apps_by_quadrant["stars"].append(app.app_name)
            elif app.business_value >= 0.5:
                apps_by_quadrant["cash_cows"].append(app.app_name)
            elif app.technical_health >= 0.5:
                apps_by_quadrant["question_marks"].append(app.app_name)
            else:
                apps_by_quadrant["dogs"].append(app.app_name)

        return dict(cost_by_category), dict(cost_by_vendor), apps_by_quadrant

    def generate_dashboard(
        self,
        portfolio_id: str,
        portfolio_name: str
    ) -> PortfolioDashboard:
        """Generate complete portfolio dashboard."""
        # Calculate all components
        scorecard = self._calculate_scorecard()
        summary = self._calculate_summary()
        investment = self._calculate_investment()
        recommendations = self._generate_recommendations()
        key_metrics = self._calculate_key_metrics()
        cost_by_cat, cost_by_vendor, quadrants = self._calculate_distribution_charts()

        # Calculate trends
        total_cost = summary.total_annual_cost
        avg_health = scorecard.technical_health
        avg_risk = 100 - scorecard.security_posture

        cost_trend = self._calculate_trend("Annual Cost", total_cost)
        health_trend = self._calculate_trend("Technical Health", avg_health)
        risk_trend = self._calculate_trend("Risk Score", avg_risk)

        return PortfolioDashboard(
            portfolio_id=portfolio_id,
            portfolio_name=portfolio_name,
            scorecard=scorecard,
            summary=summary,
            investment=investment,
            recommendations=recommendations,
            cost_trend=cost_trend,
            health_trend=health_trend,
            risk_trend=risk_trend,
            key_metrics=key_metrics,
            cost_by_category=cost_by_cat,
            cost_by_vendor=cost_by_vendor,
            apps_by_quadrant=quadrants
        )


def create_portfolio_dashboard_engine() -> PortfolioDashboardEngine:
    """Factory function to create a dashboard engine."""
    return PortfolioDashboardEngine()


def create_demo_portfolio_data(count: int = 25) -> List[ApplicationData]:
    """Create demo application data for testing."""
    categories = ["CRM", "ERP", "HRM", "Finance", "Marketing", "Analytics", "Communication", "Security"]
    vendors = ["Salesforce", "Microsoft", "SAP", "Oracle", "Workday", "Custom", "Open Source"]
    units = ["Sales", "Finance", "HR", "IT", "Operations", "Marketing"]
    stages = ["inception", "development", "pilot", "growth", "maturity", "decline", "sunset"]
    recommendations = ["tolerate", "invest", "migrate", "eliminate", "maintain", "modernize"]

    applications = []
    for i in range(count):
        app = ApplicationData(
            app_id=f"APP-{i+1:04d}",
            app_name=f"{random.choice(categories)} System {i+1}",
            annual_cost=random.uniform(10000, 500000),
            user_count=random.randint(10, 5000),
            age_years=random.uniform(1, 15),
            business_value=random.uniform(0.2, 1.0),
            technical_health=random.uniform(0.2, 1.0),
            risk_score=random.uniform(0.1, 0.9),
            cost_efficiency=random.uniform(0.2, 0.9),
            lifecycle_stage=random.choice(stages),
            time_recommendation=random.choice(recommendations),
            is_cloud_hosted=random.random() > 0.5,
            has_redundancy=random.random() > 0.7,
            category=random.choice(categories),
            vendor=random.choice(vendors),
            business_unit=random.choice(units)
        )
        applications.append(app)

    return applications
