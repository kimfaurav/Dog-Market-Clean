#!/usr/bin/env python3
import pandas as pd

platforms_data = {
    'pets4homes': {'listings': 7280, 'puppies': 30006, 'confidence': '⭐⭐⭐⭐⭐', 'reason': 'Explicit counts 100% coverage'},
    'foreverpuppy': {'listings': 604, 'puppies': 2404, 'confidence': '⭐⭐⭐⭐⭐', 'reason': 'Explicit counts 94% coverage'},
    'petify': {'listings': 575, 'puppies': 2817, 'confidence': '⭐⭐⭐⭐⭐', 'reason': 'Gender split 97% coverage'},
    'freeads': {'listings': 6071, 'puppies': 9431, 'confidence': '⭐⭐', 'reason': 'Partial explicit (11%), filtered outliers'},
    'puppies': {'listings': 532, 'puppies': 1415, 'confidence': '⭐⭐', 'reason': 'Mixed: explicit 35%, gender 25%'},
    'kennel_club': {'listings': 392, 'puppies': 392, 'confidence': '⭐⭐⭐', 'reason': 'DOB-based estimate (100% DOB)'},
    'champdogs': {'listings': 44, 'puppies': 44, 'confidence': '⭐⭐⭐', 'reason': 'DOB-based estimate (100% DOB)'},
    'gumtree': {'listings': 1497, 'puppies': 1497, 'confidence': '⭐', 'reason': 'No data - singleton assumption'},
    'preloved': {'listings': 571, 'puppies': 571, 'confidence': '⭐', 'reason': 'No data - singleton assumption'},
}

print("="*90)
print("CONFIDENCE LEVELS - ALL 9 PLATFORMS")
print("="*90)

high = {k: v for k, v in platforms_data.items() if v['confidence'].count('⭐') >= 4}
medium = {k: v for k, v in platforms_data.items() if v['confidence'].count('⭐') == 3}
medlow = {k: v for k, v in platforms_data.items() if v['confidence'] == '⭐⭐'}
low = {k: v for k, v in platforms_data.items() if v['confidence'].count('⭐') == 1}

print("\n⭐⭐⭐⭐⭐ HIGH CONFIDENCE (3 platforms):")
high_total = 0
for plat in sorted(high.keys()):
    info = high[plat]
    print(f"  {plat:15} {info['puppies']:>6,} puppies | {info['reason']}")
    high_total += info['puppies']

print(f"\n⭐⭐⭐ MEDIUM CONFIDENCE - Data-based estimate (2 platforms):")
med_total = 0
for plat in sorted(medium.keys()):
    info = medium[plat]
    print(f"  {plat:15} {info['puppies']:>6,} puppies | {info['reason']}")
    med_total += info['puppies']

print(f"\n⭐⭐ MEDIUM-LOW CONFIDENCE - Partial data (2 platforms):")
medlow_total = 0
for plat in sorted(medlow.keys()):
    info = medlow[plat]
    print(f"  {plat:15} {info['puppies']:>6,} puppies | {info['reason']}")
    medlow_total += info['puppies']

print(f"\n⭐ LOW CONFIDENCE - No quantity data (2 platforms):")
low_total = 0
for plat in sorted(low.keys()):
    info = low[plat]
    print(f"  {plat:15} {info['puppies']:>6,} puppies | {info['reason']}")
    low_total += info['puppies']

grand_total = high_total + med_total + medlow_total + low_total

print(f"\n{'='*90}")
print("TOTAL DISTRIBUTION BY CONFIDENCE:")
print(f"  High confidence (⭐⭐⭐⭐⭐):        {high_total:>6,} puppies ({100*high_total/grand_total:>5.1f}%)")
print(f"  Medium confidence (⭐⭐⭐):        {med_total:>6,} puppies ({100*med_total/grand_total:>5.1f}%)")
print(f"  Medium-Low (⭐⭐):               {medlow_total:>6,} puppies ({100*medlow_total/grand_total:>5.1f}%)")
print(f"  Low confidence (⭐):            {low_total:>6,} puppies ({100*low_total/grand_total:>5.1f}%)")
print(f"  {'─'*50}")
print(f"  TOTAL:                         {grand_total:>6,} puppies")
print("="*90)
