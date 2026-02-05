"""
Government Scoring Engine Module

Specialized scoring engine for government/public sector application portfolios.
Uses government-specific dimensions like Citizen Impact, Mission Criticality,
and Interoperability alongside traditional enterprise metrics.

Designed for:
- County governments (Dallas County, Marion County, etc.)
- State agencies (Texas DIR, Indiana IOT)
- Municipal governments
- Special districts (school districts, utility districts)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class GovernmentSector(Enum):
    """Government sector categories."""
    PUBLIC_SAFETY = "public_safety"
    HEALTH_HUMAN_SERVICES = "health_human_services"
    FINANCE_ADMIN = "finance_admin"
    TRANSPORTATION = "transportation"
    EDUCATION = "education"
    UTILITIES = "utilities"
    COURTS_LEGAL = "courts_legal"
    GENERAL_GOVERNMENT = "general_government"


class DataSensitivity(Enum):
    """Data sensitivity classifications."""
    PUBLIC = "public"
    SENSITIVE = "sensitive"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


@dataclass
class GovernmentScoringWeights:
    """
    Configurable weights for government scoring dimensions.
    Weights can be adjusted based on agency priorities.
    """
    # Core dimensions
    mission_criticality: float = 0.25
    citizen_impact: float = 0.20
    tech_health: float = 0.15
    security: float = 0.15
    interoperability: float = 0.10
    cost_efficiency: float = 0.10
    compliance: float = 0.05

    def validate(self):
        """Ensure weights sum to 1.0"""
        total = (
            self.mission_criticality +
            self.citizen_impact +
            self.tech_health +
            self.security +
            self.interoperability +
            self.cost_efficiency +
            self.compliance
        )
        return abs(total - 1.0) < 0.001


# Sector-specific weight presets
SECTOR_WEIGHTS = {
    GovernmentSector.PUBLIC_SAFETY: GovernmentScoringWeights(
        mission_criticality=0.30,
        citizen_impact=0.15,
        tech_health=0.10,
        security=0.25,
        interoperability=0.10,
        cost_efficiency=0.05,
        compliance=0.05
    ),
    GovernmentSector.HEALTH_HUMAN_SERVICES: GovernmentScoringWeights(
        mission_criticality=0.20,
        citizen_impact=0.25,
        tech_health=0.15,
        security=0.20,
        interoperability=0.10,
        cost_efficiency=0.05,
        compliance=0.05
    ),
    GovernmentSector.FINANCE_ADMIN: GovernmentScoringWeights(
        mission_criticality=0.20,
        citizen_impact=0.10,
        tech_health=0.15,
        security=0.20,
        interoperability=0.10,
        cost_efficiency=0.20,
        compliance=0.05
    ),
    GovernmentSector.COURTS_LEGAL: GovernmentScoringWeights(
        mission_criticality=0.25,
        citizen_impact=0.20,
        tech_health=0.10,
        security=0.20,
        interoperability=0.15,
        cost_efficiency=0.05,
        compliance=0.05
    ),
}


class GovernmentScoringEngine:
    """
    Scoring engine optimized for government/public sector applications.

    Key Differences from Enterprise Scoring:
    1. Mission Criticality replaces Strategic Fit
    2. Citizen Impact replaces pure Business Value
    3. Interoperability score for cross-agency data sharing
    4. Compliance requirements are weighted
    5. Security has higher baseline importance
    """

    def __init__(self, weights: Optional[GovernmentScoringWeights] = None):
        self.weights = weights or GovernmentScoringWeights()

    def set_sector_weights(self, sector: GovernmentSector):
        """Apply sector-specific weights."""
        if sector in SECTOR_WEIGHTS:
            self.weights = SECTOR_WEIGHTS[sector]
        else:
            self.weights = GovernmentScoringWeights()

    def calculate_government_score(self, app: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive government score for an application.

        Args:
            app: Application dict with government-specific fields

        Returns:
            Scoring results with breakdown
        """
        # Extract scores (normalize to 0-10 scale)
        mission_criticality = self._normalize_score(app.get('mission_criticality', 5))
        citizen_impact = self._normalize_score(app.get('citizen_impact', 5))
        tech_health = self._normalize_score(app.get('tech_health', 5))
        security = self._normalize_score(app.get('security', 5))
        interoperability = self._normalize_score(app.get('interoperability_score', 5))

        # Cost efficiency (derived from cost relative to usage)
        cost_efficiency = self._calculate_cost_efficiency(app)

        # Compliance score (based on requirements and current status)
        compliance_score = self._calculate_compliance_score(app)

        # Calculate weighted composite score
        composite_score = (
            mission_criticality * self.weights.mission_criticality +
            citizen_impact * self.weights.citizen_impact +
            tech_health * self.weights.tech_health +
            security * self.weights.security +
            interoperability * self.weights.interoperability +
            cost_efficiency * self.weights.cost_efficiency +
            compliance_score * self.weights.compliance
        ) * 10  # Scale to 0-100

        # Risk factors specific to government
        risk_factors = self._assess_government_risk_factors(app)

        # Apply risk penalty
        risk_penalty = sum(rf['penalty'] for rf in risk_factors) / 100
        adjusted_score = composite_score * (1 - risk_penalty)

        # Determine government-specific TIME category
        time_category, time_rationale = self._determine_gov_time_category(
            app, adjusted_score, mission_criticality, tech_health, citizen_impact
        )

        return {
            'gov_composite_score': round(adjusted_score, 2),
            'raw_composite_score': round(composite_score, 2),
            'dimension_scores': {
                'mission_criticality': round(mission_criticality * 10, 2),
                'citizen_impact': round(citizen_impact * 10, 2),
                'tech_health': round(tech_health * 10, 2),
                'security': round(security * 10, 2),
                'interoperability': round(interoperability * 10, 2),
                'cost_efficiency': round(cost_efficiency * 10, 2),
                'compliance': round(compliance_score * 10, 2)
            },
            'risk_factors': risk_factors,
            'risk_penalty_pct': round(risk_penalty * 100, 1),
            'time_category': time_category,
            'time_rationale': time_rationale,
            'weights_used': {
                'mission_criticality': self.weights.mission_criticality,
                'citizen_impact': self.weights.citizen_impact,
                'tech_health': self.weights.tech_health,
                'security': self.weights.security,
                'interoperability': self.weights.interoperability,
                'cost_efficiency': self.weights.cost_efficiency,
                'compliance': self.weights.compliance
            }
        }

    def _normalize_score(self, score: Any) -> float:
        """Normalize score to 0-1 range."""
        if score is None:
            return 0.5
        try:
            s = float(score)
            return max(0, min(1, s / 10))
        except (ValueError, TypeError):
            return 0.5

    def _calculate_cost_efficiency(self, app: Dict[str, Any]) -> float:
        """
        Calculate cost efficiency score.
        Government apps: cost per user/citizen served.
        """
        cost = app.get('cost', 0) or 0
        usage = app.get('usage', 0) or 0
        citizen_impact = app.get('citizen_impact', 5) or 5

        if cost == 0:
            return 0.8  # Free is efficient

        # Cost per impact unit
        if usage > 0:
            cost_per_user = cost / usage
            # Benchmark: $1000/user is neutral (0.5), lower is better
            efficiency = 1 - min(1, cost_per_user / 2000)
        else:
            # No usage data: base on cost relative to citizen impact
            efficiency = max(0.3, citizen_impact / 10 - (cost / 100000) * 0.1)

        return max(0, min(1, efficiency))

    def _calculate_compliance_score(self, app: Dict[str, Any]) -> float:
        """
        Calculate compliance readiness score.
        """
        requirements = app.get('compliance_requirements', []) or []
        security_score = (app.get('security', 5) or 5) / 10

        # If no requirements, base on security
        if not requirements:
            return security_score

        # More requirements = more compliance burden
        # But high security apps are likely to meet them
        requirement_burden = len(requirements) * 0.1
        base_compliance = security_score * 0.8

        return max(0.3, min(1, base_compliance - requirement_burden + 0.2))

    def _assess_government_risk_factors(self, app: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Assess government-specific risk factors.
        """
        risk_factors = []

        # Grant funding expiration risk
        if app.get('grant_funded'):
            grant_exp = app.get('grant_expiration')
            if grant_exp:
                risk_factors.append({
                    'factor': 'Grant-funded application',
                    'description': f'Funding tied to grant expiration',
                    'penalty': 5,
                    'category': 'financial'
                })

        # Data sensitivity without adequate security
        sensitivity = app.get('data_sensitivity', 'public')
        security = app.get('security', 5) or 5
        sensitivity_levels = {'public': 0, 'sensitive': 1, 'confidential': 2, 'restricted': 3}
        sens_level = sensitivity_levels.get(sensitivity, 0)

        if sens_level >= 2 and security < 7:
            risk_factors.append({
                'factor': 'High-sensitivity data with insufficient security',
                'description': f'{sensitivity} data requires security score >= 7',
                'penalty': 10,
                'category': 'security'
            })

        # System of record without high availability
        if app.get('system_of_record') and (app.get('tech_health', 5) or 5) < 6:
            risk_factors.append({
                'factor': 'System of Record with aging technology',
                'description': 'Authoritative systems require robust infrastructure',
                'penalty': 8,
                'category': 'operational'
            })

        # Public-facing with low security
        if app.get('public_facing') and security < 6:
            risk_factors.append({
                'factor': 'Public-facing application with low security',
                'description': 'Citizen-accessible systems need strong security',
                'penalty': 12,
                'category': 'security'
            })

        # Mission-critical with poor health
        mission_crit = app.get('mission_criticality', 5) or 5
        tech_health = app.get('tech_health', 5) or 5
        if mission_crit >= 8 and tech_health < 5:
            risk_factors.append({
                'factor': 'Mission-critical system at technical risk',
                'description': 'High criticality requires stable technology',
                'penalty': 15,
                'category': 'operational'
            })

        # Low interoperability for shared service
        if app.get('shared_service') and (app.get('interoperability_score', 5) or 5) < 5:
            risk_factors.append({
                'factor': 'Shared service with poor interoperability',
                'description': 'Multi-agency systems need data sharing capability',
                'penalty': 7,
                'category': 'integration'
            })

        return risk_factors

    def _determine_gov_time_category(
        self,
        app: Dict[str, Any],
        composite_score: float,
        mission_crit: float,
        tech_health: float,
        citizen_impact: float
    ) -> tuple:
        """
        Determine TIME category with government-specific considerations.

        Government considerations:
        - Mission-critical apps get more investment consideration
        - Citizen-facing apps need careful migration planning
        - Compliance requirements affect timing
        """
        mission_crit_10 = mission_crit * 10
        tech_health_10 = tech_health * 10
        citizen_impact_10 = citizen_impact * 10

        # INVEST: High mission criticality + good health + citizen impact
        if composite_score >= 70 and mission_crit_10 >= 7:
            if tech_health_10 >= 6:
                return ('Invest', f'High mission criticality ({mission_crit_10:.0f}) with solid technology. '
                        f'Strategic investment will enhance citizen services.')

        # TOLERATE: Mission-critical but needs work, or decent but not strategic
        if mission_crit_10 >= 6 and tech_health_10 >= 4:
            if composite_score >= 50:
                return ('Tolerate', f'Meets operational needs (score: {composite_score:.0f}). '
                        f'Maintain current state while planning future improvements.')

        # MIGRATE: Important for citizens but technology is outdated
        if citizen_impact_10 >= 6 and tech_health_10 < 5:
            return ('Migrate', f'Critical for citizens (impact: {citizen_impact_10:.0f}) but '
                    f'technology health ({tech_health_10:.0f}) requires modernization.')

        if mission_crit_10 >= 5 and tech_health_10 < 4:
            return ('Migrate', f'Mission-relevant but aging technology ({tech_health_10:.0f}). '
                    f'Plan migration to modern platform.')

        # ELIMINATE: Low value across the board
        if composite_score < 40 and mission_crit_10 < 4 and citizen_impact_10 < 4:
            return ('Eliminate', f'Low mission criticality ({mission_crit_10:.0f}) and citizen impact '
                    f'({citizen_impact_10:.0f}). Consider retirement to reduce portfolio complexity.')

        # Default to Tolerate for edge cases
        return ('Tolerate', f'Application requires further evaluation. Score: {composite_score:.0f}.')

    def batch_score(self, applications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Score multiple applications and provide portfolio summary.
        """
        results = []
        for app in applications:
            score_result = self.calculate_government_score(app)
            score_result['app_name'] = app.get('name', 'Unknown')
            score_result['app_id'] = app.get('id')
            results.append(score_result)

        # Portfolio summary
        scores = [r['gov_composite_score'] for r in results]
        avg_score = sum(scores) / len(scores) if scores else 0

        time_dist = {'Invest': 0, 'Tolerate': 0, 'Migrate': 0, 'Eliminate': 0}
        for r in results:
            cat = r.get('time_category', 'Tolerate')
            if cat in time_dist:
                time_dist[cat] += 1

        # Risk summary
        all_risks = []
        for r in results:
            all_risks.extend(r.get('risk_factors', []))

        risk_by_category = {}
        for risk in all_risks:
            cat = risk.get('category', 'other')
            risk_by_category[cat] = risk_by_category.get(cat, 0) + 1

        return {
            'application_scores': results,
            'portfolio_summary': {
                'total_applications': len(results),
                'average_score': round(avg_score, 2),
                'time_distribution': time_dist,
                'high_risk_apps': len([r for r in results if r['gov_composite_score'] < 40]),
                'investment_candidates': len([r for r in results if r['time_category'] == 'Invest']),
                'risk_by_category': risk_by_category
            }
        }

    def get_modernization_priorities(
        self,
        applications: List[Dict[str, Any]],
        budget_constraint: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate prioritized modernization recommendations.
        Considers citizen impact and mission criticality.
        """
        priorities = []

        for app in applications:
            score_result = self.calculate_government_score(app)

            # Only consider apps needing modernization
            if score_result['time_category'] not in ['Migrate', 'Eliminate']:
                continue

            mission_crit = app.get('mission_criticality', 5) or 5
            citizen_impact = app.get('citizen_impact', 5) or 5
            tech_health = app.get('tech_health', 5) or 5
            cost = app.get('cost', 0) or 0

            # Priority score: high impact + low health = urgent
            urgency = (mission_crit + citizen_impact) / 2 * (10 - tech_health)

            priorities.append({
                'app_name': app.get('name'),
                'app_id': app.get('id'),
                'current_score': score_result['gov_composite_score'],
                'time_category': score_result['time_category'],
                'urgency_score': round(urgency, 2),
                'mission_criticality': mission_crit,
                'citizen_impact': citizen_impact,
                'tech_health': tech_health,
                'estimated_cost': cost,
                'risk_factors': score_result['risk_factors'],
                'rationale': score_result['time_rationale']
            })

        # Sort by urgency
        priorities.sort(key=lambda x: x['urgency_score'], reverse=True)

        # Apply budget constraint if provided
        if budget_constraint:
            cumulative_cost = 0
            filtered = []
            for p in priorities:
                if cumulative_cost + p['estimated_cost'] <= budget_constraint:
                    filtered.append(p)
                    cumulative_cost += p['estimated_cost']
            return filtered

        return priorities
