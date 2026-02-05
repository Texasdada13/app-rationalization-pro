"""
Rationalization Module for App Rationalization Pro

Core domain logic for application portfolio rationalization.
"""

from .scoring_engine import ScoringEngine, ScoringWeights
from .time_framework import TIMEFramework, TIMECategory, TIMEThresholds
from .recommendation_engine import RecommendationEngine, ActionType
from .cost_modeler import CostModeler, TCOBreakdown
from .compliance_engine import ComplianceEngine, ComplianceFramework

__all__ = [
    'ScoringEngine',
    'ScoringWeights',
    'TIMEFramework',
    'TIMECategory',
    'TIMEThresholds',
    'RecommendationEngine',
    'ActionType',
    'RationalizationEngine',
    'CostModeler',
    'TCOBreakdown',
    'ComplianceEngine',
    'ComplianceFramework'
]


class RationalizationEngine:
    """
    Unified engine that orchestrates scoring, TIME categorization, and recommendations.

    This is the main interface for processing application portfolios.
    """

    def __init__(self):
        """Initialize all sub-engines."""
        self.scoring = ScoringEngine()
        self.time = TIMEFramework()
        self.recommendations = RecommendationEngine()

    def process_portfolio(self, applications: list) -> dict:
        """
        Process a full application portfolio through all rationalization steps.

        Args:
            applications: List of application dictionaries with criteria

        Returns:
            Dictionary with processed applications and summary statistics
        """
        # Step 1: Calculate scores
        scored = self.scoring.batch_calculate_scores(applications)

        # Step 2: Apply TIME categorization
        categorized = self.time.batch_categorize(scored)

        # Step 3: Generate recommendations
        recommended = self.recommendations.batch_generate_recommendations(categorized)

        # Step 4: Build summary
        summary = {
            'total_applications': len(recommended),
            'time_distribution': self.time.get_category_summary(),
            'recommendation_distribution': self.recommendations.get_portfolio_summary(),
            'time_matrix': self.time.get_portfolio_matrix(recommended),
            'prioritized_actions': self.recommendations.prioritize_actions(recommended)
        }

        # Calculate portfolio-level metrics
        if recommended:
            scores = [app.get('composite_score', 0) for app in recommended]
            costs = [app.get('cost', 0) for app in recommended]
            summary['average_score'] = round(sum(scores) / len(scores), 2)
            summary['total_cost'] = sum(costs)
        else:
            summary['average_score'] = 0
            summary['total_cost'] = 0

        return {
            'applications': recommended,
            'summary': summary
        }

    def process_single_application(self, app: dict) -> dict:
        """
        Process a single application through all rationalization steps.

        Args:
            app: Application dictionary with criteria

        Returns:
            Processed application with scores, TIME category, and recommendation
        """
        result = self.process_portfolio([app])
        if result['applications']:
            return result['applications'][0]
        return app

    def reset(self):
        """Reset all counters for new analysis."""
        self.time.reset_counts()
        self.recommendations.reset_counts()
