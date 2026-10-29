"""Shared helpers for the vc-deal-sourcing scripts."""
import json
import os

KEYS = ["D", "X", "T", "C", "M", "TR", "F", "TM"]
FOUNDER_KEYS = ["D", "X", "T", "C"]
LABELS = {
    "D": "Domain insight", "X": "Prior exits / scaling", "T": "Technical depth", "C": "Team completeness",
    "M": "Market", "TR": "Traction", "F": "Fund fit", "TM": "Timing",
}
DEFAULT_WEIGHTS = {"D": 0.20, "X": 0.08, "T": 0.07, "C": 0.10, "M": 0.20, "TR": 0.12, "F": 0.15, "TM": 0.08}


def load(path):
    with open(path) as f:
        return json.load(f)


def save(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def weights(data):
    w = data.get("weights") or DEFAULT_WEIGHTS
    return {k: float(w.get(k, DEFAULT_WEIGHTS[k])) for k in KEYS}


def weighted(scores, w):
    return sum(w[k] * float(scores.get(k, 2)) for k in KEYS)


def founder_score(scores, w):
    tot = sum(w[k] for k in FOUNDER_KEYS)
    return sum(w[k] * float(scores.get(k, 2)) for k in FOUNDER_KEYS) / tot if tot else 0.0


def slug(text):
    return "".join(c if c.isalnum() else "_" for c in (text or "fund")).strip("_") or "fund"
