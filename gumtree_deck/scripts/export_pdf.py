#!/usr/bin/env python3
"""
Export Reveal.js deck to PDF using Playwright
Usage: python scripts/export_pdf.py

Requires: pip install playwright && playwright install chromium
"""

import subprocess
import time
import sys
from pathlib import Path

# Try to import playwright
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
DECK_DIR = SCRIPT_DIR.parent
OUTPUT_PATH = DECK_DIR / "deck.pdf"
PORT = 8000


def export_pdf():
    """Export deck to PDF"""

    # Start local server
    print("Starting local server...")
    server = subprocess.Popen(
        ["python3", "-m", "http.server", str(PORT)],
        cwd=str(DECK_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    time.sleep(2)  # Give server time to start

    try:
        print("Launching browser...")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            # Set viewport for 16:9
            page.set_viewport_size({"width": 1920, "height": 1080})

            url = f"http://localhost:{PORT}/index.html?print-pdf"
            print(f"Loading {url}...")
            page.goto(url, wait_until="networkidle", timeout=60000)

            # Wait for Reveal.js
            page.wait_for_function("""
                () => window.Reveal && window.Reveal.isReady && window.Reveal.isReady()
            """, timeout=30000)

            # Wait for fonts and images
            time.sleep(3)

            print(f"Exporting to {OUTPUT_PATH}...")
            page.pdf(
                path=str(OUTPUT_PATH),
                width="1920px",
                height="1080px",
                print_background=True
            )

            browser.close()
            print(f"PDF exported successfully: {OUTPUT_PATH}")

    finally:
        server.terminate()
        server.wait()


if __name__ == "__main__":
    export_pdf()
