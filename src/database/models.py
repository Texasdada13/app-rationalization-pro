"""
Database Models for App Rationalization Pro

SQLAlchemy models for applications, portfolios, and chat sessions.
Includes government edition models for agency hierarchy and public sector needs.
"""

import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON

db = SQLAlchemy()


def generate_uuid():
    return str(uuid.uuid4())


# ============================================================
# GOVERNMENT EDITION MODELS
# ============================================================

class Agency(db.Model):
    """
    Government Agency/Department hierarchy model.

    Examples:
    - Dallas County (top-level)
      - Sheriff's Office (department)
      - District Attorney (department)
      - Health & Human Services (department)
    """
    __tablename__ = 'agencies'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50))  # e.g., "DCSO" for Dallas County Sheriff's Office

    # Hierarchy
    parent_id = db.Column(db.String(36), db.ForeignKey('agencies.id'), nullable=True)
    level = db.Column(db.String(50))  # county, city, state, department, division

    # Agency details
    agency_type = db.Column(db.String(100))  # law_enforcement, public_health, administration, etc.
    jurisdiction = db.Column(db.String(200))  # Geographic area served
    population_served = db.Column(db.Integer)
    employee_count = db.Column(db.Integer)
    annual_budget = db.Column(db.Float)

    # Contact/leadership
    head_official = db.Column(db.String(200))  # Sheriff, Director, Commissioner
    head_title = db.Column(db.String(100))

    # Compliance requirements
    required_frameworks = db.Column(JSON)  # ["CJIS", "HIPAA"] etc.

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    children = db.relationship('Agency', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    portfolios = db.relationship('Portfolio', backref='agency', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'parent_id': self.parent_id,
            'level': self.level,
            'agency_type': self.agency_type,
            'jurisdiction': self.jurisdiction,
            'population_served': self.population_served,
            'employee_count': self.employee_count,
            'annual_budget': self.annual_budget,
            'head_official': self.head_official,
            'head_title': self.head_title,
            'required_frameworks': self.required_frameworks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_full_hierarchy(self):
        """Get full agency hierarchy path."""
        path = [self.name]
        current = self.parent
        while current:
            path.insert(0, current.name)
            current = current.parent
        return ' > '.join(path)


class Contract(db.Model):
    """
    Government contract/procurement tracking.

    Tracks vendor contracts, renewal dates, procurement requirements.
    """
    __tablename__ = 'contracts'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    application_id = db.Column(db.String(36), db.ForeignKey('applications.id'), nullable=False)

    # Contract details
    contract_number = db.Column(db.String(100))
    vendor_name = db.Column(db.String(200))
    contract_type = db.Column(db.String(100))  # perpetual, subscription, SaaS, time_and_materials

    # Financial
    annual_cost = db.Column(db.Float)
    total_contract_value = db.Column(db.Float)

    # Dates
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    renewal_date = db.Column(db.Date)
    renewal_notice_days = db.Column(db.Integer, default=90)  # Days before renewal notice required

    # Procurement info
    procurement_method = db.Column(db.String(100))  # competitive_bid, sole_source, cooperative, DIR
    cooperative_contract = db.Column(db.String(200))  # e.g., "Texas DIR", "TIPS/TAPS", "GSA"

    # Terms
    auto_renewal = db.Column(db.Boolean, default=False)
    termination_clause = db.Column(db.Text)
    renewal_terms = db.Column(db.Text)

    # Status
    status = db.Column(db.String(50))  # active, expiring_soon, expired, pending_renewal

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'application_id': self.application_id,
            'contract_number': self.contract_number,
            'vendor_name': self.vendor_name,
            'contract_type': self.contract_type,
            'annual_cost': self.annual_cost,
            'total_contract_value': self.total_contract_value,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'renewal_date': self.renewal_date.isoformat() if self.renewal_date else None,
            'renewal_notice_days': self.renewal_notice_days,
            'procurement_method': self.procurement_method,
            'cooperative_contract': self.cooperative_contract,
            'auto_renewal': self.auto_renewal,
            'termination_clause': self.termination_clause,
            'renewal_terms': self.renewal_terms,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def days_until_renewal(self):
        """Calculate days until renewal notice is due."""
        if not self.renewal_date:
            return None
        from datetime import date
        notice_date = self.renewal_date
        return (notice_date - date.today()).days


# ============================================================
# CORE MODELS (Enhanced for Government Edition)
# ============================================================


class Portfolio(db.Model):
    """Portfolio of applications for an organization."""
    __tablename__ = 'portfolios'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(200), nullable=False)
    organization = db.Column(db.String(200))
    description = db.Column(db.Text)

    # Government Edition fields
    agency_id = db.Column(db.String(36), db.ForeignKey('agencies.id'), nullable=True)
    portfolio_type = db.Column(db.String(50), default='enterprise')  # enterprise, government
    sector = db.Column(db.String(100))  # public_safety, health, finance, education, etc.
    fiscal_year = db.Column(db.String(10))  # e.g., "FY2024"

    # Portfolio metrics (calculated)
    total_applications = db.Column(db.Integer, default=0)
    total_cost = db.Column(db.Float, default=0)
    average_score = db.Column(db.Float, default=0)

    # TIME distribution
    invest_count = db.Column(db.Integer, default=0)
    tolerate_count = db.Column(db.Integer, default=0)
    migrate_count = db.Column(db.Integer, default=0)
    eliminate_count = db.Column(db.Integer, default=0)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    applications = db.relationship('Application', backref='portfolio', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'organization': self.organization,
            'description': self.description,
            'agency_id': self.agency_id,
            'portfolio_type': self.portfolio_type,
            'sector': self.sector,
            'fiscal_year': self.fiscal_year,
            'total_applications': self.total_applications,
            'total_cost': self.total_cost,
            'average_score': self.average_score,
            'time_distribution': {
                'Invest': self.invest_count,
                'Tolerate': self.tolerate_count,
                'Migrate': self.migrate_count,
                'Eliminate': self.eliminate_count
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def update_metrics(self):
        """Recalculate portfolio metrics from applications."""
        apps = self.applications.all()
        self.total_applications = len(apps)

        if apps:
            self.total_cost = sum(app.cost or 0 for app in apps)
            scores = [app.composite_score for app in apps if app.composite_score]
            self.average_score = round(sum(scores) / len(scores), 2) if scores else 0

            # TIME distribution
            self.invest_count = sum(1 for app in apps if app.time_category == 'Invest')
            self.tolerate_count = sum(1 for app in apps if app.time_category == 'Tolerate')
            self.migrate_count = sum(1 for app in apps if app.time_category == 'Migrate')
            self.eliminate_count = sum(1 for app in apps if app.time_category == 'Eliminate')


class Application(db.Model):
    """Individual application in a portfolio."""
    __tablename__ = 'applications'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolios.id'), nullable=False)

    # Basic info
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    department = db.Column(db.String(100))
    vendor = db.Column(db.String(200))
    description = db.Column(db.Text)

    # 7 Scoring Criteria (0-10 scale) - Enterprise
    business_value = db.Column(db.Float, default=5)
    tech_health = db.Column(db.Float, default=5)
    cost = db.Column(db.Float, default=0)  # Annual cost in dollars
    usage = db.Column(db.Float, default=0)  # Usage metric
    security = db.Column(db.Float, default=5)
    strategic_fit = db.Column(db.Float, default=5)
    redundancy = db.Column(db.Integer, default=0)  # 0=unique, 1=redundant

    # Government Edition Scoring Dimensions (0-10 scale)
    citizen_impact = db.Column(db.Float)  # Impact on citizen services
    mission_criticality = db.Column(db.Float)  # Critical to agency mission
    interoperability_score = db.Column(db.Float)  # Cross-agency data sharing
    data_sensitivity = db.Column(db.String(50))  # public, sensitive, confidential, restricted
    compliance_requirements = db.Column(JSON)  # ["CJIS", "HIPAA"] etc.

    # Government-specific metadata
    system_of_record = db.Column(db.Boolean, default=False)  # Is this THE authoritative system?
    public_facing = db.Column(db.Boolean, default=False)  # Accessible by citizens?
    shared_service = db.Column(db.Boolean, default=False)  # Used by multiple agencies?
    grant_funded = db.Column(db.Boolean, default=False)  # Funded by grants?
    grant_expiration = db.Column(db.Date)  # When grant funding ends

    # Calculated Results
    composite_score = db.Column(db.Float)
    retention_score = db.Column(db.Float)
    time_category = db.Column(db.String(20))  # Invest, Tolerate, Migrate, Eliminate
    time_rationale = db.Column(db.Text)
    time_bv_score = db.Column(db.Float)  # Business value dimension score
    time_tq_score = db.Column(db.Float)  # Technical quality dimension score
    recommendation = db.Column(db.String(50))  # Action recommendation
    recommendation_rationale = db.Column(db.Text)

    # Government-specific calculated scores
    gov_composite_score = db.Column(db.Float)  # Government-weighted composite

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contracts = db.relationship('Contract', backref='application', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'name': self.name,
            'category': self.category,
            'department': self.department,
            'vendor': self.vendor,
            'description': self.description,
            # Enterprise scoring
            'business_value': self.business_value,
            'tech_health': self.tech_health,
            'cost': self.cost,
            'usage': self.usage,
            'security': self.security,
            'strategic_fit': self.strategic_fit,
            'redundancy': self.redundancy,
            # Government scoring
            'citizen_impact': self.citizen_impact,
            'mission_criticality': self.mission_criticality,
            'interoperability_score': self.interoperability_score,
            'data_sensitivity': self.data_sensitivity,
            'compliance_requirements': self.compliance_requirements,
            # Government metadata
            'system_of_record': self.system_of_record,
            'public_facing': self.public_facing,
            'shared_service': self.shared_service,
            'grant_funded': self.grant_funded,
            'grant_expiration': self.grant_expiration.isoformat() if self.grant_expiration else None,
            # Calculated scores
            'composite_score': self.composite_score,
            'retention_score': self.retention_score,
            'time_category': self.time_category,
            'time_rationale': self.time_rationale,
            'time_bv_score': self.time_bv_score,
            'time_tq_score': self.time_tq_score,
            'recommendation': self.recommendation,
            'recommendation_rationale': self.recommendation_rationale,
            'gov_composite_score': self.gov_composite_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def to_scoring_dict(self):
        """Convert to dict format expected by scoring engine."""
        return {
            'name': self.name,
            'business_value': self.business_value,
            'tech_health': self.tech_health,
            'cost': self.cost,
            'usage': self.usage,
            'security': self.security,
            'strategic_fit': self.strategic_fit,
            'redundancy': self.redundancy
        }

    def apply_scoring_results(self, results: dict):
        """Apply results from RationalizationEngine to this model."""
        self.composite_score = results.get('composite_score')
        self.retention_score = results.get('retention_score')
        self.time_category = results.get('time_category')
        self.time_rationale = results.get('time_rationale')
        self.time_bv_score = results.get('time_bv_score')
        self.time_tq_score = results.get('time_tq_score')
        self.recommendation = results.get('recommendation')
        self.recommendation_rationale = results.get('recommendation_rationale')


class ComplianceResult(db.Model):
    """Compliance assessment result for an application."""
    __tablename__ = 'compliance_results'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    application_id = db.Column(db.String(36), db.ForeignKey('applications.id'), nullable=False)
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolios.id'))

    # Framework assessed
    framework = db.Column(db.String(50), nullable=False)  # SOX, PCI-DSS, HIPAA, GDPR

    # Results
    compliance_percentage = db.Column(db.Float)
    compliance_level = db.Column(db.String(50))  # Fully Compliant, Substantially Compliant, etc.
    risk_level = db.Column(db.String(20))  # Low, Medium, High, Critical

    # Counts
    total_requirements = db.Column(db.Integer)
    compliant_count = db.Column(db.Integer)
    partial_count = db.Column(db.Integer)
    non_compliant_count = db.Column(db.Integer)
    critical_gaps_count = db.Column(db.Integer)

    # Detailed results stored as JSON
    requirement_results = db.Column(JSON)
    gaps = db.Column(JSON)
    critical_gaps = db.Column(JSON)

    # Timestamps
    assessed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'application_id': self.application_id,
            'portfolio_id': self.portfolio_id,
            'framework': self.framework,
            'compliance_percentage': self.compliance_percentage,
            'compliance_level': self.compliance_level,
            'risk_level': self.risk_level,
            'total_requirements': self.total_requirements,
            'compliant_count': self.compliant_count,
            'partial_count': self.partial_count,
            'non_compliant_count': self.non_compliant_count,
            'critical_gaps_count': self.critical_gaps_count,
            'requirement_results': self.requirement_results,
            'gaps': self.gaps,
            'critical_gaps': self.critical_gaps,
            'assessed_at': self.assessed_at.isoformat() if self.assessed_at else None
        }


class CostAnalysis(db.Model):
    """Cost analysis result for a portfolio."""
    __tablename__ = 'cost_analyses'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolios.id'), nullable=False)

    # Summary metrics
    total_portfolio_cost = db.Column(db.Float)
    hidden_costs_total = db.Column(db.Float)
    potential_savings = db.Column(db.Float)
    savings_percentage = db.Column(db.Float)

    # Detailed breakdowns stored as JSON
    component_breakdown = db.Column(JSON)  # TCO components
    department_allocation = db.Column(JSON)
    hidden_cost_categories = db.Column(JSON)
    quick_wins = db.Column(JSON)
    top_opportunities = db.Column(JSON)

    # Timestamps
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'total_portfolio_cost': self.total_portfolio_cost,
            'hidden_costs_total': self.hidden_costs_total,
            'potential_savings': self.potential_savings,
            'savings_percentage': self.savings_percentage,
            'component_breakdown': self.component_breakdown,
            'department_allocation': self.department_allocation,
            'hidden_cost_categories': self.hidden_cost_categories,
            'quick_wins': self.quick_wins,
            'top_opportunities': self.top_opportunities,
            'analyzed_at': self.analyzed_at.isoformat() if self.analyzed_at else None
        }


class ChatSession(db.Model):
    """Chat session for AI consultant conversations."""
    __tablename__ = 'chat_sessions'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolios.id'))

    organization_name = db.Column(db.String(200))
    mode = db.Column(db.String(50), default='general')

    # Conversation history stored as JSON
    conversation_history = db.Column(JSON, default=list)

    # Session state
    is_active = db.Column(db.Boolean, default=True)
    message_count = db.Column(db.Integer, default=0)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'organization_name': self.organization_name,
            'mode': self.mode,
            'is_active': self.is_active,
            'message_count': self.message_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }

    def add_message(self, role: str, content: str):
        """Add a message to conversation history."""
        if self.conversation_history is None:
            self.conversation_history = []

        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat()
        })
        self.message_count = len(self.conversation_history)
        self.last_activity = datetime.utcnow()


# ============================================================
# TIER 2 FEATURES: DEPENDENCIES, INTEGRATIONS, VENDORS
# ============================================================


class ApplicationDependency(db.Model):
    """
    Dependency relationship between applications.

    Tracks which applications depend on which other applications,
    enabling circular dependency detection and blast radius analysis.
    """
    __tablename__ = 'application_dependencies'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolios.id'), nullable=False)

    # The application that HAS the dependency
    source_app_id = db.Column(db.String(36), db.ForeignKey('applications.id'), nullable=False)

    # The application being depended ON
    target_app_id = db.Column(db.String(36), db.ForeignKey('applications.id'), nullable=False)

    # Dependency details
    dependency_type = db.Column(db.String(50))  # data, api, authentication, reporting, infrastructure
    strength = db.Column(db.String(20), default='medium')  # critical, strong, medium, weak
    description = db.Column(db.Text)

    # Data flow direction
    data_direction = db.Column(db.String(20), default='bidirectional')  # inbound, outbound, bidirectional
    data_volume = db.Column(db.String(20))  # high, medium, low

    # Risk factors
    is_critical_path = db.Column(db.Boolean, default=False)
    failure_impact = db.Column(db.String(100))  # What happens if this dependency breaks?

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    source_app = db.relationship('Application', foreign_keys=[source_app_id], backref='outgoing_dependencies')
    target_app = db.relationship('Application', foreign_keys=[target_app_id], backref='incoming_dependencies')

    def to_dict(self):
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'source_app_id': self.source_app_id,
            'target_app_id': self.target_app_id,
            'source_app_name': self.source_app.name if self.source_app else None,
            'target_app_name': self.target_app.name if self.target_app else None,
            'dependency_type': self.dependency_type,
            'strength': self.strength,
            'description': self.description,
            'data_direction': self.data_direction,
            'data_volume': self.data_volume,
            'is_critical_path': self.is_critical_path,
            'failure_impact': self.failure_impact,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ApplicationIntegration(db.Model):
    """
    Integration details for an application.

    Tracks how applications connect to each other and external systems,
    with health metrics for integration assessment.
    """
    __tablename__ = 'application_integrations'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolios.id'), nullable=False)

    # Source and target
    source_app_id = db.Column(db.String(36), db.ForeignKey('applications.id'), nullable=False)
    target_app_id = db.Column(db.String(36), db.ForeignKey('applications.id'), nullable=True)  # Null for external
    external_system = db.Column(db.String(200))  # Name of external system if target_app_id is null

    # Integration type
    integration_type = db.Column(db.String(50))  # api, database, file_transfer, message_queue, event_stream, manual
    protocol = db.Column(db.String(50))  # REST, SOAP, GraphQL, SFTP, Kafka, etc.

    # Authentication
    auth_method = db.Column(db.String(50))  # oauth2, api_key, certificate, basic, none

    # Data classification
    data_sensitivity = db.Column(db.String(20))  # public, internal, confidential, restricted, pii
    data_types = db.Column(JSON)  # List of data types exchanged

    # Health metrics
    avg_latency_ms = db.Column(db.Float)
    error_rate_percent = db.Column(db.Float)
    uptime_percent = db.Column(db.Float, default=99.0)
    daily_transactions = db.Column(db.Integer)

    # Health score (calculated)
    health_score = db.Column(db.Float)  # 0-100
    health_status = db.Column(db.String(20))  # healthy, degraded, unhealthy, critical

    # Operational details
    sync_frequency = db.Column(db.String(50))  # real-time, hourly, daily, weekly, manual
    last_sync = db.Column(db.DateTime)
    has_retry_mechanism = db.Column(db.Boolean, default=False)
    has_error_handling = db.Column(db.Boolean, default=False)
    has_monitoring = db.Column(db.Boolean, default=False)

    # Documentation
    documentation_url = db.Column(db.String(500))
    owner = db.Column(db.String(200))
    notes = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    source_app = db.relationship('Application', foreign_keys=[source_app_id], backref='integrations_as_source')
    target_app = db.relationship('Application', foreign_keys=[target_app_id], backref='integrations_as_target')

    def to_dict(self):
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'source_app_id': self.source_app_id,
            'target_app_id': self.target_app_id,
            'source_app_name': self.source_app.name if self.source_app else None,
            'target_app_name': self.target_app.name if self.target_app else None,
            'external_system': self.external_system,
            'integration_type': self.integration_type,
            'protocol': self.protocol,
            'auth_method': self.auth_method,
            'data_sensitivity': self.data_sensitivity,
            'data_types': self.data_types,
            'avg_latency_ms': self.avg_latency_ms,
            'error_rate_percent': self.error_rate_percent,
            'uptime_percent': self.uptime_percent,
            'daily_transactions': self.daily_transactions,
            'health_score': self.health_score,
            'health_status': self.health_status,
            'sync_frequency': self.sync_frequency,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'has_retry_mechanism': self.has_retry_mechanism,
            'has_error_handling': self.has_error_handling,
            'has_monitoring': self.has_monitoring,
            'documentation_url': self.documentation_url,
            'owner': self.owner,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def calculate_health_score(self):
        """Calculate health score based on metrics."""
        score = 100

        # Latency impact (0-25 points)
        if self.avg_latency_ms:
            if self.avg_latency_ms > 5000:
                score -= 25
            elif self.avg_latency_ms > 2000:
                score -= 15
            elif self.avg_latency_ms > 1000:
                score -= 10
            elif self.avg_latency_ms > 500:
                score -= 5

        # Error rate impact (0-30 points)
        if self.error_rate_percent:
            if self.error_rate_percent > 10:
                score -= 30
            elif self.error_rate_percent > 5:
                score -= 20
            elif self.error_rate_percent > 1:
                score -= 10
            elif self.error_rate_percent > 0.1:
                score -= 5

        # Uptime impact (0-25 points)
        if self.uptime_percent:
            if self.uptime_percent < 95:
                score -= 25
            elif self.uptime_percent < 99:
                score -= 15
            elif self.uptime_percent < 99.9:
                score -= 5

        # Operational maturity bonus (0-20 points deduction if missing)
        if not self.has_retry_mechanism:
            score -= 7
        if not self.has_error_handling:
            score -= 7
        if not self.has_monitoring:
            score -= 6

        self.health_score = max(0, min(100, score))

        # Determine status
        if self.health_score >= 90:
            self.health_status = 'healthy'
        elif self.health_score >= 70:
            self.health_status = 'degraded'
        elif self.health_score >= 50:
            self.health_status = 'unhealthy'
        else:
            self.health_status = 'critical'

        return self.health_score


class Vendor(db.Model):
    """
    Vendor profile for vendor risk management.

    Tracks vendor details, contract information, compliance status,
    and security posture for risk assessment.
    """
    __tablename__ = 'vendors'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolios.id'))

    # Basic info
    name = db.Column(db.String(200), nullable=False)
    tier = db.Column(db.String(20))  # strategic, tactical, commodity, emerging
    status = db.Column(db.String(20), default='active')  # active, probation, sunset, blocked, under_review

    # Financial indicators
    annual_revenue = db.Column(db.Float)
    years_in_business = db.Column(db.Integer)
    financial_rating = db.Column(db.String(10))  # AAA, AA, A, BBB, BB, B, etc.
    publicly_traded = db.Column(db.Boolean, default=False)
    stock_symbol = db.Column(db.String(20))

    # Contract details
    contract_start = db.Column(db.Date)
    contract_end = db.Column(db.Date)
    annual_spend = db.Column(db.Float, default=0.0)
    payment_terms = db.Column(db.String(50), default='NET30')
    contract_type = db.Column(db.String(50))  # subscription, perpetual, metered, custom
    auto_renewal = db.Column(db.Boolean, default=False)

    # Security & Compliance
    security_score = db.Column(db.Float)  # 0-100
    compliances = db.Column(JSON)  # ["SOC2", "ISO27001", "HIPAA", etc.]
    last_security_audit = db.Column(db.Date)
    has_incident_history = db.Column(db.Boolean, default=False)
    incident_details = db.Column(db.Text)

    # Business continuity
    has_dr_plan = db.Column(db.Boolean, default=False)
    sla_uptime = db.Column(db.Float, default=99.0)
    geographic_presence = db.Column(JSON)  # ["North America", "Europe", etc.]
    data_center_locations = db.Column(JSON)

    # Contact information
    primary_contact = db.Column(db.String(200))
    primary_email = db.Column(db.String(200))
    primary_phone = db.Column(db.String(50))
    account_manager = db.Column(db.String(200))
    support_tier = db.Column(db.String(50))  # basic, standard, premium, enterprise

    # Website and documentation
    website = db.Column(db.String(500))
    documentation_url = db.Column(db.String(500))

    # Notes
    notes = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    applications = db.relationship('Application',
                                   primaryjoin="Vendor.name == foreign(Application.vendor)",
                                   backref='vendor_profile',
                                   viewonly=True)

    def to_dict(self):
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'name': self.name,
            'tier': self.tier,
            'status': self.status,
            'annual_revenue': self.annual_revenue,
            'years_in_business': self.years_in_business,
            'financial_rating': self.financial_rating,
            'publicly_traded': self.publicly_traded,
            'stock_symbol': self.stock_symbol,
            'contract_start': self.contract_start.isoformat() if self.contract_start else None,
            'contract_end': self.contract_end.isoformat() if self.contract_end else None,
            'annual_spend': self.annual_spend,
            'payment_terms': self.payment_terms,
            'contract_type': self.contract_type,
            'auto_renewal': self.auto_renewal,
            'security_score': self.security_score,
            'compliances': self.compliances,
            'last_security_audit': self.last_security_audit.isoformat() if self.last_security_audit else None,
            'has_incident_history': self.has_incident_history,
            'incident_details': self.incident_details,
            'has_dr_plan': self.has_dr_plan,
            'sla_uptime': self.sla_uptime,
            'geographic_presence': self.geographic_presence,
            'data_center_locations': self.data_center_locations,
            'primary_contact': self.primary_contact,
            'primary_email': self.primary_email,
            'primary_phone': self.primary_phone,
            'account_manager': self.account_manager,
            'support_tier': self.support_tier,
            'website': self.website,
            'documentation_url': self.documentation_url,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def days_until_contract_end(self):
        """Calculate days until contract ends."""
        if not self.contract_end:
            return None
        from datetime import date
        return (self.contract_end - date.today()).days


class VendorAssessment(db.Model):
    """
    Vendor risk assessment result.

    Stores the results of vendor risk assessments including
    component scores, risk factors, and recommendations.
    """
    __tablename__ = 'vendor_assessments'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    vendor_id = db.Column(db.String(36), db.ForeignKey('vendors.id'), nullable=False)
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolios.id'))

    # Overall assessment
    overall_risk_level = db.Column(db.String(20))  # critical, high, medium, low, minimal
    overall_risk_score = db.Column(db.Float)  # 0-100 (higher = more risk)

    # Component scores (0-100, higher = more risk)
    financial_risk_score = db.Column(db.Float)
    security_risk_score = db.Column(db.Float)
    operational_risk_score = db.Column(db.Float)
    compliance_risk_score = db.Column(db.Float)
    strategic_risk_score = db.Column(db.Float)
    concentration_risk_score = db.Column(db.Float)

    # Context used for assessment
    industry = db.Column(db.String(100))
    total_it_spend = db.Column(db.Float)

    # Detailed results stored as JSON
    risk_factors = db.Column(JSON)  # List of identified risk factors
    recommendations = db.Column(JSON)  # List of recommendations

    # Timestamps
    assessed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    vendor = db.relationship('Vendor', backref='assessments')

    def to_dict(self):
        return {
            'id': self.id,
            'vendor_id': self.vendor_id,
            'vendor_name': self.vendor.name if self.vendor else None,
            'portfolio_id': self.portfolio_id,
            'overall_risk_level': self.overall_risk_level,
            'overall_risk_score': self.overall_risk_score,
            'financial_risk_score': self.financial_risk_score,
            'security_risk_score': self.security_risk_score,
            'operational_risk_score': self.operational_risk_score,
            'compliance_risk_score': self.compliance_risk_score,
            'strategic_risk_score': self.strategic_risk_score,
            'concentration_risk_score': self.concentration_risk_score,
            'industry': self.industry,
            'total_it_spend': self.total_it_spend,
            'risk_factors': self.risk_factors,
            'recommendations': self.recommendations,
            'assessed_at': self.assessed_at.isoformat() if self.assessed_at else None
        }


class DependencyAnalysis(db.Model):
    """
    Dependency analysis result for a portfolio.

    Stores the results of dependency mapping analysis including
    circular dependencies, critical paths, and blast radius data.
    """
    __tablename__ = 'dependency_analyses'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolios.id'), nullable=False)

    # Summary metrics
    total_applications = db.Column(db.Integer)
    total_dependencies = db.Column(db.Integer)
    circular_dependency_count = db.Column(db.Integer)
    critical_path_count = db.Column(db.Integer)

    # Detailed results stored as JSON
    circular_dependencies = db.Column(JSON)  # List of circular dependency chains
    critical_paths = db.Column(JSON)  # List of critical dependency paths
    blast_radius_data = db.Column(JSON)  # Blast radius for each application
    dependency_graph = db.Column(JSON)  # Full graph for visualization
    hub_applications = db.Column(JSON)  # Applications with most connections
    isolated_applications = db.Column(JSON)  # Applications with no dependencies

    # Risk assessment
    overall_risk_level = db.Column(db.String(20))  # low, medium, high, critical
    recommendations = db.Column(JSON)

    # Timestamps
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'total_applications': self.total_applications,
            'total_dependencies': self.total_dependencies,
            'circular_dependency_count': self.circular_dependency_count,
            'critical_path_count': self.critical_path_count,
            'circular_dependencies': self.circular_dependencies,
            'critical_paths': self.critical_paths,
            'blast_radius_data': self.blast_radius_data,
            'dependency_graph': self.dependency_graph,
            'hub_applications': self.hub_applications,
            'isolated_applications': self.isolated_applications,
            'overall_risk_level': self.overall_risk_level,
            'recommendations': self.recommendations,
            'analyzed_at': self.analyzed_at.isoformat() if self.analyzed_at else None
        }


class IntegrationAnalysis(db.Model):
    """
    Integration health analysis result for a portfolio.

    Stores the results of integration assessment including
    health scores, bottlenecks, and portfolio-wide metrics.
    """
    __tablename__ = 'integration_analyses'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolios.id'), nullable=False)

    # Summary metrics
    total_integrations = db.Column(db.Integer)
    healthy_count = db.Column(db.Integer)
    degraded_count = db.Column(db.Integer)
    unhealthy_count = db.Column(db.Integer)
    critical_count = db.Column(db.Integer)
    average_health_score = db.Column(db.Float)

    # Detailed results stored as JSON
    integration_scores = db.Column(JSON)  # Individual integration scores
    bottlenecks = db.Column(JSON)  # Identified bottlenecks
    high_risk_integrations = db.Column(JSON)  # Integrations needing attention
    data_sensitivity_breakdown = db.Column(JSON)  # By sensitivity level
    integration_type_breakdown = db.Column(JSON)  # By type (API, file, etc.)

    # Risk assessment
    overall_health = db.Column(db.String(20))  # healthy, degraded, unhealthy, critical
    recommendations = db.Column(JSON)

    # Timestamps
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'total_integrations': self.total_integrations,
            'healthy_count': self.healthy_count,
            'degraded_count': self.degraded_count,
            'unhealthy_count': self.unhealthy_count,
            'critical_count': self.critical_count,
            'average_health_score': self.average_health_score,
            'integration_scores': self.integration_scores,
            'bottlenecks': self.bottlenecks,
            'high_risk_integrations': self.high_risk_integrations,
            'data_sensitivity_breakdown': self.data_sensitivity_breakdown,
            'integration_type_breakdown': self.integration_type_breakdown,
            'overall_health': self.overall_health,
            'recommendations': self.recommendations,
            'analyzed_at': self.analyzed_at.isoformat() if self.analyzed_at else None
        }
