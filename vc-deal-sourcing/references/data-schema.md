# deals.json

Every script reads and writes this one file. Money is in millions of US dollars unless the field name says otherwise. Fields marked optional can be left out.

```json
{
  "fund": {
    "name": "Example Ventures",
    "website": "https://example.vc",
    "thesis": "One paragraph in plain words.",
    "geographies": ["IL", "IN", "OH", "A6"],
    "stages": ["Pre-seed", "Seed", "Series A"],
    "sectors": ["B2B software", "fintech"],
    "check_size_usd": 1000000,
    "check_range": "$1-7M"
  },
  "prepared_by": "Jane Doe",
  "date": "2026-10-30",
  "deal_count": 40,

  "weights": {"D": 0.20, "X": 0.08, "T": 0.07, "C": 0.10, "M": 0.20, "TR": 0.12, "F": 0.15, "TM": 0.08},
  "original_weights": null,

  "companies": [
    {
      "name": "Acme AI",
      "website": "https://acme.ai",
      "hq": "Chicago, IL",
      "region": "Chicago",
      "sector": "Insurtech; AI policy analysis (SaaS)",
      "channel": "press | edgar | cohort",
      "last_round": "Seed",
      "last_round_m": 4.3,
      "last_round_date": "Feb 2026",
      "total_raised_m": 6.9,
      "post_money_m": 20.0,
      "verified_via": "PitchBook + Form D",
      "founders": [
        {"name": "Ana Lee", "role": "CEO", "linkedin": "https://www.linkedin.com/in/...", "background": "Former coverage attorney; ..."}
      ],
      "funding_summary": "Rounds with dates, leads and valuations.",
      "traction": "Customers, revenue, growth, headcount. Say which numbers are company figures.",
      "fit": "One sentence: why it fits this fund's thesis.",
      "why": "One sentence: why it is interesting.",
      "risks": "Main risks.",
      "next_round": "What the next round likely is and when.",
      "note": "One-line note shown in the deal list.",
      "sources": ["https://..."],
      "scores": {"D": 4.5, "X": 3, "T": 4.5, "C": 4, "M": 4, "TR": 4.5, "F": 5, "TM": 4},
      "blind_scores": {"D": 4, "X": 3, "T": 4, "C": 4, "M": 4, "TR": 4.5, "F": 4, "TM": 3.5},
      "settled": [{"factor": "D", "mine": 5, "blind": 4, "final": 4.5, "reason": "..."}],
      "market": {
        "target": "US independent P&C agencies",
        "base": 39000, "base_desc": "Independent agencies (count)", "base_source": "Big I 2024 Agency Universe Study",
        "filter": 0.35, "filter_note": "Share with commercial books (assumption)", "filter_sourced": false,
        "unit": 25000, "unit_is_pct": false, "unit_note": "ACV (assumption)", "unit_sourced": false,
        "reachable_share": 0.30,
        "crosscheck": "Top-down figure for comparison", "crosscheck_source": "URL or citation"
      }
    }
  ],

  "excluded": [{"name": "Beta Co", "hq": "Detroit, MI", "reason": "Already in the fund's portfolio"}],

  "comps": [{"company": "Gamma", "hq": "Columbus, OH", "round": "Series A", "date": "Aug 2026", "size_m": 12.0, "post_m": 62.0, "note": "Fund led"}],

  "fund_facts": [{"label": "AUM ($M)", "value": 390}, {"label": "Preferred check", "value": "$0.5-5M"}],

  "backtest": [{"name": "Old Co", "outcome": "Big win | Solid | Flat | Loss | Unknown", "entry": "2016 seed",
                "scores": {"D": 4, "X": 5, "T": 4, "C": 5, "M": 4, "TR": 3, "F": 5, "TM": 3}, "note": "..."}],

  "pick": {
    "name": "Acme AI",
    "entry_route": "Seed extension, next 6 months",
    "years": 6, "exit_arr_m": 75, "exit_multiple": 8,
    "dilution": {"Series A": 0.20, "Series B": 0.15, "Series C": 0.10, "Option pool": 0.05},
    "dilution_if_wait": {"Series B": 0.15, "Series C": 0.10, "Option pool": 0.05},
    "target_multiple": 10,
    "last_post_m": 20.0, "last_post_note": "Feb 2026 seed (PitchBook)",
    "step_up": 1.5,
    "next_stage_price_m": 56.0, "next_stage_note": "Median of the fund's recent Series A entries",
    "valuation_text": "Two or three plain sentences for the one-pager.",
    "why_won": "One or two sentences on why it won overall."
  },

  "edgar_leads": [{"name": "...", "city": "...", "state": "IL", "year_inc": "2024", "industry": "Other Technology",
                   "sold": 3500000, "offering_total": "5000000", "file_date": "2026-05-01", "status": "Profiled: fit"}],

  "brief": {
    "title": "How we built the top 10",
    "summary": "Bottom line in 3-5 sentences: count, method, #1 pick and max price.",
    "sections": [{"heading": "1. ...", "body": "Paragraph text. Simple <b>bold</b> is allowed.",
                  "table": [["Header", "Header"], ["cell", "cell"]]}]
  },

  "sources": [{"topic": "Acme AI", "title": "Seed announcement", "url": "https://..."}]
}
```

Notes:
- `scores` holds the final scores, after settling the gaps with the blind scorer. `blind_scores` and `settled` are optional, and fill in when step 6 runs.
- `score.py` writes `weighted`, `founder_score` and `rank` onto each company and sorts the list.
- `backtest.py --apply` copies the old weights to `original_weights` and writes the tuned `weights`.
- Logos are saved to `logos/<company name>.png` and `logos/_fund.png`. The build scripts skip any logo that is missing.
- Any string field can be left empty. The build scripts skip empty sections.
