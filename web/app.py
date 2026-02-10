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

from database.models import (
    db, Portfolio, Application, ChatSession, ComplianceResult, CostAnalysis,
    # Tier 2 models
    ApplicationDependency, ApplicationIntegration, Vendor, VendorAssessment,
    DependencyAnalysis, IntegrationAnalysis
)
from ai_core.chat_engine import AIChatEngine, ConversationMode, get_chat_engine
from rationalization import (
    RationalizationEngine, CostModeler, ComplianceEngine,
    WhatIfScenarioEngine, PrioritizationRoadmapEngine,
    RiskAssessmentFramework, BenchmarkEngine,
    # Tier 2 engines
    DependencyMapper, IntegrationAssessor, VendorRiskEngine,
    create_demo_dependencies, create_demo_integrations, create_demo_vendors,
    # Tier 2: Lifecycle Management
    LifecycleManager, LifecycleStage, TransitionStatus, HealthStatus,
    SunsetReason, StageMetrics, create_lifecycle_manager, create_demo_lifecycles,
    # Tier 3: ML Clustering
    MLClusteringEngine, ClusteringMethod, ApplicationFeatures,
    create_clustering_engine, create_demo_applications,
    # Tier 3: Migration Planner
    MigrationPlanner, MigrationStrategy, CloudProvider, MigrationComplexity,
    ApplicationMigrationProfile, create_migration_planner, create_demo_migration_profiles,
    # Tier 3: Portfolio Dashboard
    PortfolioDashboardEngine, ApplicationData, create_portfolio_dashboard_engine, create_demo_portfolio_data,
    # Tier 3: Budget Optimizer
    BudgetOptimizer, OptimizationObjective, AllocationStrategy,
    ApplicationBudgetProfile, create_budget_optimizer, create_demo_budget_profiles,
    # Tier 3: Risk Heat Maps
    RiskHeatMapEngine, RiskCategory, RiskSeverity,
    ApplicationRiskProfile, create_risk_heatmap_engine, create_demo_risk_profiles
)

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
        # Enterprise scoring criteria
        business_value=float(data.get('business_value', 5)),
        tech_health=float(data.get('tech_health', 5)),
        cost=float(data.get('cost', 0)),
        usage=float(data.get('usage', 0)),
        security=float(data.get('security', 5)),
        strategic_fit=float(data.get('strategic_fit', 5)),
        redundancy=int(data.get('redundancy', 0)),
        # Government Edition fields
        citizen_impact=float(data['citizen_impact']) if data.get('citizen_impact') else None,
        mission_criticality=float(data['mission_criticality']) if data.get('mission_criticality') else None,
        interoperability_score=float(data['interoperability_score']) if data.get('interoperability_score') else None,
        data_sensitivity=data.get('data_sensitivity'),
        compliance_requirements=data.get('compliance_requirements'),
        system_of_record=data.get('system_of_record', False),
        public_facing=data.get('public_facing', False),
        shared_service=data.get('shared_service', False),
        grant_funded=data.get('grant_funded', False)
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
# WHAT-IF SCENARIO API
# =============================================================================

def _apps_to_whatif_format(applications):
    """Convert application objects to What-If engine format."""
    return [
        {
            'name': app.name,
            'cost': app.cost or 0,
            'tech_health': app.tech_health or 5,
            'business_value': app.business_value or 5,
            'security': app.security or 5,
            'redundancy': app.redundancy or 0,
            'category': app.category or 'Other'
        }
        for app in applications
    ]


@app.route('/api/portfolios/<portfolio_id>/whatif/scenarios', methods=['GET'])
def get_recommended_scenarios(portfolio_id):
    """Get recommended What-If scenarios for a portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()

    if not applications:
        return jsonify({'error': 'No applications to analyze'}), 400

    app_dicts = _apps_to_whatif_format(applications)
    engine = WhatIfScenarioEngine(app_dicts)
    recommendations = engine.get_recommended_scenarios()

    return jsonify({
        'portfolio_id': portfolio_id,
        'baseline': engine.baseline,
        'recommended_scenarios': recommendations
    })


@app.route('/api/portfolios/<portfolio_id>/whatif/simulate', methods=['POST'])
def simulate_scenario(portfolio_id):
    """Simulate a What-If scenario."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()
    data = request.get_json()

    if not applications:
        return jsonify({'error': 'No applications to analyze'}), 400

    app_dicts = _apps_to_whatif_format(applications)
    engine = WhatIfScenarioEngine(app_dicts)

    scenario_type = data.get('type', 'retire')

    if scenario_type == 'retire':
        app_names = data.get('apps', [])
        result = engine.simulate_retirement(app_names)
    elif scenario_type == 'modernize':
        app_names = data.get('apps', [])
        health_improvement = data.get('health_improvement', 3.0)
        result = engine.simulate_modernization(app_names, health_improvement)
    elif scenario_type == 'consolidate':
        app_groups = data.get('app_groups', [])
        cost_reduction = data.get('cost_reduction', 0.30)
        result = engine.simulate_consolidation(app_groups, cost_reduction)
    elif scenario_type == 'combined':
        scenarios = data.get('scenarios', [])
        result = engine.simulate_combined_scenario(scenarios)
    else:
        return jsonify({'error': f'Unknown scenario type: {scenario_type}'}), 400

    return jsonify({
        'success': True,
        'scenario_result': result
    })


@app.route('/whatif/<portfolio_id>')
def whatif_page(portfolio_id):
    """What-If Scenario simulator page."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()
    return render_template('whatif.html', portfolio=portfolio, applications=applications)


# =============================================================================
# ROADMAP API
# =============================================================================

def _apps_to_roadmap_format(applications):
    """Convert application objects to Roadmap engine format."""
    return [
        {
            'name': app.name,
            'cost': app.cost or 0,
            'tech_health': app.tech_health or 5,
            'business_value': app.business_value or 5,
            'category': app.category or 'Other',
            'description': app.description or ''
        }
        for app in applications
    ]


@app.route('/api/portfolios/<portfolio_id>/roadmap', methods=['GET'])
def get_roadmap(portfolio_id):
    """Get roadmap for a portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()

    if not applications:
        return jsonify({'error': 'No applications to analyze'}), 400

    app_dicts = _apps_to_roadmap_format(applications)
    engine = PrioritizationRoadmapEngine(app_dicts)

    return jsonify({
        'portfolio_id': portfolio_id,
        'roadmap': engine.get_roadmap_summary()
    })


@app.route('/api/portfolios/<portfolio_id>/roadmap/full', methods=['GET'])
def get_full_roadmap(portfolio_id):
    """Get complete roadmap with all details."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()

    if not applications:
        return jsonify({'error': 'No applications to analyze'}), 400

    app_dicts = _apps_to_roadmap_format(applications)
    engine = PrioritizationRoadmapEngine(app_dicts)

    return jsonify({
        'portfolio_id': portfolio_id,
        'executive_summary': engine.generate_executive_summary(),
        'effort_impact_matrix': engine.get_effort_impact_matrix(),
        'dependency_warnings': engine.get_dependency_warnings()
    })


@app.route('/roadmap/<portfolio_id>')
def roadmap_page(portfolio_id):
    """Roadmap planning page."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()
    return render_template('roadmap.html', portfolio=portfolio, applications=applications)


# =============================================================================
# RISK ASSESSMENT API
# =============================================================================

def _apps_to_risk_format(applications):
    """Convert application objects to Risk Assessment format."""
    return [
        {
            'name': app.name,
            'cost': app.cost or 0,
            'tech_health': app.tech_health or 5,
            'business_value': app.business_value or 5,
            'security': app.security or 5,
            'category': app.category or 'Other',
            'description': app.description or ''
        }
        for app in applications
    ]


@app.route('/api/portfolios/<portfolio_id>/risk', methods=['GET'])
def get_risk_assessment(portfolio_id):
    """Get risk assessment summary for a portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()

    if not applications:
        return jsonify({'error': 'No applications to analyze'}), 400

    app_dicts = _apps_to_risk_format(applications)
    engine = RiskAssessmentFramework(app_dicts)

    return jsonify({
        'portfolio_id': portfolio_id,
        'risk_summary': engine.get_risk_summary()
    })


@app.route('/api/portfolios/<portfolio_id>/risk/full', methods=['GET'])
def get_full_risk_assessment(portfolio_id):
    """Get complete risk assessment with all details."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()

    if not applications:
        return jsonify({'error': 'No applications to analyze'}), 400

    app_dicts = _apps_to_risk_format(applications)
    engine = RiskAssessmentFramework(app_dicts)
    portfolio_results = engine.assess_portfolio()

    return jsonify({
        'portfolio_id': portfolio_id,
        'portfolio_metrics': portfolio_results['portfolio_metrics'],
        'risk_distribution': portfolio_results['risk_distribution'],
        'priority_distribution': portfolio_results['priority_distribution'],
        'high_risk_apps': portfolio_results['high_risk_apps'][:10],
        'urgent_apps': portfolio_results['urgent_apps'],
        'heatmap_data': engine.get_risk_heatmap_data()
    })


@app.route('/api/portfolios/<portfolio_id>/risk/compliance/<framework>', methods=['GET'])
def get_risk_compliance(portfolio_id, framework):
    """Get compliance check for a specific framework."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()

    if not applications:
        return jsonify({'error': 'No applications to analyze'}), 400

    app_dicts = _apps_to_risk_format(applications)
    engine = RiskAssessmentFramework(app_dicts)
    engine.assess_portfolio()

    compliance_result = engine.check_compliance(framework)
    return jsonify(compliance_result)


@app.route('/api/applications/<app_id>/risk/mitigation', methods=['GET'])
def get_mitigation_plan(app_id):
    """Get risk mitigation plan for a specific application."""
    application = Application.query.get_or_404(app_id)
    portfolio = application.portfolio
    applications = portfolio.applications.all()

    app_dicts = _apps_to_risk_format(applications)
    engine = RiskAssessmentFramework(app_dicts)
    engine.assess_portfolio()

    mitigation = engine.generate_mitigation_plan(application.name)
    return jsonify(mitigation)


@app.route('/risk/<portfolio_id>')
def risk_page(portfolio_id):
    """Risk assessment page."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()
    # Convert to dicts for JSON serialization in template
    applications_data = [app.to_dict() for app in applications]
    return render_template('risk.html', portfolio=portfolio, applications=applications_data)


# =============================================================================
# BENCHMARK API
# =============================================================================

def _apps_to_benchmark_format(applications):
    """Convert application objects to Benchmark engine format."""
    return [
        {
            'name': app.name,
            'cost': app.cost or 0,
            'tech_health': app.tech_health or 5,
            'business_value': app.business_value or 5,
            'category': app.category or 'Other'
        }
        for app in applications
    ]


@app.route('/api/portfolios/<portfolio_id>/benchmark', methods=['GET'])
def get_benchmark(portfolio_id):
    """Get benchmark summary for a portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()

    if not applications:
        return jsonify({'error': 'No applications to analyze'}), 400

    app_dicts = _apps_to_benchmark_format(applications)
    engine = BenchmarkEngine(app_dicts)

    return jsonify({
        'portfolio_id': portfolio_id,
        'benchmark_summary': engine.get_benchmark_summary()
    })


@app.route('/api/portfolios/<portfolio_id>/benchmark/full', methods=['GET'])
def get_full_benchmark(portfolio_id):
    """Get comprehensive benchmark report."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()

    if not applications:
        return jsonify({'error': 'No applications to analyze'}), 400

    app_dicts = _apps_to_benchmark_format(applications)
    engine = BenchmarkEngine(app_dicts)

    return jsonify({
        'portfolio_id': portfolio_id,
        'benchmark_report': engine.generate_benchmark_report()
    })


@app.route('/api/portfolios/<portfolio_id>/benchmark/best-practices', methods=['GET'])
def get_best_practices(portfolio_id):
    """Get best practices recommendations."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()

    category = request.args.get('category')

    app_dicts = _apps_to_benchmark_format(applications) if applications else []
    engine = BenchmarkEngine(app_dicts)

    practices = engine.get_best_practices(category)
    return jsonify({
        'portfolio_id': portfolio_id,
        'best_practices': practices
    })


@app.route('/benchmark/<portfolio_id>')
def benchmark_page(portfolio_id):
    """Benchmark comparison page."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()
    return render_template('benchmark.html', portfolio=portfolio, applications=applications)


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
# TIER 2: DEPENDENCY MAPPING API
# =============================================================================

@app.route('/api/portfolios/<portfolio_id>/dependencies', methods=['GET'])
def get_dependencies(portfolio_id):
    """Get all dependencies in a portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    dependencies = ApplicationDependency.query.filter_by(portfolio_id=portfolio_id).all()
    return jsonify([d.to_dict() for d in dependencies])


@app.route('/api/portfolios/<portfolio_id>/dependencies', methods=['POST'])
def create_dependency(portfolio_id):
    """Create a new dependency between applications."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    data = request.get_json()

    dependency = ApplicationDependency(
        portfolio_id=portfolio_id,
        source_app_id=data['source_app_id'],
        target_app_id=data['target_app_id'],
        dependency_type=data.get('dependency_type', 'data'),
        strength=data.get('strength', 'medium'),
        description=data.get('description'),
        data_direction=data.get('data_direction', 'bidirectional'),
        data_volume=data.get('data_volume'),
        is_critical_path=data.get('is_critical_path', False),
        failure_impact=data.get('failure_impact')
    )

    db.session.add(dependency)
    db.session.commit()

    return jsonify(dependency.to_dict()), 201


@app.route('/api/dependencies/<dep_id>', methods=['DELETE'])
def delete_dependency(dep_id):
    """Delete a dependency."""
    dependency = ApplicationDependency.query.get_or_404(dep_id)
    db.session.delete(dependency)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/portfolios/<portfolio_id>/dependencies/analyze', methods=['POST'])
def analyze_dependencies(portfolio_id):
    """Run dependency analysis on a portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()
    dependencies = ApplicationDependency.query.filter_by(portfolio_id=portfolio_id).all()

    if not applications:
        return jsonify({'error': 'No applications in portfolio'}), 400

    # Build dependency mapper
    mapper = DependencyMapper()

    # Add applications as nodes
    for app in applications:
        mapper.add_application(app.id, app.name, {
            'category': app.category,
            'cost': app.cost,
            'business_value': app.business_value
        })

    # Add dependencies as edges
    for dep in dependencies:
        mapper.add_dependency(
            source_id=dep.source_app_id,
            target_id=dep.target_app_id,
            dep_type=dep.dependency_type or 'data',
            strength=dep.strength or 'medium',
            metadata={'description': dep.description}
        )

    # Run analysis
    mapper.build_graph()
    circular = mapper.find_circular_dependencies()
    critical_paths = mapper.find_critical_paths()

    # Calculate blast radius for each app
    blast_radius = {}
    for app in applications:
        blast_radius[app.id] = mapper.calculate_blast_radius(app.id)

    # Get visualization data
    viz_data = mapper.get_visualization_data()

    # Get hub and isolated apps
    hub_apps = mapper.get_hub_applications(limit=5)
    isolated = mapper.get_isolated_applications()

    # Determine overall risk level
    risk_level = 'low'
    if len(circular) > 0:
        risk_level = 'critical' if len(circular) > 3 else 'high'
    elif len(critical_paths) > 5:
        risk_level = 'medium'

    # Generate recommendations
    recommendations = []
    if circular:
        recommendations.append(f"CRITICAL: {len(circular)} circular dependencies detected - review and refactor")
    if hub_apps:
        top_hub = hub_apps[0]
        recommendations.append(f"Monitor {top_hub.get('name', 'hub')} - it has {top_hub.get('total_connections', 0)} connections")
    if isolated:
        recommendations.append(f"{len(isolated)} applications have no dependencies - verify if correct")

    # Save analysis to database
    analysis = DependencyAnalysis(
        portfolio_id=portfolio_id,
        total_applications=len(applications),
        total_dependencies=len(dependencies),
        circular_dependency_count=len(circular),
        critical_path_count=len(critical_paths),
        circular_dependencies=circular,
        critical_paths=critical_paths,
        blast_radius_data=blast_radius,
        dependency_graph=viz_data,
        hub_applications=hub_apps,
        isolated_applications=isolated,
        overall_risk_level=risk_level,
        recommendations=recommendations
    )

    db.session.add(analysis)
    db.session.commit()

    return jsonify({
        'success': True,
        'analysis': analysis.to_dict()
    })


@app.route('/api/portfolios/<portfolio_id>/dependencies/visualization', methods=['GET'])
def get_dependency_visualization(portfolio_id):
    """Get dependency graph data for visualization."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()
    dependencies = ApplicationDependency.query.filter_by(portfolio_id=portfolio_id).all()

    # Build nodes and edges for visualization
    nodes = [{
        'id': app.id,
        'name': app.name,
        'category': app.category,
        'time_category': app.time_category,
        'cost': app.cost
    } for app in applications]

    edges = [{
        'source': dep.source_app_id,
        'target': dep.target_app_id,
        'type': dep.dependency_type,
        'strength': dep.strength,
        'is_critical': dep.is_critical_path
    } for dep in dependencies]

    return jsonify({
        'nodes': nodes,
        'edges': edges,
        'total_nodes': len(nodes),
        'total_edges': len(edges)
    })


@app.route('/dependencies/<portfolio_id>')
def dependencies_page(portfolio_id):
    """Dependency mapping page."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()
    return render_template('dependencies.html', portfolio=portfolio, applications=applications)


# =============================================================================
# TIER 2: INTEGRATION ASSESSMENT API
# =============================================================================

@app.route('/api/portfolios/<portfolio_id>/integrations', methods=['GET'])
def get_integrations(portfolio_id):
    """Get all integrations in a portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    integrations = ApplicationIntegration.query.filter_by(portfolio_id=portfolio_id).all()
    return jsonify([i.to_dict() for i in integrations])


@app.route('/api/portfolios/<portfolio_id>/integrations', methods=['POST'])
def create_integration(portfolio_id):
    """Create a new integration."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    data = request.get_json()

    integration = ApplicationIntegration(
        portfolio_id=portfolio_id,
        source_app_id=data['source_app_id'],
        target_app_id=data.get('target_app_id'),
        external_system=data.get('external_system'),
        integration_type=data.get('integration_type', 'api'),
        protocol=data.get('protocol'),
        auth_method=data.get('auth_method'),
        data_sensitivity=data.get('data_sensitivity', 'internal'),
        data_types=data.get('data_types'),
        avg_latency_ms=data.get('avg_latency_ms'),
        error_rate_percent=data.get('error_rate_percent'),
        uptime_percent=data.get('uptime_percent', 99.0),
        daily_transactions=data.get('daily_transactions'),
        sync_frequency=data.get('sync_frequency'),
        has_retry_mechanism=data.get('has_retry_mechanism', False),
        has_error_handling=data.get('has_error_handling', False),
        has_monitoring=data.get('has_monitoring', False),
        documentation_url=data.get('documentation_url'),
        owner=data.get('owner'),
        notes=data.get('notes')
    )

    # Calculate health score
    integration.calculate_health_score()

    db.session.add(integration)
    db.session.commit()

    return jsonify(integration.to_dict()), 201


@app.route('/api/integrations/<int_id>', methods=['PUT'])
def update_integration(int_id):
    """Update an integration."""
    integration = ApplicationIntegration.query.get_or_404(int_id)
    data = request.get_json()

    # Update fields
    updatable_fields = [
        'integration_type', 'protocol', 'auth_method', 'data_sensitivity',
        'data_types', 'avg_latency_ms', 'error_rate_percent', 'uptime_percent',
        'daily_transactions', 'sync_frequency', 'has_retry_mechanism',
        'has_error_handling', 'has_monitoring', 'documentation_url', 'owner', 'notes'
    ]

    for field in updatable_fields:
        if field in data:
            setattr(integration, field, data[field])

    # Recalculate health score
    integration.calculate_health_score()

    db.session.commit()

    return jsonify(integration.to_dict())


@app.route('/api/integrations/<int_id>', methods=['DELETE'])
def delete_integration(int_id):
    """Delete an integration."""
    integration = ApplicationIntegration.query.get_or_404(int_id)
    db.session.delete(integration)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/portfolios/<portfolio_id>/integrations/analyze', methods=['POST'])
def analyze_integrations(portfolio_id):
    """Run integration health analysis on a portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    integrations = ApplicationIntegration.query.filter_by(portfolio_id=portfolio_id).all()

    if not integrations:
        return jsonify({'error': 'No integrations in portfolio'}), 400

    # Calculate health scores for all integrations
    for integration in integrations:
        integration.calculate_health_score()
    db.session.commit()

    # Aggregate statistics
    total = len(integrations)
    healthy = sum(1 for i in integrations if i.health_status == 'healthy')
    degraded = sum(1 for i in integrations if i.health_status == 'degraded')
    unhealthy = sum(1 for i in integrations if i.health_status == 'unhealthy')
    critical = sum(1 for i in integrations if i.health_status == 'critical')

    avg_health = sum(i.health_score or 0 for i in integrations) / total if total > 0 else 0

    # Group by data sensitivity
    sensitivity_breakdown = {}
    for integration in integrations:
        sens = integration.data_sensitivity or 'unknown'
        if sens not in sensitivity_breakdown:
            sensitivity_breakdown[sens] = {'count': 0, 'avg_health': 0, 'scores': []}
        sensitivity_breakdown[sens]['count'] += 1
        sensitivity_breakdown[sens]['scores'].append(integration.health_score or 0)

    for sens in sensitivity_breakdown:
        scores = sensitivity_breakdown[sens]['scores']
        sensitivity_breakdown[sens]['avg_health'] = sum(scores) / len(scores) if scores else 0
        del sensitivity_breakdown[sens]['scores']

    # Group by integration type
    type_breakdown = {}
    for integration in integrations:
        int_type = integration.integration_type or 'unknown'
        if int_type not in type_breakdown:
            type_breakdown[int_type] = {'count': 0, 'avg_health': 0, 'scores': []}
        type_breakdown[int_type]['count'] += 1
        type_breakdown[int_type]['scores'].append(integration.health_score or 0)

    for int_type in type_breakdown:
        scores = type_breakdown[int_type]['scores']
        type_breakdown[int_type]['avg_health'] = sum(scores) / len(scores) if scores else 0
        del type_breakdown[int_type]['scores']

    # Identify high-risk integrations (critical or unhealthy with sensitive data)
    high_risk = [
        i.to_dict() for i in integrations
        if i.health_status in ('critical', 'unhealthy') and
           i.data_sensitivity in ('confidential', 'restricted', 'pii')
    ]

    # Identify bottlenecks (high transaction count with degraded health)
    bottlenecks = [
        i.to_dict() for i in integrations
        if (i.daily_transactions or 0) > 1000 and i.health_status in ('degraded', 'unhealthy', 'critical')
    ]

    # Determine overall health
    overall_health = 'healthy'
    if critical > 0:
        overall_health = 'critical'
    elif unhealthy > total * 0.2:
        overall_health = 'unhealthy'
    elif degraded > total * 0.3:
        overall_health = 'degraded'

    # Generate recommendations
    recommendations = []
    if critical > 0:
        recommendations.append(f"URGENT: {critical} integrations in critical state - immediate attention required")
    if high_risk:
        recommendations.append(f"{len(high_risk)} high-risk integrations with sensitive data need remediation")
    if bottlenecks:
        recommendations.append(f"{len(bottlenecks)} high-volume integrations showing performance issues")

    # Check for missing operational controls
    no_monitoring = sum(1 for i in integrations if not i.has_monitoring)
    if no_monitoring > total * 0.5:
        recommendations.append(f"{no_monitoring} integrations lack monitoring - implement observability")

    # Save analysis
    analysis = IntegrationAnalysis(
        portfolio_id=portfolio_id,
        total_integrations=total,
        healthy_count=healthy,
        degraded_count=degraded,
        unhealthy_count=unhealthy,
        critical_count=critical,
        average_health_score=round(avg_health, 2),
        integration_scores=[i.to_dict() for i in integrations],
        bottlenecks=bottlenecks,
        high_risk_integrations=high_risk,
        data_sensitivity_breakdown=sensitivity_breakdown,
        integration_type_breakdown=type_breakdown,
        overall_health=overall_health,
        recommendations=recommendations
    )

    db.session.add(analysis)
    db.session.commit()

    return jsonify({
        'success': True,
        'analysis': analysis.to_dict()
    })


@app.route('/integrations/<portfolio_id>')
def integrations_page(portfolio_id):
    """Integration assessment page."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()
    return render_template('integrations.html', portfolio=portfolio, applications=applications)


# =============================================================================
# TIER 2: VENDOR RISK MANAGEMENT API
# =============================================================================

@app.route('/api/portfolios/<portfolio_id>/vendors', methods=['GET'])
def get_vendors(portfolio_id):
    """Get all vendors for a portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    vendors = Vendor.query.filter_by(portfolio_id=portfolio_id).all()
    return jsonify([v.to_dict() for v in vendors])


@app.route('/api/portfolios/<portfolio_id>/vendors', methods=['POST'])
def create_vendor(portfolio_id):
    """Create a new vendor."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    data = request.get_json()

    vendor = Vendor(
        portfolio_id=portfolio_id,
        name=data['name'],
        tier=data.get('tier', 'tactical'),
        status=data.get('status', 'active'),
        annual_revenue=data.get('annual_revenue'),
        years_in_business=data.get('years_in_business'),
        financial_rating=data.get('financial_rating'),
        publicly_traded=data.get('publicly_traded', False),
        stock_symbol=data.get('stock_symbol'),
        contract_start=datetime.strptime(data['contract_start'], '%Y-%m-%d').date() if data.get('contract_start') else None,
        contract_end=datetime.strptime(data['contract_end'], '%Y-%m-%d').date() if data.get('contract_end') else None,
        annual_spend=data.get('annual_spend', 0),
        payment_terms=data.get('payment_terms', 'NET30'),
        contract_type=data.get('contract_type'),
        auto_renewal=data.get('auto_renewal', False),
        security_score=data.get('security_score'),
        compliances=data.get('compliances', []),
        last_security_audit=datetime.strptime(data['last_security_audit'], '%Y-%m-%d').date() if data.get('last_security_audit') else None,
        has_incident_history=data.get('has_incident_history', False),
        incident_details=data.get('incident_details'),
        has_dr_plan=data.get('has_dr_plan', False),
        sla_uptime=data.get('sla_uptime', 99.0),
        geographic_presence=data.get('geographic_presence', []),
        data_center_locations=data.get('data_center_locations'),
        primary_contact=data.get('primary_contact'),
        primary_email=data.get('primary_email'),
        primary_phone=data.get('primary_phone'),
        account_manager=data.get('account_manager'),
        support_tier=data.get('support_tier'),
        website=data.get('website'),
        documentation_url=data.get('documentation_url'),
        notes=data.get('notes')
    )

    db.session.add(vendor)
    db.session.commit()

    return jsonify(vendor.to_dict()), 201


@app.route('/api/vendors/<vendor_id>', methods=['GET'])
def get_vendor(vendor_id):
    """Get a specific vendor."""
    vendor = Vendor.query.get_or_404(vendor_id)
    return jsonify(vendor.to_dict())


@app.route('/api/vendors/<vendor_id>', methods=['PUT'])
def update_vendor(vendor_id):
    """Update a vendor."""
    vendor = Vendor.query.get_or_404(vendor_id)
    data = request.get_json()

    # Update simple fields
    simple_fields = [
        'name', 'tier', 'status', 'annual_revenue', 'years_in_business',
        'financial_rating', 'publicly_traded', 'stock_symbol', 'annual_spend',
        'payment_terms', 'contract_type', 'auto_renewal', 'security_score',
        'compliances', 'has_incident_history', 'incident_details', 'has_dr_plan',
        'sla_uptime', 'geographic_presence', 'data_center_locations',
        'primary_contact', 'primary_email', 'primary_phone', 'account_manager',
        'support_tier', 'website', 'documentation_url', 'notes'
    ]

    for field in simple_fields:
        if field in data:
            setattr(vendor, field, data[field])

    # Update date fields
    if 'contract_start' in data:
        vendor.contract_start = datetime.strptime(data['contract_start'], '%Y-%m-%d').date() if data['contract_start'] else None
    if 'contract_end' in data:
        vendor.contract_end = datetime.strptime(data['contract_end'], '%Y-%m-%d').date() if data['contract_end'] else None
    if 'last_security_audit' in data:
        vendor.last_security_audit = datetime.strptime(data['last_security_audit'], '%Y-%m-%d').date() if data['last_security_audit'] else None

    db.session.commit()

    return jsonify(vendor.to_dict())


@app.route('/api/vendors/<vendor_id>', methods=['DELETE'])
def delete_vendor(vendor_id):
    """Delete a vendor."""
    vendor = Vendor.query.get_or_404(vendor_id)
    db.session.delete(vendor)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/vendors/<vendor_id>/assess', methods=['POST'])
def assess_vendor(vendor_id):
    """Run risk assessment on a vendor."""
    vendor = Vendor.query.get_or_404(vendor_id)
    data = request.get_json() or {}

    industry = data.get('industry', 'general')
    total_it_spend = data.get('total_it_spend', 1000000)

    # Use the vendor risk engine
    engine = VendorRiskEngine()

    # Convert vendor to engine format
    from rationalization.vendor_risk_engine import VendorProfile, VendorTier, VendorStatus, ComplianceFramework as VCF
    from datetime import date

    # Map compliances
    compliance_map = {
        'SOC2': VCF.SOC2, 'ISO27001': VCF.ISO27001, 'HIPAA': VCF.HIPAA,
        'PCI_DSS': VCF.PCI_DSS, 'GDPR': VCF.GDPR, 'FEDRAMP': VCF.FEDRAMP,
        'SOX': VCF.SOX, 'CJIS': VCF.CJIS, 'FISMA': VCF.FISMA
    }

    compliances = []
    for c in (vendor.compliances or []):
        if c.upper() in compliance_map:
            compliances.append(compliance_map[c.upper()])

    profile = VendorProfile(
        vendor_id=vendor.id,
        name=vendor.name,
        tier=VendorTier(vendor.tier) if vendor.tier else VendorTier.TACTICAL,
        status=VendorStatus(vendor.status) if vendor.status else VendorStatus.ACTIVE,
        annual_revenue=vendor.annual_revenue,
        years_in_business=vendor.years_in_business,
        financial_rating=vendor.financial_rating,
        publicly_traded=vendor.publicly_traded or False,
        contract_start=vendor.contract_start,
        contract_end=vendor.contract_end,
        annual_spend=vendor.annual_spend or 0,
        security_score=vendor.security_score,
        compliances=compliances,
        last_security_audit=vendor.last_security_audit,
        has_incident_history=vendor.has_incident_history or False,
        has_dr_plan=vendor.has_dr_plan or False,
        sla_uptime=vendor.sla_uptime or 99.0,
        geographic_presence=vendor.geographic_presence or []
    )

    engine.add_vendor(profile)
    assessment_result = engine.assess_vendor(vendor.id, industry, total_it_spend)

    # Save assessment to database
    assessment = VendorAssessment(
        vendor_id=vendor.id,
        portfolio_id=vendor.portfolio_id,
        overall_risk_level=assessment_result.overall_risk_level.value,
        overall_risk_score=assessment_result.overall_risk_score,
        financial_risk_score=assessment_result.financial_risk_score,
        security_risk_score=assessment_result.security_risk_score,
        operational_risk_score=assessment_result.operational_risk_score,
        compliance_risk_score=assessment_result.compliance_risk_score,
        strategic_risk_score=assessment_result.strategic_risk_score,
        concentration_risk_score=assessment_result.concentration_risk_score,
        industry=industry,
        total_it_spend=total_it_spend,
        risk_factors=assessment_result.risk_factors,
        recommendations=assessment_result.recommendations
    )

    db.session.add(assessment)
    db.session.commit()

    return jsonify({
        'success': True,
        'assessment': assessment.to_dict()
    })


@app.route('/api/portfolios/<portfolio_id>/vendors/summary', methods=['GET'])
def get_vendor_summary(portfolio_id):
    """Get vendor portfolio summary."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    vendors = Vendor.query.filter_by(portfolio_id=portfolio_id).all()

    if not vendors:
        return jsonify({
            'total_vendors': 0,
            'total_spend': 0,
            'tier_distribution': {},
            'status_distribution': {},
            'expiring_contracts': []
        })

    # Calculate summary
    total_spend = sum(v.annual_spend or 0 for v in vendors)

    tier_dist = {}
    status_dist = {}
    expiring = []

    for vendor in vendors:
        # Tier distribution
        tier = vendor.tier or 'unclassified'
        tier_dist[tier] = tier_dist.get(tier, 0) + 1

        # Status distribution
        status = vendor.status or 'unknown'
        status_dist[status] = status_dist.get(status, 0) + 1

        # Expiring contracts
        if vendor.contract_end:
            days = vendor.days_until_contract_end()
            if days is not None and 0 < days <= 180:
                expiring.append({
                    'vendor_id': vendor.id,
                    'vendor_name': vendor.name,
                    'contract_end': vendor.contract_end.isoformat(),
                    'days_remaining': days,
                    'annual_spend': vendor.annual_spend
                })

    expiring.sort(key=lambda x: x['days_remaining'])

    return jsonify({
        'total_vendors': len(vendors),
        'total_spend': total_spend,
        'tier_distribution': tier_dist,
        'status_distribution': status_dist,
        'expiring_contracts': expiring[:10]
    })


@app.route('/vendors/<portfolio_id>')
def vendors_page(portfolio_id):
    """Vendor management page."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    vendors = Vendor.query.filter_by(portfolio_id=portfolio_id).all()
    return render_template('vendors.html', portfolio=portfolio, vendors=vendors)


# =============================================================================
# TIER 2: DEMO DATA FOR NEW FEATURES
# =============================================================================

@app.route('/api/demo/tier2/<portfolio_id>', methods=['POST'])
def create_tier2_demo_data(portfolio_id):
    """Create demo data for Tier 2 features (dependencies, integrations, vendors)."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()

    if len(applications) < 3:
        return jsonify({'error': 'Need at least 3 applications for demo data'}), 400

    # Create sample dependencies
    dependencies_created = 0
    app_ids = [app.id for app in applications]

    # Create some realistic dependencies
    sample_deps = [
        (0, 1, 'api', 'strong'),
        (1, 2, 'data', 'medium'),
        (2, 0, 'reporting', 'weak'),  # Creates a cycle for testing
        (0, 3, 'authentication', 'critical') if len(app_ids) > 3 else None,
        (1, 4, 'data', 'medium') if len(app_ids) > 4 else None,
    ]

    for dep_info in sample_deps:
        if dep_info and dep_info[0] < len(app_ids) and dep_info[1] < len(app_ids):
            dep = ApplicationDependency(
                portfolio_id=portfolio_id,
                source_app_id=app_ids[dep_info[0]],
                target_app_id=app_ids[dep_info[1]],
                dependency_type=dep_info[2],
                strength=dep_info[3],
                description=f'Auto-generated {dep_info[2]} dependency'
            )
            db.session.add(dep)
            dependencies_created += 1

    # Create sample integrations
    integrations_created = 0
    sample_ints = [
        {'type': 'api', 'protocol': 'REST', 'latency': 150, 'error_rate': 0.5, 'uptime': 99.9},
        {'type': 'database', 'protocol': 'SQL', 'latency': 50, 'error_rate': 0.1, 'uptime': 99.99},
        {'type': 'file_transfer', 'protocol': 'SFTP', 'latency': 2000, 'error_rate': 2.0, 'uptime': 99.0},
        {'type': 'message_queue', 'protocol': 'Kafka', 'latency': 10, 'error_rate': 0.01, 'uptime': 99.95},
    ]

    for i, int_info in enumerate(sample_ints):
        if i < len(app_ids) - 1:
            integration = ApplicationIntegration(
                portfolio_id=portfolio_id,
                source_app_id=app_ids[i],
                target_app_id=app_ids[i + 1],
                integration_type=int_info['type'],
                protocol=int_info['protocol'],
                avg_latency_ms=int_info['latency'],
                error_rate_percent=int_info['error_rate'],
                uptime_percent=int_info['uptime'],
                data_sensitivity='internal',
                daily_transactions=1000 * (i + 1),
                has_monitoring=i % 2 == 0,
                has_error_handling=True,
                has_retry_mechanism=i % 3 == 0
            )
            integration.calculate_health_score()
            db.session.add(integration)
            integrations_created += 1

    # Create sample vendors
    vendors_created = 0
    sample_vendors = [
        {'name': 'Microsoft', 'tier': 'strategic', 'spend': 250000, 'rating': 'AAA'},
        {'name': 'Salesforce', 'tier': 'strategic', 'spend': 150000, 'rating': 'AA'},
        {'name': 'ServiceNow', 'tier': 'tactical', 'spend': 80000, 'rating': 'A'},
        {'name': 'Acme Software', 'tier': 'commodity', 'spend': 25000, 'rating': 'BBB'},
    ]

    for v_info in sample_vendors:
        vendor = Vendor(
            portfolio_id=portfolio_id,
            name=v_info['name'],
            tier=v_info['tier'],
            status='active',
            annual_spend=v_info['spend'],
            financial_rating=v_info['rating'],
            years_in_business=15,
            has_dr_plan=True,
            sla_uptime=99.9,
            compliances=['SOC2', 'ISO27001']
        )
        db.session.add(vendor)
        vendors_created += 1

    db.session.commit()

    return jsonify({
        'success': True,
        'dependencies_created': dependencies_created,
        'integrations_created': integrations_created,
        'vendors_created': vendors_created
    })


# =============================================================================
# TIER 2: TECHNICAL DEBT CALCULATOR API
# =============================================================================

@app.route('/api/portfolios/<portfolio_id>/tech-debt', methods=['GET'])
def get_tech_debt_summary(portfolio_id):
    """Get technical debt summary for a portfolio."""
    from rationalization import create_demo_tech_debt

    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()

    # Create calculator with demo data based on portfolio apps
    calc = create_demo_tech_debt()

    # Get summary
    summary = calc.get_portfolio_summary()

    return jsonify({
        'portfolio_id': portfolio_id,
        'portfolio_name': portfolio.name,
        **summary.to_dict()
    })


@app.route('/api/portfolios/<portfolio_id>/tech-debt/apps/<app_id>', methods=['GET'])
def get_app_tech_debt(portfolio_id, app_id):
    """Get technical debt profile for a specific application."""
    from rationalization import create_tech_debt_calculator

    portfolio = Portfolio.query.get_or_404(portfolio_id)
    application = Application.query.get_or_404(app_id)

    # Create calculator and assess app with metrics from app data
    calc = create_tech_debt_calculator()

    # Build metrics from application data
    metrics = {
        'code_coverage': 100 - (application.technical_debt or 50),  # Invert debt to coverage
        'code_smells': int((application.technical_debt or 50) * 1.5),
        'outdated_dependencies': max(0, (application.technical_debt or 50) // 10),
        'vulnerable_dependencies': 1 if (application.technical_debt or 50) > 70 else 0,
        'cyclomatic_complexity': 5 + ((application.technical_debt or 50) // 10),
        'documentation_coverage': max(10, 100 - (application.technical_debt or 50)),
        'avg_response_time_ms': 200 + (application.technical_debt or 50) * 10
    }

    profile = calc.assess_application(app_id, application.name, metrics)

    return jsonify({
        'portfolio_id': portfolio_id,
        'application': {
            'id': application.id,
            'name': application.name,
            'time_category': application.time_category,
            'composite_score': application.composite_score
        },
        **profile.to_dict()
    })


@app.route('/api/portfolios/<portfolio_id>/tech-debt/roadmap', methods=['GET'])
def get_tech_debt_roadmap(portfolio_id):
    """Generate technical debt paydown roadmap."""
    from rationalization import create_demo_tech_debt

    portfolio = Portfolio.query.get_or_404(portfolio_id)

    # Get parameters
    budget_hours = request.args.get('budget_hours', 40, type=float)
    sprint_weeks = request.args.get('sprint_weeks', 2, type=int)

    calc = create_demo_tech_debt()
    roadmap = calc.generate_paydown_roadmap(budget_hours, sprint_weeks)

    return jsonify({
        'portfolio_id': portfolio_id,
        'portfolio_name': portfolio.name,
        'budget_hours_per_sprint': budget_hours,
        'sprint_length_weeks': sprint_weeks,
        **roadmap
    })


@app.route('/api/portfolios/<portfolio_id>/tech-debt/trends', methods=['GET'])
def get_tech_debt_trends(portfolio_id):
    """Get technical debt trends over time."""
    from rationalization import create_demo_tech_debt

    portfolio = Portfolio.query.get_or_404(portfolio_id)

    days = request.args.get('days', 90, type=int)
    calc = create_demo_tech_debt()
    trends = calc.get_debt_trends(days)

    return jsonify({
        'portfolio_id': portfolio_id,
        'portfolio_name': portfolio.name,
        **trends
    })


@app.route('/api/portfolios/<portfolio_id>/tech-debt/items', methods=['GET'])
def get_tech_debt_items(portfolio_id):
    """Get all technical debt items for a portfolio."""
    from rationalization import create_demo_tech_debt

    portfolio = Portfolio.query.get_or_404(portfolio_id)

    # Filter parameters
    category = request.args.get('category')
    severity = request.args.get('severity')
    status = request.args.get('status')

    calc = create_demo_tech_debt()
    summary = calc.get_portfolio_summary()

    items = summary.top_priority_items

    # Apply filters
    if category:
        items = [i for i in items if i['category'] == category]
    if severity:
        items = [i for i in items if i['severity'] == severity]

    return jsonify({
        'portfolio_id': portfolio_id,
        'items': items,
        'total_count': len(items)
    })


@app.route('/tech-debt/<portfolio_id>')
def tech_debt_page(portfolio_id):
    """Technical debt dashboard page."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()
    return render_template('tech_debt.html', portfolio=portfolio, applications=applications)


# =============================================================================
# TIER 2: APPLICATION LIFECYCLE MANAGEMENT API
# =============================================================================

# Store lifecycle managers per portfolio (in production, this would be in database)
_lifecycle_managers = {}


def get_lifecycle_manager(portfolio_id: str) -> LifecycleManager:
    """Get or create a lifecycle manager for a portfolio."""
    if portfolio_id not in _lifecycle_managers:
        # Create new manager and populate with demo data
        manager, _ = create_demo_lifecycles()
        _lifecycle_managers[portfolio_id] = manager
    return _lifecycle_managers[portfolio_id]


@app.route('/api/portfolios/<portfolio_id>/lifecycle', methods=['GET'])
def get_lifecycle_summary(portfolio_id):
    """Get lifecycle management summary for a portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    manager = get_lifecycle_manager(portfolio_id)

    summary = manager.get_portfolio_summary()

    return jsonify({
        'portfolio_id': portfolio_id,
        'portfolio_name': portfolio.name,
        **summary
    })


@app.route('/api/portfolios/<portfolio_id>/lifecycle/apps', methods=['GET'])
def get_all_app_lifecycles(portfolio_id):
    """Get lifecycle info for all applications."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    manager = get_lifecycle_manager(portfolio_id)

    lifecycles = []
    for app_id, lifecycle in manager.lifecycles.items():
        lifecycles.append({
            'app_id': lifecycle.app_id,
            'app_name': lifecycle.app_name,
            'current_stage': lifecycle.current_stage.value,
            'current_health': lifecycle.current_health.value,
            'days_in_stage': lifecycle.days_in_current_stage(),
            'expected_duration': lifecycle.expected_stage_duration_days,
            'is_overdue': lifecycle.is_overdue_for_transition(),
            'lifecycle_age_days': lifecycle.lifecycle_age_days(),
            'business_criticality': lifecycle.business_criticality,
            'owner': lifecycle.owner,
            'has_sunset_plan': lifecycle.sunset_plan is not None,
            'has_pending_transition': lifecycle.pending_transition is not None
        })

    return jsonify({
        'portfolio_id': portfolio_id,
        'applications': lifecycles,
        'total_count': len(lifecycles)
    })


@app.route('/api/portfolios/<portfolio_id>/lifecycle/apps/<app_id>', methods=['GET'])
def get_app_lifecycle(portfolio_id, app_id):
    """Get detailed lifecycle info for a specific application."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    manager = get_lifecycle_manager(portfolio_id)

    lifecycle = manager.get_lifecycle(app_id)
    if not lifecycle:
        return jsonify({'error': 'Application not found in lifecycle manager'}), 404

    # Get timeline
    timeline = manager.get_stage_timeline(app_id)

    # Get forecast
    forecast = manager.forecast_lifecycle(app_id)

    return jsonify({
        'portfolio_id': portfolio_id,
        'app_id': app_id,
        'app_name': lifecycle.app_name,
        'current_stage': lifecycle.current_stage.value,
        'current_health': lifecycle.current_health.value,
        'inception_date': lifecycle.inception_date.isoformat(),
        'current_stage_start': lifecycle.current_stage_start.isoformat(),
        'days_in_stage': lifecycle.days_in_current_stage(),
        'expected_duration': lifecycle.expected_stage_duration_days,
        'is_overdue': lifecycle.is_overdue_for_transition(),
        'lifecycle_age_days': lifecycle.lifecycle_age_days(),
        'business_criticality': lifecycle.business_criticality,
        'owner': lifecycle.owner,
        'metrics': {
            'users_count': lifecycle.current_metrics.users_count,
            'transactions_per_day': lifecycle.current_metrics.transactions_per_day,
            'uptime_percentage': lifecycle.current_metrics.uptime_percentage,
            'incident_count': lifecycle.current_metrics.incident_count,
            'satisfaction_score': lifecycle.current_metrics.satisfaction_score,
            'cost_per_month': lifecycle.current_metrics.cost_per_month,
            'roi_percentage': lifecycle.current_metrics.roi_percentage
        },
        'timeline': timeline,
        'forecast': forecast,
        'sunset_plan': lifecycle.sunset_plan.id if lifecycle.sunset_plan else None,
        'pending_transition': lifecycle.pending_transition.id if lifecycle.pending_transition else None
    })


@app.route('/api/portfolios/<portfolio_id>/lifecycle/apps/<app_id>/timeline', methods=['GET'])
def get_app_lifecycle_timeline(portfolio_id, app_id):
    """Get stage transition timeline for an application."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    manager = get_lifecycle_manager(portfolio_id)

    timeline = manager.get_stage_timeline(app_id)
    if not timeline:
        return jsonify({'error': 'No timeline found for application'}), 404

    return jsonify({
        'portfolio_id': portfolio_id,
        'app_id': app_id,
        'timeline': timeline,
        'total_transitions': len(timeline)
    })


@app.route('/api/portfolios/<portfolio_id>/lifecycle/apps/<app_id>/forecast', methods=['GET'])
def get_app_lifecycle_forecast(portfolio_id, app_id):
    """Get lifecycle forecast for an application."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    manager = get_lifecycle_manager(portfolio_id)

    forecast = manager.forecast_lifecycle(app_id)
    if not forecast:
        return jsonify({'error': 'Application not found'}), 404

    return jsonify({
        'portfolio_id': portfolio_id,
        **forecast
    })


@app.route('/api/portfolios/<portfolio_id>/lifecycle/transitions', methods=['GET'])
def get_pending_transitions(portfolio_id):
    """Get all pending transition requests."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    manager = get_lifecycle_manager(portfolio_id)

    pending = []
    for request_id, request in manager.transition_requests.items():
        if request.status == TransitionStatus.PENDING:
            pending.append({
                'id': request.id,
                'app_id': request.app_id,
                'from_stage': request.from_stage.value,
                'to_stage': request.to_stage.value,
                'requested_date': request.requested_date.isoformat(),
                'requested_by': request.requested_by,
                'reason': request.reason,
                'status': request.status.value,
                'checklist_items': request.checklist_items
            })

    return jsonify({
        'portfolio_id': portfolio_id,
        'pending_transitions': pending,
        'total_count': len(pending)
    })


@app.route('/api/portfolios/<portfolio_id>/lifecycle/transitions', methods=['POST'])
def request_transition(portfolio_id):
    """Request a stage transition for an application."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    manager = get_lifecycle_manager(portfolio_id)
    data = request.get_json()

    app_id = data.get('app_id')
    to_stage = data.get('to_stage')
    requested_by = data.get('requested_by', 'System')
    reason = data.get('reason', '')

    if not app_id or not to_stage:
        return jsonify({'error': 'app_id and to_stage are required'}), 400

    try:
        stage = LifecycleStage(to_stage)
    except ValueError:
        return jsonify({'error': f'Invalid stage: {to_stage}'}), 400

    transition = manager.request_transition(app_id, stage, requested_by, reason)

    if not transition:
        return jsonify({'error': 'Invalid transition request'}), 400

    return jsonify({
        'success': True,
        'transition': {
            'id': transition.id,
            'app_id': transition.app_id,
            'from_stage': transition.from_stage.value,
            'to_stage': transition.to_stage.value,
            'status': transition.status.value,
            'checklist_items': transition.checklist_items
        }
    }), 201


@app.route('/api/portfolios/<portfolio_id>/lifecycle/transitions/<transition_id>/approve', methods=['POST'])
def approve_transition(portfolio_id, transition_id):
    """Approve a pending transition request."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    manager = get_lifecycle_manager(portfolio_id)
    data = request.get_json() or {}

    reviewed_by = data.get('reviewed_by', 'Admin')
    notes = data.get('notes', '')

    success = manager.approve_transition(transition_id, reviewed_by, notes)

    if not success:
        return jsonify({'error': 'Could not approve transition'}), 400

    return jsonify({
        'success': True,
        'message': 'Transition approved'
    })


@app.route('/api/portfolios/<portfolio_id>/lifecycle/transitions/<transition_id>/complete', methods=['POST'])
def complete_transition(portfolio_id, transition_id):
    """Complete an approved transition."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    manager = get_lifecycle_manager(portfolio_id)

    success = manager.complete_transition(transition_id)

    if not success:
        return jsonify({'error': 'Could not complete transition - must be approved first'}), 400

    return jsonify({
        'success': True,
        'message': 'Transition completed'
    })


@app.route('/api/portfolios/<portfolio_id>/lifecycle/sunset-plans', methods=['GET'])
def get_sunset_plans(portfolio_id):
    """Get all sunset plans for a portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    manager = get_lifecycle_manager(portfolio_id)

    plans = []
    for plan_id, plan in manager.sunset_plans.items():
        plans.append({
            'id': plan.id,
            'app_id': plan.app_id,
            'app_name': plan.app_name,
            'reason': plan.reason.value,
            'target_date': plan.target_date.isoformat(),
            'replacement_app_id': plan.replacement_app_id,
            'replacement_app_name': plan.replacement_app_name,
            'status': plan.status.value,
            'progress_percentage': plan.progress_percentage,
            'estimated_savings': plan.estimated_savings,
            'migration_steps_count': len(plan.migration_steps),
            'risks_count': len(plan.risks)
        })

    return jsonify({
        'portfolio_id': portfolio_id,
        'sunset_plans': plans,
        'total_count': len(plans)
    })


@app.route('/api/portfolios/<portfolio_id>/lifecycle/sunset-plans/<plan_id>', methods=['GET'])
def get_sunset_plan_detail(portfolio_id, plan_id):
    """Get detailed sunset plan information."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    manager = get_lifecycle_manager(portfolio_id)

    plan = manager.sunset_plans.get(plan_id)
    if not plan:
        return jsonify({'error': 'Sunset plan not found'}), 404

    return jsonify({
        'portfolio_id': portfolio_id,
        'id': plan.id,
        'app_id': plan.app_id,
        'app_name': plan.app_name,
        'reason': plan.reason.value,
        'target_date': plan.target_date.isoformat(),
        'replacement_app_id': plan.replacement_app_id,
        'replacement_app_name': plan.replacement_app_name,
        'migration_steps': plan.migration_steps,
        'stakeholders': plan.stakeholders,
        'communication_plan': plan.communication_plan,
        'data_retention_policy': plan.data_retention_policy,
        'rollback_plan': plan.rollback_plan,
        'estimated_savings': plan.estimated_savings,
        'risks': plan.risks,
        'status': plan.status.value,
        'progress_percentage': plan.progress_percentage
    })


@app.route('/api/portfolios/<portfolio_id>/lifecycle/sunset-plans', methods=['POST'])
def create_sunset_plan(portfolio_id):
    """Create a new sunset plan."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    manager = get_lifecycle_manager(portfolio_id)
    data = request.get_json()

    app_id = data.get('app_id')
    reason = data.get('reason', 'end_of_life')
    target_date_str = data.get('target_date')
    replacement_app_id = data.get('replacement_app_id')
    estimated_savings = data.get('estimated_savings', 0)

    if not app_id:
        return jsonify({'error': 'app_id is required'}), 400

    try:
        sunset_reason = SunsetReason(reason)
    except ValueError:
        return jsonify({'error': f'Invalid reason: {reason}'}), 400

    target_date = datetime.now() + timedelta(days=180)
    if target_date_str:
        try:
            target_date = datetime.fromisoformat(target_date_str)
        except ValueError:
            return jsonify({'error': 'Invalid target_date format'}), 400

    plan = manager.create_sunset_plan(
        app_id=app_id,
        reason=sunset_reason,
        target_date=target_date,
        replacement_app_id=replacement_app_id,
        estimated_savings=estimated_savings
    )

    if not plan:
        return jsonify({'error': 'Could not create sunset plan'}), 400

    return jsonify({
        'success': True,
        'plan': {
            'id': plan.id,
            'app_id': plan.app_id,
            'app_name': plan.app_name,
            'reason': plan.reason.value,
            'target_date': plan.target_date.isoformat()
        }
    }), 201


@app.route('/api/portfolios/<portfolio_id>/lifecycle/stages', methods=['GET'])
def get_stage_definitions(portfolio_id):
    """Get lifecycle stage definitions and metadata."""
    return jsonify({
        'stages': [
            {
                'value': stage.value,
                'name': stage.name,
                'order': i,
                'expected_duration_days': LifecycleManager.STAGE_DURATIONS.get(stage, 365),
                'checklist': LifecycleManager.TRANSITION_CHECKLISTS.get(stage, [])
            }
            for i, stage in enumerate(LifecycleManager.STAGE_ORDER)
        ],
        'health_statuses': [status.value for status in HealthStatus],
        'sunset_reasons': [reason.value for reason in SunsetReason],
        'transition_statuses': [status.value for status in TransitionStatus]
    })


@app.route('/lifecycle/<portfolio_id>')
def lifecycle_page(portfolio_id):
    """Application lifecycle management page."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()
    return render_template('lifecycle.html', portfolio=portfolio, applications=applications)


# =============================================================================
# TIER 3: ML CLUSTERING API
# =============================================================================

@app.route('/api/clustering/<portfolio_id>/analyze', methods=['POST'])
def api_clustering_analyze(portfolio_id):
    """Run ML clustering analysis on portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    applications = portfolio.applications.all()
    engine = create_clustering_engine()

    if not applications:
        demo_apps = create_demo_applications(25)
        engine.add_applications(demo_apps)
    else:
        for app in applications:
            features = ApplicationFeatures(
                app_id=str(app.id), app_name=app.name,
                business_value=app.business_value / 100 if app.business_value else 0.5,
                technical_health=app.technical_health / 100 if app.technical_health else 0.5,
                cost_efficiency=0.5, risk_score=app.risk_score / 100 if app.risk_score else 0.3,
                user_adoption=0.5, integration_complexity=0.5, compliance_score=0.7, modernization_readiness=0.5,
                category=app.category or '', vendor=app.vendor or '',
                annual_cost=app.cost or 0, user_count=app.user_base_size or 0
            )
            engine.add_application(features)

    data = request.get_json() or {}
    result = engine.cluster_applications(method=ClusteringMethod.KMEANS, num_clusters=data.get('num_clusters'))
    return jsonify(result.to_dict())


@app.route('/clustering/<portfolio_id>')
def clustering_page(portfolio_id):
    """ML Clustering analysis page."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    return render_template('clustering.html', portfolio=portfolio, applications=portfolio.applications.all())


# =============================================================================
# TIER 3: MIGRATION PLANNER API
# =============================================================================

@app.route('/api/migration/<portfolio_id>/plan', methods=['POST'])
def api_migration_plan(portfolio_id):
    """Generate migration plan for portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    data = request.get_json() or {}
    provider = CloudProvider(data.get('provider', 'aws')) if data.get('provider') in [p.value for p in CloudProvider] else CloudProvider.AWS
    planner = create_migration_planner(preferred_provider=provider)

    applications = portfolio.applications.all()
    if not applications:
        planner.add_applications(create_demo_migration_profiles(15))
    else:
        for app in applications:
            profile = ApplicationMigrationProfile(
                app_id=str(app.id), app_name=app.name,
                cloud_readiness=app.technical_health / 100 if app.technical_health else 0.5,
                business_criticality=app.business_value / 100 if app.business_value else 0.5,
                technical_debt=1 - (app.technical_health / 100) if app.technical_health else 0.3,
                current_annual_cost=app.cost or 0, estimated_users=app.user_base_size or 0
            )
            planner.add_application(profile)

    plan = planner.create_migration_plan(portfolio_name=portfolio.name)
    return jsonify(plan.to_dict())


@app.route('/migration/<portfolio_id>')
def migration_page(portfolio_id):
    """Migration planner page."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    return render_template('migration.html', portfolio=portfolio, applications=portfolio.applications.all())


# =============================================================================
# TIER 3: PORTFOLIO DASHBOARD API
# =============================================================================

@app.route('/api/portfolio-dashboard/<portfolio_id>')
def api_portfolio_dashboard(portfolio_id):
    """Get executive portfolio dashboard data."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    engine = create_portfolio_dashboard_engine()

    applications = portfolio.applications.all()
    if not applications:
        engine.add_applications(create_demo_portfolio_data(25))
    else:
        for app in applications:
            app_data = ApplicationData(
                app_id=str(app.id), app_name=app.name,
                annual_cost=app.cost or 0, user_count=app.user_base_size or 0, age_years=3.0,
                business_value=app.business_value / 100 if app.business_value else 0.5,
                technical_health=app.technical_health / 100 if app.technical_health else 0.5,
                risk_score=app.risk_score / 100 if app.risk_score else 0.3,
                time_recommendation=app.time_category or 'tolerate',
                category=app.category or '', vendor=app.vendor or ''
            )
            engine.add_application(app_data)

    dashboard = engine.generate_dashboard(portfolio_id, portfolio.name)
    return jsonify(dashboard.to_dict())


@app.route('/executive-dashboard/<portfolio_id>')
def executive_dashboard_page(portfolio_id):
    """Executive portfolio dashboard page."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    return render_template('executive_dashboard.html', portfolio=portfolio, applications=portfolio.applications.all())


# =============================================================================
# TIER 3: BUDGET OPTIMIZER API
# =============================================================================

@app.route('/api/budget/<portfolio_id>/optimize', methods=['POST'])
def api_budget_optimize(portfolio_id):
    """Optimize budget allocation for portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    data = request.get_json() or {}
    total_budget = data.get('total_budget', 1000000)
    optimizer = create_budget_optimizer()

    applications = portfolio.applications.all()
    if not applications:
        optimizer.add_applications(create_demo_budget_profiles(20))
    else:
        for app in applications:
            profile = ApplicationBudgetProfile(
                app_id=str(app.id), app_name=app.name,
                current_budget=app.cost or 50000, current_cost=app.cost or 50000,
                business_value=app.business_value / 100 if app.business_value else 0.5,
                technical_health=app.technical_health / 100 if app.technical_health else 0.5,
                risk_score=app.risk_score / 100 if app.risk_score else 0.3,
                category=app.category or ''
            )
            optimizer.add_application(profile)

    result = optimizer.full_optimization(total_budget=total_budget,
        include_what_if=data.get('include_what_if', True),
        include_multi_year=data.get('include_multi_year', True))
    return jsonify(result.to_dict())


@app.route('/budget/<portfolio_id>')
def budget_page(portfolio_id):
    """Budget optimization page."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    return render_template('budget.html', portfolio=portfolio, applications=portfolio.applications.all())


# =============================================================================
# TIER 3: RISK HEAT MAP API
# =============================================================================

@app.route('/api/risk-heatmap/<portfolio_id>')
def api_risk_heatmap(portfolio_id):
    """Get risk heat map data for portfolio."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    engine = create_risk_heatmap_engine()

    applications = portfolio.applications.all()
    if not applications:
        engine.add_applications(create_demo_risk_profiles(25))
    else:
        for app in applications:
            profile = create_demo_risk_profiles(1)[0]
            profile.app_id = str(app.id)
            profile.app_name = app.name
            profile.category = app.category or 'General'
            profile.vendor = app.vendor or 'Unknown'
            engine.add_application(profile)

    result = engine.generate_analysis()
    return jsonify(result.to_dict())


@app.route('/risk-heatmap/<portfolio_id>')
def risk_heatmap_page(portfolio_id):
    """Risk heat map page."""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    return render_template('risk_heatmap.html', portfolio=portfolio, applications=portfolio.applications.all())


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
    app.run(debug=True, port=5102)
