#!/usr/bin/env python3
"""Pull SEC Form D filings for startups in given states and dates, then filter to likely venture deals.

Uses EDGAR full-text search (efts.sec.gov) filtered by business-address location code, then reads each
filing's primary_doc.xml for industry, amount sold, incorporation year, revenue range and named people.
Location filtering uses the business address, so Delaware-incorporated companies still appear under
the state where they operate. Ontario is A6, British Columbia A1, Quebec A8.

Usage:
  python3 edgar_formd.py --states IL,IN,OH --start 2026-01-01 --end 2026-10-31 \
      --contact "you@example.com" --out edgar.json [--min 750000 --max 15000000 --since-year 2018]

Writes every kept filing to --out and prints them sorted by amount sold.
"""
import argparse
import datetime as dt
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from xml.etree import ElementTree as ET

NAME_EXCLUDE = re.compile(
    r"\b(LLC|L\.?L\.?C|L\.?P\.?|LP|FUND|FUNDS|TRUST|PARTNERS|CAPITAL|HOLDINGS?|INVESTORS?|INVESTCO|PROPERTIES|"
    r"PROPERTY|REALTY|APARTMENTS?|VENTURES|SERIES|REIT|ASSOCIATES|OPPORTUNITY|BANCORP|BANCSHARES|CHURCH|"
    r"ACQUISITION|SPV|FEEDER|MASTER|OFFSHORE|LENDING|CREDIT)\b", re.I)
KEEP_INDUSTRIES = {"Other Technology", "Computers", "Telecommunications", "Other Health Care", "Health Insurance",
                   "Insurance", "Other Banking and Financial Services", "Business Services"}
UA = None


def get(url):
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception:
            time.sleep(1.5 * (i + 1))
    return None


def search(state, start, end):
    hits, frm, total = [], 0, 0
    while True:
        q = urllib.parse.urlencode({"q": "", "forms": "D", "dateRange": "custom", "startdt": start, "enddt": end,
                                    "locationCodes": state, "from": frm})
        d = None
        for attempt in range(4):
            raw = get("https://efts.sec.gov/LATEST/search-index?" + q)
            try:
                d = json.loads(raw) if raw else None
            except ValueError:
                d = None
            if d and "hits" in d:
                break
            time.sleep(2 * (attempt + 1))
        if not d or "hits" not in d:
            print(f"{state}: search stopped early at {frm} results (EDGAR did not answer)", file=sys.stderr)
            break
        batch = d["hits"]["hits"]
        total = d["hits"]["total"]["value"]
        hits += batch
        frm += len(batch)
        if not batch or frm >= total or frm >= 1000:
            break
        time.sleep(0.15)
    return hits, total


def search_split(state, start, end):
    hits, total = search(state, start, end)
    if total >= 1000:
        s, e = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
        if (e - s).days > 14:
            mid = s + (e - s) / 2
            h1 = search_split(state, start, mid.isoformat())
            h2 = search_split(state, (mid + dt.timedelta(days=1)).isoformat(), end)
            return h1 + h2
    return hits


def text(el, path):
    if el is None:
        return None
    x = el.find(path)
    return x.text.strip() if x is not None and x.text else None


def parse(cik, adsh):
    raw = get(f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace('-', '')}/primary_doc.xml")
    if not raw:
        return {}
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return {}
    pi, od = root.find("primaryIssuer"), root.find("offeringData")
    people = []
    for rp in root.findall("relatedPersonsList/relatedPersonInfo"):
        nm = " ".join(filter(None, [text(rp, "relatedPersonName/firstName"), text(rp, "relatedPersonName/lastName")]))
        rel = ",".join(r.text for r in rp.findall("relatedPersonRelationshipList/relationship") if r.text)
        people.append(f"{nm} ({rel})")
    return {
        "entity": text(pi, "entityName"), "city": text(pi, "issuerAddress/city"),
        "state": text(pi, "issuerAddress/stateOrCountry"), "inc_state": text(pi, "jurisdictionOfInc"),
        "year_inc": text(pi, "yearOfInc/value"), "entity_type": text(pi, "entityType"),
        "industry": text(od, "industryGroup/industryGroupType"), "revenue_range": text(od, "issuerSize/revenueRange"),
        "first_sale": text(od, "typeOfFiling/dateOfFirstSale/value"),
        "offering_total": text(od, "offeringSalesAmounts/totalOfferingAmount"),
        "sold": text(od, "offeringSalesAmounts/totalAmountSold"),
        "investors": text(od, "investors/totalNumberAlreadyInvested"), "people": "; ".join(people[:6]),
    }


def main():
    global UA
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--states", required=True, help="comma-separated EDGAR location codes, e.g. IL,OH,A6")
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--contact", required=True, help="contact email or name for the SEC User-Agent header")
    ap.add_argument("--out", default="edgar.json")
    ap.add_argument("--min", type=float, default=750000)
    ap.add_argument("--max", type=float, default=15000000)
    ap.add_argument("--since-year", type=int, default=2018)
    a = ap.parse_args()
    UA = f"vc-deal-sourcing research {a.contact}"
    seen, cands = set(), []
    for st in [s.strip() for s in a.states.split(",") if s.strip()]:
        hits = search_split(st, a.start, a.end)
        kept = 0
        for h in hits:
            s = h["_source"]
            if s.get("form") != "D":
                continue
            name = re.sub(r"\s*\(CIK.*$", "", (s.get("display_names") or [""])[0]).strip()
            cik = (s.get("ciks") or [None])[0]
            if not cik or cik in seen or NAME_EXCLUDE.search(name):
                continue
            seen.add(cik)
            cands.append({"name": name, "cik": cik, "adsh": s["adsh"], "file_date": s["file_date"], "query_state": st})
            kept += 1
        print(f"{st}: {len(hits)} filings, {kept} after name filter", file=sys.stderr)
    out = []
    for i, c in enumerate(cands):
        c.update(parse(c["cik"], c["adsh"]))
        time.sleep(0.12)
        try:
            sold = float(c.get("sold") or 0)
        except ValueError:
            sold = 0
        y = c.get("year_inc")
        if c.get("industry") not in KEEP_INDUSTRIES:
            continue
        if c.get("entity_type") and "Corporation" not in c["entity_type"]:
            continue
        if y and y.isdigit() and int(y) < a.since_year:
            continue
        if not (a.min <= sold <= a.max):
            continue
        c["sold"] = sold
        out.append(c)
        if i % 100 == 0:
            print(f"read {i} of {len(cands)} filings", file=sys.stderr)
    out.sort(key=lambda c: -c["sold"])
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    for c in out:
        print(f"{c['name'][:40]:40} {(c.get('city') or '').title()[:18]:18} {c.get('state') or '':3} "
              f"{c.get('year_inc') or '':5} ${c['sold'] / 1e6:5.1f}M  {c['file_date']}  {c.get('industry')}")
    print(f"\n{len(out)} likely startup raises saved to {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
