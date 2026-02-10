"""
Application Lifecycle Management Engine

Tracks applications through their complete lifecycle from inception to retirement.
Provides stage tracking, transition management, sunset planning, and health monitoring.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from uuid import uuid4


class LifecycleStage(Enum):
    """Application lifecycle stages."""
    INCEPTION = "inception"
    DEVELOPMENT = "development"
    PILOT = "pilot"
    GROWTH = "growth"
    MATURITY = "maturity"
    DECLINE = "decline"
    SUNSET = "sunset"
    RETIRED = "retired"


class TransitionStatus(Enum):
    """Status of a stage transition request."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class HealthStatus(Enum):
    """Application health status at current stage."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class SunsetReason(Enum):
    """Reasons for application sunset."""
    END_OF_LIFE = "end_of_life"
    REPLACED = "replaced"
    CONSOLIDATED = "consolidated"
    COST_REDUCTION = "cost_reduction"
    COMPLIANCE = "compliance"
    TECHNOLOGY_OBSOLETE = "technology_obsolete"
    BUSINESS_CHANGE = "business_change"
    SECURITY_RISK = "security_risk"


@dataclass
class StageMetrics:
    """Metrics for an application at a specific stage."""
    users_count: int = 0
    transactions_per_day: int = 0
    uptime_percentage: float = 99.0
    incident_count: int = 0
    change_requests: int = 0
    satisfaction_score: float = 0.0
    cost_per_month: float = 0.0
    roi_percentage: float = 0.0


@dataclass
class StageHistory:
    """Record of an application's stage transition."""
    id: str = field(default_factory=lambda: str(uuid4()))
    from_stage: Optional[LifecycleStage] = None
    to_stage: LifecycleStage = LifecycleStage.INCEPTION
    transition_date: datetime = field(default_factory=datetime.now)
    approved_by: Optional[str] = None
    notes: str = ""
    metrics_snapshot: Optional[StageMetrics] = None
    duration_in_stage_days: int = 0


@dataclass
class TransitionRequest:
    """Request to transition an application to a new stage."""
    id: str = field(default_factory=lambda: str(uuid4()))
    app_id: str = ""
    from_stage: LifecycleStage = LifecycleStage.INCEPTION
    to_stage: LifecycleStage = LifecycleStage.DEVELOPMENT
    requested_date: datetime = field(default_factory=datetime.now)
    requested_by: str = ""
    reason: str = ""
    status: TransitionStatus = TransitionStatus.PENDING
    reviewed_by: Optional[str] = None
    reviewed_date: Optional[datetime] = None
    review_notes: str = ""
    checklist_items: List[Dict[str, Any]] = field(default_factory=list)
    completion_percentage: float = 0.0


@dataclass
class SunsetPlan:
    """Plan for retiring an application."""
    id: str = field(default_factory=lambda: str(uuid4()))
    app_id: str = ""
    app_name: str = ""
    reason: SunsetReason = SunsetReason.END_OF_LIFE
    target_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=180))
    replacement_app_id: Optional[str] = None
    replacement_app_name: Optional[str] = None
    migration_steps: List[Dict[str, Any]] = field(default_factory=list)
    stakeholders: List[str] = field(default_factory=list)
    communication_plan: str = ""
    data_retention_policy: str = ""
    rollback_plan: str = ""
    estimated_savings: float = 0.0
    risks: List[Dict[str, Any]] = field(default_factory=list)
    status: TransitionStatus = TransitionStatus.PENDING
    progress_percentage: float = 0.0


@dataclass
class AppLifecycle:
    """Complete lifecycle information for an application."""
    app_id: str = ""
    app_name: str = ""
    current_stage: LifecycleStage = LifecycleStage.INCEPTION
    current_health: HealthStatus = HealthStatus.GOOD
    inception_date: datetime = field(default_factory=datetime.now)
    current_stage_start: datetime = field(default_factory=datetime.now)
    expected_stage_duration_days: int = 365
    stage_history: List[StageHistory] = field(default_factory=list)
    current_metrics: StageMetrics = field(default_factory=StageMetrics)
    sunset_plan: Optional[SunsetPlan] = None
    pending_transition: Optional[TransitionRequest] = None
    tags: List[str] = field(default_factory=list)
    owner: str = ""
    business_criticality: str = "medium"

    def days_in_current_stage(self) -> int:
        """Calculate days in current stage."""
        return (datetime.now() - self.current_stage_start).days

    def is_overdue_for_transition(self) -> bool:
        """Check if app has exceeded expected stage duration."""
        return self.days_in_current_stage() > self.expected_stage_duration_days

    def lifecycle_age_days(self) -> int:
        """Calculate total lifecycle age in days."""
        return (datetime.now() - self.inception_date).days


class LifecycleManager:
    """
    Manages application lifecycle tracking and transitions.

    Provides:
    - Stage tracking and history
    - Transition request management
    - Health assessment
    - Sunset planning
    - Portfolio lifecycle analytics
    """

    # Stage progression order
    STAGE_ORDER = [
        LifecycleStage.INCEPTION,
        LifecycleStage.DEVELOPMENT,
        LifecycleStage.PILOT,
        LifecycleStage.GROWTH,
        LifecycleStage.MATURITY,
        LifecycleStage.DECLINE,
        LifecycleStage.SUNSET,
        LifecycleStage.RETIRED
    ]

    # Expected duration in days for each stage
    STAGE_DURATIONS = {
        LifecycleStage.INCEPTION: 90,
        LifecycleStage.DEVELOPMENT: 180,
        LifecycleStage.PILOT: 90,
        LifecycleStage.GROWTH: 365,
        LifecycleStage.MATURITY: 730,
        LifecycleStage.DECLINE: 365,
        LifecycleStage.SUNSET: 180,
        LifecycleStage.RETIRED: 0
    }

    # Transition checklists by stage
    TRANSITION_CHECKLISTS = {
        LifecycleStage.DEVELOPMENT: [
            {"item": "Business case approved", "required": True},
            {"item": "Budget allocated", "required": True},
            {"item": "Development team assigned", "required": True},
            {"item": "Architecture design reviewed", "required": True},
            {"item": "Security assessment scheduled", "required": False}
        ],
        LifecycleStage.PILOT: [
            {"item": "Development complete", "required": True},
            {"item": "Unit tests passed", "required": True},
            {"item": "Integration tests passed", "required": True},
            {"item": "Security scan completed", "required": True},
            {"item": "Pilot user group identified", "required": True},
            {"item": "Rollback plan documented", "required": True}
        ],
        LifecycleStage.GROWTH: [
            {"item": "Pilot success criteria met", "required": True},
            {"item": "User feedback incorporated", "required": True},
            {"item": "Production infrastructure ready", "required": True},
            {"item": "Support team trained", "required": True},
            {"item": "Documentation complete", "required": True},
            {"item": "Monitoring configured", "required": True}
        ],
        LifecycleStage.MATURITY: [
            {"item": "Growth targets achieved", "required": True},
            {"item": "Stable user base established", "required": True},
            {"item": "Performance optimized", "required": False},
            {"item": "Cost optimization complete", "required": False}
        ],
        LifecycleStage.DECLINE: [
            {"item": "Declining usage confirmed", "required": True},
            {"item": "Replacement evaluation started", "required": False},
            {"item": "Sunset timeline proposed", "required": False}
        ],
        LifecycleStage.SUNSET: [
            {"item": "Replacement identified", "required": True},
            {"item": "Migration plan approved", "required": True},
            {"item": "Stakeholder communication sent", "required": True},
            {"item": "Data migration plan ready", "required": True},
            {"item": "Decommission date set", "required": True}
        ],
        LifecycleStage.RETIRED: [
            {"item": "All users migrated", "required": True},
            {"item": "Data archived or migrated", "required": True},
            {"item": "Infrastructure decommissioned", "required": True},
            {"item": "Documentation archived", "required": True},
            {"item": "Final cost savings verified", "required": False}
        ]
    }

    def __init__(self):
        """Initialize the lifecycle manager."""
        self.lifecycles: Dict[str, AppLifecycle] = {}
        self.transition_requests: Dict[str, TransitionRequest] = {}
        self.sunset_plans: Dict[str, SunsetPlan] = {}

    def register_application(
        self,
        app_id: str,
        app_name: str,
        initial_stage: LifecycleStage = LifecycleStage.INCEPTION,
        owner: str = "",
        business_criticality: str = "medium",
        inception_date: Optional[datetime] = None
    ) -> AppLifecycle:
        """
        Register a new application in the lifecycle manager.

        Args:
            app_id: Unique application identifier
            app_name: Application display name
            initial_stage: Starting lifecycle stage
            owner: Application owner
            business_criticality: low, medium, high, critical
            inception_date: When the app was first created

        Returns:
            AppLifecycle record
        """
        lifecycle = AppLifecycle(
            app_id=app_id,
            app_name=app_name,
            current_stage=initial_stage,
            inception_date=inception_date or datetime.now(),
            current_stage_start=inception_date or datetime.now(),
            expected_stage_duration_days=self.STAGE_DURATIONS.get(initial_stage, 365),
            owner=owner,
            business_criticality=business_criticality
        )

        # Add initial stage to history
        lifecycle.stage_history.append(StageHistory(
            to_stage=initial_stage,
            transition_date=lifecycle.inception_date,
            notes="Initial registration"
        ))

        self.lifecycles[app_id] = lifecycle
        return lifecycle

    def get_lifecycle(self, app_id: str) -> Optional[AppLifecycle]:
        """Get lifecycle information for an application."""
        return self.lifecycles.get(app_id)

    def request_transition(
        self,
        app_id: str,
        to_stage: LifecycleStage,
        requested_by: str,
        reason: str
    ) -> Optional[TransitionRequest]:
        """
        Request a stage transition for an application.

        Args:
            app_id: Application ID
            to_stage: Target stage
            requested_by: Requester name
            reason: Reason for transition

        Returns:
            TransitionRequest or None if invalid
        """
        lifecycle = self.lifecycles.get(app_id)
        if not lifecycle:
            return None

        # Validate transition is valid
        if not self._is_valid_transition(lifecycle.current_stage, to_stage):
            return None

        # Get checklist for target stage
        checklist = self._get_transition_checklist(to_stage)

        request = TransitionRequest(
            app_id=app_id,
            from_stage=lifecycle.current_stage,
            to_stage=to_stage,
            requested_by=requested_by,
            reason=reason,
            checklist_items=[{**item, "completed": False} for item in checklist]
        )

        self.transition_requests[request.id] = request
        lifecycle.pending_transition = request

        return request

    def approve_transition(
        self,
        request_id: str,
        reviewed_by: str,
        notes: str = ""
    ) -> bool:
        """
        Approve a transition request.

        Args:
            request_id: Transition request ID
            reviewed_by: Approver name
            notes: Review notes

        Returns:
            True if approved successfully
        """
        request = self.transition_requests.get(request_id)
        if not request or request.status != TransitionStatus.PENDING:
            return False

        request.status = TransitionStatus.APPROVED
        request.reviewed_by = reviewed_by
        request.reviewed_date = datetime.now()
        request.review_notes = notes

        return True

    def complete_transition(self, request_id: str) -> bool:
        """
        Complete an approved transition.

        Args:
            request_id: Transition request ID

        Returns:
            True if completed successfully
        """
        request = self.transition_requests.get(request_id)
        if not request or request.status != TransitionStatus.APPROVED:
            return False

        lifecycle = self.lifecycles.get(request.app_id)
        if not lifecycle:
            return False

        # Record history
        history = StageHistory(
            from_stage=lifecycle.current_stage,
            to_stage=request.to_stage,
            approved_by=request.reviewed_by,
            notes=request.reason,
            metrics_snapshot=lifecycle.current_metrics,
            duration_in_stage_days=lifecycle.days_in_current_stage()
        )
        lifecycle.stage_history.append(history)

        # Update current stage
        lifecycle.current_stage = request.to_stage
        lifecycle.current_stage_start = datetime.now()
        lifecycle.expected_stage_duration_days = self.STAGE_DURATIONS.get(
            request.to_stage, 365
        )
        lifecycle.pending_transition = None

        # Update request
        request.status = TransitionStatus.COMPLETED
        request.completion_percentage = 100.0

        return True

    def assess_health(self, app_id: str, metrics: StageMetrics) -> HealthStatus:
        """
        Assess application health based on metrics.

        Args:
            app_id: Application ID
            metrics: Current metrics

        Returns:
            HealthStatus assessment
        """
        lifecycle = self.lifecycles.get(app_id)
        if not lifecycle:
            return HealthStatus.FAIR

        # Update metrics
        lifecycle.current_metrics = metrics

        # Calculate health score (0-100)
        score = 0

        # Uptime contribution (max 30 points)
        if metrics.uptime_percentage >= 99.9:
            score += 30
        elif metrics.uptime_percentage >= 99.5:
            score += 25
        elif metrics.uptime_percentage >= 99.0:
            score += 20
        elif metrics.uptime_percentage >= 98.0:
            score += 10

        # Incident contribution (max 25 points)
        if metrics.incident_count == 0:
            score += 25
        elif metrics.incident_count <= 2:
            score += 20
        elif metrics.incident_count <= 5:
            score += 10
        elif metrics.incident_count <= 10:
            score += 5

        # Satisfaction contribution (max 25 points)
        if metrics.satisfaction_score >= 4.5:
            score += 25
        elif metrics.satisfaction_score >= 4.0:
            score += 20
        elif metrics.satisfaction_score >= 3.5:
            score += 15
        elif metrics.satisfaction_score >= 3.0:
            score += 10
        elif metrics.satisfaction_score >= 2.5:
            score += 5

        # ROI contribution (max 20 points)
        if metrics.roi_percentage >= 150:
            score += 20
        elif metrics.roi_percentage >= 100:
            score += 15
        elif metrics.roi_percentage >= 50:
            score += 10
        elif metrics.roi_percentage >= 0:
            score += 5

        # Determine health status
        if score >= 85:
            health = HealthStatus.EXCELLENT
        elif score >= 70:
            health = HealthStatus.GOOD
        elif score >= 50:
            health = HealthStatus.FAIR
        elif score >= 30:
            health = HealthStatus.POOR
        else:
            health = HealthStatus.CRITICAL

        lifecycle.current_health = health
        return health

    def create_sunset_plan(
        self,
        app_id: str,
        reason: SunsetReason,
        target_date: datetime,
        replacement_app_id: Optional[str] = None,
        estimated_savings: float = 0.0
    ) -> Optional[SunsetPlan]:
        """
        Create a sunset plan for an application.

        Args:
            app_id: Application ID to sunset
            reason: Reason for sunset
            target_date: Target retirement date
            replacement_app_id: Optional replacement application
            estimated_savings: Estimated annual cost savings

        Returns:
            SunsetPlan or None
        """
        lifecycle = self.lifecycles.get(app_id)
        if not lifecycle:
            return None

        replacement_name = None
        if replacement_app_id and replacement_app_id in self.lifecycles:
            replacement_name = self.lifecycles[replacement_app_id].app_name

        plan = SunsetPlan(
            app_id=app_id,
            app_name=lifecycle.app_name,
            reason=reason,
            target_date=target_date,
            replacement_app_id=replacement_app_id,
            replacement_app_name=replacement_name,
            estimated_savings=estimated_savings,
            migration_steps=self._generate_migration_steps(reason),
            risks=self._identify_sunset_risks(lifecycle)
        )

        self.sunset_plans[plan.id] = plan
        lifecycle.sunset_plan = plan

        return plan

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Get lifecycle summary for entire portfolio.

        Returns:
            Dictionary with portfolio lifecycle statistics
        """
        if not self.lifecycles:
            return {
                "total_applications": 0,
                "stage_distribution": {},
                "health_distribution": {},
                "overdue_transitions": [],
                "pending_transitions": [],
                "active_sunset_plans": [],
                "average_age_days": 0
            }

        stage_counts = {}
        health_counts = {}
        overdue = []
        pending = []
        sunset_plans = []
        total_age = 0

        for lifecycle in self.lifecycles.values():
            # Stage distribution
            stage = lifecycle.current_stage.value
            stage_counts[stage] = stage_counts.get(stage, 0) + 1

            # Health distribution
            health = lifecycle.current_health.value
            health_counts[health] = health_counts.get(health, 0) + 1

            # Overdue transitions
            if lifecycle.is_overdue_for_transition():
                overdue.append({
                    "app_id": lifecycle.app_id,
                    "app_name": lifecycle.app_name,
                    "current_stage": lifecycle.current_stage.value,
                    "days_overdue": lifecycle.days_in_current_stage() - lifecycle.expected_stage_duration_days
                })

            # Pending transitions
            if lifecycle.pending_transition:
                pending.append({
                    "app_id": lifecycle.app_id,
                    "app_name": lifecycle.app_name,
                    "from_stage": lifecycle.pending_transition.from_stage.value,
                    "to_stage": lifecycle.pending_transition.to_stage.value,
                    "status": lifecycle.pending_transition.status.value
                })

            # Sunset plans
            if lifecycle.sunset_plan:
                sunset_plans.append({
                    "app_id": lifecycle.app_id,
                    "app_name": lifecycle.app_name,
                    "target_date": lifecycle.sunset_plan.target_date.isoformat(),
                    "reason": lifecycle.sunset_plan.reason.value,
                    "progress": lifecycle.sunset_plan.progress_percentage
                })

            total_age += lifecycle.lifecycle_age_days()

        return {
            "total_applications": len(self.lifecycles),
            "stage_distribution": stage_counts,
            "health_distribution": health_counts,
            "overdue_transitions": overdue,
            "pending_transitions": pending,
            "active_sunset_plans": sunset_plans,
            "average_age_days": round(total_age / len(self.lifecycles)) if self.lifecycles else 0
        }

    def get_stage_timeline(self, app_id: str) -> List[Dict[str, Any]]:
        """
        Get the stage transition timeline for an application.

        Args:
            app_id: Application ID

        Returns:
            List of timeline entries
        """
        lifecycle = self.lifecycles.get(app_id)
        if not lifecycle:
            return []

        timeline = []
        for history in lifecycle.stage_history:
            timeline.append({
                "id": history.id,
                "from_stage": history.from_stage.value if history.from_stage else None,
                "to_stage": history.to_stage.value,
                "date": history.transition_date.isoformat(),
                "approved_by": history.approved_by,
                "notes": history.notes,
                "duration_days": history.duration_in_stage_days
            })

        return timeline

    def forecast_lifecycle(self, app_id: str) -> Dict[str, Any]:
        """
        Forecast remaining lifecycle stages and dates.

        Args:
            app_id: Application ID

        Returns:
            Forecast of future stages with estimated dates
        """
        lifecycle = self.lifecycles.get(app_id)
        if not lifecycle:
            return {}

        current_idx = self.STAGE_ORDER.index(lifecycle.current_stage)
        remaining_stages = self.STAGE_ORDER[current_idx + 1:]

        forecast = []
        current_date = datetime.now()

        # Add remaining days in current stage
        remaining_current = max(0, lifecycle.expected_stage_duration_days - lifecycle.days_in_current_stage())
        current_date += timedelta(days=remaining_current)

        for stage in remaining_stages:
            duration = self.STAGE_DURATIONS.get(stage, 365)
            forecast.append({
                "stage": stage.value,
                "estimated_start": current_date.isoformat(),
                "estimated_duration_days": duration
            })
            current_date += timedelta(days=duration)

        return {
            "app_id": app_id,
            "current_stage": lifecycle.current_stage.value,
            "days_remaining_current": remaining_current,
            "forecast": forecast,
            "estimated_retirement": current_date.isoformat()
        }

    def _is_valid_transition(self, from_stage: LifecycleStage, to_stage: LifecycleStage) -> bool:
        """Check if a stage transition is valid."""
        from_idx = self.STAGE_ORDER.index(from_stage)
        to_idx = self.STAGE_ORDER.index(to_stage)

        # Can only move forward by one stage, or back to previous stage
        return to_idx == from_idx + 1 or to_idx == from_idx - 1

    def _get_transition_checklist(self, to_stage: LifecycleStage) -> List[Dict[str, Any]]:
        """Get checklist items for a stage transition."""
        return self.TRANSITION_CHECKLISTS.get(to_stage, [])

    def _generate_migration_steps(self, reason: SunsetReason) -> List[Dict[str, Any]]:
        """Generate default migration steps based on sunset reason."""
        base_steps = [
            {"step": "Notify all stakeholders", "order": 1, "status": "pending"},
            {"step": "Document current state and dependencies", "order": 2, "status": "pending"},
            {"step": "Identify data migration requirements", "order": 3, "status": "pending"},
            {"step": "Create rollback plan", "order": 4, "status": "pending"},
            {"step": "Execute data migration", "order": 5, "status": "pending"},
            {"step": "Migrate users in phases", "order": 6, "status": "pending"},
            {"step": "Monitor replacement system", "order": 7, "status": "pending"},
            {"step": "Decommission old system", "order": 8, "status": "pending"},
            {"step": "Archive documentation", "order": 9, "status": "pending"},
            {"step": "Final review and close", "order": 10, "status": "pending"}
        ]

        if reason == SunsetReason.CONSOLIDATED:
            base_steps.insert(4, {
                "step": "Map functionality to consolidated system",
                "order": 4.5,
                "status": "pending"
            })
        elif reason == SunsetReason.SECURITY_RISK:
            base_steps.insert(0, {
                "step": "Implement emergency security controls",
                "order": 0,
                "status": "pending"
            })

        # Renumber steps
        for i, step in enumerate(base_steps):
            step["order"] = i + 1

        return base_steps

    def _identify_sunset_risks(self, lifecycle: AppLifecycle) -> List[Dict[str, Any]]:
        """Identify risks associated with sunsetting an application."""
        risks = []

        if lifecycle.business_criticality in ["high", "critical"]:
            risks.append({
                "risk": "High business criticality may impact operations",
                "severity": "high",
                "mitigation": "Ensure comprehensive testing and staged rollout"
            })

        if lifecycle.current_metrics.users_count > 100:
            risks.append({
                "risk": f"Large user base ({lifecycle.current_metrics.users_count} users) requires extensive change management",
                "severity": "medium",
                "mitigation": "Develop detailed communication and training plan"
            })

        if lifecycle.current_metrics.transactions_per_day > 1000:
            risks.append({
                "risk": "High transaction volume may cause performance issues during migration",
                "severity": "medium",
                "mitigation": "Plan migration during low-usage periods"
            })

        if len(lifecycle.stage_history) < 3:
            risks.append({
                "risk": "Limited historical data may affect planning accuracy",
                "severity": "low",
                "mitigation": "Document all current state information thoroughly"
            })

        return risks


def create_lifecycle_manager() -> LifecycleManager:
    """Create and return a new LifecycleManager instance."""
    return LifecycleManager()


def create_demo_lifecycles() -> Tuple[LifecycleManager, Dict[str, AppLifecycle]]:
    """
    Create demo lifecycle data for testing and demonstration.

    Returns:
        Tuple of (LifecycleManager, Dict of lifecycles by app_id)
    """
    manager = LifecycleManager()

    # Application 1: Legacy CRM - in Decline stage
    crm = manager.register_application(
        app_id="APP001",
        app_name="Legacy CRM System",
        initial_stage=LifecycleStage.DECLINE,
        owner="Sales Team",
        business_criticality="high",
        inception_date=datetime.now() - timedelta(days=2190)  # 6 years old
    )
    crm.current_metrics = StageMetrics(
        users_count=150,
        transactions_per_day=500,
        uptime_percentage=98.5,
        incident_count=8,
        change_requests=2,
        satisfaction_score=3.2,
        cost_per_month=15000,
        roi_percentage=45
    )
    crm.current_health = HealthStatus.FAIR
    manager.assess_health("APP001", crm.current_metrics)

    # Create sunset plan for CRM
    manager.create_sunset_plan(
        app_id="APP001",
        reason=SunsetReason.REPLACED,
        target_date=datetime.now() + timedelta(days=180),
        replacement_app_id="APP005",
        estimated_savings=120000
    )

    # Application 2: ERP System - in Maturity stage
    erp = manager.register_application(
        app_id="APP002",
        app_name="Enterprise ERP",
        initial_stage=LifecycleStage.MATURITY,
        owner="Finance Team",
        business_criticality="critical",
        inception_date=datetime.now() - timedelta(days=1460)  # 4 years old
    )
    erp.current_metrics = StageMetrics(
        users_count=500,
        transactions_per_day=5000,
        uptime_percentage=99.9,
        incident_count=1,
        change_requests=15,
        satisfaction_score=4.5,
        cost_per_month=45000,
        roi_percentage=180
    )
    manager.assess_health("APP002", erp.current_metrics)

    # Application 3: HR Portal - in Growth stage
    hr = manager.register_application(
        app_id="APP003",
        app_name="HR Self-Service Portal",
        initial_stage=LifecycleStage.GROWTH,
        owner="HR Department",
        business_criticality="medium",
        inception_date=datetime.now() - timedelta(days=365)  # 1 year old
    )
    hr.current_metrics = StageMetrics(
        users_count=350,
        transactions_per_day=800,
        uptime_percentage=99.5,
        incident_count=3,
        change_requests=25,
        satisfaction_score=4.0,
        cost_per_month=8000,
        roi_percentage=95
    )
    manager.assess_health("APP003", hr.current_metrics)

    # Application 4: Data Analytics - in Pilot stage
    analytics = manager.register_application(
        app_id="APP004",
        app_name="Data Analytics Platform",
        initial_stage=LifecycleStage.PILOT,
        owner="IT Department",
        business_criticality="medium",
        inception_date=datetime.now() - timedelta(days=120)
    )
    analytics.current_metrics = StageMetrics(
        users_count=25,
        transactions_per_day=200,
        uptime_percentage=99.0,
        incident_count=5,
        change_requests=40,
        satisfaction_score=3.8,
        cost_per_month=12000,
        roi_percentage=0
    )
    manager.assess_health("APP004", analytics.current_metrics)

    # Create transition request for Analytics to move to Growth
    manager.request_transition(
        app_id="APP004",
        to_stage=LifecycleStage.GROWTH,
        requested_by="John Smith",
        reason="Pilot success criteria met, ready for organization-wide rollout"
    )

    # Application 5: New CRM - in Development stage (replacement for Legacy CRM)
    new_crm = manager.register_application(
        app_id="APP005",
        app_name="Salesforce CRM",
        initial_stage=LifecycleStage.DEVELOPMENT,
        owner="Sales Team",
        business_criticality="high",
        inception_date=datetime.now() - timedelta(days=60)
    )
    new_crm.current_metrics = StageMetrics(
        users_count=0,
        transactions_per_day=0,
        uptime_percentage=0,
        incident_count=0,
        change_requests=50,
        satisfaction_score=0,
        cost_per_month=25000,
        roi_percentage=0
    )

    # Application 6: Legacy Payroll - Retired
    payroll = manager.register_application(
        app_id="APP006",
        app_name="Legacy Payroll System",
        initial_stage=LifecycleStage.RETIRED,
        owner="Finance Team",
        business_criticality="low",
        inception_date=datetime.now() - timedelta(days=3650)  # 10 years old
    )
    payroll.current_health = HealthStatus.FAIR

    lifecycles = {
        "APP001": crm,
        "APP002": erp,
        "APP003": hr,
        "APP004": analytics,
        "APP005": new_crm,
        "APP006": payroll
    }

    return manager, lifecycles
