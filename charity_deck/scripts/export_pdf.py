#!/usr/bin/env python3
"""
Export Reveal.js deck to PDF using Playwright
Usage: python scripts/export_pdf.py

Requires: pip install playwright pillow && playwright install chromium
"""

import subprocess
import time
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

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

# High resolution for crisp output
SCALE = 2  # 2x for retina quality


def export_pdf():
    """Export deck to PDF by capturing each slide individually"""

    TEMP_DIR.mkdir(exist_ok=True)

    print("Starting local server...")
    server = subprocess.Popen(
        ["python3", "-m", "http.server", str(PORT)],
        cwd=str(DECK_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(2)

    try:
        print("Launching browser...")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                device_scale_factor=SCALE
            )
            page = context.new_page()

            # Load presentation in NORMAL mode (not print-pdf)
            url = f"http://localhost:{PORT}/index.html"
            print(f"Loading {url}...")
            page.goto(url, wait_until="networkidle", timeout=60000)

            # Wait for Reveal.js
            page.wait_for_function("""
                () => window.Reveal && window.Reveal.isReady && window.Reveal.isReady()
            """, timeout=30000)

            # Disable transitions for instant slide changes
            page.evaluate("() => Reveal.configure({ transition: 'none' })")
            time.sleep(1)

            total = page.evaluate("() => Reveal.getTotalSlides()")
            print(f"Capturing {total} slides at {SCALE}x resolution...")

            images = []
            for i in range(total):
                # Navigate to slide
                page.evaluate(f"() => Reveal.slide({i})")
                # Small wait for any render updates
                time.sleep(0.2)

                # Capture screenshot
                img_path = TEMP_DIR / f"slide_{i:03d}.png"
                page.screenshot(path=str(img_path))
                images.append(img_path)
                print(f"  Slide {i + 1}/{total}")

            context.close()
            browser.close()

        # Convert to PDF
        print("Creating PDF...")
        pil_images = []
        for img_path in images:
            img = Image.open(img_path).convert("RGB")
            pil_images.append(img)

        # Save as PDF with proper sizing
        # Images are 2560x1440 (1280x720 at 2x scale)
        # Set DPI so that 2560px = 1280pt (1pt = 1/72 inch at 144 DPI for 2x)
        pil_images[0].save(
            str(OUTPUT_PATH),
            "PDF",
            save_all=True,
            append_images=pil_images[1:],
            resolution=144.0  # 72 * 2 for 2x scale
        )

        # Cleanup
        for img_path in images:
            img_path.unlink()
        TEMP_DIR.rmdir()

        print(f"PDF exported: {OUTPUT_PATH}")
        print(f"  {total} pages, {OUTPUT_PATH.stat().st_size / 1024 / 1024:.1f} MB")

    finally:
        server.terminate()
        server.wait()


if __name__ == "__main__":
    export_pdf()
