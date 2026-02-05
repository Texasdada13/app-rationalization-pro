"""
Risk Assessment Framework for App Rationalization Pro

Multi-dimensional risk scoring with compliance tracking and risk mitigation recommendations.
Ported from pandas-based implementation to native Python.
"""

from typing import Dict, List, Any
from collections import defaultdict


class RiskAssessmentFramework:
    """
    Comprehensive risk assessment for application portfolio.

    Assesses risk across 5 dimensions:
    - Technical Risk (30%): Tech health, age, complexity
    - Business Risk (25%): Business criticality, downtime impact
    - Security Risk (20%): Security vulnerabilities, compliance
    - Operational Risk (15%): Support, dependencies, integration
    - Financial Risk (10%): Cost volatility, vendor lock-in

    Risk levels: Critical, High, Medium, Low, Minimal
    """

    # Risk dimension weights
    RISK_WEIGHTS = {
        'technical_risk': 0.30,
        'business_risk': 0.25,
        'security_risk': 0.20,
        'operational_risk': 0.15,
        'financial_risk': 0.10
    }

    # Risk severity thresholds
    RISK_LEVELS = {
        'critical': (80, 100),    # Immediate action required
        'high': (60, 80),         # Priority attention needed
        'medium': (40, 60),       # Monitor closely
        'low': (20, 40),          # Standard monitoring
        'minimal': (0, 20)        # Low concern
    }

    # Compliance frameworks
    COMPLIANCE_FRAMEWORKS = {
        'SOX': {'critical_controls': 5, 'weight': 0.3},
        'HIPAA': {'critical_controls': 8, 'weight': 0.25},
        'PCI-DSS': {'critical_controls': 6, 'weight': 0.2},
        'GDPR': {'critical_controls': 7, 'weight': 0.15},
        'SOC2': {'critical_controls': 4, 'weight': 0.1}
    }

    def __init__(self, applications: List[Dict[str, Any]]):
        """
        Initialize with application portfolio data.

        Args:
            applications: List of application dictionaries with keys:
                - name: Application name
                - cost: Annual cost
                - tech_health: Technical health score (0-10)
                - business_value: Business value score (0-10)
                - category: Application category
                - description: Optional description
        """
        self.applications = [app.copy() for app in applications]
        self.max_cost = max((app.get('cost', 0) for app in self.applications), default=1)
        self.risk_assessments = {}
        self.compliance_gaps = []

    def assess_technical_risk(self, app: Dict) -> Dict[str, Any]:
        """Assess technical risk based on health, age, and complexity."""
        health = app.get('tech_health', 5)
        cost = app.get('cost', 0)

        # Health-based risk (inverse relationship)
        health_risk = (10 - health) * 10  # 0-100 scale

        # Complexity risk (estimated from cost and category)
        category = str(app.get('category', '')).lower()
        complexity_multiplier = 1.0

        if any(kw in category for kw in ['core', 'critical']):
            complexity_multiplier = 1.5
        elif 'infrastructure' in category:
            complexity_multiplier = 1.3
        elif any(kw in category for kw in ['utility', 'standalone']):
            complexity_multiplier = 0.7

        complexity_risk = min(100, (cost / 100000) * 50 * complexity_multiplier)

        # Technology obsolescence risk (poor health = likely old tech)
        obsolescence_risk = health_risk * 0.8

        # Calculate weighted technical risk
        technical_risk = (
            health_risk * 0.4 +
            complexity_risk * 0.35 +
            obsolescence_risk * 0.25
        )

        return {
            'technical_risk_score': round(technical_risk, 1),
            'health_risk': round(health_risk, 1),
            'complexity_risk': round(complexity_risk, 1),
            'obsolescence_risk': round(obsolescence_risk, 1),
            'risk_factors': self._identify_technical_risk_factors(health, complexity_risk, obsolescence_risk)
        }

    def _identify_technical_risk_factors(self, health: float, complexity: float, obsolescence: float) -> List[str]:
        """Identify specific technical risk factors."""
        factors = []

        if health <= 3:
            factors.append('Critical technical health')
        elif health <= 5:
            factors.append('Poor technical health')

        if complexity >= 70:
            factors.append('High complexity system')
        elif complexity >= 50:
            factors.append('Moderate complexity')

        if obsolescence >= 60:
            factors.append('Technology obsolescence risk')

        return factors

    def assess_business_risk(self, app: Dict) -> Dict[str, Any]:
        """Assess business risk based on criticality and impact."""
        business_value = app.get('business_value', 5)

        # Criticality risk (high value = high risk if it fails)
        criticality_risk = business_value * 10  # Scale to 0-100

        # Downtime impact (estimated from business value)
        downtime_impact = criticality_risk * 0.9

        # Business continuity risk
        continuity_risk = criticality_risk * 0.8 if business_value >= 7 else 30

        # Calculate weighted business risk
        business_risk = (
            criticality_risk * 0.5 +
            downtime_impact * 0.3 +
            continuity_risk * 0.2
        )

        return {
            'business_risk_score': round(business_risk, 1),
            'criticality_risk': round(criticality_risk, 1),
            'downtime_impact': round(downtime_impact, 1),
            'continuity_risk': round(continuity_risk, 1),
            'risk_factors': self._identify_business_risk_factors(business_value, criticality_risk)
        }

    def _identify_business_risk_factors(self, business_value: float, criticality: float) -> List[str]:
        """Identify specific business risk factors."""
        factors = []

        if business_value >= 9:
            factors.append('Mission-critical application')
        elif business_value >= 7:
            factors.append('High business value')

        if criticality >= 80:
            factors.append('Single point of failure risk')

        return factors

    def assess_security_risk(self, app: Dict) -> Dict[str, Any]:
        """Assess security risk based on health and compliance requirements."""
        health = app.get('tech_health', 5)
        business_value = app.get('business_value', 5)
        security = app.get('security', 5)

        # Vulnerability risk (poor health/security = likely security issues)
        vulnerability_risk = (10 - min(health, security)) * 10

        # Data sensitivity risk (high value apps likely handle sensitive data)
        data_sensitivity = business_value * 8

        # Compliance risk (estimated from category)
        compliance_risk = 50  # Default medium risk
        category = str(app.get('category', '')).lower()

        if any(kw in category for kw in ['financial', 'payment', 'banking']):
            compliance_risk = 85  # PCI-DSS
        elif any(kw in category for kw in ['healthcare', 'patient', 'medical']):
            compliance_risk = 90  # HIPAA
        elif any(kw in category for kw in ['hr', 'personnel', 'employee']):
            compliance_risk = 70  # GDPR

        # Calculate weighted security risk
        security_risk = (
            vulnerability_risk * 0.4 +
            data_sensitivity * 0.35 +
            compliance_risk * 0.25
        )

        return {
            'security_risk_score': round(security_risk, 1),
            'vulnerability_risk': round(vulnerability_risk, 1),
            'data_sensitivity': round(data_sensitivity, 1),
            'compliance_risk': round(compliance_risk, 1),
            'risk_factors': self._identify_security_risk_factors(vulnerability_risk, data_sensitivity, compliance_risk)
        }

    def _identify_security_risk_factors(self, vulnerability: float, sensitivity: float, compliance: float) -> List[str]:
        """Identify specific security risk factors."""
        factors = []

        if vulnerability >= 70:
            factors.append('High vulnerability exposure')
        elif vulnerability >= 50:
            factors.append('Moderate vulnerability risk')

        if sensitivity >= 70:
            factors.append('Handles sensitive data')

        if compliance >= 70:
            factors.append('High compliance requirements')

        return factors

    def assess_operational_risk(self, app: Dict) -> Dict[str, Any]:
        """Assess operational risk based on support and dependencies."""
        health = app.get('tech_health', 5)
        description = str(app.get('description', '') or '').lower()

        # Support risk (poor health = difficult to support)
        support_risk = (10 - health) * 8

        # Dependency risk (look for integration keywords)
        dependency_count = 0
        dependency_keywords = ['integrates', 'depends', 'requires', 'connects', 'interfaces']
        for keyword in dependency_keywords:
            if keyword in description:
                dependency_count += 1

        dependency_risk = min(100, dependency_count * 25)

        # Vendor risk (check for vendor dependencies)
        vendor_risk = 40  # Default
        if any(kw in description for kw in ['vendor', 'third-party', 'saas', 'cloud']):
            vendor_risk = 70

        # Calculate weighted operational risk
        operational_risk = (
            support_risk * 0.4 +
            dependency_risk * 0.35 +
            vendor_risk * 0.25
        )

        return {
            'operational_risk_score': round(operational_risk, 1),
            'support_risk': round(support_risk, 1),
            'dependency_risk': round(dependency_risk, 1),
            'vendor_risk': round(vendor_risk, 1),
            'risk_factors': self._identify_operational_risk_factors(support_risk, dependency_risk, vendor_risk)
        }

    def _identify_operational_risk_factors(self, support: float, dependency: float, vendor: float) -> List[str]:
        """Identify specific operational risk factors."""
        factors = []

        if support >= 60:
            factors.append('High support complexity')

        if dependency >= 50:
            factors.append('Multiple dependencies')

        if vendor >= 60:
            factors.append('Vendor lock-in risk')

        return factors

    def assess_financial_risk(self, app: Dict) -> Dict[str, Any]:
        """Assess financial risk based on cost and volatility."""
        cost = app.get('cost', 0)
        health = app.get('tech_health', 5)

        # Cost exposure risk
        cost_exposure = min(100, (cost / 500000) * 100)

        # Maintenance cost volatility (poor health = unpredictable costs)
        maintenance_volatility = (10 - health) * 7

        # Budget overrun risk
        budget_risk = (cost_exposure * 0.6 + maintenance_volatility * 0.4)

        # Calculate weighted financial risk
        financial_risk = (
            cost_exposure * 0.5 +
            maintenance_volatility * 0.3 +
            budget_risk * 0.2
        )

        return {
            'financial_risk_score': round(financial_risk, 1),
            'cost_exposure': round(cost_exposure, 1),
            'maintenance_volatility': round(maintenance_volatility, 1),
            'budget_risk': round(budget_risk, 1),
            'risk_factors': self._identify_financial_risk_factors(cost_exposure, maintenance_volatility)
        }

    def _identify_financial_risk_factors(self, exposure: float, volatility: float) -> List[str]:
        """Identify specific financial risk factors."""
        factors = []

        if exposure >= 70:
            factors.append('High cost exposure')

        if volatility >= 60:
            factors.append('Unpredictable maintenance costs')

        return factors

    def calculate_composite_risk(self, app: Dict) -> Dict[str, Any]:
        """Calculate composite risk score across all dimensions."""
        technical = self.assess_technical_risk(app)
        business = self.assess_business_risk(app)
        security = self.assess_security_risk(app)
        operational = self.assess_operational_risk(app)
        financial = self.assess_financial_risk(app)

        # Calculate weighted composite score
        composite_score = (
            technical['technical_risk_score'] * self.RISK_WEIGHTS['technical_risk'] +
            business['business_risk_score'] * self.RISK_WEIGHTS['business_risk'] +
            security['security_risk_score'] * self.RISK_WEIGHTS['security_risk'] +
            operational['operational_risk_score'] * self.RISK_WEIGHTS['operational_risk'] +
            financial['financial_risk_score'] * self.RISK_WEIGHTS['financial_risk']
        )

        # Determine risk level
        risk_level = self._get_risk_level(composite_score)

        # Aggregate risk factors
        all_factors = (
            technical['risk_factors'] +
            business['risk_factors'] +
            security['risk_factors'] +
            operational['risk_factors'] +
            financial['risk_factors']
        )

        return {
            'app_name': app.get('name', ''),
            'composite_risk_score': round(composite_score, 1),
            'risk_level': risk_level,
            'technical_risk': technical,
            'business_risk': business,
            'security_risk': security,
            'operational_risk': operational,
            'financial_risk': financial,
            'risk_factors': all_factors,
            'mitigation_priority': self._calculate_mitigation_priority(composite_score, business['business_risk_score'])
        }

    def _get_risk_level(self, score: float) -> str:
        """Determine risk level from score."""
        for level, (min_score, max_score) in self.RISK_LEVELS.items():
            if min_score <= score < max_score:
                return level
        return 'minimal'

    def _calculate_mitigation_priority(self, composite_score: float, business_risk: float) -> str:
        """Calculate mitigation priority (risk + business impact)."""
        # High risk + high business impact = urgent
        if composite_score >= 70 and business_risk >= 70:
            return 'urgent'
        elif composite_score >= 60 or business_risk >= 80:
            return 'high'
        elif composite_score >= 40:
            return 'medium'
        else:
            return 'low'

    def assess_portfolio(self) -> Dict[str, Any]:
        """Assess risk for entire portfolio."""
        assessments = []

        for app in self.applications:
            assessment = self.calculate_composite_risk(app)
            assessments.append(assessment)
            self.risk_assessments[app.get('name', '')] = assessment

        # Sort by composite risk score
        assessments.sort(key=lambda x: x['composite_risk_score'], reverse=True)

        # Calculate portfolio-level metrics
        risk_scores = [a['composite_risk_score'] for a in assessments]

        if risk_scores:
            avg_risk = sum(risk_scores) / len(risk_scores)
            max_risk = max(risk_scores)
            min_risk = min(risk_scores)
            # Calculate standard deviation
            variance = sum((x - avg_risk) ** 2 for x in risk_scores) / len(risk_scores)
            std_dev = variance ** 0.5
        else:
            avg_risk = max_risk = min_risk = std_dev = 0

        # Risk distribution
        risk_distribution = defaultdict(int)
        for assessment in assessments:
            risk_distribution[assessment['risk_level']] += 1

        # Priority distribution
        priority_distribution = defaultdict(int)
        for assessment in assessments:
            priority_distribution[assessment['mitigation_priority']] += 1

        return {
            'assessments': assessments,
            'portfolio_metrics': {
                'total_applications': len(assessments),
                'avg_risk_score': round(avg_risk, 1),
                'max_risk_score': round(max_risk, 1),
                'min_risk_score': round(min_risk, 1),
                'std_dev': round(std_dev, 1)
            },
            'risk_distribution': dict(risk_distribution),
            'priority_distribution': dict(priority_distribution),
            'high_risk_apps': [a for a in assessments if a['risk_level'] in ['critical', 'high']],
            'urgent_apps': [a for a in assessments if a['mitigation_priority'] == 'urgent']
        }

    def check_compliance(self, framework: str = 'SOX') -> Dict[str, Any]:
        """Check compliance against specified framework."""
        if framework not in self.COMPLIANCE_FRAMEWORKS:
            return {'error': f'Unknown framework: {framework}'}

        framework_config = self.COMPLIANCE_FRAMEWORKS[framework]
        critical_controls = framework_config['critical_controls']

        compliance_issues = []

        for app in self.applications:
            app_name = app.get('name', '')
            health = app.get('tech_health', 5)
            security = app.get('security', 5)
            business_value = app.get('business_value', 5)

            # Calculate compliance score (based on health and security)
            compliance_score = ((health + security) / 2) * 10  # 0-100 scale

            # Check for critical apps with low compliance
            if business_value >= 7 and compliance_score < 60:
                compliance_issues.append({
                    'app_name': app_name,
                    'framework': framework,
                    'compliance_score': round(compliance_score, 1),
                    'gap': round(100 - compliance_score, 1),
                    'business_value': business_value,
                    'severity': 'critical' if compliance_score < 40 else 'high',
                    'required_controls': critical_controls,
                    'recommendation': f'Immediate compliance review required for {framework}'
                })

        # Calculate framework compliance rate
        total_apps = len(self.applications)
        compliant_apps = total_apps - len(compliance_issues)
        compliance_rate = (compliant_apps / total_apps * 100) if total_apps > 0 else 0

        return {
            'framework': framework,
            'compliance_rate': round(compliance_rate, 1),
            'total_applications': total_apps,
            'compliant_applications': compliant_apps,
            'non_compliant_applications': len(compliance_issues),
            'compliance_issues': compliance_issues,
            'critical_issues': [i for i in compliance_issues if i['severity'] == 'critical'],
            'recommendation': self._generate_compliance_recommendation(compliance_rate, len(compliance_issues))
        }

    def _generate_compliance_recommendation(self, compliance_rate: float, issue_count: int) -> str:
        """Generate compliance recommendation."""
        if compliance_rate >= 95:
            return 'Excellent compliance posture - maintain current controls'
        elif compliance_rate >= 80:
            return f'Good compliance - address {issue_count} identified gaps'
        elif compliance_rate >= 60:
            return f'Moderate compliance - urgent action needed on {issue_count} issues'
        else:
            return f'Critical compliance gaps - immediate remediation required for {issue_count} issues'

    def generate_mitigation_plan(self, app_name: str) -> Dict[str, Any]:
        """Generate risk mitigation plan for specific application."""
        if app_name not in self.risk_assessments:
            return {'error': 'Application not assessed'}

        assessment = self.risk_assessments[app_name]
        recommendations = []

        # Technical risk mitigation
        if assessment['technical_risk']['technical_risk_score'] >= 60:
            recommendations.append({
                'area': 'Technical',
                'priority': 'high',
                'action': 'Modernization or technology refresh',
                'rationale': 'High technical risk detected',
                'estimated_effort': 'high',
                'timeline': '6-12 months'
            })

        # Security risk mitigation
        if assessment['security_risk']['security_risk_score'] >= 60:
            recommendations.append({
                'area': 'Security',
                'priority': 'urgent',
                'action': 'Security audit and vulnerability remediation',
                'rationale': 'High security risk exposure',
                'estimated_effort': 'medium',
                'timeline': '1-3 months'
            })

        # Operational risk mitigation
        if assessment['operational_risk']['operational_risk_score'] >= 60:
            recommendations.append({
                'area': 'Operational',
                'priority': 'medium',
                'action': 'Improve monitoring and reduce dependencies',
                'rationale': 'High operational complexity',
                'estimated_effort': 'medium',
                'timeline': '3-6 months'
            })

        # Financial risk mitigation
        if assessment['financial_risk']['financial_risk_score'] >= 60:
            recommendations.append({
                'area': 'Financial',
                'priority': 'medium',
                'action': 'Cost optimization and budget stabilization',
                'rationale': 'High financial exposure',
                'estimated_effort': 'low',
                'timeline': '1-2 months'
            })

        return {
            'app_name': app_name,
            'current_risk_level': assessment['risk_level'],
            'composite_score': assessment['composite_risk_score'],
            'mitigation_priority': assessment['mitigation_priority'],
            'recommendations': recommendations,
            'total_recommendations': len(recommendations),
            'estimated_cost_reduction': self._estimate_risk_reduction_cost(assessment)
        }

    def _estimate_risk_reduction_cost(self, assessment: Dict) -> float:
        """Estimate cost of risk reduction initiatives."""
        base_cost = 50000  # Base mitigation cost

        # Scale by composite risk score
        risk_multiplier = assessment['composite_risk_score'] / 100

        # Adjust for risk areas
        area_count = sum([
            1 if assessment['technical_risk']['technical_risk_score'] >= 60 else 0,
            1 if assessment['security_risk']['security_risk_score'] >= 60 else 0,
            1 if assessment['operational_risk']['operational_risk_score'] >= 60 else 0,
            1 if assessment['financial_risk']['financial_risk_score'] >= 60 else 0
        ])

        total_cost = base_cost * risk_multiplier * (1 + area_count * 0.3)

        return round(total_cost, 0)

    def get_risk_heatmap_data(self) -> List[Dict[str, Any]]:
        """Generate data for risk heatmap visualization."""
        heatmap_data = []

        for app in self.applications:
            app_name = app.get('name', '')
            if app_name in self.risk_assessments:
                assessment = self.risk_assessments[app_name]
                heatmap_data.append({
                    'app_name': app_name,
                    'business_value': app.get('business_value', 5),
                    'composite_risk': assessment['composite_risk_score'],
                    'risk_level': assessment['risk_level'],
                    'mitigation_priority': assessment['mitigation_priority'],
                    'cost': app.get('cost', 0)
                })

        return heatmap_data

    def get_risk_summary(self) -> Dict[str, Any]:
        """Get a simplified risk summary for API responses."""
        portfolio = self.assess_portfolio()

        return {
            'portfolio_metrics': portfolio['portfolio_metrics'],
            'risk_distribution': portfolio['risk_distribution'],
            'priority_distribution': portfolio['priority_distribution'],
            'high_risk_count': len(portfolio['high_risk_apps']),
            'urgent_count': len(portfolio['urgent_apps']),
            'top_risks': [
                {
                    'app_name': a['app_name'],
                    'risk_score': a['composite_risk_score'],
                    'risk_level': a['risk_level'],
                    'top_factors': a['risk_factors'][:3]
                }
                for a in portfolio['assessments'][:5]
            ]
        }
