#!/usr/bin/env python3
"""
Extract quatrains from mnostradamus.free.fr HTML files.
Format: <h2>RomanNum.</h2><p>Line1<br>Line2<br>...</p>
"""

import re
import json
from pathlib import Path

def extract_quatrains_from_file(html_path, century_num):
    """Extract all quatrains from mnostradamus HTML file."""
    with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    quatrains = []

    # Pattern: <h2>ROMAN.</h2><p>Line1<br>Line2<br>...</p>
    # Quatrains are separated by <h2> headers
    parts = re.split(r'<h2>[IVXLCDM]+\.</h2>', content)

    for i, part in enumerate(parts[1:], 1):  # Skip first part (before first quatrain)
        quatrain_num = i

        # Remove all HTML tags, keep <br> as line separators
        # First get the <p>...</p> block
        p_match = re.search(r'<p>(.*?)</p>', part, re.DOTALL)
        if not p_match:
            continue

        block = p_match.group(1)

        # Split by <br> tags
        lines = re.split(r'<br\s*/?>', block)
        lines = [re.sub(r'<[^>]+>', '', l).strip() for l in lines]
        lines = [l for l in lines if l]

        french = ' '.join(lines)

        quatrains.append({
            "century": century_num,
            "quatrain": quatrain_num,
            "french": french,
            "english": ""  # English not available in this source
        })

    return quatrains

def main():
    all_quatrains = []

    for century in range(1, 11):
        html_file = f"nostradamus/source/centurie{century:02d}_full.html"
        try:
            quatrains = extract_quatrains_from_file(html_file, century)
            print(f"Century {century}: {len(quatrains)} quatrains")
            all_quatrains.extend(quatrains)
        except Exception as e:
            print(f"Century {century}: ERROR - {e}")

    # Sort by century, then quatrain number
    all_quatrains.sort(key=lambda x: (x["century"], x["quatrain"]))

    # Statistics
    by_century = {}
    for q in all_quatrains:
        c = q["century"]
        by_century[c] = by_century.get(c, 0) + 1

    print(f"\nTotal: {len(all_quatrains)} quatrains")
    print("\nBy century:")
    for c in sorted(by_century.keys()):
        print(f"  Century {c}: {by_century[c]}")

    # Save
    output = "nostradamus/data/processed/quatrains_bilingual.json"
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(all_quatrains, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {output}")

    # Show samples
    print("\n=== SAMPLE QUATRAINS ===")
    for q in all_quatrains[:5]:
        print(f"\nCentury {q['century']}, Quatrain {q['quatrain']}:")
        print(f"  FR: {q['french'][:70]}...")

if __name__ == "__main__":
    main()
