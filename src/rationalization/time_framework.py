"""
TIME Framework Module for App Rationalization Pro

Implements the TIME (Tolerate, Invest, Migrate, Eliminate) framework for application rationalization.
Ported from application-rationalization-tool without pandas dependency.

TIME Categories:
    - INVEST: High value, good technical quality - invest for growth
    - TOLERATE: High value, poor technical quality - maintain but plan improvements
    - MIGRATE: Low value, poor technical quality - migrate or eliminate
    - ELIMINATE: Low value, any quality - retire or decommission
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TIMECategory(Enum):
    """TIME framework categories for application rationalization."""

    INVEST = "Invest"
    TOLERATE = "Tolerate"
    MIGRATE = "Migrate"
    ELIMINATE = "Eliminate"


@dataclass
class TIMEThresholds:
    """Configurable thresholds for TIME framework categorization."""

    business_value_threshold: float = 6.0
    technical_quality_threshold: float = 6.0
    composite_score_high: float = 65.0
    composite_score_low: float = 40.0
    critical_business_value: float = 8.0
    poor_tech_health: float = 4.0
    poor_security: float = 5.0

    def validate(self) -> bool:
        """Validate threshold values are within acceptable ranges."""
        if not (0 <= self.business_value_threshold <= 10):
            return False
        if not (0 <= self.technical_quality_threshold <= 10):
            return False
        if not (0 <= self.composite_score_high <= 100):
            return False
        if not (0 <= self.composite_score_low <= 100):
            return False
        if self.composite_score_low >= self.composite_score_high:
            return False
        return True


class TIMEFramework:
    """
    TIME Framework implementation for application portfolio rationalization.

    Uses a quadrant model of business value vs. technical quality.
    """

    def __init__(self, thresholds: Optional[TIMEThresholds] = None):
        """Initialize the TIME framework with optional custom thresholds."""
        self.thresholds = thresholds or TIMEThresholds()

        if not self.thresholds.validate():
            raise ValueError("Invalid TIME framework thresholds")

        # Track categorization statistics
        self.category_counts = {cat.value: 0 for cat in TIMECategory}

    def calculate_business_value_score(
        self,
        business_value: float,
        usage: float,
        strategic_fit: float,
        max_usage: float = 1000
    ) -> float:
        """
        Calculate a composite business value score.

        Formula: BV Score = (business_value × 0.5) + (usage_normalized × 0.2) + (strategic_fit × 0.3)
        """
        # Normalize usage to 0-10 scale
        usage_normalized = min(usage / max_usage * 10, 10)

        # Calculate weighted composite
        bv_score = (
            business_value * 0.5 +
            usage_normalized * 0.2 +
            strategic_fit * 0.3
        )

        return round(bv_score, 2)

    def calculate_technical_quality_score(
        self,
        tech_health: float,
        security: float,
        strategic_fit: float,
        cost: float,
        max_cost: float = 300000
    ) -> float:
        """
        Calculate a composite technical quality score.

        Formula: TQ Score = (tech_health × 0.4) + (security × 0.3) +
                          (strategic_fit × 0.2) + (cost_efficiency × 0.1)
        """
        # Calculate cost efficiency (lower cost = higher score)
        cost_normalized = min(cost / max_cost, 1.0)
        cost_efficiency = 10 * (1 - cost_normalized)

        # Calculate weighted composite
        tq_score = (
            tech_health * 0.4 +
            security * 0.3 +
            strategic_fit * 0.2 +
            cost_efficiency * 0.1
        )

        return round(tq_score, 2)

    def categorize_application(
        self,
        business_value: float,
        tech_health: float,
        security: float,
        strategic_fit: float,
        usage: float,
        cost: float,
        composite_score: float,
        redundancy: int = 0
    ) -> Tuple[str, str]:
        """
        Categorize an application using the TIME framework.

        Returns:
            Tuple of (TIME_category, rationale_text)
        """
        # Calculate composite scores for the two TIME dimensions
        bv_score = self.calculate_business_value_score(
            business_value, usage, strategic_fit
        )
        tq_score = self.calculate_technical_quality_score(
            tech_health, security, strategic_fit, cost
        )

        # Determine high/low classifications
        high_business_value = bv_score >= self.thresholds.business_value_threshold
        high_technical_quality = tq_score >= self.thresholds.technical_quality_threshold

        # Special case flags
        critical_business = business_value >= self.thresholds.critical_business_value
        poor_tech = tech_health <= self.thresholds.poor_tech_health
        poor_security_flag = security <= self.thresholds.poor_security
        is_redundant = redundancy == 1
        high_composite = composite_score >= self.thresholds.composite_score_high
        low_composite = composite_score <= self.thresholds.composite_score_low

        # Apply TIME framework logic with detailed rationale
        category, rationale = self._apply_time_logic(
            bv_score=bv_score,
            tq_score=tq_score,
            high_business_value=high_business_value,
            high_technical_quality=high_technical_quality,
            critical_business=critical_business,
            poor_tech=poor_tech,
            poor_security_flag=poor_security_flag,
            is_redundant=is_redundant,
            high_composite=high_composite,
            low_composite=low_composite,
            composite_score=composite_score,
            business_value=business_value,
            tech_health=tech_health,
            security=security
        )

        # Track statistics
        self.category_counts[category] += 1

        return category, rationale

    def _apply_time_logic(
        self,
        bv_score: float,
        tq_score: float,
        high_business_value: bool,
        high_technical_quality: bool,
        critical_business: bool,
        poor_tech: bool,
        poor_security_flag: bool,
        is_redundant: bool,
        high_composite: bool,
        low_composite: bool,
        composite_score: float,
        business_value: float,
        tech_health: float,
        security: float
    ) -> Tuple[str, str]:
        """Apply TIME framework categorization logic."""

        # QUADRANT 1: High Business Value, High Technical Quality → INVEST
        if high_business_value and high_technical_quality:
            return (
                TIMECategory.INVEST.value,
                f"High business value (BV: {bv_score:.1f}/10) and strong technical quality "
                f"(TQ: {tq_score:.1f}/10). Continue investment to maximize returns. "
                f"Composite score: {composite_score:.1f}/100."
            )

        # QUADRANT 2: High Business Value, Low Technical Quality → TOLERATE or MIGRATE
        if high_business_value and not high_technical_quality:
            if critical_business and (poor_tech or poor_security_flag):
                return (
                    TIMECategory.MIGRATE.value,
                    f"Critical business value ({business_value:.1f}/10) but poor technical quality "
                    f"(TQ: {tq_score:.1f}/10). Technical debt requires urgent migration."
                )
            else:
                return (
                    TIMECategory.TOLERATE.value,
                    f"High business value (BV: {bv_score:.1f}/10) justifies retention despite "
                    f"moderate technical quality (TQ: {tq_score:.1f}/10). Plan improvements."
                )

        # QUADRANT 3: Low Business Value, High Technical Quality → MIGRATE
        if not high_business_value and high_technical_quality:
            if is_redundant:
                return (
                    TIMECategory.ELIMINATE.value,
                    f"Redundant functionality with low business value (BV: {bv_score:.1f}/10). "
                    f"Consolidate with primary system to reduce complexity."
                )
            else:
                return (
                    TIMECategory.MIGRATE.value,
                    f"Good technical quality (TQ: {tq_score:.1f}/10) but limited business value "
                    f"(BV: {bv_score:.1f}/10). Consider consolidation or repurposing."
                )

        # QUADRANT 4: Low Business Value, Low Technical Quality → ELIMINATE
        if not high_business_value and not high_technical_quality:
            if low_composite or is_redundant:
                return (
                    TIMECategory.ELIMINATE.value,
                    f"Low business value (BV: {bv_score:.1f}/10) and poor technical quality "
                    f"(TQ: {tq_score:.1f}/10). Strong candidate for retirement."
                )
            else:
                return (
                    TIMECategory.MIGRATE.value,
                    f"Moderate scores suggest migration opportunity. "
                    f"Composite score: {composite_score:.1f}/100."
                )

        # Edge case fallback
        if composite_score >= 60:
            return (
                TIMECategory.TOLERATE.value,
                f"Moderate composite score ({composite_score:.1f}/100). Monitor and reassess."
            )
        else:
            return (
                TIMECategory.MIGRATE.value,
                f"Below-threshold scores suggest migration planning needed."
            )

    def batch_categorize(self, applications: List[Dict]) -> List[Dict]:
        """
        Categorize multiple applications using the TIME framework.

        Args:
            applications: List of application dictionaries with assessment data

        Returns:
            List of applications with added TIME categorization
        """
        results = []

        for app in applications:
            try:
                category, rationale = self.categorize_application(
                    business_value=float(app.get('business_value', app.get('Business Value', 5))),
                    tech_health=float(app.get('tech_health', app.get('Tech Health', 5))),
                    security=float(app.get('security', app.get('Security', 5))),
                    strategic_fit=float(app.get('strategic_fit', app.get('Strategic Fit', 5))),
                    usage=float(app.get('usage', app.get('Usage', 0))),
                    cost=float(app.get('cost', app.get('Cost', 0))),
                    composite_score=float(app.get('composite_score', app.get('Composite Score', 50))),
                    redundancy=int(app.get('redundancy', app.get('Redundancy', 0)))
                )

                app_result = app.copy()
                app_result['time_category'] = category
                app_result['time_rationale'] = rationale

                # Calculate and include the dimensional scores
                bv_score = self.calculate_business_value_score(
                    float(app.get('business_value', app.get('Business Value', 5))),
                    float(app.get('usage', app.get('Usage', 0))),
                    float(app.get('strategic_fit', app.get('Strategic Fit', 5)))
                )
                tq_score = self.calculate_technical_quality_score(
                    float(app.get('tech_health', app.get('Tech Health', 5))),
                    float(app.get('security', app.get('Security', 5))),
                    float(app.get('strategic_fit', app.get('Strategic Fit', 5))),
                    float(app.get('cost', app.get('Cost', 0)))
                )

                app_result['time_bv_score'] = bv_score
                app_result['time_tq_score'] = tq_score

                results.append(app_result)

            except (ValueError, KeyError) as e:
                logger.error(f"Error categorizing {app.get('name', 'Unknown')}: {e}")
                app_result = app.copy()
                app_result['time_category'] = TIMECategory.TOLERATE.value
                app_result['time_rationale'] = "Unable to categorize - data quality issues."
                app_result['time_bv_score'] = 5.0
                app_result['time_tq_score'] = 5.0
                results.append(app_result)

        return results

    def get_category_summary(self) -> Dict:
        """Get summary statistics of TIME categorizations."""
        total = sum(self.category_counts.values())

        if total == 0:
            return {'total': 0, 'distribution': {}, 'percentages': {}}

        summary = {
            'total': total,
            'distribution': dict(self.category_counts),
            'percentages': {}
        }

        for category, count in self.category_counts.items():
            summary['percentages'][category] = round((count / total) * 100, 1)

        return summary

    def get_portfolio_matrix(self, applications: List[Dict]) -> Dict:
        """Generate a TIME framework matrix showing application distribution."""
        matrix = {
            'quadrants': {
                'invest': [],
                'tolerate': [],
                'migrate': [],
                'eliminate': []
            },
            'counts': {
                'invest': 0,
                'tolerate': 0,
                'migrate': 0,
                'eliminate': 0
            }
        }

        for app in applications:
            category = app.get('time_category', app.get('TIME Category', '')).lower()
            if category in matrix['quadrants']:
                matrix['quadrants'][category].append(app.get('name', app.get('Application Name', 'Unknown')))
                matrix['counts'][category] += 1

        return matrix

    def reset_counts(self):
        """Reset category counts for new analysis."""
        self.category_counts = {cat.value: 0 for cat in TIMECategory}
