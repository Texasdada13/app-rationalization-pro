"""
Cost Modeler Module
TCO breakdown, cost allocation, hidden cost identification, and optimization analysis.
Ported from application-rationalization-tool without pandas dependency.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime, timedelta
import random


@dataclass
class TCOBreakdown:
    """TCO breakdown percentages (industry averages)"""
    licensing: float = 0.30      # 30% - Software licenses
    support: float = 0.20        # 20% - Vendor support and maintenance
    infrastructure: float = 0.25 # 25% - Servers, storage, network
    labor: float = 0.20          # 20% - Internal staff time
    training: float = 0.03       # 3% - User training
    other: float = 0.02          # 2% - Misc costs

    def to_dict(self) -> Dict[str, float]:
        return {
            'licensing': self.licensing,
            'support': self.support,
            'infrastructure': self.infrastructure,
            'labor': self.labor,
            'training': self.training,
            'other': self.other
        }


# Cost multipliers by category
CATEGORY_MULTIPLIERS = {
    'IT & Infrastructure': {'infrastructure': 1.5, 'labor': 1.3},
    'Finance & Accounting': {'support': 1.2, 'training': 1.5},
    'Citizen Services': {'labor': 1.4, 'support': 1.1},
    'Human Resources': {'training': 1.6, 'support': 1.2},
    'Public Safety': {'infrastructure': 1.3, 'labor': 1.5},
    'Operations': {'infrastructure': 1.2, 'labor': 1.3},
    'Compliance & Reporting': {'support': 1.4, 'labor': 1.2},
    'Records Management': {'infrastructure': 1.3, 'support': 1.1},
    'ERP': {'licensing': 1.3, 'support': 1.4, 'training': 1.5},
    'CRM': {'licensing': 1.2, 'support': 1.3},
    'BI': {'infrastructure': 1.2, 'labor': 1.3},
    'Security': {'infrastructure': 1.4, 'labor': 1.5},
    'Collaboration': {'licensing': 1.1, 'training': 1.3},
}

# Category to department mapping
CATEGORY_TO_DEPARTMENT = {
    'Finance & Accounting': 'Finance Department',
    'IT & Infrastructure': 'IT Department',
    'Citizen Services': 'Citizen Services',
    'Human Resources': 'Human Resources',
    'Public Safety': 'Public Safety',
    'Operations': 'Operations',
    'Compliance & Reporting': 'Legal/Compliance',
    'Records Management': 'Administration',
    'ERP': 'Finance Department',
    'CRM': 'Sales/Marketing',
    'BI': 'IT Department',
    'Security': 'IT Department',
    'Collaboration': 'IT Department',
}


class CostModeler:
    """
    Advanced cost modeling with TCO breakdown and optimization analysis.

    Features:
    - TCO breakdown by component (licensing, support, infrastructure, etc.)
    - Department cost allocation
    - Hidden cost identification
    - Cost optimization opportunities
    - Contract renewal tracking
    """

    def __init__(self, applications: List[Dict[str, Any]]):
        """
        Initialize with application data.

        Args:
            applications: List of application dicts with keys:
                - name, category, cost, business_value, tech_health, etc.
        """
        self.applications = applications
        self.tco_data: List[Dict] = []
        self.hidden_costs: List[Dict] = []

    def calculate_tco_breakdown(self) -> Dict[str, Any]:
        """Calculate detailed TCO breakdown for each application."""
        tco_breakdown = []

        for app in self.applications:
            app_name = app.get('name', 'Unknown')
            total_cost = app.get('cost', 0) or 0
            category = app.get('category', 'Other')

            # Get base percentages
            base = TCOBreakdown()
            breakdown = base.to_dict()

            # Apply category-specific multipliers
            if category in CATEGORY_MULTIPLIERS:
                multipliers = CATEGORY_MULTIPLIERS[category]
                for component, multiplier in multipliers.items():
                    if component in breakdown:
                        breakdown[component] *= multiplier

                # Renormalize to ensure sum = 1.0
                total = sum(breakdown.values())
                breakdown = {k: v / total for k, v in breakdown.items()}

            # Calculate dollar amounts
            component_costs = {
                component: round(total_cost * percentage, 2)
                for component, percentage in breakdown.items()
            }

            tco_breakdown.append({
                'app_name': app_name,
                'app_id': app.get('id'),
                'category': category,
                'total_cost': total_cost,
                'components': component_costs,
                'percentages': {k: round(v * 100, 1) for k, v in breakdown.items()}
            })

        self.tco_data = tco_breakdown
        return self._aggregate_tco_summary(tco_breakdown)

    def _aggregate_tco_summary(self, tco_breakdown: List[Dict]) -> Dict[str, Any]:
        """Aggregate TCO data across entire portfolio."""
        component_totals = defaultdict(float)

        for app in tco_breakdown:
            for component, cost in app['components'].items():
                component_totals[component] += cost

        total_cost = sum(component_totals.values())

        return {
            'total_portfolio_cost': total_cost,
            'component_breakdown': dict(component_totals),
            'component_percentages': {
                k: round((v / total_cost) * 100, 1) if total_cost > 0 else 0
                for k, v in component_totals.items()
            },
            'top_cost_drivers': self._identify_cost_drivers(tco_breakdown),
            'application_count': len(tco_breakdown),
            'app_breakdowns': tco_breakdown
        }

    def _identify_cost_drivers(self, tco_breakdown: List[Dict]) -> List[Dict]:
        """Identify top cost-driving applications."""
        sorted_apps = sorted(tco_breakdown, key=lambda x: x['total_cost'], reverse=True)

        return [
            {
                'app_name': app['app_name'],
                'total_cost': app['total_cost'],
                'category': app['category'],
                'top_component': max(app['components'].items(), key=lambda x: x[1])[0] if app['components'] else 'N/A',
                'top_component_cost': max(app['components'].values()) if app['components'] else 0
            }
            for app in sorted_apps[:10]
        ]

    def allocate_costs_by_department(self) -> Dict[str, Any]:
        """Allocate costs to departments."""
        dept_costs = defaultdict(lambda: {
            'total_cost': 0,
            'app_count': 0,
            'avg_health': 0,
            'avg_value': 0,
            'health_sum': 0,
            'value_sum': 0,
            'apps': []
        })

        for app in self.applications:
            category = app.get('category', 'Other')
            dept = CATEGORY_TO_DEPARTMENT.get(category, 'General Administration')

            dept_costs[dept]['total_cost'] += app.get('cost', 0) or 0
            dept_costs[dept]['app_count'] += 1
            dept_costs[dept]['health_sum'] += app.get('tech_health', 5) or 5
            dept_costs[dept]['value_sum'] += app.get('business_value', 5) or 5
            dept_costs[dept]['apps'].append(app.get('name', 'Unknown'))

        # Calculate averages
        allocations = []
        for dept, data in dept_costs.items():
            if data['app_count'] > 0:
                allocations.append({
                    'department': dept,
                    'total_cost': data['total_cost'],
                    'app_count': data['app_count'],
                    'avg_health': round(data['health_sum'] / data['app_count'], 1),
                    'avg_value': round(data['value_sum'] / data['app_count'], 1),
                    'applications': data['apps']
                })

        # Sort by total cost
        allocations.sort(key=lambda x: x['total_cost'], reverse=True)

        total_cost = sum(a['total_cost'] for a in allocations)

        return {
            'allocation_method': 'category_based',
            'departments': allocations,
            'total_departments': len(allocations),
            'highest_spend': allocations[0] if allocations else None,
            'total_cost': total_cost
        }

    def identify_hidden_costs(self) -> List[Dict[str, Any]]:
        """Identify potential hidden costs and optimization opportunities."""
        hidden_costs = []

        # 1. Integration complexity costs
        integration_costs = self._estimate_integration_costs()
        if integration_costs:
            hidden_costs.append(integration_costs)

        # 2. Redundancy costs
        redundancy_costs = self._estimate_redundancy_costs()
        if redundancy_costs:
            hidden_costs.append(redundancy_costs)

        # 3. Technical debt costs
        tech_debt_costs = self._estimate_technical_debt_costs()
        if tech_debt_costs:
            hidden_costs.append(tech_debt_costs)

        # 4. Training and onboarding costs
        training_costs = self._estimate_training_costs()
        if training_costs:
            hidden_costs.append(training_costs)

        # 5. Opportunity costs
        opportunity_costs = self._estimate_opportunity_costs()
        if opportunity_costs:
            hidden_costs.append(opportunity_costs)

        self.hidden_costs = hidden_costs
        return hidden_costs

    def _estimate_integration_costs(self) -> Optional[Dict[str, Any]]:
        """Estimate costs of maintaining integrations."""
        integration_risky = [
            app for app in self.applications
            if (app.get('tech_health', 5) or 5) <= 4
        ]

        if not integration_risky:
            return None

        total_cost = sum(app.get('cost', 0) or 0 for app in integration_risky)
        integration_overhead = total_cost * 0.12

        return {
            'category': 'Integration Complexity',
            'estimated_annual_cost': round(integration_overhead, 2),
            'affected_apps': len(integration_risky),
            'description': 'Annual cost of maintaining fragile integrations',
            'potential_savings': round(integration_overhead * 0.3, 2),
            'recommendation': 'Modernize or consolidate apps with low health scores to reduce integration overhead'
        }

    def _estimate_redundancy_costs(self) -> Optional[Dict[str, Any]]:
        """Estimate costs of redundant applications."""
        category_counts = defaultdict(list)
        for app in self.applications:
            cat = app.get('category', 'Other')
            category_counts[cat].append(app)

        redundant_categories = {k: v for k, v in category_counts.items() if len(v) >= 3}

        if not redundant_categories:
            return None

        redundant_apps = []
        for apps in redundant_categories.values():
            redundant_apps.extend(apps)

        redundancy_cost = sum(app.get('cost', 0) or 0 for app in redundant_apps)
        potential_savings = redundancy_cost * 0.25

        return {
            'category': 'Application Redundancy',
            'estimated_annual_cost': round(redundancy_cost, 2),
            'affected_apps': len(redundant_apps),
            'affected_categories': len(redundant_categories),
            'description': 'Cost of maintaining redundant or overlapping applications',
            'potential_savings': round(potential_savings, 2),
            'recommendation': f'Review {len(redundant_categories)} categories with 3+ apps for consolidation opportunities'
        }

    def _estimate_technical_debt_costs(self) -> Optional[Dict[str, Any]]:
        """Estimate costs of technical debt."""
        tech_debt_apps = [
            app for app in self.applications
            if (app.get('tech_health', 5) or 5) <= 5
        ]

        if not tech_debt_apps:
            return None

        total_cost = sum(app.get('cost', 0) or 0 for app in tech_debt_apps)
        debt_cost = total_cost * 0.20

        return {
            'category': 'Technical Debt',
            'estimated_annual_cost': round(debt_cost, 2),
            'affected_apps': len(tech_debt_apps),
            'description': 'Additional maintenance costs due to aging technology',
            'potential_savings': round(debt_cost * 0.7, 2),
            'recommendation': 'Prioritize modernization of applications with health scores <= 5'
        }

    def _estimate_training_costs(self) -> Optional[Dict[str, Any]]:
        """Estimate training and support costs."""
        high_support_apps = [
            app for app in self.applications
            if (app.get('tech_health', 5) or 5) <= 6
        ]

        if not high_support_apps:
            return None

        total_cost = sum(app.get('cost', 0) or 0 for app in high_support_apps)
        training_overhead = total_cost * 0.065

        return {
            'category': 'Training & Support',
            'estimated_annual_cost': round(training_overhead, 2),
            'affected_apps': len(high_support_apps),
            'description': 'Excess training costs for difficult-to-use systems',
            'potential_savings': round(training_overhead * 0.5, 2),
            'recommendation': 'Improve UX or replace apps with poor usability'
        }

    def _estimate_opportunity_costs(self) -> Optional[Dict[str, Any]]:
        """Estimate opportunity costs of low-value applications."""
        low_value_apps = [
            app for app in self.applications
            if (app.get('business_value', 5) or 5) <= 4
        ]

        if not low_value_apps:
            return None

        opportunity_cost = sum(app.get('cost', 0) or 0 for app in low_value_apps)

        return {
            'category': 'Opportunity Cost',
            'estimated_annual_cost': round(opportunity_cost, 2),
            'affected_apps': len(low_value_apps),
            'description': 'Budget locked in low-value applications',
            'potential_savings': round(opportunity_cost * 0.6, 2),
            'recommendation': 'Retire or replace low-value apps to free budget for strategic initiatives'
        }

    def get_cost_optimization_summary(self) -> Dict[str, Any]:
        """Generate comprehensive cost optimization summary."""
        if not self.tco_data:
            self.calculate_tco_breakdown()

        if not self.hidden_costs:
            self.identify_hidden_costs()

        dept_allocation = self.allocate_costs_by_department()

        total_hidden_cost = sum(h['estimated_annual_cost'] for h in self.hidden_costs)
        total_potential_savings = sum(h['potential_savings'] for h in self.hidden_costs)

        total_portfolio_cost = sum(app.get('cost', 0) or 0 for app in self.applications)

        quick_wins = self._identify_quick_wins()

        return {
            'current_portfolio_cost': total_portfolio_cost,
            'hidden_costs_total': total_hidden_cost,
            'potential_savings': total_potential_savings,
            'savings_percentage': round((total_potential_savings / total_portfolio_cost) * 100, 1) if total_portfolio_cost > 0 else 0,
            'hidden_cost_categories': self.hidden_costs,
            'department_allocation': dept_allocation,
            'quick_wins': quick_wins,
            'top_opportunities': self._rank_optimization_opportunities()
        }

    def _identify_quick_wins(self) -> List[Dict[str, Any]]:
        """Identify quick win cost optimization opportunities."""
        quick_wins = []

        # High cost, low value apps
        retire_candidates = [
            app for app in self.applications
            if (app.get('cost', 0) or 0) > 50000
            and (app.get('business_value', 5) or 5) <= 4
            and (app.get('tech_health', 5) or 5) <= 4
        ]

        if retire_candidates:
            quick_wins.append({
                'opportunity': 'Retire High-Cost, Low-Value Apps',
                'app_count': len(retire_candidates),
                'potential_savings': sum(app.get('cost', 0) or 0 for app in retire_candidates),
                'effort': 'Low',
                'apps': [app.get('name') for app in retire_candidates[:5]]
            })

        # Redundant low-cost apps
        low_cost_redundant = [
            app for app in self.applications
            if (app.get('cost', 0) or 0) < 20000
            and (app.get('business_value', 5) or 5) <= 5
        ]

        if len(low_cost_redundant) >= 5:
            quick_wins.append({
                'opportunity': 'Consolidate Low-Cost Redundant Apps',
                'app_count': len(low_cost_redundant),
                'potential_savings': sum(app.get('cost', 0) or 0 for app in low_cost_redundant) * 0.3,
                'effort': 'Low',
                'apps': [app.get('name') for app in low_cost_redundant[:5]]
            })

        return quick_wins

    def _rank_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """Rank all cost optimization opportunities by impact."""
        opportunities = []

        # Retirement opportunities
        retire_apps = [app for app in self.applications if (app.get('business_value', 5) or 5) <= 4]
        retire_savings = sum(app.get('cost', 0) or 0 for app in retire_apps)
        opportunities.append({
            'category': 'Application Retirement',
            'potential_savings': retire_savings,
            'effort': 'Low-Medium',
            'timeframe': '3-6 months',
            'priority': 1 if retire_savings > 500000 else 2
        })

        # Consolidation opportunities
        consolidate_apps = [app for app in self.applications if (app.get('tech_health', 5) or 5) <= 6]
        consolidate_savings = sum(app.get('cost', 0) or 0 for app in consolidate_apps) * 0.25
        opportunities.append({
            'category': 'Application Consolidation',
            'potential_savings': consolidate_savings,
            'effort': 'Medium',
            'timeframe': '6-12 months',
            'priority': 1 if consolidate_savings > 1000000 else 2
        })

        # Modernization opportunities
        modernize_apps = [
            app for app in self.applications
            if (app.get('tech_health', 5) or 5) <= 5
            and (app.get('business_value', 5) or 5) >= 7
        ]
        modernize_savings = sum(app.get('cost', 0) or 0 for app in modernize_apps) * 0.15
        opportunities.append({
            'category': 'Application Modernization',
            'potential_savings': modernize_savings,
            'effort': 'High',
            'timeframe': '12-24 months',
            'priority': 1 if len(modernize_apps) > 0 else 3
        })

        opportunities.sort(key=lambda x: (x['priority'], -x['potential_savings']))
        return opportunities
