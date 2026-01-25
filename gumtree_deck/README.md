# Gumtree Supply-Side Intelligence Engine

A Reveal.js presentation pitching Gumtree's supply-side intelligence capabilities, using dogs as an illustrative case study.

## Quick Start

```bash
# Serve locally (open http://localhost:8000)
python3 -m http.server 8000

# Export to PDF (requires playwright)
python3 scripts/export_pdf.py
```

### Prerequisites

```bash
# Install Playwright if not already installed
pip3 install playwright
playwright install chromium
```

## Structure

```
gumtree_deck/
├── index.html          # Main presentation (19 slides)
├── theme.css           # Custom dark/orange theme
├── deck.pdf            # Generated PDF output
├── package.json        # npm scripts
├── assets/             # Slide images from dogs analysis
│   └── slide_01-12.png
├── scripts/
│   └── export-pdf.js   # Playwright PDF exporter
└── vendor/             # Reveal.js 5.1.0 (offline)
    ├── dist/
    └── plugin/
```

## Slides Overview

### Section A: Gumtree Framing (Slides 1-8)
1. Cover - "Supply-Side Intelligence Engine"
2. Why It Matters - Gumtree's unique data position
3. Current Blind Spots - What competitors see vs. what Gumtree could see
4. What the Engine Does - Data pipeline diagram
5. Questions Answered - Example insights
6. Outputs - Reports, alerts, API
7. Funding Rationale - Investment justification
8. Case Study Intro - Transition to dogs example

### Section B: Dogs Case Study (Slides 9-15)
9. Market Coverage - 10 platforms, 59K dogs
10. Deduplication - Cross-platform matching
11. Freshness Advantage - Real-time vs. competitors
12. Seller Intelligence - Multi-platform sellers
13. Compliance Signals - Lucy's Law detection
14. Welfare Indicators - Breeding frequency analysis
15. Summary - Key findings

### Section C: Generalise & Plan (Slides 16-19)
16. Other Verticals - Cars, jobs, property grid
17. Delivery Timeline - MVP to full product
18. Next Steps - Immediate actions
19. Close - Contact & thank you

## Keyboard Shortcuts

- **Arrow keys**: Navigate slides
- **F**: Fullscreen
- **S**: Speaker notes
- **O**: Overview mode
- **ESC**: Exit fullscreen/overview

## Customization

Edit `theme.css` to adjust colors:
- `--gt-bg`: Background color
- `--gt-orange`: Accent color
- `--gt-text`: Primary text color
- `--gt-text-muted`: Secondary text color

## Notes

- Presentation is 16:9 aspect ratio
- Works fully offline (Reveal.js bundled)
- Images from dogs analysis embedded in assets/
