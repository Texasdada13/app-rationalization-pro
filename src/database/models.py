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
