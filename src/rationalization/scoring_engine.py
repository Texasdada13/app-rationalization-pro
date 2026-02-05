"""
Scoring Engine Module for App Rationalization Pro

Calculates composite scores for applications based on multiple weighted criteria.
Ported from application-rationalization-tool without pandas dependency.
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScoringWeights:
    """Configuration for scoring weights across different criteria."""

    business_value: float = 0.25
    tech_health: float = 0.20
    cost: float = 0.15
    usage: float = 0.15
    security: float = 0.10
    strategic_fit: float = 0.10
    redundancy: float = 0.05

    def validate(self) -> bool:
        """Validate that weights sum to 1.0."""
        total = (
            self.business_value +
            self.tech_health +
            self.cost +
            self.usage +
            self.security +
            self.strategic_fit +
            self.redundancy
        )
        return abs(total - 1.0) < 0.01


class ScoringEngine:
    """
    Main scoring engine for application rationalization.

    This engine calculates composite scores based on multiple weighted criteria
    and normalizes them to a 0-100 scale for easy interpretation.
    """

    def __init__(self, weights: Optional[ScoringWeights] = None):
        """
        Initialize the scoring engine with optional custom weights.

        Args:
            weights: Custom scoring weights. Uses defaults if not provided.
        """
        self.weights = weights or ScoringWeights()
        if not self.weights.validate():
            logger.warning("Scoring weights do not sum to 1.0. Results may be skewed.")

    def normalize_cost(self, cost: float, max_cost: float = 300000) -> float:
        """
        Normalize cost to 0-10 scale (lower cost = higher score).

        Args:
            cost: Annual cost in dollars
            max_cost: Maximum expected cost for normalization

        Returns:
            Normalized score from 0-10
        """
        if cost < 0:
            return 0.0

        # Invert the cost so lower cost gets higher score
        normalized = 10 * (1 - min(cost / max_cost, 1.0))
        return round(normalized, 2)

    def normalize_usage(self, usage: float, max_usage: float = 1000) -> float:
        """
        Normalize usage metrics to 0-10 scale.

        Args:
            usage: Usage count (e.g., daily active users)
            max_usage: Maximum expected usage for normalization

        Returns:
            Normalized score from 0-10
        """
        if usage < 0:
            return 0.0

        normalized = 10 * min(usage / max_usage, 1.0)
        return round(normalized, 2)

    def calculate_composite_score(
        self,
        business_value: float,
        tech_health: float,
        cost: float,
        usage: float,
        security: float,
        strategic_fit: float,
        redundancy: float,
        normalize_inputs: bool = True
    ) -> float:
        """
        Calculate composite score based on all criteria.

        Args:
            business_value: Business value score (0-10)
            tech_health: Technical health score (0-10)
            cost: Annual cost in dollars
            usage: Usage metric (e.g., daily active users)
            security: Security score (0-10)
            strategic_fit: Strategic fit score (0-10)
            redundancy: Redundancy indicator (0=unique, 1=redundant)
            normalize_inputs: Whether to normalize cost and usage

        Returns:
            Composite score from 0-100
        """
        # Normalize cost and usage if requested
        if normalize_inputs:
            cost_score = self.normalize_cost(cost)
            usage_score = self.normalize_usage(usage)
        else:
            cost_score = cost
            usage_score = usage

        # Convert redundancy to a score (0 = good, 1 = bad)
        redundancy_score = 10 * (1 - redundancy)

        # Calculate weighted composite score
        composite = (
            business_value * self.weights.business_value +
            tech_health * self.weights.tech_health +
            cost_score * self.weights.cost +
            usage_score * self.weights.usage +
            security * self.weights.security +
            strategic_fit * self.weights.strategic_fit +
            redundancy_score * self.weights.redundancy
        )

        # Scale to 0-100
        score = composite * 10
        return round(score, 2)

    def calculate_retention_score(
        self,
        composite_score: float,
        business_value: float,
        tech_health: float,
        security: float
    ) -> float:
        """
        Calculate a retention score that emphasizes keeping the application.

        Args:
            composite_score: Overall composite score
            business_value: Business value score
            tech_health: Technical health score
            security: Security score

        Returns:
            Retention score from 0-100
        """
        # Weight composite score 50%, critical factors 50%
        critical_avg = (business_value + tech_health + security) / 3
        retention = (composite_score * 0.5) + (critical_avg * 10 * 0.5)

        return round(retention, 2)

    def batch_calculate_scores(
        self,
        applications: List[Dict]
    ) -> List[Dict]:
        """
        Calculate scores for multiple applications.

        Args:
            applications: List of application dictionaries with criteria

        Returns:
            List of applications with calculated scores
        """
        results = []

        for app in applications:
            try:
                composite = self.calculate_composite_score(
                    business_value=float(app.get('business_value', app.get('Business Value', 0))),
                    tech_health=float(app.get('tech_health', app.get('Tech Health', 0))),
                    cost=float(app.get('cost', app.get('Cost', 0))),
                    usage=float(app.get('usage', app.get('Usage', 0))),
                    security=float(app.get('security', app.get('Security', 0))),
                    strategic_fit=float(app.get('strategic_fit', app.get('Strategic Fit', 0))),
                    redundancy=float(app.get('redundancy', app.get('Redundancy', 0)))
                )

                app_result = app.copy()
                app_result['composite_score'] = composite

                # Calculate retention score
                retention = self.calculate_retention_score(
                    composite_score=composite,
                    business_value=float(app.get('business_value', app.get('Business Value', 0))),
                    tech_health=float(app.get('tech_health', app.get('Tech Health', 0))),
                    security=float(app.get('security', app.get('Security', 0)))
                )
                app_result['retention_score'] = retention

                results.append(app_result)

            except (ValueError, KeyError) as e:
                logger.error(f"Error calculating score for {app.get('name', app.get('Application Name', 'Unknown'))}: {e}")
                app_result = app.copy()
                app_result['composite_score'] = 0.0
                app_result['retention_score'] = 0.0
                results.append(app_result)

        return results

    def get_score_breakdown(
        self,
        business_value: float,
        tech_health: float,
        cost: float,
        usage: float,
        security: float,
        strategic_fit: float,
        redundancy: float
    ) -> Dict[str, float]:
        """
        Get detailed breakdown of score contributions.

        Args:
            All individual criteria scores

        Returns:
            Dictionary with breakdown of each criterion's contribution
        """
        cost_score = self.normalize_cost(cost)
        usage_score = self.normalize_usage(usage)
        redundancy_score = 10 * (1 - redundancy)

        breakdown = {
            'business_value_contribution': business_value * self.weights.business_value * 10,
            'tech_health_contribution': tech_health * self.weights.tech_health * 10,
            'cost_contribution': cost_score * self.weights.cost * 10,
            'usage_contribution': usage_score * self.weights.usage * 10,
            'security_contribution': security * self.weights.security * 10,
            'strategic_fit_contribution': strategic_fit * self.weights.strategic_fit * 10,
            'redundancy_contribution': redundancy_score * self.weights.redundancy * 10
        }

        breakdown['total'] = sum(breakdown.values())

        return {k: round(v, 2) for k, v in breakdown.items()}
