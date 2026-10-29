#!/usr/bin/env python3
"""Compare your scores with the blind second scorer's and list the gaps to settle.

For every company with blind_scores, prints each factor where the two differ by >= --gap (default 1.0)
and is not yet in that company's "settled" list. Settle each by editing the company's final score
in "scores" and adding {factor, mine, blind, final, reason} to "settled". Then re-run score.py.

Also prints how many companies the two scorers both place in the top 10.

Usage: python3 reconcile.py deals.json [--gap 1.0]
"""
import argparse
from _common import load, weights, weighted, KEYS


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deals")
    ap.add_argument("--gap", type=float, default=1.0)
    a = ap.parse_args()
    data = load(a.deals)
    w = weights(data)
    comps = [c for c in data.get("companies", []) if c.get("blind_scores")]
    if not comps:
        print("No blind_scores found.")
        return
    open_gaps = 0
    for c in comps:
        done = {s["factor"] for s in c.get("settled", [])}
        for k in KEYS:
            mine, blind = float(c["scores"].get(k, 2)), float(c["blind_scores"].get(k, 2))
            if abs(mine - blind) >= a.gap and k not in done:
                open_gaps += 1
                print(f"{c['name']:28} {k:3} mine {mine:3.1f}  blind {blind:3.1f}")
    print(f"\nOpen gaps: {open_gaps}")
    mine_top = {c["name"] for c in sorted(data["companies"], key=lambda c: -weighted(c["scores"], w))[:10]}
    blind_top = {c["name"] for c in sorted(comps, key=lambda c: -weighted(c["blind_scores"], w))[:10]}
    print(f"Top-10 overlap: {len(mine_top & blind_top)} of 10")


if __name__ == "__main__":
    main()
