#!/usr/bin/env python3
"""
Regenerate all metrics and slides.
Single command to sync all slide metrics from canonical data.

Usage:
  python3 regenerate.py
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_command(cmd, desc):
    """Run a command and report status"""
    print(f"\n{'='*60}")
    print(f"  {desc}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, cwd='/Users/kimfaura/Desktop/Dog_Market_Clean')
    if result.returncode != 0:
        print(f"❌ FAILED: {desc}")
        sys.exit(1)
    return result

if __name__ == '__main__':
    print("\n" + "🔄 REGENERATING METRICS & SLIDES".center(60))

    # Guard: refuse to run if git is dirty (prevents accidental overwrite)
    git_status = subprocess.run(
        "git status --porcelain",
        shell=True,
        cwd='/Users/kimfaura/Desktop/Dog_Market_Clean',
        capture_output=True,
        text=True,
    )
    if git_status.returncode != 0:
        print("❌ Cannot check git status. Aborting.")
        sys.exit(1)
    if git_status.stdout.strip():
        print("❌ Git working tree is not clean. Please commit or stash before regenerating.")
        sys.exit(1)
    
    # Always snapshot the current slide before regenerating
    slide_path = Path('/Users/kimfaura/Desktop/Dog_Market_Clean/uk_dog_market_slide.html')
    backup_dir = Path('/Users/kimfaura/Desktop/Dog_Market_Clean/.backups')
    backup_dir.mkdir(exist_ok=True)
    if slide_path.exists():
        ts = datetime.now().strftime('%Y%m%d-%H%M%S')
        backup_path = backup_dir / f"uk_dog_market_slide.{ts}.html"
        backup_path.write_bytes(slide_path.read_bytes())
        print(f"📦 Backup saved: {backup_path}")
    
    # Step 1: Generate canonical metrics
    run_command(
        'python3 canonical_metrics.py',
        'Step 1: Compute canonical metrics from derived.csv'
    )
    
    # Step 2: Generate slides
    run_command(
        'python3 generate_slides.py',
        'Step 2: Generate HTML slides from metrics'
    )
    
    print("\n" + "="*60)
    print("  ✅ SUCCESS: All slides regenerated!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Open uk_dog_market_slide.html in your browser")
    print("  2. All metrics are now synced from canonical_metrics.json")
    print("\nTo modify metrics:")
    print("  1. Edit canonical_metrics.py (compute_metrics function)")
    print("  2. Run: python3 regenerate.py")
    print("="*60 + "\n")
