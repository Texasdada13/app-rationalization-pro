"""
Migration Planner for Application Rationalization Pro
Plans and tracks cloud migration paths for applications.

Features:
- 7R Migration Strategy Assessment (Rehost, Replatform, Refactor, etc.)
- Cloud Provider Recommendations (AWS, Azure, GCP)
- Migration Wave Planning
- Dependency-Aware Sequencing
- Cost and Effort Estimation
- Risk Assessment and Mitigation
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from datetime import datetime, timedelta
import random


class MigrationStrategy(Enum):
    """7R Migration Strategies."""
    REHOST = "rehost"  # Lift and shift
    REPLATFORM = "replatform"  # Lift, tinker, and shift
    REFACTOR = "refactor"  # Re-architect for cloud
    REPURCHASE = "repurchase"  # Move to SaaS
    RETAIN = "retain"  # Keep on-premises
    RETIRE = "retire"  # Decommission
    RELOCATE = "relocate"  # Move to different data center


class CloudProvider(Enum):
    """Supported cloud providers."""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ORACLE_CLOUD = "oracle_cloud"
    IBM_CLOUD = "ibm_cloud"
    MULTI_CLOUD = "multi_cloud"
    HYBRID = "hybrid"
    ON_PREMISES = "on_premises"


class MigrationComplexity(Enum):
    """Migration complexity levels."""
    TRIVIAL = "trivial"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class MigrationPhase(Enum):
    """Migration project phases."""
    ASSESSMENT = "assessment"
    PLANNING = "planning"
    PREPARATION = "preparation"
    MIGRATION = "migration"
    VALIDATION = "validation"
    OPTIMIZATION = "optimization"
    COMPLETE = "complete"


class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ApplicationMigrationProfile:
    """Migration profile for a single application."""
    app_id: str
    app_name: str

    # Current state
    current_hosting: str = "on_premises"
    technology_stack: List[str] = field(default_factory=list)
    database_type: str = ""
    has_legacy_dependencies: bool = False
    is_stateful: bool = True
    data_sensitivity: str = "internal"

    # Scores (0-1)
    cloud_readiness: float = 0.5
    business_criticality: float = 0.5
    technical_debt: float = 0.3
    modernization_urgency: float = 0.5

    # Dependencies
    dependency_count: int = 0
    is_dependency_for: int = 0

    # Costs
    current_annual_cost: float = 0.0
    estimated_users: int = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "app_id": self.app_id,
            "app_name": self.app_name,
            "current_hosting": self.current_hosting,
            "technology_stack": self.technology_stack,
            "database_type": self.database_type,
            "has_legacy_dependencies": self.has_legacy_dependencies,
            "is_stateful": self.is_stateful,
            "data_sensitivity": self.data_sensitivity,
            "cloud_readiness": self.cloud_readiness,
            "business_criticality": self.business_criticality,
            "technical_debt": self.technical_debt,
            "modernization_urgency": self.modernization_urgency,
            "dependency_count": self.dependency_count,
            "is_dependency_for": self.is_dependency_for,
            "current_annual_cost": self.current_annual_cost,
            "estimated_users": self.estimated_users
        }


@dataclass
class MigrationRecommendation:
    """Migration recommendation for an application."""
    app_id: str
    app_name: str

    # Recommended strategy
    primary_strategy: MigrationStrategy = MigrationStrategy.RETAIN
    alternative_strategy: Optional[MigrationStrategy] = None
    strategy_rationale: str = ""

    # Target
    target_provider: CloudProvider = CloudProvider.ON_PREMISES
    target_services: List[str] = field(default_factory=list)

    # Estimates
    complexity: MigrationComplexity = MigrationComplexity.MEDIUM
    estimated_duration_weeks: int = 0
    estimated_effort_hours: int = 0
    estimated_cost: float = 0.0

    # Expected benefits
    estimated_annual_savings: float = 0.0
    performance_improvement: float = 0.0
    scalability_improvement: float = 0.0

    # Risks
    risk_level: RiskLevel = RiskLevel.MEDIUM
    risks: List[str] = field(default_factory=list)
    mitigations: List[str] = field(default_factory=list)

    # Prerequisites
    prerequisites: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "app_id": self.app_id,
            "app_name": self.app_name,
            "primary_strategy": self.primary_strategy.value,
            "alternative_strategy": self.alternative_strategy.value if self.alternative_strategy else None,
            "strategy_rationale": self.strategy_rationale,
            "target_provider": self.target_provider.value,
            "target_services": self.target_services,
            "complexity": self.complexity.value,
            "estimated_duration_weeks": self.estimated_duration_weeks,
            "estimated_effort_hours": self.estimated_effort_hours,
            "estimated_cost": self.estimated_cost,
            "estimated_annual_savings": self.estimated_annual_savings,
            "performance_improvement": self.performance_improvement,
            "scalability_improvement": self.scalability_improvement,
            "risk_level": self.risk_level.value,
            "risks": self.risks,
            "mitigations": self.mitigations,
            "prerequisites": self.prerequisites,
            "blockers": self.blockers
        }


@dataclass
class MigrationWave:
    """A wave of application migrations."""
    wave_id: int
    name: str
    applications: List[MigrationRecommendation] = field(default_factory=list)

    # Timeline
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration_weeks: int = 0

    # Aggregates
    total_effort_hours: int = 0
    total_cost: float = 0.0
    total_savings: float = 0.0

    # Status
    phase: MigrationPhase = MigrationPhase.ASSESSMENT
    completion_percentage: float = 0.0

    # Team
    required_team_size: int = 0
    required_skills: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "wave_id": self.wave_id,
            "name": self.name,
            "applications": [app.to_dict() for app in self.applications],
            "application_count": len(self.applications),
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "duration_weeks": self.duration_weeks,
            "total_effort_hours": self.total_effort_hours,
            "total_cost": self.total_cost,
            "total_savings": self.total_savings,
            "phase": self.phase.value,
            "completion_percentage": self.completion_percentage,
            "required_team_size": self.required_team_size,
            "required_skills": self.required_skills
        }


@dataclass
class MigrationPlan:
    """Complete migration plan for a portfolio."""
    plan_id: str
    portfolio_name: str
    waves: List[MigrationWave] = field(default_factory=list)

    # Summary
    total_applications: int = 0
    applications_to_migrate: int = 0
    applications_to_retire: int = 0
    applications_to_retain: int = 0

    # Strategy breakdown
    strategy_distribution: Dict[str, int] = field(default_factory=dict)
    provider_distribution: Dict[str, int] = field(default_factory=dict)

    # Timeline
    plan_start_date: Optional[datetime] = None
    plan_end_date: Optional[datetime] = None
    total_duration_weeks: int = 0

    # Financials
    total_migration_cost: float = 0.0
    total_annual_savings: float = 0.0
    payback_months: float = 0.0
    roi_percentage: float = 0.0

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    version: str = "1.0"

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "plan_id": self.plan_id,
            "portfolio_name": self.portfolio_name,
            "waves": [wave.to_dict() for wave in self.waves],
            "wave_count": len(self.waves),
            "total_applications": self.total_applications,
            "applications_to_migrate": self.applications_to_migrate,
            "applications_to_retire": self.applications_to_retire,
            "applications_to_retain": self.applications_to_retain,
            "strategy_distribution": self.strategy_distribution,
            "provider_distribution": self.provider_distribution,
            "plan_start_date": self.plan_start_date.isoformat() if self.plan_start_date else None,
            "plan_end_date": self.plan_end_date.isoformat() if self.plan_end_date else None,
            "total_duration_weeks": self.total_duration_weeks,
            "total_migration_cost": self.total_migration_cost,
            "total_annual_savings": self.total_annual_savings,
            "payback_months": self.payback_months,
            "roi_percentage": self.roi_percentage,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "version": self.version
        }


class MigrationPlanner:
    """
    Migration Planner Engine for cloud migration planning and tracking.
    """

    # Strategy complexity factors
    STRATEGY_COMPLEXITY = {
        MigrationStrategy.RETIRE: 0.1,
        MigrationStrategy.RETAIN: 0.0,
        MigrationStrategy.REPURCHASE: 0.3,
        MigrationStrategy.REHOST: 0.4,
        MigrationStrategy.RELOCATE: 0.5,
        MigrationStrategy.REPLATFORM: 0.6,
        MigrationStrategy.REFACTOR: 1.0,
    }

    # Base effort hours per strategy (for medium complexity app)
    STRATEGY_BASE_EFFORT = {
        MigrationStrategy.RETIRE: 40,
        MigrationStrategy.RETAIN: 0,
        MigrationStrategy.REPURCHASE: 120,
        MigrationStrategy.REHOST: 200,
        MigrationStrategy.RELOCATE: 160,
        MigrationStrategy.REPLATFORM: 400,
        MigrationStrategy.REFACTOR: 800,
    }

    # Provider-specific services mapping
    PROVIDER_SERVICES = {
        CloudProvider.AWS: {
            "compute": ["EC2", "Lambda", "ECS", "EKS"],
            "database": ["RDS", "Aurora", "DynamoDB", "Redshift"],
            "storage": ["S3", "EBS", "EFS"],
            "networking": ["VPC", "Route 53", "CloudFront"],
        },
        CloudProvider.AZURE: {
            "compute": ["Virtual Machines", "Functions", "AKS", "App Service"],
            "database": ["SQL Database", "Cosmos DB", "PostgreSQL"],
            "storage": ["Blob Storage", "Files", "Disk"],
            "networking": ["Virtual Network", "DNS", "CDN"],
        },
        CloudProvider.GCP: {
            "compute": ["Compute Engine", "Cloud Functions", "GKE", "App Engine"],
            "database": ["Cloud SQL", "Spanner", "Firestore", "BigQuery"],
            "storage": ["Cloud Storage", "Persistent Disk"],
            "networking": ["VPC", "Cloud DNS", "Cloud CDN"],
        },
    }

    def __init__(self, preferred_provider: CloudProvider = CloudProvider.AWS):
        """Initialize migration planner."""
        self.preferred_provider = preferred_provider
        self._applications: List[ApplicationMigrationProfile] = []
        self._recommendations: Dict[str, MigrationRecommendation] = {}
        self._plan: Optional[MigrationPlan] = None

    def add_application(self, app: ApplicationMigrationProfile) -> None:
        """Add an application for migration planning."""
        self._applications.append(app)

    def add_applications(self, apps: List[ApplicationMigrationProfile]) -> None:
        """Add multiple applications."""
        self._applications.extend(apps)

    def clear_applications(self) -> None:
        """Clear all applications."""
        self._applications = []
        self._recommendations = {}
        self._plan = None

    def _assess_strategy(self, app: ApplicationMigrationProfile) -> Tuple[MigrationStrategy, str]:
        """Determine the best migration strategy for an application."""
        # Decision tree for strategy selection
        if app.business_criticality < 0.2 and app.cloud_readiness < 0.3:
            return MigrationStrategy.RETIRE, "Low business value and poor cloud readiness suggest retirement"

        if app.modernization_urgency < 0.2 and app.cloud_readiness < 0.3:
            return MigrationStrategy.RETAIN, "Low urgency and readiness - retain on current platform"

        if app.has_legacy_dependencies and app.technical_debt > 0.7:
            return MigrationStrategy.RETAIN, "Legacy dependencies require staying on-premises"

        # Check for SaaS replacement opportunity
        if app.technical_debt > 0.6 and not app.is_dependency_for > 3:
            return MigrationStrategy.REPURCHASE, "High technical debt makes SaaS replacement attractive"

        if app.cloud_readiness > 0.8 and app.technical_debt < 0.3:
            return MigrationStrategy.REHOST, "High cloud readiness allows simple lift-and-shift"

        if app.cloud_readiness > 0.6 and app.modernization_urgency > 0.7:
            return MigrationStrategy.REFACTOR, "Good readiness and high urgency justify re-architecture"

        if app.cloud_readiness > 0.5:
            return MigrationStrategy.REPLATFORM, "Moderate readiness suits replatforming approach"

        return MigrationStrategy.REHOST, "Default to lift-and-shift for cloud migration"

    def _select_provider(self, app: ApplicationMigrationProfile) -> CloudProvider:
        """Select the best cloud provider for an application."""
        # For now, use preferred provider with some exceptions
        if "Microsoft" in app.technology_stack or ".NET" in app.technology_stack:
            return CloudProvider.AZURE
        if "Google" in app.technology_stack or "Firebase" in app.technology_stack:
            return CloudProvider.GCP
        if app.data_sensitivity == "highly_regulated":
            return CloudProvider.HYBRID
        return self.preferred_provider

    def _select_services(
        self,
        app: ApplicationMigrationProfile,
        provider: CloudProvider,
        strategy: MigrationStrategy
    ) -> List[str]:
        """Select appropriate cloud services for migration."""
        if provider not in self.PROVIDER_SERVICES:
            return []

        services = []
        provider_services = self.PROVIDER_SERVICES[provider]

        # Add compute services
        if strategy == MigrationStrategy.REHOST:
            services.extend(provider_services["compute"][:1])  # VMs
        elif strategy in [MigrationStrategy.REPLATFORM, MigrationStrategy.REFACTOR]:
            services.extend(provider_services["compute"][1:3])  # Containers/Serverless

        # Add database services if needed
        if app.database_type:
            services.extend(provider_services["database"][:1])

        # Add storage
        services.extend(provider_services["storage"][:1])

        return services

    def _calculate_complexity(
        self,
        app: ApplicationMigrationProfile,
        strategy: MigrationStrategy
    ) -> MigrationComplexity:
        """Calculate migration complexity."""
        score = self.STRATEGY_COMPLEXITY[strategy]

        # Adjust for app characteristics
        score += app.dependency_count * 0.05
        score += app.is_dependency_for * 0.1
        score += app.technical_debt * 0.3
        score -= app.cloud_readiness * 0.2

        if app.has_legacy_dependencies:
            score += 0.3
        if app.data_sensitivity == "highly_regulated":
            score += 0.2

        if score < 0.2:
            return MigrationComplexity.TRIVIAL
        elif score < 0.4:
            return MigrationComplexity.LOW
        elif score < 0.6:
            return MigrationComplexity.MEDIUM
        elif score < 0.8:
            return MigrationComplexity.HIGH
        else:
            return MigrationComplexity.VERY_HIGH

    def _estimate_effort(
        self,
        app: ApplicationMigrationProfile,
        strategy: MigrationStrategy,
        complexity: MigrationComplexity
    ) -> Tuple[int, int, float]:
        """Estimate effort hours, duration weeks, and cost."""
        base_effort = self.STRATEGY_BASE_EFFORT[strategy]

        # Complexity multipliers
        complexity_multipliers = {
            MigrationComplexity.TRIVIAL: 0.5,
            MigrationComplexity.LOW: 0.75,
            MigrationComplexity.MEDIUM: 1.0,
            MigrationComplexity.HIGH: 1.5,
            MigrationComplexity.VERY_HIGH: 2.0,
        }

        effort_hours = int(base_effort * complexity_multipliers[complexity])

        # Adjust for dependencies
        effort_hours += app.dependency_count * 20
        effort_hours += app.is_dependency_for * 40

        # Calculate duration (assuming team velocity)
        duration_weeks = max(1, effort_hours // 80)  # 80 hours per week team capacity

        # Estimate cost (blended rate assumption)
        hourly_rate = 150  # Blended consulting rate
        migration_cost = effort_hours * hourly_rate

        # Add cloud infrastructure setup costs
        migration_cost += 5000  # Base setup cost

        return effort_hours, duration_weeks, migration_cost

    def _estimate_savings(
        self,
        app: ApplicationMigrationProfile,
        strategy: MigrationStrategy
    ) -> float:
        """Estimate annual savings from migration."""
        current_cost = app.current_annual_cost
        if current_cost == 0:
            return 0.0

        # Savings percentages by strategy
        savings_rates = {
            MigrationStrategy.RETIRE: 1.0,  # 100% savings
            MigrationStrategy.RETAIN: 0.0,
            MigrationStrategy.REPURCHASE: 0.2,
            MigrationStrategy.REHOST: 0.25,
            MigrationStrategy.RELOCATE: 0.15,
            MigrationStrategy.REPLATFORM: 0.35,
            MigrationStrategy.REFACTOR: 0.45,
        }

        return current_cost * savings_rates[strategy]

    def _identify_risks(
        self,
        app: ApplicationMigrationProfile,
        strategy: MigrationStrategy
    ) -> Tuple[RiskLevel, List[str], List[str]]:
        """Identify risks and mitigations."""
        risks = []
        mitigations = []

        # Data-related risks
        if app.data_sensitivity in ["confidential", "highly_regulated"]:
            risks.append("Sensitive data requires careful handling during migration")
            mitigations.append("Implement encryption in transit and at rest")

        # Dependency risks
        if app.dependency_count > 5:
            risks.append("High number of dependencies may cause integration issues")
            mitigations.append("Create detailed dependency map and migration sequence")

        if app.is_dependency_for > 3:
            risks.append("Application is critical dependency for other systems")
            mitigations.append("Plan migration with careful coordination of dependent systems")

        # Technical risks
        if app.has_legacy_dependencies:
            risks.append("Legacy dependencies may not be compatible with cloud")
            mitigations.append("Evaluate modernization or wrapper solutions")

        if app.technical_debt > 0.6:
            risks.append("High technical debt increases migration complexity")
            mitigations.append("Address critical technical debt before migration")

        # Business risks
        if app.business_criticality > 0.8:
            risks.append("High business criticality requires zero-downtime migration")
            mitigations.append("Implement blue-green deployment strategy")

        # Strategy-specific risks
        if strategy == MigrationStrategy.REFACTOR:
            risks.append("Re-architecture may introduce new bugs")
            mitigations.append("Comprehensive testing and gradual rollout")

        # Determine overall risk level
        if len(risks) >= 4 or app.business_criticality > 0.9:
            level = RiskLevel.CRITICAL
        elif len(risks) >= 3:
            level = RiskLevel.HIGH
        elif len(risks) >= 1:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW

        return level, risks, mitigations

    def _identify_prerequisites(
        self,
        app: ApplicationMigrationProfile,
        strategy: MigrationStrategy,
        provider: CloudProvider
    ) -> Tuple[List[str], List[str]]:
        """Identify prerequisites and blockers."""
        prerequisites = []
        blockers = []

        # Common prerequisites
        prerequisites.append("Complete dependency mapping")
        prerequisites.append("Establish cloud account and networking")

        if strategy != MigrationStrategy.RETIRE:
            prerequisites.append("Set up monitoring and alerting")
            prerequisites.append("Create rollback plan")

        # Strategy-specific
        if strategy == MigrationStrategy.REHOST:
            prerequisites.append("Assess VM sizing requirements")
        elif strategy == MigrationStrategy.REPLATFORM:
            prerequisites.append("Identify platform-specific changes needed")
            prerequisites.append("Update configuration management")
        elif strategy == MigrationStrategy.REFACTOR:
            prerequisites.append("Complete architecture design review")
            prerequisites.append("Set up CI/CD pipeline for cloud")
        elif strategy == MigrationStrategy.REPURCHASE:
            prerequisites.append("Complete vendor evaluation")
            prerequisites.append("Plan data migration to SaaS")

        # Blockers based on issues
        if app.has_legacy_dependencies:
            blockers.append("Legacy dependency modernization required first")

        if app.data_sensitivity == "highly_regulated" and provider not in [CloudProvider.HYBRID, CloudProvider.ON_PREMISES]:
            blockers.append("Regulatory compliance review required")

        return prerequisites, blockers

    def generate_recommendation(self, app: ApplicationMigrationProfile) -> MigrationRecommendation:
        """Generate migration recommendation for a single application."""
        # Determine strategy
        strategy, rationale = self._assess_strategy(app)

        # Select provider and services
        provider = self._select_provider(app)
        services = self._select_services(app, provider, strategy)

        # Calculate complexity
        complexity = self._calculate_complexity(app, strategy)

        # Estimate effort and cost
        effort_hours, duration_weeks, migration_cost = self._estimate_effort(app, strategy, complexity)

        # Estimate savings
        annual_savings = self._estimate_savings(app, strategy)

        # Identify risks
        risk_level, risks, mitigations = self._identify_risks(app, strategy)

        # Identify prerequisites
        prerequisites, blockers = self._identify_prerequisites(app, strategy, provider)

        # Build recommendation
        rec = MigrationRecommendation(
            app_id=app.app_id,
            app_name=app.app_name,
            primary_strategy=strategy,
            strategy_rationale=rationale,
            target_provider=provider,
            target_services=services,
            complexity=complexity,
            estimated_duration_weeks=duration_weeks,
            estimated_effort_hours=effort_hours,
            estimated_cost=migration_cost,
            estimated_annual_savings=annual_savings,
            risk_level=risk_level,
            risks=risks,
            mitigations=mitigations,
            prerequisites=prerequisites,
            blockers=blockers
        )

        self._recommendations[app.app_id] = rec
        return rec

    def generate_all_recommendations(self) -> List[MigrationRecommendation]:
        """Generate recommendations for all applications."""
        recommendations = []
        for app in self._applications:
            rec = self.generate_recommendation(app)
            recommendations.append(rec)
        return recommendations

    def _create_waves(
        self,
        recommendations: List[MigrationRecommendation],
        max_apps_per_wave: int = 10,
        max_parallel_effort: int = 2000
    ) -> List[MigrationWave]:
        """Organize applications into migration waves."""
        waves = []
        current_wave_apps = []
        current_wave_effort = 0
        wave_id = 0

        # Sort by priority: retire first, then by complexity and risk
        priority_order = {
            MigrationStrategy.RETIRE: 0,
            MigrationStrategy.REPURCHASE: 1,
            MigrationStrategy.REHOST: 2,
            MigrationStrategy.RELOCATE: 3,
            MigrationStrategy.REPLATFORM: 4,
            MigrationStrategy.REFACTOR: 5,
            MigrationStrategy.RETAIN: 6,
        }

        sorted_recs = sorted(
            recommendations,
            key=lambda r: (priority_order[r.primary_strategy], r.estimated_effort_hours)
        )

        wave_names = [
            "Quick Wins",
            "Foundation",
            "Accelerate",
            "Transform",
            "Optimize",
            "Complete"
        ]

        for rec in sorted_recs:
            # Skip retain applications
            if rec.primary_strategy == MigrationStrategy.RETAIN:
                continue

            # Check if we need to start a new wave
            if (len(current_wave_apps) >= max_apps_per_wave or
                current_wave_effort + rec.estimated_effort_hours > max_parallel_effort):

                if current_wave_apps:
                    wave = MigrationWave(
                        wave_id=wave_id,
                        name=wave_names[min(wave_id, len(wave_names)-1)],
                        applications=current_wave_apps.copy(),
                        total_effort_hours=current_wave_effort
                    )
                    waves.append(wave)
                    wave_id += 1

                current_wave_apps = []
                current_wave_effort = 0

            current_wave_apps.append(rec)
            current_wave_effort += rec.estimated_effort_hours

        # Add remaining apps
        if current_wave_apps:
            wave = MigrationWave(
                wave_id=wave_id,
                name=wave_names[min(wave_id, len(wave_names)-1)],
                applications=current_wave_apps.copy(),
                total_effort_hours=current_wave_effort
            )
            waves.append(wave)

        return waves

    def _calculate_wave_details(
        self,
        wave: MigrationWave,
        start_date: datetime
    ) -> MigrationWave:
        """Calculate detailed metrics for a wave."""
        wave.start_date = start_date
        wave.duration_weeks = max(1, max(
            app.estimated_duration_weeks for app in wave.applications
        ) if wave.applications else 0)
        wave.end_date = start_date + timedelta(weeks=wave.duration_weeks)

        wave.total_effort_hours = sum(app.estimated_effort_hours for app in wave.applications)
        wave.total_cost = sum(app.estimated_cost for app in wave.applications)
        wave.total_savings = sum(app.estimated_annual_savings for app in wave.applications)

        # Estimate team size (assume 40 hours/week per person)
        if wave.duration_weeks > 0:
            wave.required_team_size = max(1, wave.total_effort_hours // (wave.duration_weeks * 40))

        # Identify required skills
        skills = set()
        for app in wave.applications:
            if app.target_provider == CloudProvider.AWS:
                skills.add("AWS Certified")
            elif app.target_provider == CloudProvider.AZURE:
                skills.add("Azure Certified")
            elif app.target_provider == CloudProvider.GCP:
                skills.add("GCP Certified")

            if app.primary_strategy == MigrationStrategy.REFACTOR:
                skills.add("Cloud Architecture")
                skills.add("DevOps/CI-CD")
            if app.primary_strategy == MigrationStrategy.REPLATFORM:
                skills.add("Container Orchestration")

        wave.required_skills = list(skills)

        return wave

    def create_migration_plan(
        self,
        portfolio_name: str,
        start_date: Optional[datetime] = None
    ) -> MigrationPlan:
        """Create a complete migration plan."""
        if start_date is None:
            start_date = datetime.now() + timedelta(weeks=4)

        # Generate recommendations if not done
        if not self._recommendations:
            self.generate_all_recommendations()

        recommendations = list(self._recommendations.values())

        # Create waves
        waves = self._create_waves(recommendations)

        # Calculate wave details
        current_date = start_date
        for wave in waves:
            wave = self._calculate_wave_details(wave, current_date)
            current_date = wave.end_date + timedelta(weeks=1)  # 1 week buffer between waves

        # Calculate strategy distribution
        strategy_dist = {}
        provider_dist = {}
        for rec in recommendations:
            strategy = rec.primary_strategy.value
            strategy_dist[strategy] = strategy_dist.get(strategy, 0) + 1

            provider = rec.target_provider.value
            provider_dist[provider] = provider_dist.get(provider, 0) + 1

        # Count by category
        migrate_count = sum(1 for r in recommendations if r.primary_strategy not in
                           [MigrationStrategy.RETAIN, MigrationStrategy.RETIRE])
        retire_count = sum(1 for r in recommendations if r.primary_strategy == MigrationStrategy.RETIRE)
        retain_count = sum(1 for r in recommendations if r.primary_strategy == MigrationStrategy.RETAIN)

        # Calculate financials
        total_cost = sum(wave.total_cost for wave in waves)
        total_savings = sum(wave.total_savings for wave in waves)

        if total_savings > 0:
            payback_months = (total_cost / total_savings) * 12
            roi = ((total_savings - total_cost) / total_cost) * 100 if total_cost > 0 else 0
        else:
            payback_months = 0
            roi = 0

        # Build plan
        plan = MigrationPlan(
            plan_id=f"MIGPLAN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            portfolio_name=portfolio_name,
            waves=waves,
            total_applications=len(self._applications),
            applications_to_migrate=migrate_count,
            applications_to_retire=retire_count,
            applications_to_retain=retain_count,
            strategy_distribution=strategy_dist,
            provider_distribution=provider_dist,
            plan_start_date=start_date,
            plan_end_date=waves[-1].end_date if waves else start_date,
            total_duration_weeks=sum(wave.duration_weeks for wave in waves),
            total_migration_cost=total_cost,
            total_annual_savings=total_savings,
            payback_months=payback_months,
            roi_percentage=roi
        )

        self._plan = plan
        return plan

    def get_plan_summary(self) -> Dict:
        """Get summary of current migration plan."""
        if not self._plan:
            return {}

        return {
            "plan_id": self._plan.plan_id,
            "total_applications": self._plan.total_applications,
            "applications_to_migrate": self._plan.applications_to_migrate,
            "applications_to_retire": self._plan.applications_to_retire,
            "applications_to_retain": self._plan.applications_to_retain,
            "wave_count": len(self._plan.waves),
            "total_duration_weeks": self._plan.total_duration_weeks,
            "total_migration_cost": self._plan.total_migration_cost,
            "total_annual_savings": self._plan.total_annual_savings,
            "payback_months": self._plan.payback_months,
            "roi_percentage": self._plan.roi_percentage,
            "strategy_distribution": self._plan.strategy_distribution,
            "provider_distribution": self._plan.provider_distribution
        }


def create_migration_planner(
    preferred_provider: CloudProvider = CloudProvider.AWS
) -> MigrationPlanner:
    """Factory function to create a migration planner."""
    return MigrationPlanner(preferred_provider=preferred_provider)


def create_demo_migration_profiles(count: int = 20) -> List[ApplicationMigrationProfile]:
    """Create demo application profiles for testing."""
    tech_stacks = [
        ["Java", "Spring Boot", "PostgreSQL"],
        ["Python", "Django", "MySQL"],
        [".NET", "C#", "SQL Server"],
        ["Node.js", "Express", "MongoDB"],
        ["PHP", "Laravel", "MySQL"],
        ["Ruby", "Rails", "PostgreSQL"],
        ["Go", "Gin", "PostgreSQL"],
        ["COBOL", "DB2", "Mainframe"],
        ["Java", "Struts", "Oracle"],
    ]

    db_types = ["PostgreSQL", "MySQL", "SQL Server", "Oracle", "MongoDB", "DB2"]
    sensitivity_levels = ["public", "internal", "confidential", "highly_regulated"]

    profiles = []
    for i in range(count):
        is_legacy = random.random() < 0.3

        profile = ApplicationMigrationProfile(
            app_id=f"APP-{i+1:04d}",
            app_name=f"Application {i+1}",
            current_hosting="on_premises" if random.random() < 0.7 else "colocation",
            technology_stack=random.choice(tech_stacks),
            database_type=random.choice(db_types),
            has_legacy_dependencies=is_legacy,
            is_stateful=random.random() < 0.6,
            data_sensitivity=random.choice(sensitivity_levels),
            cloud_readiness=random.uniform(0.1, 0.9) if not is_legacy else random.uniform(0.1, 0.4),
            business_criticality=random.uniform(0.2, 1.0),
            technical_debt=random.uniform(0.1, 0.9) if not is_legacy else random.uniform(0.5, 0.9),
            modernization_urgency=random.uniform(0.2, 1.0),
            dependency_count=random.randint(0, 10),
            is_dependency_for=random.randint(0, 5),
            current_annual_cost=random.uniform(20000, 500000),
            estimated_users=random.randint(50, 5000)
        )
        profiles.append(profile)

    return profiles
