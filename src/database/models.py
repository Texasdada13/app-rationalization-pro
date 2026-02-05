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
