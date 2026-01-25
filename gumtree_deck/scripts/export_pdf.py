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

# Try to import PIL for PDF creation
try:
    from PIL import Image
except ImportError:
    print("Pillow not installed. Run: pip install Pillow")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
DECK_DIR = SCRIPT_DIR.parent
OUTPUT_PATH = DECK_DIR / "deck.pdf"
TEMP_DIR = DECK_DIR / ".pdf_temp"
PORT = 8000

# Scale factor for high-resolution output (2 = retina quality)
SCALE_FACTOR = 2


def export_pdf():
    """Export deck to PDF by capturing each slide as a high-res image"""

    # Create temp directory
    TEMP_DIR.mkdir(exist_ok=True)

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

            # Create context with high DPI for crisp rendering
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                device_scale_factor=SCALE_FACTOR
            )
            page = context.new_page()

            # Load the presentation
            url = f"http://localhost:{PORT}/index.html"
            print(f"Loading {url}...")
            page.goto(url, wait_until="networkidle", timeout=60000)

            # Wait for Reveal.js
            page.wait_for_function("""
                () => window.Reveal && window.Reveal.isReady && window.Reveal.isReady()
            """, timeout=30000)

            # Wait for fonts and images
            time.sleep(2)

            # Get total number of slides
            total_slides = page.evaluate("() => Reveal.getTotalSlides()")
            print(f"Found {total_slides} slides (capturing at {SCALE_FACTOR}x resolution)")

            # Capture each slide
            slide_images = []
            for i in range(total_slides):
                print(f"Capturing slide {i + 1}/{total_slides}...")

                # Navigate to slide
                page.evaluate(f"() => Reveal.slide({i})")
                time.sleep(0.3)  # Wait for transition

                # Screenshot (will be 2560x1440 at 2x scale)
                img_path = TEMP_DIR / f"slide_{i:03d}.png"
                page.screenshot(path=str(img_path))
                slide_images.append(img_path)

            context.close()
            browser.close()

        # Convert images to PDF
        print(f"Creating PDF with {len(slide_images)} pages...")
        images = [Image.open(p).convert("RGB") for p in slide_images]

        if images:
            # Save with high DPI for print quality
            images[0].save(
                str(OUTPUT_PATH),
                save_all=True,
                append_images=images[1:] if len(images) > 1 else [],
                resolution=300.0  # 300 DPI for print quality
            )

        # Cleanup temp files
        for img_path in slide_images:
            img_path.unlink()
        TEMP_DIR.rmdir()

        print(f"PDF exported successfully: {OUTPUT_PATH}")

    finally:
        server.terminate()
        server.wait()


if __name__ == "__main__":
    export_pdf()
