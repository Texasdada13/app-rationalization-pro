"""
Government Demo Portfolio Seed Script

Creates a realistic county government portfolio for demonstration purposes.
Based on typical large county government IT portfolios (Dallas County, Marion County, etc.)

Usage:
    python scripts/seed_gov_demo.py

This will create:
- County government agency hierarchy
- Department-level agencies
- Realistic application portfolio with government-specific attributes
- Sample contracts and compliance requirements
"""

import os
import sys
from datetime import date, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app import create_app
from src.database.models import db, Agency, Portfolio, Application, Contract


def seed_county_government():
    """Create a realistic county government portfolio."""

    app = create_app()

    with app.app_context():
        print("Creating county government demo portfolio...")

        # =====================================================
        # AGENCY HIERARCHY
        # =====================================================

        # Top-level county
        county = Agency(
            name="Demo County Government",
            code="DEMO",
            level="county",
            agency_type="general_government",
            jurisdiction="Demo County, TX",
            population_served=2800000,
            employee_count=7500,
            annual_budget=950000000,
            head_official="Sarah Mitchell",
            head_title="County Judge",
            required_frameworks=["StateRAMP", "TX-RAMP"]
        )
        db.session.add(county)
        db.session.flush()  # Get ID

        # Department-level agencies
        departments = [
            {
                "name": "Sheriff's Office",
                "code": "DCSO",
                "agency_type": "law_enforcement",
                "employee_count": 2400,
                "annual_budget": 320000000,
                "head_official": "Robert Johnson",
                "head_title": "Sheriff",
                "required_frameworks": ["CJIS", "StateRAMP"]
            },
            {
                "name": "District Attorney",
                "code": "DA",
                "agency_type": "courts_legal",
                "employee_count": 450,
                "annual_budget": 55000000,
                "head_official": "Maria Garcia",
                "head_title": "District Attorney",
                "required_frameworks": ["CJIS"]
            },
            {
                "name": "Health & Human Services",
                "code": "HHS",
                "agency_type": "health_human_services",
                "employee_count": 1200,
                "annual_budget": 180000000,
                "head_official": "Dr. James Wilson",
                "head_title": "Director",
                "required_frameworks": ["HIPAA", "StateRAMP"]
            },
            {
                "name": "Tax Office",
                "code": "TAX",
                "agency_type": "finance_admin",
                "employee_count": 280,
                "annual_budget": 28000000,
                "head_official": "Jennifer Adams",
                "head_title": "Tax Assessor-Collector",
                "required_frameworks": ["PCI-DSS", "SOX"]
            },
            {
                "name": "Information Technology",
                "code": "IT",
                "agency_type": "general_government",
                "employee_count": 180,
                "annual_budget": 42000000,
                "head_official": "Michael Chen",
                "head_title": "CIO",
                "required_frameworks": ["StateRAMP", "TX-RAMP"]
            },
            {
                "name": "Elections",
                "code": "ELEC",
                "agency_type": "general_government",
                "employee_count": 45,
                "annual_budget": 12000000,
                "head_official": "Patricia Thompson",
                "head_title": "Elections Administrator",
                "required_frameworks": ["StateRAMP"]
            }
        ]

        dept_records = {}
        for dept in departments:
            agency = Agency(
                name=dept["name"],
                code=dept["code"],
                parent_id=county.id,
                level="department",
                agency_type=dept["agency_type"],
                jurisdiction="Demo County, TX",
                employee_count=dept["employee_count"],
                annual_budget=dept["annual_budget"],
                head_official=dept["head_official"],
                head_title=dept["head_title"],
                required_frameworks=dept["required_frameworks"]
            )
            db.session.add(agency)
            db.session.flush()
            dept_records[dept["code"]] = agency

        # =====================================================
        # PORTFOLIO
        # =====================================================

        portfolio = Portfolio(
            name="Demo County IT Portfolio",
            organization="Demo County Government",
            description="Comprehensive IT application portfolio for Demo County government operations",
            agency_id=county.id,
            portfolio_type="government",
            sector="general_government",
            fiscal_year="FY2024"
        )
        db.session.add(portfolio)
        db.session.flush()

        # =====================================================
        # APPLICATIONS
        # =====================================================

        applications_data = [
            # Sheriff's Office Applications
            {
                "name": "Computer Aided Dispatch (CAD)",
                "category": "Public Safety",
                "department": "Sheriff's Office",
                "vendor": "Hexagon Safety & Infrastructure",
                "business_value": 9,
                "tech_health": 7,
                "cost": 850000,
                "usage": 450,
                "security": 8,
                "strategic_fit": 9,
                "citizen_impact": 10,
                "mission_criticality": 10,
                "interoperability_score": 8,
                "data_sensitivity": "restricted",
                "compliance_requirements": ["CJIS"],
                "system_of_record": True,
                "public_facing": False,
                "shared_service": True
            },
            {
                "name": "Records Management System (RMS)",
                "category": "Public Safety",
                "department": "Sheriff's Office",
                "vendor": "Tyler Technologies",
                "business_value": 9,
                "tech_health": 5,
                "cost": 620000,
                "usage": 380,
                "security": 7,
                "strategic_fit": 8,
                "citizen_impact": 8,
                "mission_criticality": 9,
                "interoperability_score": 6,
                "data_sensitivity": "restricted",
                "compliance_requirements": ["CJIS"],
                "system_of_record": True,
                "public_facing": False
            },
            {
                "name": "Jail Management System",
                "category": "Public Safety",
                "department": "Sheriff's Office",
                "vendor": "Black Creek ISC",
                "business_value": 8,
                "tech_health": 4,
                "cost": 420000,
                "usage": 220,
                "security": 6,
                "strategic_fit": 7,
                "citizen_impact": 6,
                "mission_criticality": 9,
                "interoperability_score": 4,
                "data_sensitivity": "restricted",
                "compliance_requirements": ["CJIS"],
                "system_of_record": True
            },
            {
                "name": "Body Camera Management",
                "category": "Public Safety",
                "department": "Sheriff's Office",
                "vendor": "Axon Enterprise",
                "business_value": 8,
                "tech_health": 9,
                "cost": 380000,
                "usage": 1800,
                "security": 9,
                "strategic_fit": 9,
                "citizen_impact": 8,
                "mission_criticality": 8,
                "interoperability_score": 7,
                "data_sensitivity": "confidential",
                "compliance_requirements": ["CJIS"]
            },

            # District Attorney Applications
            {
                "name": "Case Management System",
                "category": "Legal",
                "department": "District Attorney",
                "vendor": "Journal Technologies",
                "business_value": 9,
                "tech_health": 6,
                "cost": 280000,
                "usage": 420,
                "security": 7,
                "strategic_fit": 8,
                "citizen_impact": 7,
                "mission_criticality": 9,
                "interoperability_score": 5,
                "data_sensitivity": "confidential",
                "compliance_requirements": ["CJIS"],
                "system_of_record": True
            },
            {
                "name": "E-Discovery Platform",
                "category": "Legal",
                "department": "District Attorney",
                "vendor": "Relativity",
                "business_value": 7,
                "tech_health": 8,
                "cost": 180000,
                "usage": 85,
                "security": 8,
                "strategic_fit": 7,
                "citizen_impact": 4,
                "mission_criticality": 7,
                "interoperability_score": 6,
                "data_sensitivity": "confidential"
            },

            # Health & Human Services Applications
            {
                "name": "Eligibility Determination System",
                "category": "Social Services",
                "department": "Health & Human Services",
                "vendor": "Deloitte",
                "business_value": 9,
                "tech_health": 5,
                "cost": 520000,
                "usage": 340,
                "security": 7,
                "strategic_fit": 8,
                "citizen_impact": 10,
                "mission_criticality": 9,
                "interoperability_score": 7,
                "data_sensitivity": "confidential",
                "compliance_requirements": ["HIPAA"],
                "system_of_record": True,
                "public_facing": True,
                "grant_funded": True,
                "grant_expiration": date.today() + timedelta(days=540)
            },
            {
                "name": "Public Health Surveillance",
                "category": "Health",
                "department": "Health & Human Services",
                "vendor": "Conduent",
                "business_value": 8,
                "tech_health": 6,
                "cost": 220000,
                "usage": 120,
                "security": 8,
                "strategic_fit": 9,
                "citizen_impact": 9,
                "mission_criticality": 8,
                "interoperability_score": 7,
                "data_sensitivity": "confidential",
                "compliance_requirements": ["HIPAA"],
                "shared_service": True
            },
            {
                "name": "WIC Program Management",
                "category": "Social Services",
                "department": "Health & Human Services",
                "vendor": "GCOM Software",
                "business_value": 8,
                "tech_health": 4,
                "cost": 85000,
                "usage": 180,
                "security": 6,
                "strategic_fit": 7,
                "citizen_impact": 9,
                "mission_criticality": 7,
                "interoperability_score": 4,
                "data_sensitivity": "confidential",
                "compliance_requirements": ["HIPAA"],
                "grant_funded": True,
                "grant_expiration": date.today() + timedelta(days=365)
            },

            # Tax Office Applications
            {
                "name": "Property Tax System",
                "category": "Finance",
                "department": "Tax Office",
                "vendor": "Tyler Technologies",
                "business_value": 10,
                "tech_health": 6,
                "cost": 380000,
                "usage": 250,
                "security": 7,
                "strategic_fit": 9,
                "citizen_impact": 10,
                "mission_criticality": 10,
                "interoperability_score": 7,
                "data_sensitivity": "sensitive",
                "compliance_requirements": ["PCI-DSS", "SOX"],
                "system_of_record": True,
                "public_facing": True
            },
            {
                "name": "Online Tax Payment Portal",
                "category": "Finance",
                "department": "Tax Office",
                "vendor": "Point & Pay",
                "business_value": 8,
                "tech_health": 8,
                "cost": 120000,
                "usage": 45000,
                "security": 9,
                "strategic_fit": 9,
                "citizen_impact": 9,
                "mission_criticality": 8,
                "interoperability_score": 8,
                "data_sensitivity": "sensitive",
                "compliance_requirements": ["PCI-DSS"],
                "public_facing": True
            },
            {
                "name": "Vehicle Registration System",
                "category": "Finance",
                "department": "Tax Office",
                "vendor": "Texas DMV (State)",
                "business_value": 7,
                "tech_health": 5,
                "cost": 0,
                "usage": 280,
                "security": 6,
                "strategic_fit": 6,
                "citizen_impact": 8,
                "mission_criticality": 7,
                "interoperability_score": 3,
                "data_sensitivity": "sensitive",
                "shared_service": True
            },

            # IT Department Applications
            {
                "name": "ServiceNow ITSM",
                "category": "IT Operations",
                "department": "Information Technology",
                "vendor": "ServiceNow",
                "business_value": 8,
                "tech_health": 9,
                "cost": 280000,
                "usage": 7500,
                "security": 9,
                "strategic_fit": 9,
                "citizen_impact": 3,
                "mission_criticality": 7,
                "interoperability_score": 9,
                "data_sensitivity": "sensitive",
                "shared_service": True
            },
            {
                "name": "Microsoft 365",
                "category": "Productivity",
                "department": "Information Technology",
                "vendor": "Microsoft",
                "business_value": 9,
                "tech_health": 10,
                "cost": 1200000,
                "usage": 7500,
                "security": 9,
                "strategic_fit": 9,
                "citizen_impact": 5,
                "mission_criticality": 9,
                "interoperability_score": 10,
                "data_sensitivity": "sensitive",
                "compliance_requirements": ["StateRAMP"],
                "shared_service": True
            },
            {
                "name": "Legacy Mainframe (CICS)",
                "category": "Core Systems",
                "department": "Information Technology",
                "vendor": "IBM",
                "business_value": 6,
                "tech_health": 3,
                "cost": 450000,
                "usage": 120,
                "security": 5,
                "strategic_fit": 2,
                "citizen_impact": 4,
                "mission_criticality": 6,
                "interoperability_score": 2,
                "data_sensitivity": "sensitive",
                "system_of_record": True
            },
            {
                "name": "Network Monitoring (SolarWinds)",
                "category": "IT Operations",
                "department": "Information Technology",
                "vendor": "SolarWinds",
                "business_value": 7,
                "tech_health": 7,
                "cost": 95000,
                "usage": 25,
                "security": 6,
                "strategic_fit": 7,
                "citizen_impact": 2,
                "mission_criticality": 7,
                "interoperability_score": 7,
                "data_sensitivity": "sensitive"
            },

            # Elections Applications
            {
                "name": "Voter Registration System",
                "category": "Elections",
                "department": "Elections",
                "vendor": "Texas Secretary of State",
                "business_value": 9,
                "tech_health": 6,
                "cost": 0,
                "usage": 45,
                "security": 8,
                "strategic_fit": 9,
                "citizen_impact": 10,
                "mission_criticality": 10,
                "interoperability_score": 6,
                "data_sensitivity": "confidential",
                "compliance_requirements": ["StateRAMP"],
                "system_of_record": True,
                "public_facing": True,
                "shared_service": True
            },
            {
                "name": "Election Results Reporting",
                "category": "Elections",
                "department": "Elections",
                "vendor": "Scytl",
                "business_value": 8,
                "tech_health": 7,
                "cost": 85000,
                "usage": 15,
                "security": 9,
                "strategic_fit": 8,
                "citizen_impact": 10,
                "mission_criticality": 9,
                "interoperability_score": 5,
                "data_sensitivity": "public",
                "public_facing": True
            },

            # Cross-Department Applications
            {
                "name": "County Website (CMS)",
                "category": "Communications",
                "department": "Information Technology",
                "vendor": "Granicus",
                "business_value": 8,
                "tech_health": 7,
                "cost": 65000,
                "usage": 7500,
                "security": 7,
                "strategic_fit": 8,
                "citizen_impact": 9,
                "mission_criticality": 6,
                "interoperability_score": 8,
                "data_sensitivity": "public",
                "public_facing": True,
                "shared_service": True
            },
            {
                "name": "GIS Platform",
                "category": "Data Analytics",
                "department": "Information Technology",
                "vendor": "Esri",
                "business_value": 9,
                "tech_health": 9,
                "cost": 320000,
                "usage": 450,
                "security": 8,
                "strategic_fit": 9,
                "citizen_impact": 8,
                "mission_criticality": 7,
                "interoperability_score": 9,
                "data_sensitivity": "public",
                "public_facing": True,
                "shared_service": True
            },
            {
                "name": "ERP Financial System",
                "category": "Finance",
                "department": "Information Technology",
                "vendor": "Tyler Technologies (Munis)",
                "business_value": 10,
                "tech_health": 6,
                "cost": 680000,
                "usage": 850,
                "security": 8,
                "strategic_fit": 8,
                "citizen_impact": 5,
                "mission_criticality": 10,
                "interoperability_score": 7,
                "data_sensitivity": "confidential",
                "compliance_requirements": ["SOX"],
                "system_of_record": True,
                "shared_service": True
            },
            {
                "name": "HR/Payroll System",
                "category": "Human Resources",
                "department": "Information Technology",
                "vendor": "Workday",
                "business_value": 9,
                "tech_health": 9,
                "cost": 420000,
                "usage": 7500,
                "security": 9,
                "strategic_fit": 9,
                "citizen_impact": 2,
                "mission_criticality": 8,
                "interoperability_score": 8,
                "data_sensitivity": "confidential",
                "system_of_record": True,
                "shared_service": True
            },
        ]

        for app_data in applications_data:
            app = Application(
                portfolio_id=portfolio.id,
                name=app_data["name"],
                category=app_data.get("category"),
                department=app_data.get("department"),
                vendor=app_data.get("vendor"),
                business_value=app_data.get("business_value", 5),
                tech_health=app_data.get("tech_health", 5),
                cost=app_data.get("cost", 0),
                usage=app_data.get("usage", 0),
                security=app_data.get("security", 5),
                strategic_fit=app_data.get("strategic_fit", 5),
                citizen_impact=app_data.get("citizen_impact", 5),
                mission_criticality=app_data.get("mission_criticality", 5),
                interoperability_score=app_data.get("interoperability_score", 5),
                data_sensitivity=app_data.get("data_sensitivity", "sensitive"),
                compliance_requirements=app_data.get("compliance_requirements"),
                system_of_record=app_data.get("system_of_record", False),
                public_facing=app_data.get("public_facing", False),
                shared_service=app_data.get("shared_service", False),
                grant_funded=app_data.get("grant_funded", False),
                grant_expiration=app_data.get("grant_expiration")
            )
            db.session.add(app)
            db.session.flush()

            # Add sample contract for some applications
            if app_data.get("cost", 0) > 100000:
                contract = Contract(
                    application_id=app.id,
                    contract_number=f"CTR-2024-{app.id[:8].upper()}",
                    vendor_name=app_data.get("vendor"),
                    contract_type="subscription" if "Cloud" in app_data.get("vendor", "") or app_data.get("vendor") in ["ServiceNow", "Microsoft", "Workday"] else "perpetual",
                    annual_cost=app_data.get("cost"),
                    total_contract_value=app_data.get("cost") * 3,
                    start_date=date.today() - timedelta(days=365),
                    end_date=date.today() + timedelta(days=730),
                    renewal_date=date.today() + timedelta(days=640),
                    renewal_notice_days=90,
                    procurement_method="cooperative" if app_data.get("vendor") in ["Tyler Technologies", "Microsoft", "ServiceNow"] else "competitive_bid",
                    cooperative_contract="Texas DIR" if app_data.get("vendor") in ["Tyler Technologies", "Microsoft", "ServiceNow"] else None,
                    auto_renewal=True,
                    status="active"
                )
                db.session.add(contract)

        # Update portfolio metrics
        portfolio.update_metrics()

        db.session.commit()

        print(f"Created agency hierarchy with {len(departments) + 1} agencies")
        print(f"Created portfolio with {len(applications_data)} applications")
        print(f"Portfolio ID: {portfolio.id}")
        print("\nDemo county government portfolio ready!")


if __name__ == "__main__":
    seed_county_government()
