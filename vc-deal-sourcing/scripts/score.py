#!/usr/bin/env python3
"""Rank companies in deals.json by weighted score.

Writes weighted, founder_score and rank onto each company, sorts the list, and prints the top N.

Usage: python3 score.py deals.json [--top 40]
"""
import argparse
from _common import load, save, weights, weighted, founder_score, KEYS


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deals")
    ap.add_argument("--top", type=int, default=None, help="rows to print (default: deal_count)")
    a = ap.parse_args()
    data = load(a.deals)
    w = weights(data)
    tot = sum(w.values())
    if abs(tot - 1) > 0.001:
        print(f"Warning: weights sum to {tot:.3f}, not 1.0")
    missing = []
    for c in data.get("companies", []):
        s = c.get("scores") or {}
        gaps = [k for k in KEYS if k not in s]
        if gaps:
            missing.append((c.get("name"), gaps))
        c["weighted"] = round(weighted(s, w), 4)
        c["founder_score"] = round(founder_score(s, w), 4)
    data["companies"].sort(key=lambda c: -c["weighted"])
    for i, c in enumerate(data["companies"], 1):
        c["rank"] = i
    save(a.deals, data)
    n = a.top or data.get("deal_count", 40)
    print(f"{'#':>3}  {'Company':28} {'Score':>6} {'Founder':>8}  HQ")
    for c in data["companies"][:n]:
        print(f"{c['rank']:>3}  {c['name'][:28]:28} {c['weighted']:6.2f} {c['founder_score']:8.2f}  {c.get('hq', '')}")
    if missing:
        print("\nMissing scores (counted as 2):")
        for name, gaps in missing:
            print(f"  {name}: {', '.join(gaps)}")


if __name__ == "__main__":
    main()
