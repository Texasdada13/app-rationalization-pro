"""
Integration Assessment Engine
Evaluates health and risks of integrations between applications
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import uuid


class IntegrationType(Enum):
    """Types of integrations between applications"""
    API_REST = "api_rest"
    API_SOAP = "api_soap"
    API_GRAPHQL = "api_graphql"
    DATABASE_DIRECT = "database_direct"
    DATABASE_REPLICATION = "database_replication"
    FILE_TRANSFER = "file_transfer"
    MESSAGE_QUEUE = "message_queue"
    EVENT_STREAM = "event_stream"
    EMBEDDED = "embedded"
    SSO_AUTH = "sso_auth"
    ETL_BATCH = "etl_batch"
    REAL_TIME_SYNC = "real_time_sync"


class DataSensitivity(Enum):
    """Data sensitivity levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    SENSITIVE = "sensitive"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class IntegrationHealth(Enum):
    """Integration health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    AT_RISK = "at_risk"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class Integration:
    """Represents an integration between two applications"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_app_id: str = ""
    source_app_name: str = ""
    target_app_id: str = ""
    target_app_name: str = ""
    integration_type: IntegrationType = IntegrationType.API_REST
    frequency: str = "real_time"  # real_time, hourly, daily, weekly, monthly
    data_sensitivity: DataSensitivity = DataSensitivity.INTERNAL
    criticality: str = "medium"  # critical, high, medium, low
    bidirectional: bool = False
    documentation_complete: bool = False
    monitoring_enabled: bool = False

    # Health metrics
    health_score: float = 5.0  # 0-10
    latency_ms: float = 100.0
    error_rate_percent: float = 0.5
    uptime_percent: float = 99.0
    last_successful_sync: Optional[datetime] = None
    error_count_30d: int = 0

    # Metadata
    owner_team: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    notes: str = ""


@dataclass
class IntegrationAssessmentResult:
    """Result of integration assessment"""
    integration_id: str
    source_app: str
    target_app: str
    overall_health: IntegrationHealth
    health_score: float
    risk_score: float
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    modernization_opportunities: List[str]


@dataclass
class PortfolioIntegrationSummary:
    """Summary of all integrations in a portfolio"""
    total_integrations: int
    healthy_count: int
    degraded_count: int
    at_risk_count: int
    critical_count: int
    average_health_score: float
    top_issues: List[Dict[str, Any]]
    bottlenecks: List[Dict[str, Any]]
    compliance_gaps: List[Dict[str, Any]]
    recommendations: List[str]


class IntegrationAssessor:
    """
    Assesses health and risks of application integrations.

    Features:
    - Score integration health based on multiple factors
    - Identify integration bottlenecks
    - Detect compliance gaps
    - Recommend modernization opportunities
    """

    # Scoring thresholds
    HEALTH_THRESHOLDS = {
        'latency_ms': {'good': 100, 'acceptable': 500, 'poor': 1000},
        'error_rate': {'good': 0.1, 'acceptable': 1.0, 'poor': 5.0},
        'uptime': {'good': 99.9, 'acceptable': 99.0, 'poor': 95.0}
    }

    # Integration type risk factors
    TYPE_RISK_FACTORS = {
        IntegrationType.DATABASE_DIRECT: 1.5,      # Tight coupling
        IntegrationType.EMBEDDED: 1.8,              # Very tight coupling
        IntegrationType.API_SOAP: 1.2,              # Legacy technology
        IntegrationType.FILE_TRANSFER: 1.3,         # Data staleness risk
        IntegrationType.API_REST: 0.8,              # Modern, flexible
        IntegrationType.API_GRAPHQL: 0.7,           # Modern, efficient
        IntegrationType.MESSAGE_QUEUE: 0.9,         # Decoupled
        IntegrationType.EVENT_STREAM: 0.8,          # Modern, scalable
        IntegrationType.ETL_BATCH: 1.1,             # Batch delays
        IntegrationType.DATABASE_REPLICATION: 1.0,  # Standard
        IntegrationType.SSO_AUTH: 0.9,              # Security layer
        IntegrationType.REAL_TIME_SYNC: 1.0         # Standard
    }

    # Data sensitivity risk multipliers
    SENSITIVITY_RISK = {
        DataSensitivity.PUBLIC: 0.5,
        DataSensitivity.INTERNAL: 0.8,
        DataSensitivity.SENSITIVE: 1.2,
        DataSensitivity.CONFIDENTIAL: 1.5,
        DataSensitivity.RESTRICTED: 2.0
    }

    def __init__(self):
        self.integrations: Dict[str, Integration] = {}

    def add_integration(self, integration: Integration) -> str:
        """Add an integration to the assessor"""
        self.integrations[integration.id] = integration
        return integration.id

    def add_integrations_from_apps(self, applications: List[Dict]) -> List[Integration]:
        """
        Create integrations from application dependency data.

        Args:
            applications: List of app dicts with 'dependencies' and 'integrations' fields

        Returns:
            List of created Integration objects
        """
        created = []
        app_map = {str(app.get('id', '')): app for app in applications}

        for app in applications:
            app_id = str(app.get('id', ''))
            app_name = app.get('name', 'Unknown')

            # Process dependencies as integrations
            for dep_id in app.get('dependencies', []):
                if dep_id in app_map:
                    dep = app_map[dep_id]
                    integration = Integration(
                        source_app_id=app_id,
                        source_app_name=app_name,
                        target_app_id=dep_id,
                        target_app_name=dep.get('name', 'Unknown'),
                        integration_type=self._infer_integration_type(app, dep),
                        frequency=self._infer_frequency(app, dep),
                        data_sensitivity=self._infer_sensitivity(app, dep),
                        criticality=self._infer_criticality(app, dep),
                        health_score=self._estimate_health_score(app, dep),
                        created_at=datetime.utcnow()
                    )
                    self.integrations[integration.id] = integration
                    created.append(integration)

            # Process explicit integrations if available
            for int_data in app.get('integrations', []):
                target_id = int_data.get('target_app_id')
                if target_id and target_id in app_map:
                    target = app_map[target_id]
                    integration = Integration(
                        source_app_id=app_id,
                        source_app_name=app_name,
                        target_app_id=target_id,
                        target_app_name=target.get('name', 'Unknown'),
                        integration_type=IntegrationType(int_data.get('type', 'api_rest')),
                        frequency=int_data.get('frequency', 'daily'),
                        data_sensitivity=DataSensitivity(int_data.get('sensitivity', 'internal')),
                        criticality=int_data.get('criticality', 'medium'),
                        health_score=int_data.get('health_score', 5.0),
                        latency_ms=int_data.get('latency_ms', 100),
                        error_rate_percent=int_data.get('error_rate', 0.5),
                        uptime_percent=int_data.get('uptime', 99.0),
                        documentation_complete=int_data.get('documented', False),
                        monitoring_enabled=int_data.get('monitored', False),
                        created_at=datetime.utcnow()
                    )
                    self.integrations[integration.id] = integration
                    created.append(integration)

        return created

    def _infer_integration_type(self, source: Dict, target: Dict) -> IntegrationType:
        """Infer integration type from app categories"""
        source_cat = source.get('category', '').lower()
        target_cat = target.get('category', '').lower()

        if 'database' in source_cat or 'database' in target_cat:
            return IntegrationType.DATABASE_DIRECT
        elif 'etl' in source_cat or 'etl' in target_cat:
            return IntegrationType.ETL_BATCH
        elif 'auth' in target_cat or 'identity' in target_cat:
            return IntegrationType.SSO_AUTH
        elif 'queue' in source_cat or 'messaging' in target_cat:
            return IntegrationType.MESSAGE_QUEUE
        elif 'analytics' in source_cat or 'report' in target_cat:
            return IntegrationType.FILE_TRANSFER
        return IntegrationType.API_REST

    def _infer_frequency(self, source: Dict, target: Dict) -> str:
        """Infer integration frequency from app characteristics"""
        source_cat = source.get('category', '').lower()

        if 'real' in source_cat or 'transaction' in source_cat:
            return 'real_time'
        elif 'report' in source_cat or 'analytics' in source_cat:
            return 'daily'
        elif 'batch' in source_cat or 'etl' in source_cat:
            return 'daily'
        return 'hourly'

    def _infer_sensitivity(self, source: Dict, target: Dict) -> DataSensitivity:
        """Infer data sensitivity from app characteristics"""
        source_cat = source.get('category', '').lower()
        target_cat = target.get('category', '').lower()

        if any(x in source_cat + target_cat for x in ['hr', 'payroll', 'pii', 'health']):
            return DataSensitivity.CONFIDENTIAL
        elif any(x in source_cat + target_cat for x in ['finance', 'accounting', 'payment']):
            return DataSensitivity.SENSITIVE
        elif any(x in source_cat + target_cat for x in ['public', 'website', 'marketing']):
            return DataSensitivity.PUBLIC
        return DataSensitivity.INTERNAL

    def _infer_criticality(self, source: Dict, target: Dict) -> str:
        """Infer criticality from app scores"""
        source_bv = source.get('business_value', 5)
        target_bv = target.get('business_value', 5)
        max_bv = max(source_bv, target_bv)

        if max_bv >= 9:
            return 'critical'
        elif max_bv >= 7:
            return 'high'
        elif max_bv >= 5:
            return 'medium'
        return 'low'

    def _estimate_health_score(self, source: Dict, target: Dict) -> float:
        """Estimate integration health from app health scores"""
        source_health = source.get('tech_health', 5)
        target_health = target.get('tech_health', 5)
        return (source_health + target_health) / 2

    def assess_integration(self, integration_id: str) -> IntegrationAssessmentResult:
        """
        Assess a single integration's health and risks.

        Returns detailed assessment with recommendations.
        """
        if integration_id not in self.integrations:
            return IntegrationAssessmentResult(
                integration_id=integration_id,
                source_app="Unknown",
                target_app="Unknown",
                overall_health=IntegrationHealth.UNKNOWN,
                health_score=0.0,
                risk_score=10.0,
                issues=[],
                recommendations=["Integration not found"],
                modernization_opportunities=[]
            )

        integration = self.integrations[integration_id]
        issues = []
        recommendations = []
        modernization_opps = []

        # Calculate health score components
        latency_score = self._score_latency(integration.latency_ms)
        error_score = self._score_error_rate(integration.error_rate_percent)
        uptime_score = self._score_uptime(integration.uptime_percent)
        documentation_score = 10.0 if integration.documentation_complete else 3.0
        monitoring_score = 10.0 if integration.monitoring_enabled else 2.0

        # Weighted health score
        health_score = (
            latency_score * 0.25 +
            error_score * 0.25 +
            uptime_score * 0.25 +
            documentation_score * 0.15 +
            monitoring_score * 0.10
        )

        # Calculate risk score
        type_risk = self.TYPE_RISK_FACTORS.get(integration.integration_type, 1.0)
        sensitivity_risk = self.SENSITIVITY_RISK.get(integration.data_sensitivity, 1.0)
        risk_score = (10 - health_score) * type_risk * sensitivity_risk

        # Identify issues
        if integration.latency_ms > self.HEALTH_THRESHOLDS['latency_ms']['poor']:
            issues.append({
                'type': 'latency',
                'severity': 'high',
                'message': f"High latency: {integration.latency_ms}ms (threshold: 1000ms)"
            })
        elif integration.latency_ms > self.HEALTH_THRESHOLDS['latency_ms']['acceptable']:
            issues.append({
                'type': 'latency',
                'severity': 'medium',
                'message': f"Elevated latency: {integration.latency_ms}ms"
            })

        if integration.error_rate_percent > self.HEALTH_THRESHOLDS['error_rate']['poor']:
            issues.append({
                'type': 'errors',
                'severity': 'critical',
                'message': f"Critical error rate: {integration.error_rate_percent}%"
            })
        elif integration.error_rate_percent > self.HEALTH_THRESHOLDS['error_rate']['acceptable']:
            issues.append({
                'type': 'errors',
                'severity': 'medium',
                'message': f"Elevated error rate: {integration.error_rate_percent}%"
            })

        if integration.uptime_percent < self.HEALTH_THRESHOLDS['uptime']['poor']:
            issues.append({
                'type': 'uptime',
                'severity': 'critical',
                'message': f"Poor uptime: {integration.uptime_percent}%"
            })

        if not integration.documentation_complete:
            issues.append({
                'type': 'documentation',
                'severity': 'medium',
                'message': "Integration lacks complete documentation"
            })

        if not integration.monitoring_enabled:
            issues.append({
                'type': 'monitoring',
                'severity': 'medium',
                'message': "No active monitoring configured"
            })

        # Generate recommendations
        if issues:
            for issue in issues:
                if issue['type'] == 'latency':
                    recommendations.append("Optimize database queries or add caching layer")
                    recommendations.append("Consider async processing for non-critical operations")
                elif issue['type'] == 'errors':
                    recommendations.append("Implement retry logic with exponential backoff")
                    recommendations.append("Add circuit breaker pattern to prevent cascade failures")
                elif issue['type'] == 'documentation':
                    recommendations.append("Create API documentation using OpenAPI/Swagger")
                elif issue['type'] == 'monitoring':
                    recommendations.append("Set up APM monitoring (DataDog, New Relic, etc.)")

        # Modernization opportunities
        if integration.integration_type == IntegrationType.API_SOAP:
            modernization_opps.append("Migrate from SOAP to REST API for better performance")
        elif integration.integration_type == IntegrationType.DATABASE_DIRECT:
            modernization_opps.append("Replace direct DB access with API layer for loose coupling")
        elif integration.integration_type == IntegrationType.FILE_TRANSFER:
            modernization_opps.append("Consider real-time streaming for fresher data")

        if integration.frequency in ['daily', 'weekly'] and integration.criticality in ['critical', 'high']:
            modernization_opps.append("Increase sync frequency for critical data flows")

        # Determine overall health
        if health_score >= 8:
            overall_health = IntegrationHealth.HEALTHY
        elif health_score >= 6:
            overall_health = IntegrationHealth.DEGRADED
        elif health_score >= 4:
            overall_health = IntegrationHealth.AT_RISK
        else:
            overall_health = IntegrationHealth.CRITICAL

        return IntegrationAssessmentResult(
            integration_id=integration_id,
            source_app=integration.source_app_name,
            target_app=integration.target_app_name,
            overall_health=overall_health,
            health_score=round(health_score, 2),
            risk_score=round(risk_score, 2),
            issues=issues,
            recommendations=list(set(recommendations)),  # Deduplicate
            modernization_opportunities=modernization_opps
        )

    def _score_latency(self, latency_ms: float) -> float:
        """Convert latency to 0-10 score"""
        if latency_ms <= self.HEALTH_THRESHOLDS['latency_ms']['good']:
            return 10.0
        elif latency_ms <= self.HEALTH_THRESHOLDS['latency_ms']['acceptable']:
            return 7.0
        elif latency_ms <= self.HEALTH_THRESHOLDS['latency_ms']['poor']:
            return 4.0
        return 2.0

    def _score_error_rate(self, error_rate: float) -> float:
        """Convert error rate to 0-10 score"""
        if error_rate <= self.HEALTH_THRESHOLDS['error_rate']['good']:
            return 10.0
        elif error_rate <= self.HEALTH_THRESHOLDS['error_rate']['acceptable']:
            return 7.0
        elif error_rate <= self.HEALTH_THRESHOLDS['error_rate']['poor']:
            return 4.0
        return 1.0

    def _score_uptime(self, uptime: float) -> float:
        """Convert uptime to 0-10 score"""
        if uptime >= self.HEALTH_THRESHOLDS['uptime']['good']:
            return 10.0
        elif uptime >= self.HEALTH_THRESHOLDS['uptime']['acceptable']:
            return 7.0
        elif uptime >= self.HEALTH_THRESHOLDS['uptime']['poor']:
            return 4.0
        return 2.0

    def batch_assess(self) -> List[IntegrationAssessmentResult]:
        """Assess all integrations"""
        return [
            self.assess_integration(int_id)
            for int_id in self.integrations
        ]

    def get_portfolio_summary(self) -> PortfolioIntegrationSummary:
        """Get summary of all integrations in the portfolio"""
        if not self.integrations:
            return PortfolioIntegrationSummary(
                total_integrations=0,
                healthy_count=0,
                degraded_count=0,
                at_risk_count=0,
                critical_count=0,
                average_health_score=0.0,
                top_issues=[],
                bottlenecks=[],
                compliance_gaps=[],
                recommendations=[]
            )

        assessments = self.batch_assess()

        # Count by health status
        health_counts = {
            IntegrationHealth.HEALTHY: 0,
            IntegrationHealth.DEGRADED: 0,
            IntegrationHealth.AT_RISK: 0,
            IntegrationHealth.CRITICAL: 0
        }
        for a in assessments:
            if a.overall_health in health_counts:
                health_counts[a.overall_health] += 1

        # Average health
        avg_health = sum(a.health_score for a in assessments) / len(assessments)

        # Collect all issues
        all_issues = []
        for a in assessments:
            for issue in a.issues:
                all_issues.append({
                    **issue,
                    'source_app': a.source_app,
                    'target_app': a.target_app
                })

        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_issues.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 4))

        # Find bottlenecks (apps with many problematic integrations)
        app_issue_counts: Dict[str, int] = {}
        for a in assessments:
            if a.issues:
                for app in [a.source_app, a.target_app]:
                    app_issue_counts[app] = app_issue_counts.get(app, 0) + len(a.issues)

        bottlenecks = [
            {'app_name': app, 'issue_count': count}
            for app, count in sorted(app_issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        # Compliance gaps
        compliance_gaps = []
        for int_id, integration in self.integrations.items():
            if integration.data_sensitivity in [DataSensitivity.CONFIDENTIAL, DataSensitivity.RESTRICTED]:
                if not integration.documentation_complete:
                    compliance_gaps.append({
                        'integration': f"{integration.source_app_name} → {integration.target_app_name}",
                        'issue': 'Missing documentation for sensitive data flow',
                        'severity': 'high'
                    })
                if not integration.monitoring_enabled:
                    compliance_gaps.append({
                        'integration': f"{integration.source_app_name} → {integration.target_app_name}",
                        'issue': 'No monitoring for sensitive data flow',
                        'severity': 'high'
                    })

        # High-level recommendations
        recommendations = []
        if health_counts[IntegrationHealth.CRITICAL] > 0:
            recommendations.append(
                f"Address {health_counts[IntegrationHealth.CRITICAL]} critical integrations immediately"
            )
        if len(bottlenecks) > 0:
            recommendations.append(
                f"Focus on {bottlenecks[0]['app_name']} - highest integration issue count"
            )
        if len(compliance_gaps) > 0:
            recommendations.append(
                f"Close {len(compliance_gaps)} compliance gaps for sensitive integrations"
            )
        if avg_health < 6:
            recommendations.append("Portfolio-wide integration health improvement needed")

        return PortfolioIntegrationSummary(
            total_integrations=len(self.integrations),
            healthy_count=health_counts[IntegrationHealth.HEALTHY],
            degraded_count=health_counts[IntegrationHealth.DEGRADED],
            at_risk_count=health_counts[IntegrationHealth.AT_RISK],
            critical_count=health_counts[IntegrationHealth.CRITICAL],
            average_health_score=round(avg_health, 2),
            top_issues=all_issues[:10],
            bottlenecks=bottlenecks,
            compliance_gaps=compliance_gaps,
            recommendations=recommendations
        )

    def get_app_integrations(self, app_id: str, direction: str = 'all') -> List[Dict]:
        """
        Get integrations for a specific application.

        Args:
            app_id: Application ID
            direction: 'inbound', 'outbound', or 'all'
        """
        results = []

        for integration in self.integrations.values():
            include = False
            if direction in ['outbound', 'all'] and integration.source_app_id == app_id:
                include = True
            if direction in ['inbound', 'all'] and integration.target_app_id == app_id:
                include = True

            if include:
                assessment = self.assess_integration(integration.id)
                results.append({
                    'id': integration.id,
                    'source_app': integration.source_app_name,
                    'target_app': integration.target_app_name,
                    'type': integration.integration_type.value,
                    'frequency': integration.frequency,
                    'sensitivity': integration.data_sensitivity.value,
                    'health_score': assessment.health_score,
                    'health_status': assessment.overall_health.value,
                    'direction': 'outbound' if integration.source_app_id == app_id else 'inbound'
                })

        return results

    def identify_bottlenecks(self) -> List[Dict]:
        """Identify integration performance bottlenecks"""
        bottlenecks = []

        for int_id, integration in self.integrations.items():
            issues = []

            # High latency
            if integration.latency_ms > 500:
                issues.append(f"High latency: {integration.latency_ms}ms")

            # High error rate
            if integration.error_rate_percent > 1.0:
                issues.append(f"High errors: {integration.error_rate_percent}%")

            # Low uptime
            if integration.uptime_percent < 99.0:
                issues.append(f"Low uptime: {integration.uptime_percent}%")

            if issues:
                bottlenecks.append({
                    'integration_id': int_id,
                    'source_app': integration.source_app_name,
                    'target_app': integration.target_app_name,
                    'type': integration.integration_type.value,
                    'criticality': integration.criticality,
                    'issues': issues,
                    'impact': 'high' if integration.criticality in ['critical', 'high'] else 'medium'
                })

        # Sort by impact
        impact_order = {'high': 0, 'medium': 1, 'low': 2}
        bottlenecks.sort(key=lambda x: impact_order.get(x['impact'], 3))

        return bottlenecks


# Factory function
def create_integration_assessor() -> IntegrationAssessor:
    """Create a new IntegrationAssessor instance"""
    return IntegrationAssessor()
