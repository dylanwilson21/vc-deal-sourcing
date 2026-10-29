#!/usr/bin/env python3
"""Backtest the scoring weights on the fund's historical first checks.

Reads deals.json["backtest"]: a list of {name, outcome, scores}. "Big win" and "Solid" count as wins;
"Flat" and "Loss" count as losses; "Unknown" is ignored. For each factor it measures how well that
factor alone separates wins from losses (AUC: 0.5 = no signal, 1.0 = perfect). With --apply it moves
weight toward factors with more signal, within limits, and saves the result.

Tuning rule (deliberately conservative for small samples):
  new weight = old weight x (0.6 + 0.8 x AUC), renormalized to 100%,
  then each factor capped at +/-5 points from its old weight and kept between 4% and 25%.

Usage: python3 backtest.py deals.json [--apply]
"""
import argparse
from _common import load, save, weights, weighted, KEYS, LABELS

WIN = {"big win", "solid"}
LOSS = {"flat", "loss", "flat?", "loss?"}


def auc(wins, losses):
    if not wins or not losses:
        return float("nan")
    return sum((a > b) + 0.5 * (a == b) for a in wins for b in losses) / (len(wins) * len(losses))


def tune(old, aucs):
    raw = {k: old[k] * (0.6 + 0.8 * (aucs[k] if aucs[k] == aucs[k] else 0.5)) for k in KEYS}
    tot = sum(raw.values())
    new = {k: raw[k] / tot for k in KEYS}
    for _ in range(20):
        new = {k: min(max(new[k], old[k] - 0.05, 0.04), old[k] + 0.05, 0.25) for k in KEYS}
        tot = sum(new.values())
        new = {k: new[k] / tot for k in KEYS}
    rounded = {k: round(new[k] * 100) / 100 for k in KEYS}
    diff = round(1 - sum(rounded.values()), 2)
    top = max(KEYS, key=lambda k: rounded[k])
    rounded[top] = round(rounded[top] + diff, 2)
    return rounded


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deals")
    ap.add_argument("--apply", action="store_true", help="write tuned weights back to deals.json")
    a = ap.parse_args()
    data = load(a.deals)
    rows = data.get("backtest") or []
    wins = [r for r in rows if str(r.get("outcome", "")).strip().lower() in WIN]
    losses = [r for r in rows if str(r.get("outcome", "")).strip().lower() in LOSS]
    if len(wins) < 4 or len(losses) < 4:
        print(f"Need at least 4 wins and 4 losses with outcomes; have {len(wins)} and {len(losses)}. Weights unchanged.")
        return
    old = weights(data)
    aucs = {k: auc([float(r["scores"].get(k, 2)) for r in wins], [float(r["scores"].get(k, 2)) for r in losses]) for k in KEYS}
    new = tune(old, aucs)
    print(f"Backtest on {len(wins)} wins and {len(losses)} losses\n")
    print(f"{'Factor':24} {'AUC':>5} {'Old':>6} {'New':>6}")
    for k in KEYS:
        print(f"{LABELS[k]:24} {aucs[k]:5.2f} {old[k]:6.0%} {new[k]:6.0%}")

    def report(w, label):
        sw = [weighted(r["scores"], w) for r in wins]
        sl = [weighted(r["scores"], w) for r in losses]
        ranked = sorted(wins + losses, key=lambda r: -weighted(r["scores"], w))[:len(wins)]
        hits = sum(1 for r in ranked if r in wins)
        print(f"{label}: AUC {auc(sw, sl):.2f}; winners in top {len(wins)}: {hits} of {len(wins)}")
        return auc(sw, sl), hits
    print()
    a_old, h_old = report(old, "Old weights")
    a_new, h_new = report(new, "New weights")
    data["backtest_summary"] = {
        "factor_auc": {k: round(aucs[k], 3) for k in KEYS}, "wins": len(wins), "losses": len(losses),
        "auc_old": round(a_old, 3), "auc_new": round(a_new, 3), "hits_old": h_old, "hits_new": h_new,
    }
    if a.apply:
        if not data.get("original_weights"):
            data["original_weights"] = old
        data["weights"] = new
        print("\nSaved new weights. Re-run score.py.")
    save(a.deals, data)


if __name__ == "__main__":
    main()
