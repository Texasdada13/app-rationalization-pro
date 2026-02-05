"""
Benchmark Engine for App Rationalization Pro

Industry benchmarking and peer comparison with best practice recommendations.
Ported from pandas-based implementation to native Python.
"""

from typing import Dict, List, Any, Optional
import re


class BenchmarkEngine:
    """
    Compare portfolio against industry benchmarks and best practices.

    Features:
    - Portfolio size classification
    - Health distribution benchmarking
    - Cost efficiency analysis
    - Maturity assessment
    - Best practices recommendations
    """

    # Industry benchmark data (based on typical enterprise portfolios)
    INDUSTRY_BENCHMARKS = {
        'portfolio_size': {
            'small': {'apps': 50, 'cost_per_app': 75000},
            'medium': {'apps': 150, 'cost_per_app': 95000},
            'large': {'apps': 300, 'cost_per_app': 110000},
            'enterprise': {'apps': 500, 'cost_per_app': 125000}
        },
        'health_distribution': {
            'best_in_class': {'critical': 0.02, 'poor': 0.08, 'fair': 0.20, 'good': 0.40, 'excellent': 0.30},
            'industry_average': {'critical': 0.08, 'poor': 0.15, 'fair': 0.30, 'good': 0.35, 'excellent': 0.12},
            'needs_improvement': {'critical': 0.15, 'poor': 0.25, 'fair': 0.35, 'good': 0.20, 'excellent': 0.05}
        },
        'cost_efficiency': {
            'best_in_class': {'cost_per_user': 250, 'maintenance_ratio': 0.15, 'tech_debt_ratio': 0.10},
            'industry_average': {'cost_per_user': 400, 'maintenance_ratio': 0.25, 'tech_debt_ratio': 0.20},
            'needs_improvement': {'cost_per_user': 600, 'maintenance_ratio': 0.40, 'tech_debt_ratio': 0.35}
        },
        'modernization_rate': {
            'best_in_class': 0.25,   # 25% of portfolio modernized per year
            'industry_average': 0.15,
            'needs_improvement': 0.08
        },
        'rationalization_rate': {
            'best_in_class': 0.12,   # 12% reduction in app count per year
            'industry_average': 0.08,
            'needs_improvement': 0.03
        }
    }

    # Best practices catalog
    BEST_PRACTICES = {
        'portfolio_optimization': [
            {
                'practice': 'Regular portfolio reviews',
                'description': 'Conduct quarterly portfolio health assessments',
                'benefit': 'Early identification of technical debt and risks',
                'effort': 'Low',
                'impact': 'High'
            },
            {
                'practice': 'Application rationalization program',
                'description': 'Retire 8-12% of applications annually',
                'benefit': '15-25% cost reduction over 3 years',
                'effort': 'Medium',
                'impact': 'High'
            },
            {
                'practice': 'Standardized technology stack',
                'description': 'Limit to 3-5 core technology platforms',
                'benefit': 'Reduced complexity and support costs',
                'effort': 'High',
                'impact': 'High'
            }
        ],
        'cost_management': [
            {
                'practice': 'TCO tracking',
                'description': 'Track total cost of ownership for all applications',
                'benefit': 'Identify hidden costs and optimization opportunities',
                'effort': 'Medium',
                'impact': 'High'
            },
            {
                'practice': 'Chargeback model',
                'description': 'Implement cost allocation to business units',
                'benefit': 'Improved accountability and cost consciousness',
                'effort': 'Medium',
                'impact': 'Medium'
            },
            {
                'practice': 'Cloud optimization',
                'description': 'Right-size cloud resources and eliminate waste',
                'benefit': '20-40% cloud cost reduction',
                'effort': 'Low',
                'impact': 'High'
            }
        ],
        'risk_management': [
            {
                'practice': 'Risk-based prioritization',
                'description': 'Prioritize investments based on risk scoring',
                'benefit': 'Focus resources on highest-impact areas',
                'effort': 'Low',
                'impact': 'High'
            },
            {
                'practice': 'Continuous compliance monitoring',
                'description': 'Automated compliance checking and reporting',
                'benefit': 'Reduced audit findings and regulatory risk',
                'effort': 'Medium',
                'impact': 'High'
            },
            {
                'practice': 'Disaster recovery testing',
                'description': 'Annual DR tests for critical applications',
                'benefit': 'Reduced downtime and business continuity',
                'effort': 'Medium',
                'impact': 'High'
            }
        ],
        'modernization': [
            {
                'practice': 'API-first architecture',
                'description': 'Build integration layer with modern APIs',
                'benefit': 'Faster innovation and easier integration',
                'effort': 'High',
                'impact': 'High'
            },
            {
                'practice': 'Microservices adoption',
                'description': 'Decompose monoliths into microservices',
                'benefit': 'Improved scalability and maintainability',
                'effort': 'High',
                'impact': 'Medium'
            },
            {
                'practice': 'DevOps practices',
                'description': 'Implement CI/CD and automated testing',
                'benefit': 'Faster deployment and higher quality',
                'effort': 'Medium',
                'impact': 'High'
            }
        ]
    }

    def __init__(self, applications: List[Dict[str, Any]]):
        """
        Initialize with application portfolio data.

        Args:
            applications: List of application dictionaries with keys:
                - name: Application name
                - cost: Annual cost
                - tech_health: Technical health score (0-10)
                - business_value: Business value score (0-10)
        """
        self.applications = [app.copy() for app in applications]
        self.portfolio_size = len(self.applications)
        self.total_cost = sum(app.get('cost', 0) for app in self.applications)
        self.benchmark_results = {}

    def classify_portfolio_size(self) -> str:
        """Classify portfolio size category."""
        if self.portfolio_size < 75:
            return 'small'
        elif self.portfolio_size < 200:
            return 'medium'
        elif self.portfolio_size < 400:
            return 'large'
        else:
            return 'enterprise'

    def calculate_health_distribution(self) -> Dict[str, float]:
        """Calculate actual health distribution."""
        if self.portfolio_size == 0:
            return {'critical': 0, 'poor': 0, 'fair': 0, 'good': 0, 'excellent': 0}

        critical = sum(1 for app in self.applications if app.get('tech_health', 5) <= 3)
        poor = sum(1 for app in self.applications if 3 < app.get('tech_health', 5) <= 5)
        fair = sum(1 for app in self.applications if 5 < app.get('tech_health', 5) <= 7)
        good = sum(1 for app in self.applications if 7 < app.get('tech_health', 5) <= 9)
        excellent = sum(1 for app in self.applications if app.get('tech_health', 5) == 10)

        total = self.portfolio_size
        return {
            'critical': round(critical / total, 3),
            'poor': round(poor / total, 3),
            'fair': round(fair / total, 3),
            'good': round(good / total, 3),
            'excellent': round(excellent / total, 3)
        }

    def benchmark_health_distribution(self) -> Dict[str, Any]:
        """Benchmark health distribution against industry standards."""
        actual = self.calculate_health_distribution()
        benchmarks = self.INDUSTRY_BENCHMARKS['health_distribution']

        # Calculate distance from each benchmark
        distances = {}
        for benchmark_name, benchmark_dist in benchmarks.items():
            distance = sum(abs(actual[k] - benchmark_dist[k]) for k in actual.keys())
            distances[benchmark_name] = distance

        # Find closest benchmark
        closest = min(distances.items(), key=lambda x: x[1])

        # Calculate score (0-100, lower distance = higher score)
        score = max(0, 100 - (closest[1] * 200))

        return {
            'actual_distribution': actual,
            'benchmark_category': closest[0],
            'benchmark_distribution': benchmarks[closest[0]],
            'health_score': round(score, 1),
            'gaps': {k: round(actual[k] - benchmarks[closest[0]][k], 3) for k in actual.keys()},
            'recommendation': self._generate_health_recommendation(actual, benchmarks[closest[0]])
        }

    def _generate_health_recommendation(self, actual: Dict, benchmark: Dict) -> str:
        """Generate recommendation for health improvement."""
        critical_gap = actual['critical'] - benchmark['critical']
        poor_gap = actual['poor'] - benchmark['poor']

        if critical_gap > 0.05:
            return f"Urgent: {critical_gap*100:.1f}% more critical applications than benchmark - immediate action required"
        elif poor_gap > 0.05:
            return f"Priority: {poor_gap*100:.1f}% more poor-health applications than benchmark - modernization needed"
        elif actual['excellent'] < benchmark['excellent']:
            gap = (benchmark['excellent'] - actual['excellent']) * 100
            return f"Opportunity: {gap:.1f}% fewer excellent applications than benchmark - invest in quality"
        else:
            return "Good performance - maintain current health standards"

    def benchmark_cost_efficiency(self) -> Dict[str, Any]:
        """Benchmark cost efficiency metrics."""
        if self.portfolio_size == 0:
            return {
                'actual_metrics': {'avg_cost_per_app': 0, 'maintenance_ratio': 0, 'tech_debt_ratio': 0},
                'benchmark_category': 'industry_average',
                'benchmark_metrics': self.INDUSTRY_BENCHMARKS['cost_efficiency']['industry_average'],
                'efficiency_score': 0,
                'comparison_scores': {},
                'recommendation': 'No applications to analyze'
            }

        avg_cost_per_app = self.total_cost / self.portfolio_size

        # Calculate tech debt ratio (apps with health < 5)
        tech_debt_apps = sum(1 for app in self.applications if app.get('tech_health', 5) < 5)
        tech_debt_ratio = tech_debt_apps / self.portfolio_size

        # Maintenance ratio estimate (apps with health < 7)
        maintenance_apps = sum(1 for app in self.applications if app.get('tech_health', 5) < 7)
        maintenance_ratio = maintenance_apps / self.portfolio_size

        benchmarks = self.INDUSTRY_BENCHMARKS['cost_efficiency']

        # Score each metric against benchmarks
        scores = {}
        for benchmark_name, benchmark_metrics in benchmarks.items():
            # Cost per app score (lower is better)
            cost_diff = abs(avg_cost_per_app - benchmark_metrics['cost_per_user'])
            cost_score = max(0, 100 - (cost_diff / 1000))

            # Maintenance ratio score (lower is better)
            maint_diff = abs(maintenance_ratio - benchmark_metrics['maintenance_ratio'])
            maint_score = max(0, 100 - (maint_diff * 200))

            # Tech debt ratio score (lower is better)
            debt_diff = abs(tech_debt_ratio - benchmark_metrics['tech_debt_ratio'])
            debt_score = max(0, 100 - (debt_diff * 200))

            # Composite score
            composite = (cost_score * 0.4 + maint_score * 0.3 + debt_score * 0.3)
            scores[benchmark_name] = round(composite, 1)

        # Best match
        best_match = max(scores.items(), key=lambda x: x[1])

        return {
            'actual_metrics': {
                'avg_cost_per_app': round(avg_cost_per_app, 2),
                'maintenance_ratio': round(maintenance_ratio, 3),
                'tech_debt_ratio': round(tech_debt_ratio, 3)
            },
            'benchmark_category': best_match[0],
            'benchmark_metrics': benchmarks[best_match[0]],
            'efficiency_score': best_match[1],
            'comparison_scores': scores,
            'recommendation': self._generate_cost_recommendation(avg_cost_per_app, maintenance_ratio, tech_debt_ratio)
        }

    def _generate_cost_recommendation(self, cost_per_app: float, maint_ratio: float, debt_ratio: float) -> str:
        """Generate cost efficiency recommendation."""
        if cost_per_app > 120000:
            return f"Cost per app (${cost_per_app:,.0f}) exceeds enterprise average - rationalization recommended"
        elif maint_ratio > 0.30:
            return f"Maintenance ratio ({maint_ratio*100:.1f}%) is high - modernization needed"
        elif debt_ratio > 0.25:
            return f"Technical debt ({debt_ratio*100:.1f}%) is elevated - invest in quality improvement"
        else:
            return "Cost efficiency is within acceptable range - continue optimization efforts"

    def benchmark_portfolio_maturity(self) -> Dict[str, Any]:
        """Assess overall portfolio maturity against best practices."""
        # Calculate maturity scores across dimensions
        health_benchmark = self.benchmark_health_distribution()
        cost_benchmark = self.benchmark_cost_efficiency()

        # Additional maturity indicators
        if self.portfolio_size == 0:
            avg_health = 0
            avg_value = 0
            value_cost_ratio = 0
        else:
            avg_health = sum(app.get('tech_health', 5) for app in self.applications) / self.portfolio_size
            avg_value = sum(app.get('business_value', 5) for app in self.applications) / self.portfolio_size

            # Value-to-cost ratio
            median_cost = sorted(app.get('cost', 0) for app in self.applications)[self.portfolio_size // 2]
            high_value_apps = sum(1 for app in self.applications if app.get('business_value', 5) >= 7)
            high_cost_apps = sum(1 for app in self.applications if app.get('cost', 0) > median_cost)
            value_cost_ratio = high_value_apps / max(high_cost_apps, 1)

        # Maturity level determination
        health_score = health_benchmark['health_score']
        cost_score = cost_benchmark['efficiency_score']
        value_score = (avg_value / 10) * 100

        composite_maturity = (health_score * 0.4 + cost_score * 0.35 + value_score * 0.25)

        if composite_maturity >= 80:
            maturity_level = 'Optimized'
        elif composite_maturity >= 65:
            maturity_level = 'Managed'
        elif composite_maturity >= 50:
            maturity_level = 'Defined'
        elif composite_maturity >= 35:
            maturity_level = 'Repeatable'
        else:
            maturity_level = 'Initial'

        return {
            'maturity_level': maturity_level,
            'composite_score': round(composite_maturity, 1),
            'dimension_scores': {
                'health_management': health_score,
                'cost_efficiency': cost_score,
                'value_alignment': round(value_score, 1)
            },
            'metrics': {
                'avg_health': round(avg_health, 2),
                'avg_business_value': round(avg_value, 2),
                'value_cost_ratio': round(value_cost_ratio, 2)
            },
            'next_level_requirements': self._get_next_level_requirements(maturity_level),
            'recommendation': self._generate_maturity_recommendation(maturity_level, composite_maturity)
        }

    def _get_next_level_requirements(self, current_level: str) -> List[str]:
        """Get requirements to reach next maturity level."""
        requirements = {
            'Initial': [
                'Establish application inventory',
                'Implement basic health scoring',
                'Track annual costs'
            ],
            'Repeatable': [
                'Define rationalization process',
                'Implement quarterly reviews',
                'Establish cost tracking by category'
            ],
            'Defined': [
                'Adopt risk-based prioritization',
                'Implement modernization roadmap',
                'Track TCO for all applications'
            ],
            'Managed': [
                'Automate compliance monitoring',
                'Implement predictive analytics',
                'Optimize cloud costs continuously'
            ],
            'Optimized': [
                'Maintain excellence through innovation',
                'Benchmark regularly against peers',
                'Lead industry best practices'
            ]
        }

        return requirements.get(current_level, [])

    def _generate_maturity_recommendation(self, level: str, score: float) -> str:
        """Generate maturity improvement recommendation."""
        if level == 'Initial':
            return "Focus on establishing basic portfolio management practices"
        elif level == 'Repeatable':
            return "Standardize processes and implement regular portfolio reviews"
        elif level == 'Defined':
            return "Adopt advanced analytics and risk-based decision making"
        elif level == 'Managed':
            return "Optimize through automation and continuous improvement"
        else:
            return "Maintain leadership position through innovation"

    def get_best_practices(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get best practices recommendations."""
        if category and category in self.BEST_PRACTICES:
            return self.BEST_PRACTICES[category]

        # Return all practices with priority
        all_practices = []
        for cat, practices in self.BEST_PRACTICES.items():
            for practice in practices:
                practice_copy = practice.copy()
                practice_copy['category'] = cat
                all_practices.append(practice_copy)

        return all_practices

    def identify_peer_gaps(self) -> List[Dict[str, Any]]:
        """Identify gaps compared to peer benchmarks."""
        gaps = []

        health_bench = self.benchmark_health_distribution()
        cost_bench = self.benchmark_cost_efficiency()

        # Health gaps
        if health_bench['health_score'] < 70:
            gaps.append({
                'area': 'Technical Health',
                'severity': 'high' if health_bench['health_score'] < 50 else 'medium',
                'gap': f"Portfolio health {100 - health_bench['health_score']:.1f} points below benchmark",
                'recommendation': health_bench['recommendation'],
                'estimated_improvement': '15-25% cost reduction through modernization'
            })

        # Cost gaps
        if cost_bench['efficiency_score'] < 70:
            gaps.append({
                'area': 'Cost Efficiency',
                'severity': 'high' if cost_bench['efficiency_score'] < 50 else 'medium',
                'gap': f"Cost efficiency {100 - cost_bench['efficiency_score']:.1f} points below benchmark",
                'recommendation': cost_bench['recommendation'],
                'estimated_improvement': '10-20% cost optimization potential'
            })

        # Rationalization gap
        eliminate_candidates = sum(
            1 for app in self.applications
            if app.get('tech_health', 5) <= 3 and app.get('business_value', 5) <= 4
        )

        if eliminate_candidates > self.portfolio_size * 0.05:
            candidate_cost = sum(
                app.get('cost', 0) for app in self.applications
                if app.get('tech_health', 5) <= 3 and app.get('business_value', 5) <= 4
            )
            gaps.append({
                'area': 'Application Rationalization',
                'severity': 'medium',
                'gap': f"{eliminate_candidates} applications ({eliminate_candidates/self.portfolio_size*100:.1f}%) are retirement candidates",
                'recommendation': 'Implement rationalization program to retire low-value applications',
                'estimated_improvement': f'${candidate_cost:,.0f} annual savings potential'
            })

        return gaps

    def generate_benchmark_report(self) -> Dict[str, Any]:
        """Generate comprehensive benchmark report."""
        portfolio_category = self.classify_portfolio_size()
        health_benchmark = self.benchmark_health_distribution()
        cost_benchmark = self.benchmark_cost_efficiency()
        maturity_assessment = self.benchmark_portfolio_maturity()
        peer_gaps = self.identify_peer_gaps()
        best_practices = self.get_best_practices()

        return {
            'portfolio_profile': {
                'size_category': portfolio_category,
                'total_applications': self.portfolio_size,
                'total_annual_cost': self.total_cost,
                'avg_cost_per_app': round(self.total_cost / max(self.portfolio_size, 1), 2)
            },
            'health_benchmark': health_benchmark,
            'cost_benchmark': cost_benchmark,
            'maturity_assessment': maturity_assessment,
            'peer_gaps': peer_gaps,
            'best_practices': best_practices,
            'executive_summary': {
                'overall_score': round((health_benchmark['health_score'] + cost_benchmark['efficiency_score']) / 2, 1),
                'maturity_level': maturity_assessment['maturity_level'],
                'critical_gaps': len([g for g in peer_gaps if g['severity'] == 'high']),
                'improvement_potential': self._calculate_improvement_potential(peer_gaps)
            }
        }

    def _calculate_improvement_potential(self, gaps: List[Dict]) -> str:
        """Calculate total improvement potential."""
        total_savings = 0

        for gap in gaps:
            if 'estimated_improvement' in gap and '$' in gap['estimated_improvement']:
                # Extract dollar amount
                match = re.search(r'\$([0-9,]+)', gap['estimated_improvement'])
                if match:
                    total_savings += float(match.group(1).replace(',', ''))

        if total_savings > 0:
            return f"${total_savings:,.0f} annual cost reduction potential"
        else:
            return "15-30% overall portfolio efficiency improvement potential"

    def get_benchmark_summary(self) -> Dict[str, Any]:
        """Get a simplified benchmark summary for API responses."""
        maturity = self.benchmark_portfolio_maturity()
        health = self.benchmark_health_distribution()
        cost = self.benchmark_cost_efficiency()

        return {
            'portfolio_size': self.classify_portfolio_size(),
            'total_applications': self.portfolio_size,
            'maturity_level': maturity['maturity_level'],
            'maturity_score': maturity['composite_score'],
            'health_score': health['health_score'],
            'health_category': health['benchmark_category'],
            'cost_efficiency_score': cost['efficiency_score'],
            'cost_category': cost['benchmark_category'],
            'peer_gaps_count': len(self.identify_peer_gaps()),
            'recommendations': [
                health['recommendation'],
                cost['recommendation'],
                maturity['recommendation']
            ]
        }
