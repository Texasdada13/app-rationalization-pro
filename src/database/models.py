"""
Database Models for App Rationalization Pro

SQLAlchemy models for applications, portfolios, and chat sessions.
"""

import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON

db = SQLAlchemy()


def generate_uuid():
    return str(uuid.uuid4())


class Portfolio(db.Model):
    """Portfolio of applications for an organization."""
    __tablename__ = 'portfolios'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(200), nullable=False)
    organization = db.Column(db.String(200))
    description = db.Column(db.Text)

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

    # 7 Scoring Criteria (0-10 scale)
    business_value = db.Column(db.Float, default=5)
    tech_health = db.Column(db.Float, default=5)
    cost = db.Column(db.Float, default=0)  # Annual cost in dollars
    usage = db.Column(db.Float, default=0)  # Usage metric
    security = db.Column(db.Float, default=5)
    strategic_fit = db.Column(db.Float, default=5)
    redundancy = db.Column(db.Integer, default=0)  # 0=unique, 1=redundant

    # Calculated Results
    composite_score = db.Column(db.Float)
    retention_score = db.Column(db.Float)
    time_category = db.Column(db.String(20))  # Invest, Tolerate, Migrate, Eliminate
    time_rationale = db.Column(db.Text)
    time_bv_score = db.Column(db.Float)  # Business value dimension score
    time_tq_score = db.Column(db.Float)  # Technical quality dimension score
    recommendation = db.Column(db.String(50))  # Action recommendation
    recommendation_rationale = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'name': self.name,
            'category': self.category,
            'department': self.department,
            'vendor': self.vendor,
            'description': self.description,
            'business_value': self.business_value,
            'tech_health': self.tech_health,
            'cost': self.cost,
            'usage': self.usage,
            'security': self.security,
            'strategic_fit': self.strategic_fit,
            'redundancy': self.redundancy,
            'composite_score': self.composite_score,
            'retention_score': self.retention_score,
            'time_category': self.time_category,
            'time_rationale': self.time_rationale,
            'time_bv_score': self.time_bv_score,
            'time_tq_score': self.time_tq_score,
            'recommendation': self.recommendation,
            'recommendation_rationale': self.recommendation_rationale,
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
