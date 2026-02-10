"""
Screenshot Tool for App Rationalization Pro
Automatically captures screenshots of all pages in the application.

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    python capture_screenshots.py
    python capture_screenshots.py --mobile      # Include mobile/tablet views
    python capture_screenshots.py --portfolio   # Use existing portfolio ID
"""

import os
import sys
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

# Configuration
BASE_URL = "http://127.0.0.1:5102"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "screenshots")

# Viewport configurations
VIEWPORTS = {
    "desktop": {"width": 1920, "height": 1080},
    "tablet": {"width": 768, "height": 1024},
    "mobile": {"width": 375, "height": 812},
}

# Define all pages to capture (static pages without portfolio)
STATIC_PAGES = [
    {
        "name": "01_Landing_Page",
        "url": "/",
        "wait_for": "body",
        "description": "Main landing page"
    },
    {
        "name": "02_Dashboard",
        "url": "/dashboard",
        "wait_for": ".container",
        "description": "Portfolio dashboard"
    },
    {
        "name": "03_Chat_Interface",
        "url": "/chat",
        "wait_for": ".container",
        "description": "AI Chat consultant"
    },
]

# Pages that require a portfolio ID
PORTFOLIO_PAGES = [
    {
        "name": "04_Portfolio_Detail",
        "url": "/portfolio/{portfolio_id}",
        "wait_for": ".container",
        "description": "Portfolio detail view"
    },
    {
        "name": "05_Results",
        "url": "/results/{portfolio_id}",
        "wait_for": ".container",
        "description": "Rationalization results"
    },
    {
        "name": "06_Cost_Analysis",
        "url": "/costs/{portfolio_id}",
        "wait_for": ".container",
        "description": "Cost analysis dashboard"
    },
    {
        "name": "07_Compliance",
        "url": "/compliance/{portfolio_id}",
        "wait_for": ".container",
        "description": "Compliance assessment"
    },
    {
        "name": "08_WhatIf_Scenarios",
        "url": "/whatif/{portfolio_id}",
        "wait_for": ".container",
        "description": "What-If scenario simulator"
    },
    {
        "name": "09_Roadmap",
        "url": "/roadmap/{portfolio_id}",
        "wait_for": ".container",
        "description": "Prioritization roadmap"
    },
    {
        "name": "10_Risk_Assessment",
        "url": "/risk/{portfolio_id}",
        "wait_for": ".container",
        "description": "Risk assessment dashboard"
    },
    {
        "name": "11_Benchmark",
        "url": "/benchmark/{portfolio_id}",
        "wait_for": ".container",
        "description": "Industry benchmark comparison"
    },
    {
        "name": "12_Dependencies",
        "url": "/dependencies/{portfolio_id}",
        "wait_for": ".container",
        "description": "Dependency mapping"
    },
    {
        "name": "13_Integrations",
        "url": "/integrations/{portfolio_id}",
        "wait_for": ".container",
        "description": "Integration assessment"
    },
    {
        "name": "14_Vendors",
        "url": "/vendors/{portfolio_id}",
        "wait_for": ".container",
        "description": "Vendor risk management"
    },
    {
        "name": "15_Technical_Debt",
        "url": "/tech-debt/{portfolio_id}",
        "wait_for": ".container",
        "description": "Technical debt calculator"
    },
    {
        "name": "16_Lifecycle_Management",
        "url": "/lifecycle/{portfolio_id}",
        "wait_for": ".container",
        "description": "Application lifecycle management"
    },
]


def sanitize_filename(name):
    """Convert a name to a safe filename."""
    return name.replace(" ", "_").replace("/", "_").replace("?", "_").replace("&", "_")


async def take_screenshot(page, name, output_path, full_page=True):
    """Take a screenshot and save it."""
    await page.screenshot(path=output_path, full_page=full_page)
    print(f"  [OK] Captured: {name}")


async def capture_page(page, page_config, output_dir, portfolio_id=None, viewport_name="desktop"):
    """Capture a single page."""
    name = page_config["name"]
    url = page_config["url"]

    # Replace portfolio_id placeholder if needed
    if "{portfolio_id}" in url:
        if not portfolio_id:
            print(f"  [SKIP] Skipping {name} - no portfolio ID")
            return
        url = url.replace("{portfolio_id}", portfolio_id)

    wait_for = page_config.get("wait_for", "body")
    description = page_config.get("description", name)
    prefix = f"{viewport_name}_" if viewport_name != "desktop" else ""

    # Navigate to page
    try:
        await page.goto(f"{BASE_URL}{url}", timeout=30000)
    except Exception as e:
        print(f"  [ERROR] Could not navigate to {name}: {e}")
        return

    # Wait for content to load
    try:
        await page.wait_for_selector(wait_for, timeout=15000)
    except:
        print(f"  [WARN] Could not find {wait_for} on {name}")

    # Wait for charts/animations to render
    await asyncio.sleep(2)

    # Take screenshot
    filename = f"{prefix}{sanitize_filename(name)}.png"
    await take_screenshot(
        page,
        f"{description} ({viewport_name})" if viewport_name != "desktop" else description,
        os.path.join(output_dir, filename)
    )


async def create_demo_portfolio(page):
    """Create a demo portfolio and return its ID."""
    print("Creating demo portfolio...")

    # Navigate to dashboard
    await page.goto(f"{BASE_URL}/dashboard")
    await asyncio.sleep(1)

    # Click create demo button via API
    response = await page.evaluate("""
        async () => {
            const res = await fetch('/api/demo/create', { method: 'POST' });
            return await res.json();
        }
    """)

    if response and response.get('portfolio', {}).get('id'):
        portfolio_id = response['portfolio']['id']
        print(f"  [OK] Created demo portfolio: {portfolio_id}")
        return portfolio_id
    else:
        print("  [ERROR] Could not create demo portfolio")
        return None


async def main():
    """Main function to capture all screenshots."""
    # Parse command line arguments
    include_mobile = "--mobile" in sys.argv
    use_existing = "--portfolio" in sys.argv

    # Get portfolio ID from args if provided
    portfolio_id = None
    for i, arg in enumerate(sys.argv):
        if arg == "--portfolio" and i + 1 < len(sys.argv):
            portfolio_id = sys.argv[i + 1]
            break

    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(OUTPUT_DIR, timestamp)
    os.makedirs(output_dir, exist_ok=True)

    # Create subdirectories for mobile/tablet
    if include_mobile:
        os.makedirs(os.path.join(output_dir, "mobile"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "tablet"), exist_ok=True)

    print(f"\n{'='*60}")
    print("App Rationalization Pro - Screenshot Tool")
    print(f"{'='*60}")
    print(f"Output directory: {output_dir}")
    print(f"Base URL: {BASE_URL}")
    print(f"Options: mobile={include_mobile}")
    print(f"{'='*60}\n")

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)

        # Desktop context with retina quality
        desktop_context = await browser.new_context(
            viewport=VIEWPORTS["desktop"],
            device_scale_factor=2  # Retina quality
        )
        page = await desktop_context.new_page()

        # Test connection
        print("Testing connection to App Rationalization Pro...")
        try:
            await page.goto(BASE_URL, timeout=10000)
            print("[OK] Connected successfully\n")
        except Exception as e:
            print(f"[ERROR] Could not connect to {BASE_URL}")
            print(f"  Make sure the Flask server is running:")
            print(f"  Run: python web/app.py")
            await browser.close()
            return

        # Create demo portfolio if none provided
        if not portfolio_id:
            portfolio_id = await create_demo_portfolio(page)

        # Capture static pages
        print("\nCapturing static pages...")
        print("-" * 40)
        for page_config in STATIC_PAGES:
            try:
                await capture_page(page, page_config, output_dir)
            except Exception as e:
                print(f"  [ERROR] Error capturing {page_config['name']}: {e}")

        # Capture portfolio-dependent pages
        if portfolio_id:
            print("\nCapturing portfolio pages...")
            print("-" * 40)
            for page_config in PORTFOLIO_PAGES:
                try:
                    await capture_page(page, page_config, output_dir, portfolio_id)
                except Exception as e:
                    print(f"  [ERROR] Error capturing {page_config['name']}: {e}")
        else:
            print("\n[WARN] Skipping portfolio pages - no portfolio available")

        await desktop_context.close()

        # Mobile and tablet views
        if include_mobile and portfolio_id:
            print("\nCapturing mobile and tablet views...")
            print("-" * 40)

            # Key pages to capture in mobile/tablet
            responsive_pages = [
                {"name": "01_Landing_Page", "url": "/", "wait_for": "body"},
                {"name": "02_Dashboard", "url": "/dashboard", "wait_for": ".container"},
                {"name": "04_Portfolio_Detail", "url": f"/portfolio/{portfolio_id}", "wait_for": ".container"},
                {"name": "15_Technical_Debt", "url": f"/tech-debt/{portfolio_id}", "wait_for": ".container"},
                {"name": "16_Lifecycle_Management", "url": f"/lifecycle/{portfolio_id}", "wait_for": ".container"},
            ]

            for viewport_name in ["tablet", "mobile"]:
                print(f"\n  {viewport_name.title()} viewport...")
                context = await browser.new_context(
                    viewport=VIEWPORTS[viewport_name],
                    device_scale_factor=2
                )
                resp_page = await context.new_page()

                for page_config in responsive_pages:
                    try:
                        # Don't replace portfolio_id since we already included it in the URL
                        await capture_page(
                            resp_page,
                            page_config,
                            os.path.join(output_dir, viewport_name),
                            None,  # Already in URL
                            viewport_name
                        )
                    except Exception as e:
                        print(f"    [ERROR] Error: {e}")

                await context.close()

        await browser.close()

    # Summary
    total_screenshots = 0
    for root, dirs, files in os.walk(output_dir):
        total_screenshots += len([f for f in files if f.endswith('.png')])

    print(f"\n{'='*60}")
    print(f"Complete! Captured {total_screenshots} screenshots")
    print(f"Location: {os.path.abspath(output_dir)}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
