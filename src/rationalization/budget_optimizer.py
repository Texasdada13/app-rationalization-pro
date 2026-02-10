"""
Budget Allocation Optimizer for Application Rationalization Pro
Optimizes IT budget allocation across applications and initiatives.

Features:
- Value-Based Budget Allocation
- Constraint Optimization (total budget, min/max per app)
- What-If Scenario Modeling
- ROI Maximization
- Risk-Adjusted Returns
- Multi-Year Planning
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from datetime import datetime
from collections import defaultdict
import random
import math


class BudgetCategory(Enum):
    """Budget allocation categories."""
    MAINTENANCE = "maintenance"
    ENHANCEMENT = "enhancement"
    MODERNIZATION = "modernization"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    INNOVATION = "innovation"
    RETIREMENT = "retirement"


class OptimizationObjective(Enum):
    """Optimization objectives."""
    MAXIMIZE_VALUE = "maximize_value"
    MINIMIZE_RISK = "minimize_risk"
    MAXIMIZE_ROI = "maximize_roi"
    BALANCE = "balance"
    COST_REDUCTION = "cost_reduction"


class AllocationStrategy(Enum):
    """Budget allocation strategies."""
    VALUE_BASED = "value_based"
    RISK_BASED = "risk_based"
    EQUAL_DISTRIBUTION = "equal_distribution"
    STRATEGIC_PRIORITY = "strategic_priority"
    HYBRID = "hybrid"


@dataclass
class ApplicationBudgetProfile:
    """Budget profile for an application."""
    app_id: str
    app_name: str

    # Current state
    current_budget: float = 0.0
    current_cost: float = 0.0

    # Value metrics (0-1)
    business_value: float = 0.5
    strategic_alignment: float = 0.5
    user_impact: float = 0.5

    # Health metrics (0-1)
    technical_health: float = 0.5
    risk_score: float = 0.3

    # Efficiency
    roi_potential: float = 0.0
    cost_per_user: float = 0.0

    # Constraints
    minimum_budget: float = 0.0
    maximum_budget: float = float('inf')
    is_mandatory: bool = False

    # Categories
    category: str = ""
    strategic_priority: int = 3  # 1=highest, 5=lowest

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "app_id": self.app_id,
            "app_name": self.app_name,
            "current_budget": self.current_budget,
            "current_cost": self.current_cost,
            "business_value": self.business_value,
            "strategic_alignment": self.strategic_alignment,
            "user_impact": self.user_impact,
            "technical_health": self.technical_health,
            "risk_score": self.risk_score,
            "roi_potential": self.roi_potential,
            "cost_per_user": self.cost_per_user,
            "minimum_budget": self.minimum_budget,
            "maximum_budget": self.maximum_budget,
            "is_mandatory": self.is_mandatory,
            "category": self.category,
            "strategic_priority": self.strategic_priority
        }


@dataclass
class BudgetAllocation:
    """Optimized budget allocation for an application."""
    app_id: str
    app_name: str

    # Allocations
    recommended_budget: float = 0.0
    current_budget: float = 0.0
    change_amount: float = 0.0
    change_percentage: float = 0.0

    # Category breakdown
    maintenance_budget: float = 0.0
    enhancement_budget: float = 0.0
    modernization_budget: float = 0.0

    # Metrics
    expected_roi: float = 0.0
    risk_reduction: float = 0.0
    value_score: float = 0.0

    # Rationale
    allocation_rationale: str = ""
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "app_id": self.app_id,
            "app_name": self.app_name,
            "recommended_budget": self.recommended_budget,
            "current_budget": self.current_budget,
            "change_amount": self.change_amount,
            "change_percentage": self.change_percentage,
            "maintenance_budget": self.maintenance_budget,
            "enhancement_budget": self.enhancement_budget,
            "modernization_budget": self.modernization_budget,
            "expected_roi": self.expected_roi,
            "risk_reduction": self.risk_reduction,
            "value_score": self.value_score,
            "allocation_rationale": self.allocation_rationale,
            "recommendations": self.recommendations
        }


@dataclass
class OptimizationScenario:
    """A budget optimization scenario."""
    scenario_id: str
    scenario_name: str

    # Parameters
    total_budget: float = 0.0
    objective: OptimizationObjective = OptimizationObjective.BALANCE
    strategy: AllocationStrategy = AllocationStrategy.HYBRID

    # Allocations
    allocations: List[BudgetAllocation] = field(default_factory=list)

    # Aggregate metrics
    total_allocated: float = 0.0
    unallocated: float = 0.0
    expected_total_roi: float = 0.0
    risk_score: float = 0.0
    value_score: float = 0.0

    # Comparisons
    vs_current_savings: float = 0.0
    vs_current_value_gain: float = 0.0

    # Constraints status
    constraints_satisfied: bool = True
    constraint_violations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
            "total_budget": self.total_budget,
            "objective": self.objective.value,
            "strategy": self.strategy.value,
            "allocations": [a.to_dict() for a in self.allocations],
            "total_allocated": self.total_allocated,
            "unallocated": self.unallocated,
            "expected_total_roi": self.expected_total_roi,
            "risk_score": self.risk_score,
            "value_score": self.value_score,
            "vs_current_savings": self.vs_current_savings,
            "vs_current_value_gain": self.vs_current_value_gain,
            "constraints_satisfied": self.constraints_satisfied,
            "constraint_violations": self.constraint_violations
        }


@dataclass
class MultiYearPlan:
    """Multi-year budget plan."""
    plan_id: str
    years: int
    yearly_scenarios: List[OptimizationScenario] = field(default_factory=list)

    # Projections
    cumulative_investment: float = 0.0
    cumulative_savings: float = 0.0
    cumulative_roi: float = 0.0

    # Trend
    value_trajectory: List[float] = field(default_factory=list)
    risk_trajectory: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "plan_id": self.plan_id,
            "years": self.years,
            "yearly_scenarios": [s.to_dict() for s in self.yearly_scenarios],
            "cumulative_investment": self.cumulative_investment,
            "cumulative_savings": self.cumulative_savings,
            "cumulative_roi": self.cumulative_roi,
            "value_trajectory": self.value_trajectory,
            "risk_trajectory": self.risk_trajectory
        }


@dataclass
class OptimizationResult:
    """Complete budget optimization result."""
    base_scenario: OptimizationScenario
    alternative_scenarios: List[OptimizationScenario] = field(default_factory=list)
    multi_year_plan: Optional[MultiYearPlan] = None

    # Summary
    recommended_changes: List[Dict] = field(default_factory=list)
    key_insights: List[str] = field(default_factory=list)
    quick_wins: List[Dict] = field(default_factory=list)

    # Metadata
    generated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "base_scenario": self.base_scenario.to_dict(),
            "alternative_scenarios": [s.to_dict() for s in self.alternative_scenarios],
            "multi_year_plan": self.multi_year_plan.to_dict() if self.multi_year_plan else None,
            "recommended_changes": self.recommended_changes,
            "key_insights": self.key_insights,
            "quick_wins": self.quick_wins,
            "generated_at": self.generated_at.isoformat()
        }


class BudgetOptimizer:
    """
    Budget Allocation Optimizer for IT portfolio optimization.
    """

    # Category allocation defaults (percentage of app budget)
    CATEGORY_DEFAULTS = {
        BudgetCategory.MAINTENANCE: 0.50,
        BudgetCategory.ENHANCEMENT: 0.25,
        BudgetCategory.MODERNIZATION: 0.15,
        BudgetCategory.SECURITY: 0.05,
        BudgetCategory.COMPLIANCE: 0.03,
        BudgetCategory.INNOVATION: 0.02,
    }

    # Priority multipliers
    PRIORITY_MULTIPLIERS = {
        1: 1.5,  # Highest priority
        2: 1.25,
        3: 1.0,
        4: 0.75,
        5: 0.5   # Lowest priority
    }

    def __init__(self):
        """Initialize optimizer."""
        self._applications: List[ApplicationBudgetProfile] = []
        self._constraints: Dict[str, Any] = {}

    def add_application(self, app: ApplicationBudgetProfile) -> None:
        """Add an application for optimization."""
        self._applications.append(app)

    def add_applications(self, apps: List[ApplicationBudgetProfile]) -> None:
        """Add multiple applications."""
        self._applications.extend(apps)

    def clear_applications(self) -> None:
        """Clear all applications."""
        self._applications = []

    def set_constraint(self, name: str, value: Any) -> None:
        """Set an optimization constraint."""
        self._constraints[name] = value

    def _calculate_value_score(self, app: ApplicationBudgetProfile) -> float:
        """Calculate composite value score for an application."""
        weights = {
            "business_value": 0.35,
            "strategic_alignment": 0.25,
            "user_impact": 0.20,
            "roi_potential": 0.20
        }

        score = (
            app.business_value * weights["business_value"] +
            app.strategic_alignment * weights["strategic_alignment"] +
            app.user_impact * weights["user_impact"] +
            app.roi_potential * weights["roi_potential"]
        )

        # Apply priority multiplier
        score *= self.PRIORITY_MULTIPLIERS.get(app.strategic_priority, 1.0)

        return min(1.0, score)

    def _calculate_risk_adjusted_value(self, app: ApplicationBudgetProfile) -> float:
        """Calculate risk-adjusted value."""
        value = self._calculate_value_score(app)
        risk_penalty = app.risk_score * 0.3
        health_bonus = app.technical_health * 0.2

        return max(0, min(1, value - risk_penalty + health_bonus))

    def _calculate_base_allocation(
        self,
        app: ApplicationBudgetProfile,
        strategy: AllocationStrategy,
        total_budget: float,
        total_value: float
    ) -> float:
        """Calculate base budget allocation for an application."""
        if strategy == AllocationStrategy.EQUAL_DISTRIBUTION:
            return total_budget / len(self._applications)

        elif strategy == AllocationStrategy.VALUE_BASED:
            value_score = self._calculate_value_score(app)
            if total_value > 0:
                return total_budget * (value_score / total_value)
            return total_budget / len(self._applications)

        elif strategy == AllocationStrategy.RISK_BASED:
            # Higher allocation to higher risk apps (for remediation)
            risk_weight = app.risk_score + (1 - app.technical_health)
            total_risk = sum(a.risk_score + (1 - a.technical_health) for a in self._applications)
            if total_risk > 0:
                return total_budget * (risk_weight / total_risk)
            return total_budget / len(self._applications)

        elif strategy == AllocationStrategy.STRATEGIC_PRIORITY:
            priority_weight = self.PRIORITY_MULTIPLIERS.get(app.strategic_priority, 1.0)
            total_priority = sum(
                self.PRIORITY_MULTIPLIERS.get(a.strategic_priority, 1.0)
                for a in self._applications
            )
            return total_budget * (priority_weight / total_priority)

        else:  # HYBRID
            value_score = self._calculate_risk_adjusted_value(app)
            priority_weight = self.PRIORITY_MULTIPLIERS.get(app.strategic_priority, 1.0)
            combined = value_score * priority_weight
            total_combined = sum(
                self._calculate_risk_adjusted_value(a) *
                self.PRIORITY_MULTIPLIERS.get(a.strategic_priority, 1.0)
                for a in self._applications
            )
            if total_combined > 0:
                return total_budget * (combined / total_combined)
            return total_budget / len(self._applications)

    def _apply_constraints(
        self,
        allocations: Dict[str, float]
    ) -> Tuple[Dict[str, float], List[str]]:
        """Apply min/max constraints and return violations."""
        violations = []
        adjusted = allocations.copy()

        for app in self._applications:
            current = adjusted.get(app.app_id, 0)

            # Apply minimum
            if current < app.minimum_budget:
                if app.is_mandatory:
                    adjusted[app.app_id] = app.minimum_budget
                    violations.append(
                        f"{app.app_name}: Increased to minimum ${app.minimum_budget:,.0f} (mandatory)"
                    )
                else:
                    adjusted[app.app_id] = app.minimum_budget
                    violations.append(
                        f"{app.app_name}: Adjusted to minimum ${app.minimum_budget:,.0f}"
                    )

            # Apply maximum
            if current > app.maximum_budget:
                adjusted[app.app_id] = app.maximum_budget
                violations.append(
                    f"{app.app_name}: Capped at maximum ${app.maximum_budget:,.0f}"
                )

        return adjusted, violations

    def _calculate_category_breakdown(
        self,
        app: ApplicationBudgetProfile,
        total_allocation: float
    ) -> Dict[str, float]:
        """Calculate budget breakdown by category."""
        # Adjust ratios based on app characteristics
        maintenance_ratio = 0.50
        enhancement_ratio = 0.25
        modernization_ratio = 0.15

        # Increase modernization for low health apps
        if app.technical_health < 0.4:
            modernization_ratio += 0.15
            maintenance_ratio -= 0.10
            enhancement_ratio -= 0.05

        # Increase maintenance for high-risk apps
        if app.risk_score > 0.6:
            maintenance_ratio += 0.10
            enhancement_ratio -= 0.10

        # Increase enhancement for high-value apps
        if app.business_value > 0.7:
            enhancement_ratio += 0.10
            maintenance_ratio -= 0.10

        return {
            "maintenance": total_allocation * maintenance_ratio,
            "enhancement": total_allocation * enhancement_ratio,
            "modernization": total_allocation * modernization_ratio,
            "other": total_allocation * (1 - maintenance_ratio - enhancement_ratio - modernization_ratio)
        }

    def _generate_allocation_rationale(
        self,
        app: ApplicationBudgetProfile,
        allocation: BudgetAllocation
    ) -> str:
        """Generate rationale for budget allocation."""
        reasons = []

        if allocation.change_percentage > 10:
            if app.business_value > 0.7:
                reasons.append("high business value")
            if app.strategic_priority <= 2:
                reasons.append("strategic priority")
            if app.roi_potential > 0.7:
                reasons.append("strong ROI potential")
        elif allocation.change_percentage < -10:
            if app.business_value < 0.4:
                reasons.append("lower business impact")
            if app.technical_health > 0.8:
                reasons.append("minimal maintenance needs")
        else:
            reasons.append("aligned with current needs")

        if not reasons:
            reasons.append("balanced portfolio approach")

        return f"Allocation based on {', '.join(reasons)}"

    def _generate_recommendations(
        self,
        app: ApplicationBudgetProfile,
        allocation: BudgetAllocation
    ) -> List[str]:
        """Generate recommendations for an application."""
        recs = []

        if allocation.change_percentage > 20:
            recs.append(f"Significant budget increase of {allocation.change_percentage:.0f}% - ensure capacity to utilize")

        if app.technical_health < 0.4 and allocation.modernization_budget < allocation.recommended_budget * 0.2:
            recs.append("Consider increasing modernization investment to address technical debt")

        if app.risk_score > 0.7:
            recs.append("Prioritize security and stability improvements")

        if app.roi_potential > 0.7 and allocation.enhancement_budget < allocation.recommended_budget * 0.3:
            recs.append("High ROI potential - consider increasing enhancement budget")

        if allocation.change_percentage < -20 and app.is_mandatory:
            recs.append("Warning: Large reduction on mandatory application - review carefully")

        return recs

    def optimize(
        self,
        total_budget: float,
        objective: OptimizationObjective = OptimizationObjective.BALANCE,
        strategy: AllocationStrategy = AllocationStrategy.HYBRID,
        scenario_name: str = "Optimized Allocation"
    ) -> OptimizationScenario:
        """
        Optimize budget allocation across applications.

        Args:
            total_budget: Total budget to allocate
            objective: Optimization objective
            strategy: Allocation strategy
            scenario_name: Name for this scenario

        Returns:
            OptimizationScenario with allocations
        """
        if not self._applications:
            return OptimizationScenario(
                scenario_id=f"OPT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                scenario_name=scenario_name,
                total_budget=total_budget
            )

        # Calculate total value for normalization
        total_value = sum(self._calculate_value_score(app) for app in self._applications)

        # Calculate base allocations
        base_allocations = {}
        for app in self._applications:
            base_allocations[app.app_id] = self._calculate_base_allocation(
                app, strategy, total_budget, total_value
            )

        # Apply constraints
        adjusted_allocations, violations = self._apply_constraints(base_allocations)

        # Build allocation objects
        allocations = []
        total_allocated = 0
        total_expected_roi = 0
        total_risk = 0
        total_value_score = 0

        for app in self._applications:
            recommended = adjusted_allocations.get(app.app_id, 0)
            change = recommended - app.current_budget
            change_pct = (change / app.current_budget * 100) if app.current_budget > 0 else 0

            # Category breakdown
            categories = self._calculate_category_breakdown(app, recommended)

            # Calculate expected metrics
            value_score = self._calculate_value_score(app)
            expected_roi = value_score * 0.3 + app.roi_potential * 0.7

            allocation = BudgetAllocation(
                app_id=app.app_id,
                app_name=app.app_name,
                recommended_budget=recommended,
                current_budget=app.current_budget,
                change_amount=change,
                change_percentage=change_pct,
                maintenance_budget=categories["maintenance"],
                enhancement_budget=categories["enhancement"],
                modernization_budget=categories["modernization"],
                expected_roi=expected_roi,
                risk_reduction=min(0.3, recommended / 100000 * 0.1) if app.risk_score > 0.5 else 0,
                value_score=value_score
            )

            allocation.allocation_rationale = self._generate_allocation_rationale(app, allocation)
            allocation.recommendations = self._generate_recommendations(app, allocation)

            allocations.append(allocation)
            total_allocated += recommended
            total_expected_roi += expected_roi * recommended
            total_risk += app.risk_score * recommended
            total_value_score += value_score * recommended

        # Build scenario
        scenario = OptimizationScenario(
            scenario_id=f"OPT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            scenario_name=scenario_name,
            total_budget=total_budget,
            objective=objective,
            strategy=strategy,
            allocations=allocations,
            total_allocated=total_allocated,
            unallocated=total_budget - total_allocated,
            expected_total_roi=(total_expected_roi / total_allocated * 100) if total_allocated > 0 else 0,
            risk_score=(total_risk / total_allocated) if total_allocated > 0 else 0,
            value_score=(total_value_score / total_allocated) if total_allocated > 0 else 0,
            constraints_satisfied=len(violations) == 0,
            constraint_violations=violations
        )

        # Calculate vs current
        current_total = sum(app.current_budget for app in self._applications)
        scenario.vs_current_savings = current_total - total_allocated
        scenario.vs_current_value_gain = (scenario.value_score - 0.5) * 100  # Assuming 0.5 baseline

        return scenario

    def generate_what_if_scenarios(
        self,
        base_budget: float,
        budget_variations: List[float] = None
    ) -> List[OptimizationScenario]:
        """Generate what-if scenarios with different budgets."""
        if budget_variations is None:
            budget_variations = [0.8, 0.9, 1.0, 1.1, 1.2]

        scenarios = []
        for factor in budget_variations:
            budget = base_budget * factor
            pct = int((factor - 1) * 100)
            sign = "+" if pct >= 0 else ""
            name = f"Budget {sign}{pct}%"

            scenario = self.optimize(
                total_budget=budget,
                objective=OptimizationObjective.BALANCE,
                strategy=AllocationStrategy.HYBRID,
                scenario_name=name
            )
            scenarios.append(scenario)

        return scenarios

    def generate_multi_year_plan(
        self,
        annual_budget: float,
        years: int = 3,
        annual_growth: float = 0.05
    ) -> MultiYearPlan:
        """Generate multi-year budget plan."""
        yearly_scenarios = []
        cumulative_investment = 0
        value_trajectory = []
        risk_trajectory = []

        for year in range(1, years + 1):
            year_budget = annual_budget * (1 + annual_growth) ** (year - 1)
            scenario = self.optimize(
                total_budget=year_budget,
                objective=OptimizationObjective.BALANCE,
                strategy=AllocationStrategy.HYBRID,
                scenario_name=f"Year {year}"
            )

            yearly_scenarios.append(scenario)
            cumulative_investment += scenario.total_allocated
            value_trajectory.append(scenario.value_score)
            risk_trajectory.append(scenario.risk_score)

        # Calculate cumulative metrics
        cumulative_roi = sum(s.expected_total_roi * s.total_allocated for s in yearly_scenarios)
        cumulative_roi = cumulative_roi / cumulative_investment if cumulative_investment > 0 else 0

        return MultiYearPlan(
            plan_id=f"PLAN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            years=years,
            yearly_scenarios=yearly_scenarios,
            cumulative_investment=cumulative_investment,
            cumulative_savings=annual_budget * years - cumulative_investment,
            cumulative_roi=cumulative_roi,
            value_trajectory=value_trajectory,
            risk_trajectory=risk_trajectory
        )

    def full_optimization(
        self,
        total_budget: float,
        include_what_if: bool = True,
        include_multi_year: bool = True,
        years: int = 3
    ) -> OptimizationResult:
        """Run full budget optimization with scenarios and plans."""
        # Base optimization
        base = self.optimize(
            total_budget=total_budget,
            objective=OptimizationObjective.BALANCE,
            strategy=AllocationStrategy.HYBRID,
            scenario_name="Recommended Allocation"
        )

        # Alternative scenarios
        alternatives = []
        if include_what_if:
            alternatives = self.generate_what_if_scenarios(total_budget)

        # Multi-year plan
        multi_year = None
        if include_multi_year:
            multi_year = self.generate_multi_year_plan(total_budget, years=years)

        # Generate insights
        key_insights = []
        quick_wins = []
        recommended_changes = []

        # Analyze allocations
        increases = [a for a in base.allocations if a.change_percentage > 10]
        decreases = [a for a in base.allocations if a.change_percentage < -10]

        if increases:
            key_insights.append(
                f"{len(increases)} applications recommended for increased investment"
            )
        if decreases:
            key_insights.append(
                f"{len(decreases)} applications identified for budget reduction"
            )

        if base.unallocated > 0:
            key_insights.append(
                f"${base.unallocated:,.0f} unallocated - consider new initiatives"
            )

        # Quick wins
        for alloc in base.allocations:
            if alloc.expected_roi > 0.7 and alloc.change_amount > 0:
                quick_wins.append({
                    "app_name": alloc.app_name,
                    "investment": alloc.change_amount,
                    "expected_roi": alloc.expected_roi,
                    "description": "High ROI opportunity"
                })

        quick_wins.sort(key=lambda x: x["expected_roi"], reverse=True)
        quick_wins = quick_wins[:5]

        # Recommended changes
        for alloc in sorted(base.allocations, key=lambda x: abs(x.change_amount), reverse=True)[:10]:
            if abs(alloc.change_percentage) > 5:
                recommended_changes.append({
                    "app_name": alloc.app_name,
                    "current": alloc.current_budget,
                    "recommended": alloc.recommended_budget,
                    "change": alloc.change_amount,
                    "change_percentage": alloc.change_percentage,
                    "rationale": alloc.allocation_rationale
                })

        return OptimizationResult(
            base_scenario=base,
            alternative_scenarios=alternatives,
            multi_year_plan=multi_year,
            recommended_changes=recommended_changes,
            key_insights=key_insights,
            quick_wins=quick_wins
        )


def create_budget_optimizer() -> BudgetOptimizer:
    """Factory function to create a budget optimizer."""
    return BudgetOptimizer()


def create_demo_budget_profiles(count: int = 20) -> List[ApplicationBudgetProfile]:
    """Create demo budget profiles for testing."""
    categories = ["CRM", "ERP", "HRM", "Finance", "Marketing", "Analytics", "Security"]

    profiles = []
    for i in range(count):
        current_budget = random.uniform(50000, 500000)
        profile = ApplicationBudgetProfile(
            app_id=f"APP-{i+1:04d}",
            app_name=f"{random.choice(categories)} System {i+1}",
            current_budget=current_budget,
            current_cost=current_budget * random.uniform(0.9, 1.1),
            business_value=random.uniform(0.2, 1.0),
            strategic_alignment=random.uniform(0.3, 1.0),
            user_impact=random.uniform(0.2, 0.9),
            technical_health=random.uniform(0.3, 1.0),
            risk_score=random.uniform(0.1, 0.8),
            roi_potential=random.uniform(0.2, 0.9),
            cost_per_user=random.uniform(100, 1000),
            minimum_budget=current_budget * 0.5 if random.random() > 0.7 else 0,
            maximum_budget=current_budget * 2 if random.random() > 0.5 else float('inf'),
            is_mandatory=random.random() > 0.8,
            category=random.choice(categories),
            strategic_priority=random.randint(1, 5)
        )
        profiles.append(profile)

    return profiles
