"""
Vendor Risk Engine for App Rationalization Pro

Provides comprehensive vendor risk assessment including:
- Financial stability analysis
- Security posture evaluation
- Compliance status tracking
- Strategic alignment scoring
- Contract risk assessment
- Concentration risk analysis
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date
import json


class VendorTier(Enum):
    """Vendor classification by strategic importance"""
    STRATEGIC = "strategic"      # Critical to business operations
    TACTICAL = "tactical"        # Important but replaceable
    COMMODITY = "commodity"      # Easily substitutable
    EMERGING = "emerging"        # New vendor under evaluation


class RiskLevel(Enum):
    """Risk severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class VendorStatus(Enum):
    """Vendor relationship status"""
    ACTIVE = "active"
    PROBATION = "probation"
    SUNSET = "sunset"
    BLOCKED = "blocked"
    UNDER_REVIEW = "under_review"


class ComplianceFramework(Enum):
    """Common compliance frameworks"""
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    CCPA = "ccpa"
    FEDRAMP = "fedramp"
    SOX = "sox"
    CJIS = "cjis"
    FISMA = "fisma"
    STATERAMP = "stateramp"
    TX_RAMP = "tx_ramp"


@dataclass
class VendorProfile:
    """Complete vendor profile"""
    vendor_id: str
    name: str
    tier: VendorTier
    status: VendorStatus

    # Financial indicators
    annual_revenue: Optional[float] = None
    years_in_business: Optional[int] = None
    financial_rating: Optional[str] = None  # e.g., "A", "BBB", "BB"
    publicly_traded: bool = False

    # Contract details
    contract_start: Optional[date] = None
    contract_end: Optional[date] = None
    annual_spend: float = 0.0
    payment_terms: str = "NET30"

    # Security & Compliance
    security_score: Optional[float] = None  # 0-100
    compliances: List[ComplianceFramework] = field(default_factory=list)
    last_security_audit: Optional[date] = None
    has_incident_history: bool = False

    # Business continuity
    has_dr_plan: bool = False
    sla_uptime: float = 99.0  # percentage
    geographic_presence: List[str] = field(default_factory=list)

    # Applications using this vendor
    applications: List[str] = field(default_factory=list)

    # Metadata
    primary_contact: Optional[str] = None
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'vendor_id': self.vendor_id,
            'name': self.name,
            'tier': self.tier.value,
            'status': self.status.value,
            'annual_revenue': self.annual_revenue,
            'years_in_business': self.years_in_business,
            'financial_rating': self.financial_rating,
            'publicly_traded': self.publicly_traded,
            'contract_start': self.contract_start.isoformat() if self.contract_start else None,
            'contract_end': self.contract_end.isoformat() if self.contract_end else None,
            'annual_spend': self.annual_spend,
            'payment_terms': self.payment_terms,
            'security_score': self.security_score,
            'compliances': [c.value for c in self.compliances],
            'last_security_audit': self.last_security_audit.isoformat() if self.last_security_audit else None,
            'has_incident_history': self.has_incident_history,
            'has_dr_plan': self.has_dr_plan,
            'sla_uptime': self.sla_uptime,
            'geographic_presence': self.geographic_presence,
            'applications': self.applications,
            'primary_contact': self.primary_contact,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class RiskAssessment:
    """Individual risk assessment result"""
    vendor_id: str
    vendor_name: str

    # Overall scores
    overall_risk_level: RiskLevel
    overall_risk_score: float  # 0-100 (higher = more risk)

    # Component scores
    financial_risk_score: float
    security_risk_score: float
    operational_risk_score: float
    compliance_risk_score: float
    strategic_risk_score: float
    concentration_risk_score: float

    # Risk factors identified
    risk_factors: List[Dict[str, Any]] = field(default_factory=list)

    # Recommendations
    recommendations: List[str] = field(default_factory=list)

    # Metadata
    assessed_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'vendor_id': self.vendor_id,
            'vendor_name': self.vendor_name,
            'overall_risk_level': self.overall_risk_level.value,
            'overall_risk_score': self.overall_risk_score,
            'financial_risk_score': self.financial_risk_score,
            'security_risk_score': self.security_risk_score,
            'operational_risk_score': self.operational_risk_score,
            'compliance_risk_score': self.compliance_risk_score,
            'strategic_risk_score': self.strategic_risk_score,
            'concentration_risk_score': self.concentration_risk_score,
            'risk_factors': self.risk_factors,
            'recommendations': self.recommendations,
            'assessed_at': self.assessed_at.isoformat()
        }


class VendorRiskEngine:
    """
    Engine for assessing and managing vendor-related risks.

    Features:
    - Multi-dimensional risk scoring
    - Concentration risk analysis
    - Contract risk tracking
    - Compliance gap identification
    - Strategic alignment assessment
    """

    def __init__(self):
        self.vendors: Dict[str, VendorProfile] = {}
        self.assessments: Dict[str, RiskAssessment] = {}
        self.risk_weights = {
            'financial': 0.20,
            'security': 0.25,
            'operational': 0.15,
            'compliance': 0.20,
            'strategic': 0.10,
            'concentration': 0.10
        }

        # Required compliances by industry
        self.industry_compliances = {
            'healthcare': [ComplianceFramework.HIPAA, ComplianceFramework.SOC2],
            'finance': [ComplianceFramework.SOX, ComplianceFramework.PCI_DSS, ComplianceFramework.SOC2],
            'government': [ComplianceFramework.FEDRAMP, ComplianceFramework.FISMA, ComplianceFramework.CJIS],
            'retail': [ComplianceFramework.PCI_DSS, ComplianceFramework.SOC2],
            'technology': [ComplianceFramework.SOC2, ComplianceFramework.ISO27001],
            'general': [ComplianceFramework.SOC2]
        }

    def add_vendor(self, vendor: VendorProfile) -> None:
        """Add or update a vendor profile"""
        vendor.updated_at = datetime.utcnow()
        self.vendors[vendor.vendor_id] = vendor

    def get_vendor(self, vendor_id: str) -> Optional[VendorProfile]:
        """Retrieve vendor by ID"""
        return self.vendors.get(vendor_id)

    def assess_vendor(self, vendor_id: str,
                      industry: str = 'general',
                      total_it_spend: float = 1000000) -> RiskAssessment:
        """
        Perform comprehensive risk assessment for a vendor.

        Args:
            vendor_id: Vendor to assess
            industry: Industry context for compliance requirements
            total_it_spend: Organization's total IT spend for concentration analysis
        """
        vendor = self.vendors.get(vendor_id)
        if not vendor:
            raise ValueError(f"Vendor {vendor_id} not found")

        # Calculate component scores
        financial_score = self._assess_financial_risk(vendor)
        security_score = self._assess_security_risk(vendor)
        operational_score = self._assess_operational_risk(vendor)
        compliance_score = self._assess_compliance_risk(vendor, industry)
        strategic_score = self._assess_strategic_risk(vendor)
        concentration_score = self._assess_concentration_risk(vendor, total_it_spend)

        # Calculate weighted overall score
        overall_score = (
            financial_score * self.risk_weights['financial'] +
            security_score * self.risk_weights['security'] +
            operational_score * self.risk_weights['operational'] +
            compliance_score * self.risk_weights['compliance'] +
            strategic_score * self.risk_weights['strategic'] +
            concentration_score * self.risk_weights['concentration']
        )

        # Determine risk level
        risk_level = self._score_to_level(overall_score)

        # Identify specific risk factors
        risk_factors = self._identify_risk_factors(
            vendor, financial_score, security_score,
            operational_score, compliance_score,
            strategic_score, concentration_score, industry
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(vendor, risk_factors)

        assessment = RiskAssessment(
            vendor_id=vendor_id,
            vendor_name=vendor.name,
            overall_risk_level=risk_level,
            overall_risk_score=overall_score,
            financial_risk_score=financial_score,
            security_risk_score=security_score,
            operational_risk_score=operational_score,
            compliance_risk_score=compliance_score,
            strategic_risk_score=strategic_score,
            concentration_risk_score=concentration_score,
            risk_factors=risk_factors,
            recommendations=recommendations
        )

        self.assessments[vendor_id] = assessment
        return assessment

    def _assess_financial_risk(self, vendor: VendorProfile) -> float:
        """Assess financial stability risk (0-100, higher = more risk)"""
        score = 50  # Start neutral

        # Years in business
        if vendor.years_in_business:
            if vendor.years_in_business < 2:
                score += 30
            elif vendor.years_in_business < 5:
                score += 15
            elif vendor.years_in_business > 10:
                score -= 20
        else:
            score += 20  # Unknown = risk

        # Financial rating
        rating_adjustments = {
            'AAA': -30, 'AA': -25, 'A': -20, 'BBB': -10,
            'BB': 10, 'B': 20, 'CCC': 35, 'CC': 45, 'C': 50, 'D': 60
        }
        if vendor.financial_rating:
            score += rating_adjustments.get(vendor.financial_rating.upper(), 0)
        else:
            score += 15  # No rating = some risk

        # Publicly traded (more transparency)
        if vendor.publicly_traded:
            score -= 10

        # Revenue relative to spend (dependency risk)
        if vendor.annual_revenue and vendor.annual_spend:
            revenue_ratio = vendor.annual_spend / vendor.annual_revenue
            if revenue_ratio > 0.1:  # >10% of their revenue
                score += 20
            elif revenue_ratio > 0.05:
                score += 10

        return max(0, min(100, score))

    def _assess_security_risk(self, vendor: VendorProfile) -> float:
        """Assess security posture risk (0-100, higher = more risk)"""
        score = 50

        # Security score from vendor
        if vendor.security_score is not None:
            # Invert since our vendor score is good=high, but risk=high here
            score = 100 - vendor.security_score
        else:
            score += 20  # Unknown = risk

        # Security audit recency
        if vendor.last_security_audit:
            days_since = (date.today() - vendor.last_security_audit).days
            if days_since > 730:  # >2 years
                score += 25
            elif days_since > 365:  # >1 year
                score += 15
            elif days_since < 180:  # <6 months
                score -= 10
        else:
            score += 30  # No audit = high risk

        # Incident history
        if vendor.has_incident_history:
            score += 20

        # Key security certifications
        security_certs = {ComplianceFramework.SOC2, ComplianceFramework.ISO27001}
        has_security_cert = bool(set(vendor.compliances) & security_certs)
        if has_security_cert:
            score -= 15
        else:
            score += 10

        return max(0, min(100, score))

    def _assess_operational_risk(self, vendor: VendorProfile) -> float:
        """Assess operational/continuity risk (0-100, higher = more risk)"""
        score = 50

        # DR plan
        if not vendor.has_dr_plan:
            score += 25
        else:
            score -= 10

        # SLA uptime
        if vendor.sla_uptime >= 99.99:
            score -= 25
        elif vendor.sla_uptime >= 99.9:
            score -= 15
        elif vendor.sla_uptime >= 99.5:
            score -= 5
        elif vendor.sla_uptime < 99:
            score += 20

        # Geographic presence (single point of failure)
        if len(vendor.geographic_presence) == 0:
            score += 15
        elif len(vendor.geographic_presence) == 1:
            score += 10
        elif len(vendor.geographic_presence) >= 3:
            score -= 10

        # Number of applications depending on this vendor
        app_count = len(vendor.applications)
        if app_count > 10:
            score += 15  # Too many dependencies
        elif app_count > 5:
            score += 5

        return max(0, min(100, score))

    def _assess_compliance_risk(self, vendor: VendorProfile, industry: str) -> float:
        """Assess compliance gap risk (0-100, higher = more risk)"""
        score = 30  # Start lower since compliance is binary often

        # Get required compliances for industry
        required = set(self.industry_compliances.get(industry.lower(),
                                                     self.industry_compliances['general']))
        vendor_compliances = set(vendor.compliances)

        # Calculate coverage
        if required:
            coverage = len(required & vendor_compliances) / len(required)
            missing_score = (1 - coverage) * 70  # Up to 70 points for missing
            score += missing_score

        # Bonus for extra compliances
        extra = vendor_compliances - required
        score -= len(extra) * 5  # Small bonus per extra compliance

        return max(0, min(100, score))

    def _assess_strategic_risk(self, vendor: VendorProfile) -> float:
        """Assess strategic alignment risk (0-100, higher = more risk)"""
        score = 50

        # Vendor tier alignment
        tier_scores = {
            VendorTier.STRATEGIC: -20,
            VendorTier.TACTICAL: 0,
            VendorTier.COMMODITY: 10,
            VendorTier.EMERGING: 25
        }
        score += tier_scores.get(vendor.tier, 0)

        # Vendor status
        status_scores = {
            VendorStatus.ACTIVE: -15,
            VendorStatus.PROBATION: 30,
            VendorStatus.SUNSET: 40,
            VendorStatus.BLOCKED: 60,
            VendorStatus.UNDER_REVIEW: 20
        }
        score += status_scores.get(vendor.status, 0)

        # Contract expiration
        if vendor.contract_end:
            days_to_expiry = (vendor.contract_end - date.today()).days
            if days_to_expiry < 0:
                score += 40  # Expired!
            elif days_to_expiry < 90:
                score += 25
            elif days_to_expiry < 180:
                score += 10

        return max(0, min(100, score))

    def _assess_concentration_risk(self, vendor: VendorProfile,
                                    total_it_spend: float) -> float:
        """Assess spend concentration risk (0-100, higher = more risk)"""
        if total_it_spend <= 0:
            return 50

        concentration = vendor.annual_spend / total_it_spend

        if concentration > 0.30:  # >30% with one vendor
            return 90
        elif concentration > 0.20:
            return 70
        elif concentration > 0.10:
            return 50
        elif concentration > 0.05:
            return 30
        else:
            return 10

    def _score_to_level(self, score: float) -> RiskLevel:
        """Convert numeric score to risk level"""
        if score >= 80:
            return RiskLevel.CRITICAL
        elif score >= 60:
            return RiskLevel.HIGH
        elif score >= 40:
            return RiskLevel.MEDIUM
        elif score >= 20:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL

    def _identify_risk_factors(self, vendor: VendorProfile,
                               financial: float, security: float,
                               operational: float, compliance: float,
                               strategic: float, concentration: float,
                               industry: str) -> List[Dict[str, Any]]:
        """Identify specific risk factors"""
        factors = []

        # Financial factors
        if financial >= 60:
            if vendor.years_in_business and vendor.years_in_business < 3:
                factors.append({
                    'category': 'financial',
                    'severity': 'high',
                    'factor': 'Limited operating history',
                    'detail': f'Only {vendor.years_in_business} years in business'
                })
            if not vendor.financial_rating:
                factors.append({
                    'category': 'financial',
                    'severity': 'medium',
                    'factor': 'No financial rating available',
                    'detail': 'Unable to assess creditworthiness'
                })

        # Security factors
        if security >= 60:
            if vendor.has_incident_history:
                factors.append({
                    'category': 'security',
                    'severity': 'high',
                    'factor': 'Previous security incidents',
                    'detail': 'Vendor has history of security breaches'
                })
            if not vendor.last_security_audit:
                factors.append({
                    'category': 'security',
                    'severity': 'high',
                    'factor': 'No security audit on record',
                    'detail': 'No recent security assessment available'
                })

        # Operational factors
        if operational >= 60:
            if not vendor.has_dr_plan:
                factors.append({
                    'category': 'operational',
                    'severity': 'high',
                    'factor': 'No disaster recovery plan',
                    'detail': 'Business continuity risk'
                })
            if vendor.sla_uptime < 99.5:
                factors.append({
                    'category': 'operational',
                    'severity': 'medium',
                    'factor': 'Low SLA uptime guarantee',
                    'detail': f'Only {vendor.sla_uptime}% uptime SLA'
                })

        # Compliance factors
        required = set(self.industry_compliances.get(industry.lower(),
                                                     self.industry_compliances['general']))
        missing = required - set(vendor.compliances)
        for compliance in missing:
            factors.append({
                'category': 'compliance',
                'severity': 'high',
                'factor': f'Missing {compliance.value.upper()} certification',
                'detail': f'Required for {industry} industry'
            })

        # Strategic factors
        if strategic >= 60:
            if vendor.status == VendorStatus.PROBATION:
                factors.append({
                    'category': 'strategic',
                    'severity': 'high',
                    'factor': 'Vendor on probation',
                    'detail': 'Performance or relationship issues identified'
                })
            if vendor.contract_end:
                days_to_expiry = (vendor.contract_end - date.today()).days
                if days_to_expiry < 90:
                    factors.append({
                        'category': 'strategic',
                        'severity': 'high' if days_to_expiry < 30 else 'medium',
                        'factor': 'Contract expiring soon',
                        'detail': f'{max(0, days_to_expiry)} days until expiration'
                    })

        # Concentration factors
        if concentration >= 60:
            factors.append({
                'category': 'concentration',
                'severity': 'high' if concentration >= 80 else 'medium',
                'factor': 'High spend concentration',
                'detail': f'${vendor.annual_spend:,.0f} annual spend with this vendor'
            })

        return factors

    def _generate_recommendations(self, vendor: VendorProfile,
                                   risk_factors: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations based on risk factors"""
        recommendations = []

        categories_found = {f['category'] for f in risk_factors}
        high_severity = [f for f in risk_factors if f['severity'] == 'high']

        if 'financial' in categories_found:
            recommendations.append(
                "Request updated financial statements and credit report"
            )
            if vendor.tier == VendorTier.STRATEGIC:
                recommendations.append(
                    "Consider establishing escrow arrangement for source code"
                )

        if 'security' in categories_found:
            if not vendor.last_security_audit:
                recommendations.append(
                    "Require vendor to complete security assessment (SOC2/ISO27001)"
                )
            if vendor.has_incident_history:
                recommendations.append(
                    "Request detailed incident report and remediation evidence"
                )

        if 'operational' in categories_found:
            if not vendor.has_dr_plan:
                recommendations.append(
                    "Require vendor to provide disaster recovery documentation"
                )
            recommendations.append(
                "Consider adding performance SLAs with financial penalties"
            )

        if 'compliance' in categories_found:
            recommendations.append(
                "Include compliance certification requirements in contract renewal"
            )

        if 'strategic' in categories_found:
            if vendor.status == VendorStatus.PROBATION:
                recommendations.append(
                    "Initiate formal vendor review process with clear improvement milestones"
                )
            if vendor.contract_end:
                days_to_expiry = (vendor.contract_end - date.today()).days
                if days_to_expiry < 180:
                    recommendations.append(
                        "Begin contract renewal or replacement evaluation immediately"
                    )

        if 'concentration' in categories_found:
            recommendations.append(
                "Identify and evaluate alternative vendors to reduce concentration"
            )
            if len(vendor.applications) > 5:
                recommendations.append(
                    "Consider splitting workload across multiple vendors"
                )

        # General high-risk recommendations
        if len(high_severity) >= 3:
            recommendations.insert(0,
                "PRIORITY: Schedule executive review of vendor relationship"
            )

        return recommendations

    def batch_assess(self, vendor_ids: Optional[List[str]] = None,
                     industry: str = 'general',
                     total_it_spend: float = 1000000) -> List[RiskAssessment]:
        """Assess multiple vendors at once"""
        if vendor_ids is None:
            vendor_ids = list(self.vendors.keys())

        results = []
        for vid in vendor_ids:
            if vid in self.vendors:
                results.append(self.assess_vendor(vid, industry, total_it_spend))

        # Sort by risk score descending
        results.sort(key=lambda x: x.overall_risk_score, reverse=True)
        return results

    def get_portfolio_summary(self, industry: str = 'general',
                              total_it_spend: float = 1000000) -> Dict[str, Any]:
        """Get summary of vendor risk across portfolio"""
        if not self.vendors:
            return {
                'total_vendors': 0,
                'risk_distribution': {},
                'top_risks': [],
                'compliance_gaps': [],
                'expiring_contracts': [],
                'total_spend': 0.0
            }

        # Assess all vendors
        assessments = self.batch_assess(industry=industry, total_it_spend=total_it_spend)

        # Risk distribution
        risk_dist = {level.value: 0 for level in RiskLevel}
        for a in assessments:
            risk_dist[a.overall_risk_level.value] += 1

        # Top 5 risks
        top_risks = [a.to_dict() for a in assessments[:5]]

        # Compliance gaps
        required = set(self.industry_compliances.get(industry.lower(),
                                                     self.industry_compliances['general']))
        compliance_gaps = []
        for vendor in self.vendors.values():
            missing = required - set(vendor.compliances)
            if missing:
                compliance_gaps.append({
                    'vendor_id': vendor.vendor_id,
                    'vendor_name': vendor.name,
                    'missing': [c.value for c in missing]
                })

        # Expiring contracts (next 180 days)
        expiring = []
        for vendor in self.vendors.values():
            if vendor.contract_end:
                days_to_expiry = (vendor.contract_end - date.today()).days
                if 0 < days_to_expiry <= 180:
                    expiring.append({
                        'vendor_id': vendor.vendor_id,
                        'vendor_name': vendor.name,
                        'expires': vendor.contract_end.isoformat(),
                        'days_remaining': days_to_expiry,
                        'annual_spend': vendor.annual_spend
                    })
        expiring.sort(key=lambda x: x['days_remaining'])

        # Tier distribution
        tier_dist = {tier.value: 0 for tier in VendorTier}
        for vendor in self.vendors.values():
            tier_dist[vendor.tier.value] += 1

        # Total spend
        total_spend = sum(v.annual_spend for v in self.vendors.values())

        # Concentration analysis
        concentration = []
        for vendor in self.vendors.values():
            if total_it_spend > 0:
                pct = (vendor.annual_spend / total_it_spend) * 100
                if pct >= 5:  # Only show vendors with >=5% spend
                    concentration.append({
                        'vendor_id': vendor.vendor_id,
                        'vendor_name': vendor.name,
                        'annual_spend': vendor.annual_spend,
                        'percentage': round(pct, 1)
                    })
        concentration.sort(key=lambda x: x['percentage'], reverse=True)

        return {
            'total_vendors': len(self.vendors),
            'total_spend': total_spend,
            'risk_distribution': risk_dist,
            'tier_distribution': tier_dist,
            'top_risks': top_risks,
            'compliance_gaps': compliance_gaps,
            'expiring_contracts': expiring,
            'spend_concentration': concentration[:10],  # Top 10
            'assessed_at': datetime.utcnow().isoformat()
        }

    def find_replacement_candidates(self, vendor_id: str) -> List[VendorProfile]:
        """Find potential replacement vendors based on similar tier/capabilities"""
        vendor = self.vendors.get(vendor_id)
        if not vendor:
            return []

        candidates = []
        for v in self.vendors.values():
            if v.vendor_id == vendor_id:
                continue
            if v.status in (VendorStatus.BLOCKED, VendorStatus.SUNSET):
                continue

            # Score similarity
            score = 0

            # Similar tier
            if v.tier == vendor.tier:
                score += 30
            elif (v.tier == VendorTier.STRATEGIC and vendor.tier == VendorTier.TACTICAL) or \
                 (v.tier == VendorTier.TACTICAL and vendor.tier == VendorTier.STRATEGIC):
                score += 20

            # Better or equal security
            if v.security_score and vendor.security_score:
                if v.security_score >= vendor.security_score:
                    score += 20

            # Has required compliances
            if set(vendor.compliances).issubset(set(v.compliances)):
                score += 25

            # Active status
            if v.status == VendorStatus.ACTIVE:
                score += 15

            # Good SLA
            if v.sla_uptime >= vendor.sla_uptime:
                score += 10

            if score >= 50:  # Threshold for consideration
                candidates.append((score, v))

        # Sort by score descending
        candidates.sort(key=lambda x: x[0], reverse=True)
        return [v for _, v in candidates[:5]]

    def get_vendor_timeline(self, vendor_id: str) -> Dict[str, Any]:
        """Get timeline view of vendor relationship"""
        vendor = self.vendors.get(vendor_id)
        if not vendor:
            return {}

        events = []

        if vendor.contract_start:
            events.append({
                'date': vendor.contract_start.isoformat(),
                'event': 'Contract Started',
                'type': 'milestone'
            })

        if vendor.last_security_audit:
            events.append({
                'date': vendor.last_security_audit.isoformat(),
                'event': 'Last Security Audit',
                'type': 'audit'
            })

        if vendor.contract_end:
            events.append({
                'date': vendor.contract_end.isoformat(),
                'event': 'Contract Expires',
                'type': 'deadline'
            })

        events.sort(key=lambda x: x['date'])

        return {
            'vendor_id': vendor_id,
            'vendor_name': vendor.name,
            'timeline': events
        }

    def export_to_dict(self) -> Dict[str, Any]:
        """Export all vendor data"""
        return {
            'vendors': {vid: v.to_dict() for vid, v in self.vendors.items()},
            'assessments': {vid: a.to_dict() for vid, a in self.assessments.items()},
            'exported_at': datetime.utcnow().isoformat()
        }

    def import_from_dict(self, data: Dict[str, Any]) -> int:
        """Import vendor data from dictionary"""
        count = 0
        for vid, vdata in data.get('vendors', {}).items():
            try:
                vendor = VendorProfile(
                    vendor_id=vdata['vendor_id'],
                    name=vdata['name'],
                    tier=VendorTier(vdata['tier']),
                    status=VendorStatus(vdata['status']),
                    annual_revenue=vdata.get('annual_revenue'),
                    years_in_business=vdata.get('years_in_business'),
                    financial_rating=vdata.get('financial_rating'),
                    publicly_traded=vdata.get('publicly_traded', False),
                    contract_start=date.fromisoformat(vdata['contract_start']) if vdata.get('contract_start') else None,
                    contract_end=date.fromisoformat(vdata['contract_end']) if vdata.get('contract_end') else None,
                    annual_spend=vdata.get('annual_spend', 0.0),
                    payment_terms=vdata.get('payment_terms', 'NET30'),
                    security_score=vdata.get('security_score'),
                    compliances=[ComplianceFramework(c) for c in vdata.get('compliances', [])],
                    last_security_audit=date.fromisoformat(vdata['last_security_audit']) if vdata.get('last_security_audit') else None,
                    has_incident_history=vdata.get('has_incident_history', False),
                    has_dr_plan=vdata.get('has_dr_plan', False),
                    sla_uptime=vdata.get('sla_uptime', 99.0),
                    geographic_presence=vdata.get('geographic_presence', []),
                    applications=vdata.get('applications', []),
                    primary_contact=vdata.get('primary_contact'),
                    notes=vdata.get('notes', '')
                )
                self.add_vendor(vendor)
                count += 1
            except (KeyError, ValueError) as e:
                continue  # Skip invalid entries
        return count


def create_demo_vendors() -> VendorRiskEngine:
    """Create demo vendor data for testing"""
    engine = VendorRiskEngine()

    # Strategic vendor - low risk
    engine.add_vendor(VendorProfile(
        vendor_id='v001',
        name='Microsoft Azure',
        tier=VendorTier.STRATEGIC,
        status=VendorStatus.ACTIVE,
        annual_revenue=200000000000,
        years_in_business=49,
        financial_rating='AAA',
        publicly_traded=True,
        contract_start=date(2023, 1, 1),
        contract_end=date(2026, 12, 31),
        annual_spend=500000,
        security_score=95,
        compliances=[
            ComplianceFramework.SOC2, ComplianceFramework.ISO27001,
            ComplianceFramework.HIPAA, ComplianceFramework.PCI_DSS,
            ComplianceFramework.FEDRAMP, ComplianceFramework.GDPR
        ],
        last_security_audit=date(2025, 6, 15),
        has_dr_plan=True,
        sla_uptime=99.99,
        geographic_presence=['North America', 'Europe', 'Asia', 'Australia'],
        applications=['app001', 'app002', 'app003', 'app004', 'app005']
    ))

    # Tactical vendor - medium risk
    engine.add_vendor(VendorProfile(
        vendor_id='v002',
        name='Acme Software Solutions',
        tier=VendorTier.TACTICAL,
        status=VendorStatus.ACTIVE,
        annual_revenue=50000000,
        years_in_business=12,
        financial_rating='BBB',
        publicly_traded=False,
        contract_start=date(2024, 6, 1),
        contract_end=date(2026, 5, 31),
        annual_spend=150000,
        security_score=75,
        compliances=[ComplianceFramework.SOC2],
        last_security_audit=date(2024, 11, 1),
        has_dr_plan=True,
        sla_uptime=99.5,
        geographic_presence=['North America'],
        applications=['app006', 'app007']
    ))

    # Commodity vendor - higher risk
    engine.add_vendor(VendorProfile(
        vendor_id='v003',
        name='QuickDev Tools',
        tier=VendorTier.COMMODITY,
        status=VendorStatus.ACTIVE,
        annual_revenue=5000000,
        years_in_business=4,
        financial_rating='BB',
        publicly_traded=False,
        contract_start=date(2025, 1, 1),
        contract_end=date(2026, 3, 31),  # Expiring soon
        annual_spend=25000,
        security_score=60,
        compliances=[],
        last_security_audit=None,
        has_dr_plan=False,
        sla_uptime=99.0,
        geographic_presence=['North America'],
        applications=['app008']
    ))

    # Emerging vendor - under evaluation
    engine.add_vendor(VendorProfile(
        vendor_id='v004',
        name='AI Startup Inc',
        tier=VendorTier.EMERGING,
        status=VendorStatus.UNDER_REVIEW,
        annual_revenue=2000000,
        years_in_business=2,
        financial_rating=None,
        publicly_traded=False,
        contract_start=date(2025, 9, 1),
        contract_end=date(2026, 8, 31),
        annual_spend=75000,
        security_score=70,
        compliances=[ComplianceFramework.SOC2],
        last_security_audit=date(2025, 7, 1),
        has_dr_plan=True,
        sla_uptime=99.9,
        geographic_presence=['North America', 'Europe'],
        applications=['app009']
    ))

    # Vendor on probation - high risk
    engine.add_vendor(VendorProfile(
        vendor_id='v005',
        name='Legacy Systems Corp',
        tier=VendorTier.TACTICAL,
        status=VendorStatus.PROBATION,
        annual_revenue=100000000,
        years_in_business=25,
        financial_rating='B',
        publicly_traded=True,
        contract_start=date(2020, 1, 1),
        contract_end=date(2026, 1, 31),  # Expiring very soon
        annual_spend=200000,
        security_score=50,
        compliances=[ComplianceFramework.SOC2],
        last_security_audit=date(2023, 6, 1),  # Old audit
        has_dr_plan=False,
        has_incident_history=True,
        sla_uptime=98.5,
        geographic_presence=['North America'],
        applications=['app010', 'app011', 'app012']
    ))

    return engine
