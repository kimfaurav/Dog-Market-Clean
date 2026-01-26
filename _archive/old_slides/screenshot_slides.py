#!/usr/bin/env python3
"""
screenshot_slides.py - Screenshot each slide and combine into PDF

Uses Playwright to render the HTML slides and capture each one,
then combines them into a single PDF document using PIL.
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from PIL import Image

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
        # Use 2x scale for crisp/retina quality screenshots
        page = await browser.new_page(
            viewport={"width": 900, "height": 600},
            device_scale_factor=2
        )

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

        await browser.close()

    # Combine screenshots into PDF using PIL
    print(f"\nGenerating PDF from {len(screenshot_paths)} screenshots...")

    images = []
    for path in screenshot_paths:
        img = Image.open(path)
        # Convert to RGB if necessary (PNG might have alpha channel)
        if img.mode == 'RGBA':
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # Use alpha as mask
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        images.append(img)

    # Save as PDF with high resolution
    if images:
        images[0].save(
            PDF_PATH,
            save_all=True,
            append_images=images[1:],
            resolution=300.0  # High DPI for crisp output
        )

    print(f"\nDone!")
    print(f"  Screenshots: {OUTPUT_DIR}/")
    print(f"  PDF: {PDF_PATH}")


def main():
    asyncio.run(screenshot_slides())


if __name__ == "__main__":
    main()
