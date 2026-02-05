"""
What-If Scenario Analysis Engine for App Rationalization Pro

Interactive simulation of portfolio rationalization scenarios.
Ported from pandas-based implementation to native Python.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ScenarioResult:
    """Result of a what-if scenario simulation"""
    scenario_type: str
    apps_affected: List[str]
    baseline: Dict[str, Any]
    new_state: Dict[str, Any]
    impact: Dict[str, Any]
    details: Dict[str, Any]
    timestamp: str


class WhatIfScenarioEngine:
    """
    Interactive scenario simulator for portfolio rationalization.

    Allows users to test questions like:
    - "What if we retire these applications?"
    - "What if we modernize these critical apps?"
    - "What if we consolidate redundant systems?"

    Provides impact analysis including cost savings, health improvements,
    and portfolio risk changes.
    """

    def __init__(self, applications: List[Dict[str, Any]]):
        """
        Initialize with application portfolio data.

        Args:
            applications: List of application dictionaries with keys:
                - name: Application name
                - cost: Annual cost
                - tech_health: Technical health score (0-10)
                - business_value: Business value score (0-10)
                - security: Security score (0-10)
                - redundancy: 0 or 1 indicating redundancy
                - category: Optional category for grouping
        """
        self.applications = [app.copy() for app in applications]
        self.baseline = self._calculate_baseline_metrics()

    def _calculate_baseline_metrics(self) -> Dict[str, Any]:
        """Calculate current state metrics as baseline."""
        if not self.applications:
            return {
                'total_apps': 0,
                'total_cost': 0,
                'avg_health': 0,
                'avg_value': 0,
                'avg_security': 0,
                'total_redundancy_count': 0,
                'risk_score': 0
            }

        total_cost = sum(app.get('cost', 0) for app in self.applications)

        health_values = [app.get('tech_health', 5) for app in self.applications]
        avg_health = sum(health_values) / len(health_values) if health_values else 0

        value_values = [app.get('business_value', 5) for app in self.applications]
        avg_value = sum(value_values) / len(value_values) if value_values else 0

        security_values = [app.get('security', 5) for app in self.applications]
        avg_security = sum(security_values) / len(security_values) if security_values else 0

        redundancy_count = sum(1 for app in self.applications if app.get('redundancy', 0) > 0)

        return {
            'total_apps': len(self.applications),
            'total_cost': total_cost,
            'avg_health': round(avg_health, 2),
            'avg_value': round(avg_value, 2),
            'avg_security': round(avg_security, 2),
            'total_redundancy_count': redundancy_count,
            'risk_score': self._calculate_portfolio_risk(self.applications)
        }

    def _calculate_portfolio_risk(self, apps: List[Dict]) -> float:
        """
        Calculate overall portfolio risk score (0-100, lower is better).

        Risk factors:
        - Low tech health = high risk (50% weight)
        - Low security = high risk (30% weight)
        - High redundancy = high risk (20% weight)
        """
        if not apps:
            return 0

        # Calculate averages
        avg_health = sum(app.get('tech_health', 5) for app in apps) / len(apps)
        avg_security = sum(app.get('security', 5) for app in apps) / len(apps)
        redundancy_count = sum(1 for app in apps if app.get('redundancy', 0) > 0)

        # Risk factors (inverted from quality scores)
        health_risk = (10 - avg_health) * 10  # Low health = high risk
        security_risk = (10 - avg_security) * 10
        redundancy_risk = (redundancy_count / len(apps)) * 20 if apps else 0

        # Weighted risk score
        total_risk = (health_risk * 0.5) + (security_risk * 0.3) + (redundancy_risk * 0.2)

        return round(min(100, max(0, total_risk)), 1)

    def simulate_retirement(self, app_names: List[str]) -> Dict[str, Any]:
        """
        Simulate retiring a list of applications.

        Args:
            app_names: Names of applications to retire

        Returns:
            Impact analysis including cost savings and portfolio changes
        """
        if not app_names:
            return self._create_scenario_result('retirement', [], self.baseline, self.baseline)

        # Split into retired and remaining
        retired_apps = [app for app in self.applications if app.get('name') in app_names]
        remaining_apps = [app for app in self.applications if app.get('name') not in app_names]

        # Calculate new metrics for remaining portfolio
        new_metrics = self._calculate_metrics_for_apps(remaining_apps)

        # Calculate impact
        impact = self._calculate_impact(self.baseline, new_metrics)

        # Retirement details
        retirement_details = {
            'apps_retired': len(retired_apps),
            'cost_savings': sum(app.get('cost', 0) for app in retired_apps),
            'avg_retired_health': self._safe_avg([app.get('tech_health', 5) for app in retired_apps]),
            'avg_retired_value': self._safe_avg([app.get('business_value', 5) for app in retired_apps]),
            'retired_apps': [
                {
                    'name': app.get('name'),
                    'cost': app.get('cost', 0),
                    'tech_health': app.get('tech_health', 5),
                    'business_value': app.get('business_value', 5)
                }
                for app in retired_apps
            ]
        }

        return self._create_scenario_result('retirement', app_names, new_metrics, impact, retirement_details)

    def simulate_modernization(
        self,
        app_names: List[str],
        health_improvement: float = 3.0
    ) -> Dict[str, Any]:
        """
        Simulate modernizing applications (improving tech health).

        Args:
            app_names: Names of applications to modernize
            health_improvement: Points to add to tech health (default 3.0)

        Returns:
            Impact analysis including one-time cost and health improvements
        """
        if not app_names:
            return self._create_scenario_result('modernization', [], self.baseline, self.baseline)

        # Copy and modify applications
        modernized_apps = []
        modernized_list = []
        original_health_values = []
        new_health_values = []

        for app in self.applications:
            app_copy = app.copy()
            if app.get('name') in app_names:
                original_health = app_copy.get('tech_health', 5)
                original_health_values.append(original_health)

                # Improve tech health (cap at 10)
                new_health = min(10, original_health + health_improvement)
                app_copy['tech_health'] = new_health
                new_health_values.append(new_health)

                # Improve security as well (40% of health improvement)
                original_security = app_copy.get('security', 5)
                app_copy['security'] = min(10, original_security + (health_improvement * 0.4))

                modernized_list.append({
                    'name': app.get('name'),
                    'cost': app.get('cost', 0),
                    'original_health': original_health,
                    'new_health': new_health,
                    'business_value': app.get('business_value', 5)
                })

            modernized_apps.append(app_copy)

        # Calculate modernization cost (15% of annual cost per health point)
        modernization_cost = sum(
            app.get('cost', 0) * 0.15 * health_improvement
            for app in self.applications
            if app.get('name') in app_names
        )

        # Calculate new metrics
        new_metrics = self._calculate_metrics_for_apps(modernized_apps)

        # Calculate impact
        impact = self._calculate_impact(self.baseline, new_metrics)

        # Modernization details
        modernization_details = {
            'apps_modernized': len(modernized_list),
            'one_time_cost': round(modernization_cost, 2),
            'health_improvement': health_improvement,
            'avg_original_health': self._safe_avg(original_health_values),
            'avg_new_health': self._safe_avg(new_health_values),
            'modernized_apps': modernized_list
        }

        return self._create_scenario_result('modernization', app_names, new_metrics, impact, modernization_details)

    def simulate_consolidation(
        self,
        app_groups: List[List[str]],
        consolidation_cost_reduction: float = 0.30
    ) -> Dict[str, Any]:
        """
        Simulate consolidating redundant applications.

        For each group, keeps the highest business value app and retires others.
        The surviving app gets a cost reduction.

        Args:
            app_groups: List of lists, each inner list contains app names to consolidate
            consolidation_cost_reduction: Percentage cost reduction (default 30%)

        Returns:
            Impact analysis including annual savings and one-time costs
        """
        if not app_groups:
            return self._create_scenario_result('consolidation', [], self.baseline, self.baseline)

        working_apps = [app.copy() for app in self.applications]
        total_cost_saved = 0
        apps_eliminated = []
        consolidation_cost = 0

        for group in app_groups:
            if len(group) <= 1:
                continue

            # Get apps in this consolidation group
            group_apps = [app for app in working_apps if app.get('name') in group]
            if not group_apps:
                continue

            # Total cost of group
            group_cost = sum(app.get('cost', 0) for app in group_apps)

            # Find highest business value app (keep this one)
            best_app = max(group_apps, key=lambda x: x.get('business_value', 0))
            best_app_name = best_app.get('name')

            # New cost after consolidation
            new_cost = best_app.get('cost', 0) * (1 - consolidation_cost_reduction)

            cost_saved = group_cost - new_cost
            total_cost_saved += cost_saved

            # One-time consolidation cost (50% of first-year savings)
            consolidation_cost += cost_saved * 0.5

            # Remove consolidated apps (except the primary one)
            apps_to_remove = [name for name in group if name != best_app_name]
            apps_eliminated.extend(apps_to_remove)

            # Update working apps list
            working_apps = [app for app in working_apps if app.get('name') not in apps_to_remove]

            # Update cost for the surviving app
            for app in working_apps:
                if app.get('name') == best_app_name:
                    app['cost'] = new_cost
                    break

        # Calculate new metrics
        new_metrics = self._calculate_metrics_for_apps(working_apps)

        # Calculate impact
        impact = self._calculate_impact(self.baseline, new_metrics)

        # Consolidation details
        consolidation_details = {
            'groups_consolidated': len([g for g in app_groups if len(g) > 1]),
            'apps_eliminated': len(apps_eliminated),
            'annual_savings': round(total_cost_saved, 2),
            'one_time_cost': round(consolidation_cost, 2),
            'eliminated_apps': apps_eliminated
        }

        all_consolidated_apps = [app for group in app_groups for app in group]

        return self._create_scenario_result('consolidation', all_consolidated_apps, new_metrics, impact, consolidation_details)

    def simulate_combined_scenario(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Simulate a combined scenario with multiple actions.

        Args:
            scenarios: List of scenario dicts, each with 'type' and relevant params:
                - {'type': 'retire', 'apps': ['App1', 'App2']}
                - {'type': 'modernize', 'apps': ['App3'], 'health_improvement': 4}
                - {'type': 'consolidate', 'app_groups': [['App4', 'App5']]}

        Returns:
            Combined impact analysis with ROI calculations
        """
        if not scenarios:
            return self._create_scenario_result('combined', [], self.baseline, self.baseline)

        working_apps = [app.copy() for app in self.applications]
        total_cost_saved = 0
        total_one_time_cost = 0
        actions_summary = []

        for scenario in scenarios:
            scenario_type = scenario.get('type')

            if scenario_type == 'retire':
                apps = scenario.get('apps', [])
                if apps:
                    retired = [app for app in working_apps if app.get('name') in apps]
                    total_cost_saved += sum(app.get('cost', 0) for app in retired)
                    working_apps = [app for app in working_apps if app.get('name') not in apps]
                    actions_summary.append(f"Retired {len(apps)} applications")

            elif scenario_type == 'modernize':
                apps = scenario.get('apps', [])
                health_improvement = scenario.get('health_improvement', 3.0)
                if apps:
                    modernized_count = 0
                    for app in working_apps:
                        if app.get('name') in apps:
                            total_one_time_cost += app.get('cost', 0) * 0.15 * health_improvement
                            app['tech_health'] = min(10, app.get('tech_health', 5) + health_improvement)
                            app['security'] = min(10, app.get('security', 5) + (health_improvement * 0.4))
                            modernized_count += 1
                    actions_summary.append(f"Modernized {modernized_count} applications (+{health_improvement} health)")

            elif scenario_type == 'consolidate':
                app_groups = scenario.get('app_groups', [])
                cost_reduction = scenario.get('cost_reduction', 0.30)

                for group in app_groups:
                    if len(group) <= 1:
                        continue

                    group_apps = [app for app in working_apps if app.get('name') in group]
                    if not group_apps:
                        continue

                    group_cost = sum(app.get('cost', 0) for app in group_apps)
                    best_app = max(group_apps, key=lambda x: x.get('business_value', 0))
                    best_app_name = best_app.get('name')
                    new_cost = best_app.get('cost', 0) * (1 - cost_reduction)

                    cost_saved = group_cost - new_cost
                    total_cost_saved += cost_saved
                    total_one_time_cost += cost_saved * 0.5

                    apps_to_remove = [name for name in group if name != best_app_name]
                    working_apps = [app for app in working_apps if app.get('name') not in apps_to_remove]

                    for app in working_apps:
                        if app.get('name') == best_app_name:
                            app['cost'] = new_cost
                            break

                if app_groups:
                    actions_summary.append(f"Consolidated {len(app_groups)} groups")

        # Calculate new metrics
        new_metrics = self._calculate_metrics_for_apps(working_apps)

        # Calculate impact
        impact = self._calculate_impact(self.baseline, new_metrics)

        # Combined scenario details
        combined_details = {
            'actions_performed': len(scenarios),
            'actions_summary': actions_summary,
            'total_annual_savings': round(total_cost_saved, 2),
            'total_one_time_cost': round(total_one_time_cost, 2),
            'net_first_year_impact': round(total_cost_saved - total_one_time_cost, 2),
            'roi_percentage': round((total_cost_saved / total_one_time_cost * 100), 1) if total_one_time_cost > 0 else 0
        }

        return self._create_scenario_result('combined', [], new_metrics, impact, combined_details)

    def get_recommended_scenarios(self) -> List[Dict[str, Any]]:
        """
        Generate 3-5 recommended scenarios based on portfolio analysis.

        Analyzes the portfolio to suggest:
        - Aggressive retirement of low-value, poor-health apps
        - Critical modernization of high-value apps with aging tech
        - Consolidation of redundant applications
        - Balanced optimization combining multiple strategies

        Returns:
            List of recommended scenarios with estimated impacts
        """
        recommendations = []

        # Scenario 1: Retire low-value, low-health apps
        retire_candidates = [
            app for app in self.applications
            if app.get('tech_health', 5) <= 3 and app.get('business_value', 5) <= 4
        ]

        if retire_candidates:
            recommendations.append({
                'name': 'Aggressive Retirement',
                'description': f'Retire {len(retire_candidates)} low-value, poor-health applications',
                'apps': [app.get('name') for app in retire_candidates],
                'type': 'retire',
                'estimated_savings': round(sum(app.get('cost', 0) for app in retire_candidates), 2)
            })

        # Scenario 2: Modernize critical apps with poor health
        modernize_candidates = [
            app for app in self.applications
            if app.get('tech_health', 5) <= 5 and app.get('business_value', 5) >= 7
        ]

        if modernize_candidates:
            estimated_cost = sum(app.get('cost', 0) * 0.15 * 3 for app in modernize_candidates)
            recommendations.append({
                'name': 'Critical Modernization',
                'description': f'Modernize {len(modernize_candidates)} critical applications with aging tech',
                'apps': [app.get('name') for app in modernize_candidates],
                'type': 'modernize',
                'estimated_cost': round(estimated_cost, 2)
            })

        # Scenario 3: Consolidate redundant apps by category
        redundant_apps = [app for app in self.applications if app.get('redundancy', 0) > 0]
        if len(redundant_apps) >= 4:
            # Group by category
            categories = {}
            for app in redundant_apps:
                category = app.get('category', 'Other')
                if category not in categories:
                    categories[category] = []
                categories[category].append(app.get('name'))

            consolidation_groups = [
                names[:4]  # Max 4 per group
                for names in categories.values()
                if len(names) >= 2
            ]

            if consolidation_groups:
                recommendations.append({
                    'name': 'Redundancy Consolidation',
                    'description': f'Consolidate {len(consolidation_groups)} groups of redundant applications',
                    'app_groups': consolidation_groups,
                    'type': 'consolidate'
                })

        # Scenario 4: Balanced approach
        # Get top 10 retirement candidates (lowest business value)
        retire_some = sorted(retire_candidates, key=lambda x: x.get('business_value', 5))[:10]
        retire_some_names = [app.get('name') for app in retire_some]

        # Get top 5 modernization candidates (highest business value)
        modernize_some = sorted(modernize_candidates, key=lambda x: x.get('business_value', 5), reverse=True)[:5]
        modernize_some_names = [app.get('name') for app in modernize_some]

        if retire_some_names and modernize_some_names:
            recommendations.append({
                'name': 'Balanced Optimization',
                'description': f'Retire {len(retire_some_names)} apps + Modernize {len(modernize_some_names)} critical apps',
                'scenarios': [
                    {'type': 'retire', 'apps': retire_some_names},
                    {'type': 'modernize', 'apps': modernize_some_names, 'health_improvement': 3}
                ],
                'type': 'combined'
            })

        return recommendations

    def _calculate_metrics_for_apps(self, apps: List[Dict]) -> Dict[str, Any]:
        """Calculate metrics for a given list of applications."""
        if not apps:
            return {
                'total_apps': 0,
                'total_cost': 0,
                'avg_health': 0,
                'avg_value': 0,
                'avg_security': 0,
                'total_redundancy_count': 0,
                'risk_score': 0
            }

        return {
            'total_apps': len(apps),
            'total_cost': sum(app.get('cost', 0) for app in apps),
            'avg_health': self._safe_avg([app.get('tech_health', 5) for app in apps]),
            'avg_value': self._safe_avg([app.get('business_value', 5) for app in apps]),
            'avg_security': self._safe_avg([app.get('security', 5) for app in apps]),
            'total_redundancy_count': sum(1 for app in apps if app.get('redundancy', 0) > 0),
            'risk_score': self._calculate_portfolio_risk(apps)
        }

    def _calculate_impact(self, baseline: Dict, new_metrics: Dict) -> Dict[str, Any]:
        """Calculate the delta/impact between baseline and new metrics."""
        def pct_change(new_val, old_val):
            if old_val == 0:
                return 0
            return round(((new_val - old_val) / old_val * 100), 1)

        return {
            'apps_change': new_metrics['total_apps'] - baseline['total_apps'],
            'apps_change_pct': pct_change(new_metrics['total_apps'], baseline['total_apps']),

            'cost_change': new_metrics['total_cost'] - baseline['total_cost'],
            'cost_change_pct': pct_change(new_metrics['total_cost'], baseline['total_cost']),

            'health_change': round(new_metrics['avg_health'] - baseline['avg_health'], 2),
            'health_change_pct': pct_change(new_metrics['avg_health'], baseline['avg_health']),

            'value_change': round(new_metrics['avg_value'] - baseline['avg_value'], 2),
            'value_change_pct': pct_change(new_metrics['avg_value'], baseline['avg_value']),

            'security_change': round(new_metrics['avg_security'] - baseline['avg_security'], 2),
            'security_change_pct': pct_change(new_metrics['avg_security'], baseline['avg_security']),

            'risk_change': round(new_metrics['risk_score'] - baseline['risk_score'], 2),
            'risk_change_pct': pct_change(new_metrics['risk_score'], baseline['risk_score']),
        }

    def _create_scenario_result(
        self,
        scenario_type: str,
        app_names: List[str],
        new_metrics: Dict,
        impact: Dict,
        details: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create standardized scenario result object."""
        return {
            'scenario_type': scenario_type,
            'timestamp': datetime.now().isoformat(),
            'apps_affected': app_names,
            'baseline': self.baseline,
            'new_state': new_metrics,
            'impact': impact,
            'details': details or {}
        }

    def _safe_avg(self, values: List[float]) -> float:
        """Calculate average safely handling empty lists."""
        if not values:
            return 0
        return round(sum(values) / len(values), 2)
