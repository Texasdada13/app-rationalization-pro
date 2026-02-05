"""
Compliance Engine Module
Security & Compliance Assessment for SOX, PCI-DSS, HIPAA, GDPR frameworks.
Ported from application-rationalization-tool without pandas dependency.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import random


@dataclass
class ComplianceRequirement:
    """Individual compliance requirement."""
    id: str
    name: str
    description: str
    framework: str  # SOX, PCI-DSS, HIPAA, GDPR
    category: str   # e.g., "Data Security", "Access Control", "Audit Trail"
    severity: str   # Critical, High, Medium, Low
    weight: float = 1.0


@dataclass
class ComplianceFramework:
    """Compliance framework definition."""
    name: str
    description: str
    requirements: List[ComplianceRequirement] = field(default_factory=list)

    def add_requirement(self, requirement: ComplianceRequirement):
        self.requirements.append(requirement)

    def get_requirements_by_category(self, category: str) -> List[ComplianceRequirement]:
        return [r for r in self.requirements if r.category == category]


class ComplianceEngine:
    """
    Assesses applications against compliance frameworks.

    Features:
    - Multi-framework support (SOX, PCI-DSS, HIPAA, GDPR)
    - Automated compliance scoring
    - Gap analysis and remediation recommendations
    - Risk level assessment
    """

    def __init__(self):
        self.frameworks: Dict[str, ComplianceFramework] = {}
        self._initialize_frameworks()

    def _initialize_frameworks(self):
        """Initialize standard compliance frameworks."""

        # SOX (Sarbanes-Oxley) - Financial Controls
        sox = ComplianceFramework(
            name="SOX",
            description="Sarbanes-Oxley Act - Financial Reporting Controls"
        )
        sox.add_requirement(ComplianceRequirement(
            id="SOX-001", name="Data Integrity",
            description="Ensure accuracy and completeness of financial data",
            framework="SOX", category="Data Security", severity="Critical", weight=1.5
        ))
        sox.add_requirement(ComplianceRequirement(
            id="SOX-002", name="Access Controls",
            description="Implement role-based access controls for financial systems",
            framework="SOX", category="Access Control", severity="Critical", weight=1.5
        ))
        sox.add_requirement(ComplianceRequirement(
            id="SOX-003", name="Audit Trail",
            description="Maintain comprehensive audit logs for all financial transactions",
            framework="SOX", category="Audit Trail", severity="Critical", weight=1.5
        ))
        sox.add_requirement(ComplianceRequirement(
            id="SOX-004", name="Change Management",
            description="Document and approve all system changes",
            framework="SOX", category="Change Management", severity="High", weight=1.2
        ))
        sox.add_requirement(ComplianceRequirement(
            id="SOX-005", name="Segregation of Duties",
            description="Separate responsibilities to prevent fraud",
            framework="SOX", category="Access Control", severity="Critical", weight=1.5
        ))
        self.frameworks["SOX"] = sox

        # PCI-DSS (Payment Card Industry Data Security Standard)
        pci = ComplianceFramework(
            name="PCI-DSS",
            description="Payment Card Industry Data Security Standard"
        )
        pci.add_requirement(ComplianceRequirement(
            id="PCI-001", name="Encryption at Rest",
            description="Encrypt stored cardholder data",
            framework="PCI-DSS", category="Data Security", severity="Critical", weight=2.0
        ))
        pci.add_requirement(ComplianceRequirement(
            id="PCI-002", name="Encryption in Transit",
            description="Encrypt transmission of cardholder data across networks",
            framework="PCI-DSS", category="Data Security", severity="Critical", weight=2.0
        ))
        pci.add_requirement(ComplianceRequirement(
            id="PCI-003", name="Firewall Configuration",
            description="Install and maintain firewall to protect cardholder data",
            framework="PCI-DSS", category="Network Security", severity="Critical", weight=1.8
        ))
        pci.add_requirement(ComplianceRequirement(
            id="PCI-004", name="Vulnerability Management",
            description="Regular security scanning and patching",
            framework="PCI-DSS", category="Security Maintenance", severity="High", weight=1.5
        ))
        pci.add_requirement(ComplianceRequirement(
            id="PCI-005", name="Multi-Factor Authentication",
            description="Implement MFA for system access",
            framework="PCI-DSS", category="Access Control", severity="Critical", weight=1.8
        ))
        pci.add_requirement(ComplianceRequirement(
            id="PCI-006", name="Security Monitoring",
            description="Track and monitor all access to network resources",
            framework="PCI-DSS", category="Monitoring", severity="High", weight=1.5
        ))
        self.frameworks["PCI-DSS"] = pci

        # HIPAA (Health Insurance Portability and Accountability Act)
        hipaa = ComplianceFramework(
            name="HIPAA",
            description="Health Insurance Portability and Accountability Act"
        )
        hipaa.add_requirement(ComplianceRequirement(
            id="HIPAA-001", name="PHI Encryption",
            description="Encrypt Protected Health Information at rest and in transit",
            framework="HIPAA", category="Data Security", severity="Critical", weight=2.0
        ))
        hipaa.add_requirement(ComplianceRequirement(
            id="HIPAA-002", name="Access Controls",
            description="Implement unique user identification and authentication",
            framework="HIPAA", category="Access Control", severity="Critical", weight=1.8
        ))
        hipaa.add_requirement(ComplianceRequirement(
            id="HIPAA-003", name="Audit Controls",
            description="Implement mechanisms to record and examine activity",
            framework="HIPAA", category="Audit Trail", severity="Critical", weight=1.7
        ))
        hipaa.add_requirement(ComplianceRequirement(
            id="HIPAA-004", name="Data Backup",
            description="Establish and implement procedures for data backup",
            framework="HIPAA", category="Business Continuity", severity="High", weight=1.5
        ))
        hipaa.add_requirement(ComplianceRequirement(
            id="HIPAA-005", name="Breach Notification",
            description="Procedures for breach detection and notification",
            framework="HIPAA", category="Incident Response", severity="Critical", weight=1.8
        ))
        hipaa.add_requirement(ComplianceRequirement(
            id="HIPAA-006", name="Minimum Necessary",
            description="Limit PHI access to minimum necessary",
            framework="HIPAA", category="Access Control", severity="High", weight=1.4
        ))
        self.frameworks["HIPAA"] = hipaa

        # GDPR (General Data Protection Regulation)
        gdpr = ComplianceFramework(
            name="GDPR",
            description="General Data Protection Regulation (EU)"
        )
        gdpr.add_requirement(ComplianceRequirement(
            id="GDPR-001", name="Data Encryption",
            description="Pseudonymization and encryption of personal data",
            framework="GDPR", category="Data Security", severity="Critical", weight=1.8
        ))
        gdpr.add_requirement(ComplianceRequirement(
            id="GDPR-002", name="Right to Erasure",
            description="Capability to delete personal data upon request",
            framework="GDPR", category="Data Rights", severity="Critical", weight=1.7
        ))
        gdpr.add_requirement(ComplianceRequirement(
            id="GDPR-003", name="Data Portability",
            description="Ability to export data in machine-readable format",
            framework="GDPR", category="Data Rights", severity="High", weight=1.4
        ))
        gdpr.add_requirement(ComplianceRequirement(
            id="GDPR-004", name="Breach Notification",
            description="72-hour breach notification requirement",
            framework="GDPR", category="Incident Response", severity="Critical", weight=1.9
        ))
        gdpr.add_requirement(ComplianceRequirement(
            id="GDPR-005", name="Data Processing Records",
            description="Maintain records of processing activities",
            framework="GDPR", category="Audit Trail", severity="High", weight=1.5
        ))
        gdpr.add_requirement(ComplianceRequirement(
            id="GDPR-006", name="Privacy by Design",
            description="Data protection integrated into system design",
            framework="GDPR", category="System Design", severity="High", weight=1.6
        ))
        gdpr.add_requirement(ComplianceRequirement(
            id="GDPR-007", name="Consent Management",
            description="Obtain and manage user consent for data processing",
            framework="GDPR", category="Data Rights", severity="Critical", weight=1.7
        ))
        self.frameworks["GDPR"] = gdpr

    def assess_application(
        self,
        app: Dict[str, Any],
        framework_name: str,
        compliance_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess a single application against a compliance framework.

        Args:
            app: Application dict with name, security score, tech_health, etc.
            framework_name: Framework to assess (SOX, PCI-DSS, HIPAA, GDPR)
            compliance_data: Optional dict with compliance status per requirement

        Returns:
            Compliance assessment results
        """
        if framework_name not in self.frameworks:
            return {'error': f'Framework {framework_name} not found'}

        framework = self.frameworks[framework_name]
        app_name = app.get('name', 'Unknown')

        # If no compliance data, generate heuristics based on app characteristics
        if compliance_data is None:
            compliance_data = self._generate_compliance_heuristics(app, framework)

        requirement_results = []
        total_weight = 0
        weighted_score = 0

        for req in framework.requirements:
            req_data = compliance_data.get(req.id, {'status': 'non_compliant'})
            status = req_data.get('status', 'non_compliant')

            # Score: compliant=1.0, partial=0.5, non_compliant=0.0
            if status == 'compliant':
                score = 1.0
            elif status == 'partial':
                score = 0.5
            else:
                score = 0.0

            weighted_score += score * req.weight
            total_weight += req.weight

            requirement_results.append({
                'requirement_id': req.id,
                'requirement_name': req.name,
                'description': req.description,
                'category': req.category,
                'severity': req.severity,
                'status': status,
                'score': score,
                'weight': req.weight,
                'notes': req_data.get('notes', '')
            })

        # Calculate overall compliance percentage
        compliance_percentage = (weighted_score / total_weight * 100) if total_weight > 0 else 0

        # Determine compliance level
        if compliance_percentage >= 95:
            compliance_level = 'Fully Compliant'
            risk_level = 'Low'
        elif compliance_percentage >= 80:
            compliance_level = 'Substantially Compliant'
            risk_level = 'Medium'
        elif compliance_percentage >= 60:
            compliance_level = 'Partially Compliant'
            risk_level = 'High'
        else:
            compliance_level = 'Non-Compliant'
            risk_level = 'Critical'

        # Identify gaps
        gaps = [r for r in requirement_results if r['status'] != 'compliant']
        critical_gaps = [r for r in gaps if r['severity'] == 'Critical']

        return {
            'application_name': app_name,
            'application_id': app.get('id'),
            'framework': framework_name,
            'assessment_date': datetime.now().isoformat(),
            'compliance_percentage': round(compliance_percentage, 2),
            'compliance_level': compliance_level,
            'risk_level': risk_level,
            'total_requirements': len(framework.requirements),
            'compliant_count': len([r for r in requirement_results if r['status'] == 'compliant']),
            'partial_count': len([r for r in requirement_results if r['status'] == 'partial']),
            'non_compliant_count': len([r for r in requirement_results if r['status'] == 'non_compliant']),
            'critical_gaps_count': len(critical_gaps),
            'requirement_results': requirement_results,
            'gaps': gaps,
            'critical_gaps': critical_gaps
        }

    def _generate_compliance_heuristics(
        self,
        app: Dict[str, Any],
        framework: ComplianceFramework
    ) -> Dict[str, Dict[str, str]]:
        """Generate compliance estimates based on app characteristics."""
        # Use Security score and Tech Health as compliance indicators
        security_score = (app.get('security', 5) or 5) / 10  # Normalize to 0-1
        tech_health = (app.get('tech_health', 5) or 5) / 10

        # Average as base compliance probability
        base_compliance = (security_score + tech_health) / 2

        req_statuses = {}
        for req in framework.requirements:
            # Higher severity requirements are harder to meet
            severity_modifier = {
                'Critical': -0.15,
                'High': -0.10,
                'Medium': -0.05,
                'Low': 0
            }.get(req.severity, 0)

            probability = base_compliance + severity_modifier
            random_factor = random.random()

            if random_factor < probability:
                status = 'compliant'
            elif random_factor < probability + 0.2:
                status = 'partial'
            else:
                status = 'non_compliant'

            req_statuses[req.id] = {'status': status}

        return req_statuses

    def batch_assess(
        self,
        applications: List[Dict[str, Any]],
        framework_name: str
    ) -> Dict[str, Any]:
        """
        Assess multiple applications against a framework.

        Returns:
            Portfolio-wide compliance summary
        """
        if framework_name not in self.frameworks:
            return {'error': f'Framework {framework_name} not found'}

        assessments = []
        for app in applications:
            assessment = self.assess_application(app, framework_name)
            assessments.append(assessment)

        # Calculate portfolio statistics
        avg_compliance = sum(a['compliance_percentage'] for a in assessments) / len(assessments) if assessments else 0

        return {
            'framework': framework_name,
            'assessment_date': datetime.now().isoformat(),
            'portfolio_summary': {
                'total_applications': len(assessments),
                'avg_compliance_percentage': round(avg_compliance, 2),
                'fully_compliant': len([a for a in assessments if a['compliance_level'] == 'Fully Compliant']),
                'substantially_compliant': len([a for a in assessments if a['compliance_level'] == 'Substantially Compliant']),
                'partially_compliant': len([a for a in assessments if a['compliance_level'] == 'Partially Compliant']),
                'non_compliant': len([a for a in assessments if a['compliance_level'] == 'Non-Compliant']),
                'critical_risk_apps': len([a for a in assessments if a['risk_level'] == 'Critical']),
                'high_risk_apps': len([a for a in assessments if a['risk_level'] == 'High'])
            },
            'risk_distribution': {
                'Low': len([a for a in assessments if a['risk_level'] == 'Low']),
                'Medium': len([a for a in assessments if a['risk_level'] == 'Medium']),
                'High': len([a for a in assessments if a['risk_level'] == 'High']),
                'Critical': len([a for a in assessments if a['risk_level'] == 'Critical'])
            },
            'application_assessments': assessments,
            'remediation_priorities': self._generate_remediation_priorities(assessments)
        }

    def _generate_remediation_priorities(
        self,
        assessments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate prioritized remediation recommendations."""
        # Collect all critical gaps across applications
        gap_summary = {}

        for assessment in assessments:
            for gap in assessment.get('critical_gaps', []):
                req_id = gap['requirement_id']
                if req_id not in gap_summary:
                    gap_summary[req_id] = {
                        'requirement_id': req_id,
                        'requirement_name': gap['requirement_name'],
                        'category': gap['category'],
                        'severity': gap['severity'],
                        'affected_apps': [],
                        'affected_count': 0
                    }
                gap_summary[req_id]['affected_apps'].append(assessment['application_name'])
                gap_summary[req_id]['affected_count'] += 1

        # Sort by severity and affected count
        priorities = list(gap_summary.values())
        priorities.sort(key=lambda x: (
            -{'Critical': 3, 'High': 2, 'Medium': 1, 'Low': 0}.get(x['severity'], 0),
            -x['affected_count']
        ))

        # Add remediation actions
        remediation_actions = {
            'Data Security': 'Implement encryption and data protection controls',
            'Access Control': 'Deploy identity and access management solution',
            'Audit Trail': 'Enable comprehensive logging and monitoring',
            'Network Security': 'Update firewall rules and network segmentation',
            'Monitoring': 'Deploy SIEM and security monitoring tools',
            'Business Continuity': 'Implement backup and disaster recovery procedures',
            'Incident Response': 'Develop and test incident response procedures',
            'Data Rights': 'Implement data subject rights management system',
            'System Design': 'Redesign system with privacy by design principles',
            'Change Management': 'Establish formal change management process',
            'Security Maintenance': 'Implement patch management and vulnerability scanning'
        }

        for i, priority in enumerate(priorities[:10]):  # Top 10 priorities
            priority['priority_rank'] = i + 1
            priority['recommended_action'] = remediation_actions.get(
                priority['category'],
                'Review and implement appropriate controls'
            )
            priority['estimated_effort'] = self._estimate_effort(priority)

        return priorities[:10]

    def _estimate_effort(self, gap: Dict[str, Any]) -> str:
        """Estimate remediation effort."""
        affected = gap['affected_count']
        severity = gap['severity']

        if severity == 'Critical' and affected > 10:
            return 'High (3-6 months)'
        elif severity in ['Critical', 'High'] and affected > 5:
            return 'Medium (1-3 months)'
        else:
            return 'Low (< 1 month)'

    def get_framework_summary(self, framework_name: str) -> Dict[str, Any]:
        """Get summary of a compliance framework."""
        if framework_name not in self.frameworks:
            return {'error': f'Framework {framework_name} not found'}

        framework = self.frameworks[framework_name]

        categories = {}
        for req in framework.requirements:
            if req.category not in categories:
                categories[req.category] = []
            categories[req.category].append({
                'id': req.id,
                'name': req.name,
                'severity': req.severity,
                'description': req.description
            })

        return {
            'name': framework.name,
            'description': framework.description,
            'total_requirements': len(framework.requirements),
            'categories': categories,
            'severity_breakdown': {
                'Critical': len([r for r in framework.requirements if r.severity == 'Critical']),
                'High': len([r for r in framework.requirements if r.severity == 'High']),
                'Medium': len([r for r in framework.requirements if r.severity == 'Medium']),
                'Low': len([r for r in framework.requirements if r.severity == 'Low'])
            }
        }

    def list_frameworks(self) -> List[Dict[str, str]]:
        """List all available frameworks."""
        return [
            {
                'name': f.name,
                'description': f.description,
                'requirements_count': len(f.requirements)
            }
            for f in self.frameworks.values()
        ]
