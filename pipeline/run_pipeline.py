#!/usr/bin/env python3
"""
Master Pipeline Runner

Runs all pipeline steps in sequence:
1. Build Facts (raw CSVs → facts.csv)
2. Build Derived (facts.csv → derived.csv)
3. Build Summary (derived.csv → platform_supply_summary.csv)

Usage:
    python run_pipeline.py
"""

import subprocess
import sys
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parent

STEPS = [
    ("Step 1: Build Facts", "pipeline_01_build_facts.py"),
    ("Step 2: Build Derived Views", "pipeline_02_build_derived.py"),
    ("Step 3: Build Summary", "pipeline_03_build_summary.py"),
]


def run_step(name: str, script: str) -> bool:
    """Run a pipeline step and return success status."""
    print("\n" + "=" * 70)
    print(f"RUNNING: {name}")
    print("=" * 70 + "\n")
    
    script_path = PIPELINE_DIR / script
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(PIPELINE_DIR.parent),  # Run from repo root
    )
    
    if result.returncode != 0:
        print(f"\n❌ FAILED: {name}")
        return False
    
    print(f"\n✓ Completed: {name}")
    return True


def main():
    print("=" * 70)
    print("DOG MARKET PIPELINE - CLEAN REBUILD")
    print("=" * 70)
    
    for name, script in STEPS:
        if not run_step(name, script):
            print(f"\n⚠️  Pipeline stopped at: {name}")
            sys.exit(1)
    
    print("\n" + "=" * 70)
    print("✓ PIPELINE COMPLETE")
    print("=" * 70)
    print("\nOutputs:")
    print("  - output/facts/facts.csv")
    print("  - output/views/derived.csv")
    print("  - output/views/platform_supply_summary.csv")


if __name__ == "__main__":
    main()
