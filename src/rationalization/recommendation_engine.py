"""
Recommendation Engine Module for App Rationalization Pro

Generates actionable recommendations for application rationalization.
Ported from application-rationalization-tool without pandas dependency.
"""

from typing import Dict, List, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Possible rationalization actions."""

    RETAIN = "Retain"
    INVEST = "Invest"
    MAINTAIN = "Maintain"
    TOLERATE = "Tolerate"
    MIGRATE = "Migrate"
    CONSOLIDATE = "Consolidate"
    RETIRE = "Retire"
    IMMEDIATE_ACTION = "Immediate Action Required"


class RecommendationEngine:
    """
    Generates rationalization recommendations based on application scores.

    Uses a decision matrix approach combining composite score, business criticality,
    technical health, and other factors.
    """

    # Score thresholds
    HIGH_SCORE = 70.0
    MEDIUM_SCORE = 50.0
    LOW_SCORE = 30.0

    # Individual criteria thresholds
    CRITICAL_BUSINESS_VALUE = 8.0
    POOR_TECH_HEALTH = 4.0
    CRITICAL_SECURITY = 8.0
    POOR_SECURITY = 4.0

    def __init__(self):
        """Initialize the recommendation engine."""
        self.recommendation_counts = {action.value: 0 for action in ActionType}

    def generate_recommendation(
        self,
        composite_score: float,
        business_value: float,
        tech_health: float,
        security: float,
        strategic_fit: float,
        redundancy: int,
        cost: float
    ) -> Tuple[str, str]:
        """
        Generate recommendation and rationale for a single application.

        Returns:
            Tuple of (action_recommendation, rationale_text)
        """
        # Critical flags
        is_critical = business_value >= self.CRITICAL_BUSINESS_VALUE
        poor_tech = tech_health <= self.POOR_TECH_HEALTH
        poor_security = security <= self.POOR_SECURITY
        critical_security = security >= self.CRITICAL_SECURITY
        is_redundant = redundancy == 1
        high_strategic = strategic_fit >= self.CRITICAL_BUSINESS_VALUE

        # Decision logic
        action, rationale = self._apply_decision_logic(
            composite_score=composite_score,
            is_critical=is_critical,
            poor_tech=poor_tech,
            poor_security=poor_security,
            critical_security=critical_security,
            is_redundant=is_redundant,
            high_strategic=high_strategic,
            business_value=business_value,
            tech_health=tech_health,
            security=security,
            strategic_fit=strategic_fit,
            cost=cost
        )

        # Track recommendation counts
        self.recommendation_counts[action] += 1

        return action, rationale

    def _apply_decision_logic(
        self,
        composite_score: float,
        is_critical: bool,
        poor_tech: bool,
        poor_security: bool,
        critical_security: bool,
        is_redundant: bool,
        high_strategic: bool,
        business_value: float,
        tech_health: float,
        security: float,
        strategic_fit: float,
        cost: float
    ) -> Tuple[str, str]:
        """Apply decision matrix logic to determine recommendation."""

        # IMMEDIATE ACTION: Security risk
        if poor_security and (is_critical or tech_health <= 3):
            return (
                ActionType.IMMEDIATE_ACTION.value,
                f"Critical security risk (score: {security}/10) requires immediate remediation. "
                f"{'High business value' if is_critical else 'Poor technical health'} makes this urgent."
            )

        # RETIRE: Low value, redundant, or obsolete
        if composite_score < self.LOW_SCORE and not is_critical:
            if is_redundant:
                return (
                    ActionType.RETIRE.value,
                    f"Low composite score ({composite_score}/100) with redundant functionality. "
                    f"Consolidation opportunity to reduce costs (${cost:,.0f}/year)."
                )
            elif poor_tech and business_value <= 5:
                return (
                    ActionType.RETIRE.value,
                    f"Low business value ({business_value}/10) and poor technical health ({tech_health}/10). "
                    f"Decommissioning recommended to reduce technical debt."
                )

        # CONSOLIDATE: Redundant but with some value
        if is_redundant and composite_score >= self.LOW_SCORE:
            return (
                ActionType.CONSOLIDATE.value,
                f"Redundant functionality identified. Consolidate with primary system to "
                f"eliminate duplication and save ${cost:,.0f}/year while preserving key features."
            )

        # INVEST: High value, strategic, good health
        if composite_score >= self.HIGH_SCORE and high_strategic:
            if tech_health >= 7:
                return (
                    ActionType.INVEST.value,
                    f"Excellent composite score ({composite_score}/100) with high strategic alignment ({strategic_fit}/10). "
                    f"Continue investment to maximize business value ({business_value}/10)."
                )
            else:
                return (
                    ActionType.INVEST.value,
                    f"High strategic value ({strategic_fit}/10) and business value ({business_value}/10). "
                    f"Invest in technical improvements (current health: {tech_health}/10)."
                )

        # MIGRATE: Good value but poor technical health
        if is_critical and poor_tech:
            return (
                ActionType.MIGRATE.value,
                f"Critical business value ({business_value}/10) but poor technical health ({tech_health}/10). "
                f"Migration to modern platform recommended."
            )

        # RETAIN: High score overall
        if composite_score >= self.HIGH_SCORE:
            return (
                ActionType.RETAIN.value,
                f"Strong composite score ({composite_score}/100) with balanced metrics. "
                f"Continue current operations with standard maintenance."
            )

        # MAINTAIN: Medium-high score with good tech health
        if composite_score >= self.MEDIUM_SCORE and tech_health >= 6:
            return (
                ActionType.MAINTAIN.value,
                f"Good composite score ({composite_score}/100) and technical health ({tech_health}/10). "
                f"Maintain current state with routine updates."
            )

        # TOLERATE: Medium score with issues but necessary
        if self.MEDIUM_SCORE <= composite_score < self.HIGH_SCORE and is_critical:
            return (
                ActionType.TOLERATE.value,
                f"Critical business function ({business_value}/10) with moderate composite score ({composite_score}/100). "
                f"Accept current limitations while planning improvements."
            )

        # TOLERATE: Default for medium scores
        if composite_score >= self.MEDIUM_SCORE:
            return (
                ActionType.TOLERATE.value,
                f"Moderate composite score ({composite_score}/100). Monitor for changes."
            )

        # MIGRATE: Low-medium score with strategic value
        if high_strategic and composite_score < self.MEDIUM_SCORE:
            return (
                ActionType.MIGRATE.value,
                f"High strategic fit ({strategic_fit}/10) but low composite score ({composite_score}/100). "
                f"Consider migration or modernization."
            )

        # Default: TOLERATE for edge cases
        return (
            ActionType.TOLERATE.value,
            f"Composite score of {composite_score}/100 warrants monitoring."
        )

    def batch_generate_recommendations(
        self,
        applications: List[Dict]
    ) -> List[Dict]:
        """
        Generate recommendations for multiple applications.

        Args:
            applications: List of application dictionaries with scores

        Returns:
            List of applications with recommendations added
        """
        results = []

        for app in applications:
            try:
                action, rationale = self.generate_recommendation(
                    composite_score=float(app.get('composite_score', app.get('Composite Score', 0))),
                    business_value=float(app.get('business_value', app.get('Business Value', 0))),
                    tech_health=float(app.get('tech_health', app.get('Tech Health', 0))),
                    security=float(app.get('security', app.get('Security', 0))),
                    strategic_fit=float(app.get('strategic_fit', app.get('Strategic Fit', 0))),
                    redundancy=int(app.get('redundancy', app.get('Redundancy', 0))),
                    cost=float(app.get('cost', app.get('Cost', 0)))
                )

                app_result = app.copy()
                app_result['recommendation'] = action
                app_result['recommendation_rationale'] = rationale

                results.append(app_result)

            except (ValueError, KeyError) as e:
                logger.error(f"Error generating recommendation for {app.get('name', 'Unknown')}: {e}")
                app_result = app.copy()
                app_result['recommendation'] = ActionType.TOLERATE.value
                app_result['recommendation_rationale'] = "Unable to generate recommendation due to data issues."
                results.append(app_result)

        return results

    def get_portfolio_summary(self) -> Dict:
        """Get summary statistics of recommendations generated."""
        total = sum(self.recommendation_counts.values())

        if total == 0:
            return {"total": 0, "distribution": {}}

        summary = {
            "total": total,
            "distribution": {},
            "percentages": {}
        }

        for action, count in self.recommendation_counts.items():
            summary["distribution"][action] = count
            summary["percentages"][action] = round((count / total) * 100, 1)

        return summary

    def prioritize_actions(
        self,
        applications: List[Dict],
        top_n: int = 10
    ) -> Dict[str, List[Dict]]:
        """
        Prioritize applications by action type for focused execution.

        Args:
            applications: List of applications with recommendations
            top_n: Number of top priority items per category

        Returns:
            Dictionary of action types with prioritized applications
        """
        prioritized = {}

        # Group by action
        for action in ActionType:
            action_apps = [
                app for app in applications
                if app.get('recommendation', app.get('Action Recommendation')) == action.value
            ]

            # Sort by composite score
            if action in [ActionType.RETIRE, ActionType.IMMEDIATE_ACTION]:
                # Lowest scores first for retirement/action
                sorted_apps = sorted(
                    action_apps,
                    key=lambda x: (
                        x.get('composite_score', x.get('Composite Score', 0)),
                        -x.get('business_value', x.get('Business Value', 0))
                    )
                )
            else:
                # Highest scores first for investment/retention
                sorted_apps = sorted(
                    action_apps,
                    key=lambda x: (
                        -x.get('composite_score', x.get('Composite Score', 100)),
                        -x.get('business_value', x.get('Business Value', 0))
                    )
                )

            prioritized[action.value] = sorted_apps[:top_n]

        return prioritized

    def reset_counts(self):
        """Reset recommendation counts for new analysis."""
        self.recommendation_counts = {action.value: 0 for action in ActionType}
