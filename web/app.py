"""
App Rationalization Pro - Flask Application

AI-powered application portfolio rationalization tool.
"""

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, Response

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.models import db, Portfolio, Application, ChatSession, ComplianceResult, CostAnalysis
from ai_core.chat_engine import AIChatEngine, ConversationMode, get_chat_engine
from rationalization import RationalizationEngine, CostModeler, ComplianceEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(basedir, "..", "data", "app.db")}')

# Fix for Render/Heroku PostgreSQL URLs
if db_path.startswith('postgres://'):
    db_path = db_path.replace('postgres://', 'postgresql://', 1)

# Ensure data directory exists for SQLite
if db_path.startswith('sqlite'):
    data_dir = os.path.join(basedir, '..', 'data')
    os.makedirs(data_dir, exist_ok=True)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Initialize engines
rationalization_engine = RationalizationEngine()


# =============================================================================
# TEMPLATE CONTEXT
# =============================================================================

@app.context_processor
def inject_globals():
    """Inject global variables into all templates."""
    return {
        'app_name': 'App Rationalization Pro',
        'company_name': 'Patriot Tech Systems',
        'current_year': datetime.now().year
    }


# =============================================================================
# MAIN PAGES
# =============================================================================

@app.route('/')
def index():
    """Landing page."""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Main dashboard showing portfolio overview."""
    portfolios = Portfolio.query.order_by(Portfolio.updated_at.desc()).all()
    return render_template('dashboard.html', portfolios=portfolios)


@app.route('/chat')
def chat_page():
    """AI Consultant chat interface."""
    portfolio_id = request.args.get('portfolio_id')
    portfolio = None
    if portfolio_id:
        portfolio = Portfolio.query.get(portfolio_id)
    return render_template('chat.html', portfolio=portfolio)


@app.route('/portfolio/<portfolio_id>')
def portfolio_detail(portfolio_id):
    """Portfolio detail view with all applications."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.order_by(Application.composite_score.desc()).all()
    return render_template('portfolio.html', portfolio=portfolio, applications=applications)


@app.route('/results/<portfolio_id>')
def results_page(portfolio_id):
    """Rationalization results view."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()
    return render_template('results.html', portfolio=portfolio, applications=applications)


# =============================================================================
# PORTFOLIO API
# =============================================================================

@app.route('/api/portfolios', methods=['GET'])
def get_portfolios():
    """Get all portfolios."""
    portfolios = Portfolio.query.order_by(Portfolio.updated_at.desc()).all()
    return jsonify([p.to_dict() for p in portfolios])


@app.route('/api/portfolios', methods=['POST'])
def create_portfolio():
    """Create a new portfolio."""
    data = request.get_json()

    portfolio = Portfolio(
        name=data.get('name', 'New Portfolio'),
        organization=data.get('organization', ''),
        description=data.get('description', '')
    )

    db.session.add(portfolio)
    db.session.commit()

    return jsonify(portfolio.to_dict()), 201


@app.route('/api/portfolios/<portfolio_id>', methods=['GET'])
def get_portfolio(portfolio_id):
    """Get a specific portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    return jsonify(portfolio.to_dict())


@app.route('/api/portfolios/<portfolio_id>', methods=['DELETE'])
def delete_portfolio(portfolio_id):
    """Delete a portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    db.session.delete(portfolio)
    db.session.commit()
    return jsonify({'success': True})


# =============================================================================
# APPLICATION API
# =============================================================================

@app.route('/api/portfolios/<portfolio_id>/applications', methods=['GET'])
def get_applications(portfolio_id):
    """Get all applications in a portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()
    return jsonify([a.to_dict() for a in applications])


@app.route('/api/portfolios/<portfolio_id>/applications', methods=['POST'])
def create_application(portfolio_id):
    """Create a new application in a portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    data = request.get_json()

    app_data = Application(
        portfolio_id=portfolio_id,
        name=data.get('name', 'New Application'),
        category=data.get('category'),
        department=data.get('department'),
        vendor=data.get('vendor'),
        description=data.get('description'),
        business_value=float(data.get('business_value', 5)),
        tech_health=float(data.get('tech_health', 5)),
        cost=float(data.get('cost', 0)),
        usage=float(data.get('usage', 0)),
        security=float(data.get('security', 5)),
        strategic_fit=float(data.get('strategic_fit', 5)),
        redundancy=int(data.get('redundancy', 0))
    )

    # Process through rationalization engine
    results = rationalization_engine.process_single_application(app_data.to_scoring_dict())
    app_data.apply_scoring_results(results)

    db.session.add(app_data)
    db.session.commit()

    # Update portfolio metrics
    portfolio.update_metrics()
    db.session.commit()

    return jsonify(app_data.to_dict()), 201


@app.route('/api/applications/<app_id>', methods=['GET'])
def get_application(app_id):
    """Get a specific application."""
    application = Application.query.get_or_404(app_id)
    return jsonify(application.to_dict())


@app.route('/api/applications/<app_id>', methods=['PUT'])
def update_application(app_id):
    """Update an application."""
    application = Application.query.get_or_404(app_id)
    data = request.get_json()

    # Update fields
    for field in ['name', 'category', 'department', 'vendor', 'description']:
        if field in data:
            setattr(application, field, data[field])

    # Update scoring criteria
    for field in ['business_value', 'tech_health', 'cost', 'usage', 'security', 'strategic_fit']:
        if field in data:
            setattr(application, field, float(data[field]))

    if 'redundancy' in data:
        application.redundancy = int(data['redundancy'])

    # Recalculate scores
    results = rationalization_engine.process_single_application(application.to_scoring_dict())
    application.apply_scoring_results(results)

    db.session.commit()

    # Update portfolio metrics
    application.portfolio.update_metrics()
    db.session.commit()

    return jsonify(application.to_dict())


@app.route('/api/applications/<app_id>', methods=['DELETE'])
def delete_application(app_id):
    """Delete an application."""
    application = Application.query.get_or_404(app_id)
    portfolio = application.portfolio

    db.session.delete(application)
    db.session.commit()

    # Update portfolio metrics
    portfolio.update_metrics()
    db.session.commit()

    return jsonify({'success': True})


# =============================================================================
# RATIONALIZATION API
# =============================================================================

@app.route('/api/portfolios/<portfolio_id>/analyze', methods=['POST'])
def analyze_portfolio(portfolio_id):
    """Run rationalization analysis on all applications in a portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()

    if not applications:
        return jsonify({'error': 'No applications to analyze'}), 400

    # Reset engine counters
    rationalization_engine.reset()

    # Process all applications
    app_dicts = [app.to_scoring_dict() for app in applications]
    results = rationalization_engine.process_portfolio(app_dicts)

    # Apply results back to database
    for app, result in zip(applications, results['applications']):
        app.apply_scoring_results(result)

    db.session.commit()

    # Update portfolio metrics
    portfolio.update_metrics()
    db.session.commit()

    return jsonify({
        'success': True,
        'summary': results['summary'],
        'portfolio': portfolio.to_dict()
    })


# =============================================================================
# COST MODELER API
# =============================================================================

@app.route('/api/portfolios/<portfolio_id>/cost-analysis', methods=['GET'])
def get_cost_analysis(portfolio_id):
    """Get the latest cost analysis for a portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)

    # Get latest analysis
    analysis = CostAnalysis.query.filter_by(portfolio_id=portfolio_id).order_by(
        CostAnalysis.analyzed_at.desc()
    ).first()

    if analysis:
        return jsonify(analysis.to_dict())
    return jsonify({'error': 'No cost analysis found. Run analysis first.'}), 404


@app.route('/api/portfolios/<portfolio_id>/cost-analysis', methods=['POST'])
def run_cost_analysis(portfolio_id):
    """Run cost analysis on a portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()

    if not applications:
        return jsonify({'error': 'No applications to analyze'}), 400

    # Convert to list of dicts for cost modeler
    app_dicts = [app.to_dict() for app in applications]

    # Run cost analysis
    cost_modeler = CostModeler(app_dicts)
    tco_summary = cost_modeler.calculate_tco_breakdown()
    cost_modeler.identify_hidden_costs()
    optimization = cost_modeler.get_cost_optimization_summary()

    # Save to database
    analysis = CostAnalysis(
        portfolio_id=portfolio_id,
        total_portfolio_cost=optimization['current_portfolio_cost'],
        hidden_costs_total=optimization['hidden_costs_total'],
        potential_savings=optimization['potential_savings'],
        savings_percentage=optimization['savings_percentage'],
        component_breakdown=tco_summary['component_breakdown'],
        department_allocation=optimization['department_allocation'],
        hidden_cost_categories=optimization['hidden_cost_categories'],
        quick_wins=optimization['quick_wins'],
        top_opportunities=optimization['top_opportunities']
    )

    db.session.add(analysis)
    db.session.commit()

    return jsonify({
        'success': True,
        'analysis': analysis.to_dict(),
        'tco_summary': tco_summary
    })


@app.route('/costs/<portfolio_id>')
def costs_page(portfolio_id):
    """Cost analysis page."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()

    # Get latest analysis if exists
    analysis = CostAnalysis.query.filter_by(portfolio_id=portfolio_id).order_by(
        CostAnalysis.analyzed_at.desc()
    ).first()

    return render_template('costs.html',
                          portfolio=portfolio,
                          applications=applications,
                          analysis=analysis)


# =============================================================================
# COMPLIANCE ENGINE API
# =============================================================================

@app.route('/api/compliance/frameworks', methods=['GET'])
def get_frameworks():
    """Get list of available compliance frameworks."""
    engine = ComplianceEngine()
    return jsonify(engine.list_frameworks())


@app.route('/api/compliance/frameworks/<framework_name>', methods=['GET'])
def get_framework_details(framework_name):
    """Get details of a specific compliance framework."""
    engine = ComplianceEngine()
    summary = engine.get_framework_summary(framework_name)
    if 'error' in summary:
        return jsonify(summary), 404
    return jsonify(summary)


@app.route('/api/portfolios/<portfolio_id>/compliance/<framework_name>', methods=['GET'])
def get_compliance_results(portfolio_id, framework_name):
    """Get compliance assessment results for a portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)

    # Get all compliance results for this framework
    results = ComplianceResult.query.filter_by(
        portfolio_id=portfolio_id,
        framework=framework_name
    ).all()

    if not results:
        return jsonify({'error': 'No compliance assessment found. Run assessment first.'}), 404

    return jsonify({
        'framework': framework_name,
        'portfolio_id': portfolio_id,
        'assessments': [r.to_dict() for r in results]
    })


@app.route('/api/portfolios/<portfolio_id>/compliance/<framework_name>', methods=['POST'])
def run_compliance_assessment(portfolio_id, framework_name):
    """Run compliance assessment on a portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()

    if not applications:
        return jsonify({'error': 'No applications to assess'}), 400

    # Convert to list of dicts
    app_dicts = [app.to_dict() for app in applications]

    # Run compliance assessment
    engine = ComplianceEngine()
    results = engine.batch_assess(app_dicts, framework_name)

    if 'error' in results:
        return jsonify(results), 400

    # Clear old results for this framework
    ComplianceResult.query.filter_by(
        portfolio_id=portfolio_id,
        framework=framework_name
    ).delete()

    # Save individual application results
    for assessment in results['application_assessments']:
        result = ComplianceResult(
            application_id=assessment.get('application_id'),
            portfolio_id=portfolio_id,
            framework=framework_name,
            compliance_percentage=assessment['compliance_percentage'],
            compliance_level=assessment['compliance_level'],
            risk_level=assessment['risk_level'],
            total_requirements=assessment['total_requirements'],
            compliant_count=assessment['compliant_count'],
            partial_count=assessment['partial_count'],
            non_compliant_count=assessment['non_compliant_count'],
            critical_gaps_count=assessment['critical_gaps_count'],
            requirement_results=assessment['requirement_results'],
            gaps=assessment['gaps'],
            critical_gaps=assessment['critical_gaps']
        )
        db.session.add(result)

    db.session.commit()

    return jsonify({
        'success': True,
        'framework': framework_name,
        'portfolio_summary': results['portfolio_summary'],
        'risk_distribution': results['risk_distribution'],
        'remediation_priorities': results['remediation_priorities']
    })


@app.route('/compliance/<portfolio_id>')
def compliance_page(portfolio_id):
    """Compliance assessment page."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()

    # Get all compliance results
    engine = ComplianceEngine()
    frameworks = engine.list_frameworks()

    compliance_data = {}
    for fw in frameworks:
        fw_name = fw['name']
        results = ComplianceResult.query.filter_by(
            portfolio_id=portfolio_id,
            framework=fw_name
        ).all()
        if results:
            compliance_data[fw_name] = {
                'assessments': [r.to_dict() for r in results],
                'avg_compliance': sum(r.compliance_percentage for r in results) / len(results) if results else 0
            }

    return render_template('compliance.html',
                          portfolio=portfolio,
                          applications=applications,
                          frameworks=frameworks,
                          compliance_data=compliance_data)


# =============================================================================
# AI CHAT API
# =============================================================================

@app.route('/api/chat/start', methods=['POST'])
def start_chat():
    """Start a new chat session."""
    try:
        data = request.get_json() or {}
        organization = data.get('organization', 'Demo Organization')
        portfolio_id = data.get('portfolio_id')

        # Get portfolio data for context
        portfolio_data = None
        if portfolio_id:
            portfolio = Portfolio.query.get(portfolio_id)
            if portfolio:
                applications = portfolio.applications.all()
                portfolio_data = {
                    'total_applications': portfolio.total_applications,
                    'total_cost': portfolio.total_cost,
                    'average_score': portfolio.average_score,
                    'time_distribution': {
                        'INVEST': portfolio.invest_count,
                        'TOLERATE': portfolio.tolerate_count,
                        'MIGRATE': portfolio.migrate_count,
                        'ELIMINATE': portfolio.eliminate_count
                    },
                    'applications': [app.to_dict() for app in applications[:20]]
                }

        # Create chat session
        chat_engine = get_chat_engine()
        chat_session = chat_engine.create_session(
            organization_name=organization,
            portfolio_data=portfolio_data
        )

        # Store session ID
        session['chat_session_id'] = chat_session.session_id

        # Save to database
        db_session = ChatSession(
            id=chat_session.session_id,
            portfolio_id=portfolio_id,
            organization_name=organization
        )
        db.session.add(db_session)
        db.session.commit()

        return jsonify({
            'session_id': chat_session.session_id,
            'mode': chat_session.mode.value,
            'suggested_prompts': chat_engine.get_suggested_prompts(chat_session.session_id)
        })

    except Exception as e:
        logger.error(f"Error starting chat session: {str(e)}")
        return jsonify({'error': f'Failed to start chat session: {str(e)}'}), 500


@app.route('/api/chat/message', methods=['POST'])
def chat_message():
    """Send a chat message (non-streaming)."""
    try:
        data = request.get_json()
        message = data.get('message', '')
        chat_session_id = session.get('chat_session_id')

        if not chat_session_id:
            return jsonify({'error': 'No active chat session'}), 400

        chat_engine = get_chat_engine()
        response = chat_engine.chat(chat_session_id, message)

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error in chat_message: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """Stream a chat response using Server-Sent Events."""
    try:
        data = request.get_json()
        message = data.get('message', '')
        chat_session_id = session.get('chat_session_id')

        if not chat_session_id:
            return jsonify({'error': 'No active chat session'}), 400

        def generate():
            chat_engine = get_chat_engine()
            for chunk in chat_engine.stream_chat(chat_session_id, message):
                yield f"data: {json.dumps(chunk)}\n\n"

        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )

    except Exception as e:
        logger.error(f"Error in chat_stream: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/mode', methods=['POST'])
def change_chat_mode():
    """Change chat conversation mode."""
    data = request.get_json()
    new_mode = data.get('mode', 'general')
    chat_session_id = session.get('chat_session_id')

    if not chat_session_id:
        return jsonify({'error': 'No active chat session'}), 400

    chat_engine = get_chat_engine()
    success = chat_engine.change_mode(chat_session_id, ConversationMode(new_mode))

    return jsonify({
        'success': success,
        'mode': new_mode,
        'suggested_prompts': chat_engine.get_suggested_prompts(chat_session_id)
    })


# =============================================================================
# DEMO DATA
# =============================================================================

@app.route('/api/demo/create', methods=['POST'])
def create_demo_data():
    """Create demo portfolio with sample applications."""
    # Create demo portfolio
    portfolio = Portfolio(
        name='Enterprise IT Portfolio',
        organization='Demo Corporation',
        description='Sample portfolio for demonstration purposes'
    )
    db.session.add(portfolio)
    db.session.flush()

    # Sample applications
    sample_apps = [
        {'name': 'SAP ERP', 'category': 'ERP', 'department': 'Finance', 'business_value': 9, 'tech_health': 7, 'cost': 250000, 'usage': 800, 'security': 8, 'strategic_fit': 9, 'redundancy': 0},
        {'name': 'Legacy CRM', 'category': 'CRM', 'department': 'Sales', 'business_value': 6, 'tech_health': 3, 'cost': 80000, 'usage': 200, 'security': 4, 'strategic_fit': 4, 'redundancy': 1},
        {'name': 'Salesforce', 'category': 'CRM', 'department': 'Sales', 'business_value': 8, 'tech_health': 9, 'cost': 120000, 'usage': 450, 'security': 9, 'strategic_fit': 8, 'redundancy': 0},
        {'name': 'Custom Reporting Tool', 'category': 'BI', 'department': 'IT', 'business_value': 4, 'tech_health': 2, 'cost': 40000, 'usage': 50, 'security': 3, 'strategic_fit': 2, 'redundancy': 1},
        {'name': 'Power BI', 'category': 'BI', 'department': 'IT', 'business_value': 8, 'tech_health': 9, 'cost': 60000, 'usage': 300, 'security': 8, 'strategic_fit': 9, 'redundancy': 0},
        {'name': 'HR System', 'category': 'HR', 'department': 'HR', 'business_value': 7, 'tech_health': 5, 'cost': 90000, 'usage': 400, 'security': 6, 'strategic_fit': 6, 'redundancy': 0},
        {'name': 'Expense Tracker', 'category': 'Finance', 'department': 'Finance', 'business_value': 5, 'tech_health': 4, 'cost': 25000, 'usage': 150, 'security': 5, 'strategic_fit': 5, 'redundancy': 0},
        {'name': 'Document Management', 'category': 'Productivity', 'department': 'Operations', 'business_value': 6, 'tech_health': 6, 'cost': 35000, 'usage': 500, 'security': 7, 'strategic_fit': 7, 'redundancy': 0},
        {'name': 'Legacy Inventory', 'category': 'Operations', 'department': 'Operations', 'business_value': 3, 'tech_health': 2, 'cost': 55000, 'usage': 20, 'security': 2, 'strategic_fit': 1, 'redundancy': 0},
        {'name': 'ServiceNow', 'category': 'ITSM', 'department': 'IT', 'business_value': 8, 'tech_health': 8, 'cost': 150000, 'usage': 600, 'security': 8, 'strategic_fit': 8, 'redundancy': 0},
    ]

    # Process and add applications
    for app_data in sample_apps:
        application = Application(
            portfolio_id=portfolio.id,
            **app_data
        )

        # Process through rationalization engine
        results = rationalization_engine.process_single_application(application.to_scoring_dict())
        application.apply_scoring_results(results)

        db.session.add(application)

    db.session.commit()

    # Update portfolio metrics
    portfolio.update_metrics()
    db.session.commit()

    return jsonify({
        'success': True,
        'portfolio': portfolio.to_dict(),
        'applications_created': len(sample_apps)
    })


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    app.run(debug=True, port=5000)
