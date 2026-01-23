#!/usr/bin/env python3
"""
screenshot_slides.py - Screenshot each slide and combine into PDF

Uses Playwright to render the HTML slides and capture each one,
then combines them into a single PDF document.
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SCRIPT_DIR = Path(__file__).parent
HTML_PATH = SCRIPT_DIR / "uk_dog_market_slide.html"
OUTPUT_DIR = SCRIPT_DIR / "slide_screenshots"
PDF_PATH = SCRIPT_DIR / "uk_dog_market_slides.pdf"


async def screenshot_slides():
    """Take screenshots of each slide and combine into PDF."""

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1200, "height": 900})

        # Load the HTML file
        file_url = f"file://{HTML_PATH.absolute()}"
        print(f"Loading {file_url}")
        await page.goto(file_url)

        # Wait for fonts to load
        await page.wait_for_timeout(1000)

        # Find all slides
        slides = await page.query_selector_all(".slide")
        num_slides = len(slides)
        print(f"Found {num_slides} slides")

        screenshot_paths = []

        for i, slide in enumerate(slides, 1):
            # Scroll slide into view
            await slide.scroll_into_view_if_needed()
            await page.wait_for_timeout(200)  # Let animations settle

            # Screenshot the slide
            screenshot_path = OUTPUT_DIR / f"slide_{i:02d}.png"
            await slide.screenshot(path=str(screenshot_path))
            screenshot_paths.append(screenshot_path)
            print(f"  Captured slide {i}/{num_slides}")

        # Now create PDF by printing the page
        print(f"\nGenerating PDF...")

        # Create a new page with proper PDF settings
        pdf_page = await browser.new_page()
        await pdf_page.goto(file_url)
        await pdf_page.wait_for_timeout(1000)

        # Generate PDF with proper slide dimensions
        await pdf_page.pdf(
            path=str(PDF_PATH),
            width="900px",
            height="600px",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}
        )

        await browser.close()

    print(f"\nDone!")
    print(f"  Screenshots: {OUTPUT_DIR}/")
    print(f"  PDF: {PDF_PATH}")


def main():
    asyncio.run(screenshot_slides())


if __name__ == "__main__":
    main()
