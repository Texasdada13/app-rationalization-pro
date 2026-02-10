"""
Technical Debt Calculator Engine
Quantifies and prioritizes technical debt across application portfolios
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import uuid


class DebtCategory(Enum):
    """Categories of technical debt"""
    CODE_QUALITY = "code_quality"
    ARCHITECTURE = "architecture"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    SECURITY = "security"
    DEPENDENCIES = "dependencies"
    INFRASTRUCTURE = "infrastructure"
    PERFORMANCE = "performance"


class DebtSeverity(Enum):
    """Severity levels for technical debt"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DebtStatus(Enum):
    """Status of technical debt items"""
    IDENTIFIED = "identified"
    ACKNOWLEDGED = "acknowledged"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ACCEPTED = "accepted"  # Intentionally not fixing


@dataclass
class DebtItem:
    """Individual technical debt item"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    app_id: str = ""
    app_name: str = ""
    category: DebtCategory = DebtCategory.CODE_QUALITY
    severity: DebtSeverity = DebtSeverity.MEDIUM
    status: DebtStatus = DebtStatus.IDENTIFIED
    title: str = ""
    description: str = ""

    # Impact metrics
    impact_score: float = 5.0  # 1-10
    effort_hours: float = 8.0
    cost_estimate: float = 0.0

    # Business impact
    affects_reliability: bool = False
    affects_security: bool = False
    affects_performance: bool = False
    affects_maintainability: bool = True
    blocks_features: bool = False

    # Tracking
    identified_date: datetime = field(default_factory=datetime.utcnow)
    target_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None
    owner: str = ""

    # Interest accumulation
    interest_rate_monthly: float = 5.0  # % increase per month

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'app_id': self.app_id,
            'app_name': self.app_name,
            'category': self.category.value,
            'severity': self.severity.value,
            'status': self.status.value,
            'title': self.title,
            'description': self.description,
            'impact_score': self.impact_score,
            'effort_hours': self.effort_hours,
            'cost_estimate': self.cost_estimate,
            'affects_reliability': self.affects_reliability,
            'affects_security': self.affects_security,
            'affects_performance': self.affects_performance,
            'affects_maintainability': self.affects_maintainability,
            'blocks_features': self.blocks_features,
            'identified_date': self.identified_date.isoformat() if self.identified_date else None,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'resolved_date': self.resolved_date.isoformat() if self.resolved_date else None,
            'owner': self.owner,
            'interest_rate_monthly': self.interest_rate_monthly,
            'accumulated_interest': self.calculate_interest(),
            'total_cost': self.calculate_total_cost(),
            'priority_score': self.calculate_priority()
        }

    def calculate_interest(self) -> float:
        """Calculate accumulated interest on debt"""
        if self.status == DebtStatus.RESOLVED:
            return 0.0

        months_outstanding = (datetime.utcnow() - self.identified_date).days / 30
        interest = self.effort_hours * (self.interest_rate_monthly / 100) * months_outstanding
        return round(interest, 1)

    def calculate_total_cost(self) -> float:
        """Calculate total cost including interest"""
        base_cost = self.effort_hours * 150  # $150/hour default rate
        interest_cost = self.calculate_interest() * 150
        return round(base_cost + interest_cost, 2)

    def calculate_priority(self) -> float:
        """Calculate priority score (higher = more urgent)"""
        severity_weights = {
            DebtSeverity.CRITICAL: 10,
            DebtSeverity.HIGH: 7,
            DebtSeverity.MEDIUM: 4,
            DebtSeverity.LOW: 2
        }

        base_priority = severity_weights.get(self.severity, 4)

        # Boost for business impact
        if self.affects_security:
            base_priority += 3
        if self.affects_reliability:
            base_priority += 2
        if self.blocks_features:
            base_priority += 2
        if self.affects_performance:
            base_priority += 1

        # Factor in ROI (impact vs effort)
        roi_factor = self.impact_score / max(self.effort_hours / 8, 1)

        return round(base_priority * roi_factor, 2)


@dataclass
class AppDebtProfile:
    """Technical debt profile for an application"""
    app_id: str
    app_name: str
    debt_items: List[DebtItem] = field(default_factory=list)
    overall_score: float = 0.0  # 0-100, higher = more debt
    debt_grade: str = "A"
    category_scores: Dict[str, float] = field(default_factory=dict)
    total_effort_hours: float = 0.0
    total_cost: float = 0.0
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'app_id': self.app_id,
            'app_name': self.app_name,
            'debt_items': [item.to_dict() for item in self.debt_items],
            'overall_score': self.overall_score,
            'debt_grade': self.debt_grade,
            'category_scores': self.category_scores,
            'total_effort_hours': self.total_effort_hours,
            'total_cost': self.total_cost,
            'recommendations': self.recommendations,
            'item_count': len(self.debt_items),
            'critical_count': sum(1 for d in self.debt_items if d.severity == DebtSeverity.CRITICAL),
            'high_count': sum(1 for d in self.debt_items if d.severity == DebtSeverity.HIGH)
        }


@dataclass
class PortfolioDebtSummary:
    """Summary of technical debt across portfolio"""
    total_apps: int = 0
    total_debt_items: int = 0
    total_effort_hours: float = 0.0
    total_cost: float = 0.0
    average_debt_score: float = 0.0
    portfolio_grade: str = "A"
    apps_by_grade: Dict[str, int] = field(default_factory=dict)
    category_breakdown: Dict[str, Dict] = field(default_factory=dict)
    top_priority_items: List[Dict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    trend: str = "stable"  # improving, stable, worsening

    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_apps': self.total_apps,
            'total_debt_items': self.total_debt_items,
            'total_effort_hours': self.total_effort_hours,
            'total_cost': self.total_cost,
            'average_debt_score': self.average_debt_score,
            'portfolio_grade': self.portfolio_grade,
            'apps_by_grade': self.apps_by_grade,
            'category_breakdown': self.category_breakdown,
            'top_priority_items': self.top_priority_items,
            'recommendations': self.recommendations,
            'trend': self.trend
        }


class TechDebtCalculator:
    """
    Calculate and analyze technical debt across application portfolios.

    Features:
    - Score debt across 8 categories
    - Calculate remediation costs with interest accumulation
    - Prioritize debt items by business impact
    - Generate paydown roadmaps
    - Track debt trends over time
    """

    # Category weights for overall score
    CATEGORY_WEIGHTS = {
        DebtCategory.SECURITY: 0.20,
        DebtCategory.ARCHITECTURE: 0.15,
        DebtCategory.CODE_QUALITY: 0.15,
        DebtCategory.DEPENDENCIES: 0.12,
        DebtCategory.TESTING: 0.12,
        DebtCategory.PERFORMANCE: 0.10,
        DebtCategory.DOCUMENTATION: 0.08,
        DebtCategory.INFRASTRUCTURE: 0.08
    }

    # Scoring thresholds
    GRADE_THRESHOLDS = {
        'A': (0, 20),
        'B': (20, 40),
        'C': (40, 60),
        'D': (60, 80),
        'F': (80, 100)
    }

    # Default hourly rate for cost calculations
    HOURLY_RATE = 150

    def __init__(self):
        self.debt_items: Dict[str, DebtItem] = {}
        self.app_profiles: Dict[str, AppDebtProfile] = {}

    def add_debt_item(self, item: DebtItem) -> DebtItem:
        """Add a debt item to the calculator"""
        self.debt_items[item.id] = item
        return item

    def remove_debt_item(self, item_id: str) -> bool:
        """Remove a debt item"""
        if item_id in self.debt_items:
            del self.debt_items[item_id]
            return True
        return False

    def update_debt_item(self, item_id: str, updates: Dict[str, Any]) -> Optional[DebtItem]:
        """Update a debt item"""
        if item_id not in self.debt_items:
            return None

        item = self.debt_items[item_id]
        for key, value in updates.items():
            if hasattr(item, key):
                if key == 'category' and isinstance(value, str):
                    value = DebtCategory(value)
                elif key == 'severity' and isinstance(value, str):
                    value = DebtSeverity(value)
                elif key == 'status' and isinstance(value, str):
                    value = DebtStatus(value)
                setattr(item, key, value)

        return item

    def assess_application(self, app_id: str, app_name: str,
                          metrics: Optional[Dict[str, Any]] = None) -> AppDebtProfile:
        """
        Assess technical debt for an application based on metrics.

        Args:
            app_id: Application identifier
            app_name: Application name
            metrics: Optional metrics dict with debt indicators

        Returns:
            AppDebtProfile with debt analysis
        """
        # Get existing debt items for this app
        app_items = [item for item in self.debt_items.values() if item.app_id == app_id]

        # If metrics provided, auto-generate debt items
        if metrics:
            app_items.extend(self._generate_debt_from_metrics(app_id, app_name, metrics))

        # Calculate category scores
        category_scores = {}
        for category in DebtCategory:
            cat_items = [i for i in app_items if i.category == category]
            if cat_items:
                avg_severity = sum(
                    {'critical': 10, 'high': 7, 'medium': 4, 'low': 2}.get(i.severity.value, 4)
                    for i in cat_items
                ) / len(cat_items)
                category_scores[category.value] = min(100, avg_severity * len(cat_items))
            else:
                category_scores[category.value] = 0

        # Calculate weighted overall score
        overall_score = sum(
            category_scores.get(cat.value, 0) * weight
            for cat, weight in self.CATEGORY_WEIGHTS.items()
        )

        # Determine grade
        debt_grade = 'F'
        for grade, (low, high) in self.GRADE_THRESHOLDS.items():
            if low <= overall_score < high:
                debt_grade = grade
                break

        # Calculate totals
        total_effort = sum(item.effort_hours + item.calculate_interest() for item in app_items)
        total_cost = sum(item.calculate_total_cost() for item in app_items)

        # Generate recommendations
        recommendations = self._generate_app_recommendations(app_items, category_scores)

        profile = AppDebtProfile(
            app_id=app_id,
            app_name=app_name,
            debt_items=app_items,
            overall_score=round(overall_score, 1),
            debt_grade=debt_grade,
            category_scores=category_scores,
            total_effort_hours=round(total_effort, 1),
            total_cost=round(total_cost, 2),
            recommendations=recommendations
        )

        self.app_profiles[app_id] = profile
        return profile

    def _generate_debt_from_metrics(self, app_id: str, app_name: str,
                                    metrics: Dict[str, Any]) -> List[DebtItem]:
        """Generate debt items from application metrics"""
        items = []

        # Code quality metrics
        if metrics.get('code_coverage', 100) < 60:
            items.append(DebtItem(
                app_id=app_id,
                app_name=app_name,
                category=DebtCategory.TESTING,
                severity=DebtSeverity.HIGH if metrics.get('code_coverage', 100) < 30 else DebtSeverity.MEDIUM,
                title="Insufficient Test Coverage",
                description=f"Code coverage at {metrics.get('code_coverage', 0)}%, below 60% threshold",
                effort_hours=40,
                affects_reliability=True
            ))

        if metrics.get('code_smells', 0) > 50:
            items.append(DebtItem(
                app_id=app_id,
                app_name=app_name,
                category=DebtCategory.CODE_QUALITY,
                severity=DebtSeverity.HIGH if metrics.get('code_smells', 0) > 100 else DebtSeverity.MEDIUM,
                title="High Code Smell Count",
                description=f"{metrics.get('code_smells', 0)} code smells detected",
                effort_hours=max(8, metrics.get('code_smells', 0) * 0.5),
                affects_maintainability=True
            ))

        # Dependency metrics
        if metrics.get('outdated_dependencies', 0) > 10:
            items.append(DebtItem(
                app_id=app_id,
                app_name=app_name,
                category=DebtCategory.DEPENDENCIES,
                severity=DebtSeverity.HIGH,
                title="Outdated Dependencies",
                description=f"{metrics.get('outdated_dependencies', 0)} dependencies need updates",
                effort_hours=metrics.get('outdated_dependencies', 0) * 2,
                affects_security=True
            ))

        if metrics.get('vulnerable_dependencies', 0) > 0:
            items.append(DebtItem(
                app_id=app_id,
                app_name=app_name,
                category=DebtCategory.SECURITY,
                severity=DebtSeverity.CRITICAL,
                title="Security Vulnerabilities in Dependencies",
                description=f"{metrics.get('vulnerable_dependencies', 0)} known vulnerabilities",
                effort_hours=metrics.get('vulnerable_dependencies', 0) * 4,
                affects_security=True
            ))

        # Architecture metrics
        if metrics.get('cyclomatic_complexity', 0) > 20:
            items.append(DebtItem(
                app_id=app_id,
                app_name=app_name,
                category=DebtCategory.ARCHITECTURE,
                severity=DebtSeverity.MEDIUM,
                title="High Cyclomatic Complexity",
                description=f"Average complexity of {metrics.get('cyclomatic_complexity', 0)}, indicating convoluted logic",
                effort_hours=24,
                affects_maintainability=True
            ))

        if metrics.get('coupling_score', 0) > 70:
            items.append(DebtItem(
                app_id=app_id,
                app_name=app_name,
                category=DebtCategory.ARCHITECTURE,
                severity=DebtSeverity.HIGH,
                title="High Component Coupling",
                description="Tightly coupled components make changes risky",
                effort_hours=40,
                affects_maintainability=True,
                blocks_features=True
            ))

        # Documentation metrics
        if metrics.get('documentation_coverage', 100) < 30:
            items.append(DebtItem(
                app_id=app_id,
                app_name=app_name,
                category=DebtCategory.DOCUMENTATION,
                severity=DebtSeverity.LOW,
                title="Insufficient Documentation",
                description=f"Only {metrics.get('documentation_coverage', 0)}% of code is documented",
                effort_hours=20,
                affects_maintainability=True
            ))

        # Performance metrics
        if metrics.get('avg_response_time_ms', 0) > 1000:
            items.append(DebtItem(
                app_id=app_id,
                app_name=app_name,
                category=DebtCategory.PERFORMANCE,
                severity=DebtSeverity.HIGH if metrics.get('avg_response_time_ms', 0) > 3000 else DebtSeverity.MEDIUM,
                title="Slow Response Times",
                description=f"Average response time of {metrics.get('avg_response_time_ms', 0)}ms exceeds threshold",
                effort_hours=16,
                affects_performance=True
            ))

        return items

    def _generate_app_recommendations(self, items: List[DebtItem],
                                      category_scores: Dict[str, float]) -> List[str]:
        """Generate recommendations based on debt analysis"""
        recommendations = []

        # Sort categories by score
        sorted_cats = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)

        if sorted_cats and sorted_cats[0][1] > 50:
            cat_name = sorted_cats[0][0].replace('_', ' ').title()
            recommendations.append(f"Priority: Address {cat_name} debt first (score: {sorted_cats[0][1]:.0f})")

        # Security is always priority if present
        security_items = [i for i in items if i.category == DebtCategory.SECURITY]
        if security_items:
            recommendations.append(f"Security Alert: {len(security_items)} security-related debt items need immediate attention")

        # High priority items
        critical_items = [i for i in items if i.severity == DebtSeverity.CRITICAL]
        if critical_items:
            recommendations.append(f"Critical: {len(critical_items)} critical items blocking progress")

        # Quick wins (low effort, high impact)
        quick_wins = [i for i in items if i.effort_hours <= 8 and i.impact_score >= 7]
        if quick_wins:
            recommendations.append(f"Quick Wins: {len(quick_wins)} items can be resolved in <1 day each")

        # Accumulating interest
        high_interest = [i for i in items if i.calculate_interest() > 10]
        if high_interest:
            total_interest = sum(i.calculate_interest() for i in high_interest)
            recommendations.append(f"Interest Alert: {total_interest:.0f} hours of accumulated interest across {len(high_interest)} items")

        return recommendations

    def get_portfolio_summary(self) -> PortfolioDebtSummary:
        """Get summary of technical debt across all assessed applications"""
        if not self.app_profiles:
            return PortfolioDebtSummary()

        profiles = list(self.app_profiles.values())

        # Aggregate metrics
        total_items = sum(len(p.debt_items) for p in profiles)
        total_effort = sum(p.total_effort_hours for p in profiles)
        total_cost = sum(p.total_cost for p in profiles)
        avg_score = sum(p.overall_score for p in profiles) / len(profiles)

        # Grade distribution
        apps_by_grade = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        for p in profiles:
            apps_by_grade[p.debt_grade] = apps_by_grade.get(p.debt_grade, 0) + 1

        # Category breakdown
        category_breakdown = {}
        for category in DebtCategory:
            cat_items = [
                item for p in profiles for item in p.debt_items
                if item.category == category
            ]
            if cat_items:
                category_breakdown[category.value] = {
                    'count': len(cat_items),
                    'effort_hours': sum(i.effort_hours for i in cat_items),
                    'avg_severity': sum(
                        {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}.get(i.severity.value, 2)
                        for i in cat_items
                    ) / len(cat_items)
                }

        # Top priority items across portfolio
        all_items = [item for p in profiles for item in p.debt_items]
        sorted_items = sorted(all_items, key=lambda x: x.calculate_priority(), reverse=True)
        top_priority = [
            {
                'id': item.id,
                'app_name': item.app_name,
                'title': item.title,
                'category': item.category.value,
                'severity': item.severity.value,
                'priority_score': item.calculate_priority(),
                'effort_hours': item.effort_hours
            }
            for item in sorted_items[:10]
        ]

        # Portfolio grade
        portfolio_grade = 'F'
        for grade, (low, high) in self.GRADE_THRESHOLDS.items():
            if low <= avg_score < high:
                portfolio_grade = grade
                break

        # Generate portfolio recommendations
        recommendations = []
        if apps_by_grade.get('F', 0) > 0:
            recommendations.append(f"Critical: {apps_by_grade['F']} applications have failing debt grades")
        if total_cost > 100000:
            recommendations.append(f"Budget Alert: Portfolio debt remediation estimated at ${total_cost:,.0f}")
        if category_breakdown.get('security', {}).get('count', 0) > 0:
            recommendations.append("Security debt should be prioritized across portfolio")

        # Quick win recommendations
        quick_win_hours = sum(
            i.effort_hours for i in all_items
            if i.effort_hours <= 8 and i.impact_score >= 6
        )
        if quick_win_hours > 0:
            recommendations.append(f"Quick wins: {quick_win_hours:.0f} hours of high-impact, low-effort fixes available")

        return PortfolioDebtSummary(
            total_apps=len(profiles),
            total_debt_items=total_items,
            total_effort_hours=round(total_effort, 1),
            total_cost=round(total_cost, 2),
            average_debt_score=round(avg_score, 1),
            portfolio_grade=portfolio_grade,
            apps_by_grade=apps_by_grade,
            category_breakdown=category_breakdown,
            top_priority_items=top_priority,
            recommendations=recommendations,
            trend="stable"
        )

    def generate_paydown_roadmap(self, budget_hours_per_sprint: float = 40,
                                 sprint_length_weeks: int = 2) -> List[Dict[str, Any]]:
        """
        Generate a prioritized roadmap for paying down technical debt.

        Args:
            budget_hours_per_sprint: Hours allocated for debt work per sprint
            sprint_length_weeks: Sprint length in weeks

        Returns:
            List of sprints with assigned debt items
        """
        # Get all unresolved items sorted by priority
        all_items = [
            item for p in self.app_profiles.values()
            for item in p.debt_items
            if item.status not in [DebtStatus.RESOLVED, DebtStatus.ACCEPTED]
        ]
        sorted_items = sorted(all_items, key=lambda x: x.calculate_priority(), reverse=True)

        roadmap = []
        remaining_items = list(sorted_items)
        sprint_number = 1
        current_date = datetime.utcnow()

        while remaining_items and sprint_number <= 12:  # Max 12 sprints (6 months)
            sprint_items = []
            sprint_hours = 0
            items_to_remove = []

            for item in remaining_items:
                if sprint_hours + item.effort_hours <= budget_hours_per_sprint:
                    sprint_items.append({
                        'id': item.id,
                        'app_name': item.app_name,
                        'title': item.title,
                        'category': item.category.value,
                        'severity': item.severity.value,
                        'effort_hours': item.effort_hours,
                        'priority_score': item.calculate_priority()
                    })
                    sprint_hours += item.effort_hours
                    items_to_remove.append(item)

            for item in items_to_remove:
                remaining_items.remove(item)

            if sprint_items:
                sprint_end = current_date + timedelta(weeks=sprint_length_weeks)
                roadmap.append({
                    'sprint': sprint_number,
                    'start_date': current_date.isoformat(),
                    'end_date': sprint_end.isoformat(),
                    'items': sprint_items,
                    'total_hours': sprint_hours,
                    'item_count': len(sprint_items),
                    'estimated_cost': sprint_hours * self.HOURLY_RATE
                })
                current_date = sprint_end
                sprint_number += 1

        # Summary
        total_roadmap_hours = sum(s['total_hours'] for s in roadmap)
        remaining_hours = sum(i.effort_hours for i in remaining_items)

        return {
            'sprints': roadmap,
            'total_sprints': len(roadmap),
            'total_hours_planned': total_roadmap_hours,
            'remaining_hours': remaining_hours,
            'remaining_items': len(remaining_items),
            'completion_percentage': round(
                total_roadmap_hours / (total_roadmap_hours + remaining_hours) * 100, 1
            ) if (total_roadmap_hours + remaining_hours) > 0 else 100
        }

    def get_debt_trends(self, days: int = 90) -> Dict[str, Any]:
        """Get debt trends over time (simulated for demo)"""
        # In production, this would query historical data
        # For now, generate representative trend data

        all_items = [item for p in self.app_profiles.values() for item in p.debt_items]
        current_count = len(all_items)
        current_hours = sum(i.effort_hours for i in all_items)

        # Simulate historical data points
        data_points = []
        for i in range(days, 0, -7):  # Weekly data points
            date = datetime.utcnow() - timedelta(days=i)
            # Simulate gradual increase with some fluctuation
            factor = 1 + (i / days) * 0.3
            data_points.append({
                'date': date.isoformat(),
                'item_count': int(current_count / factor),
                'total_hours': round(current_hours / factor, 1)
            })

        # Add current point
        data_points.append({
            'date': datetime.utcnow().isoformat(),
            'item_count': current_count,
            'total_hours': current_hours
        })

        # Calculate trend
        if len(data_points) >= 2:
            start_count = data_points[0]['item_count']
            end_count = data_points[-1]['item_count']
            if end_count > start_count * 1.1:
                trend = "worsening"
            elif end_count < start_count * 0.9:
                trend = "improving"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            'data_points': data_points,
            'trend': trend,
            'period_days': days,
            'change_percentage': round(
                (data_points[-1]['item_count'] - data_points[0]['item_count']) /
                max(data_points[0]['item_count'], 1) * 100, 1
            )
        }


# Factory function
def create_tech_debt_calculator() -> TechDebtCalculator:
    """Create a new TechDebtCalculator instance"""
    return TechDebtCalculator()


def create_demo_tech_debt() -> TechDebtCalculator:
    """Create calculator with demo data"""
    calc = TechDebtCalculator()

    # Demo applications with varying debt levels
    demo_apps = [
        {
            'id': 'app-001',
            'name': 'Customer Portal',
            'metrics': {
                'code_coverage': 45,
                'code_smells': 78,
                'outdated_dependencies': 15,
                'vulnerable_dependencies': 2,
                'cyclomatic_complexity': 25,
                'documentation_coverage': 20,
                'avg_response_time_ms': 800
            }
        },
        {
            'id': 'app-002',
            'name': 'Payment Service',
            'metrics': {
                'code_coverage': 85,
                'code_smells': 12,
                'outdated_dependencies': 3,
                'vulnerable_dependencies': 0,
                'cyclomatic_complexity': 8,
                'documentation_coverage': 70,
                'avg_response_time_ms': 150
            }
        },
        {
            'id': 'app-003',
            'name': 'Legacy ERP',
            'metrics': {
                'code_coverage': 15,
                'code_smells': 245,
                'outdated_dependencies': 45,
                'vulnerable_dependencies': 8,
                'cyclomatic_complexity': 45,
                'coupling_score': 85,
                'documentation_coverage': 5,
                'avg_response_time_ms': 3500
            }
        },
        {
            'id': 'app-004',
            'name': 'Mobile API',
            'metrics': {
                'code_coverage': 72,
                'code_smells': 34,
                'outdated_dependencies': 8,
                'vulnerable_dependencies': 1,
                'cyclomatic_complexity': 12,
                'documentation_coverage': 55,
                'avg_response_time_ms': 250
            }
        },
        {
            'id': 'app-005',
            'name': 'Analytics Dashboard',
            'metrics': {
                'code_coverage': 60,
                'code_smells': 56,
                'outdated_dependencies': 12,
                'vulnerable_dependencies': 0,
                'cyclomatic_complexity': 18,
                'documentation_coverage': 40,
                'avg_response_time_ms': 1200
            }
        }
    ]

    for app in demo_apps:
        calc.assess_application(app['id'], app['name'], app['metrics'])

    return calc
