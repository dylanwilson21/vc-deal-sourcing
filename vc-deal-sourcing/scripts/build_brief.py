#!/usr/bin/env python3
"""Build the process brief PDF from deals.json["brief"].

You write the content (summary plus numbered sections, each with an optional table); this script lays
it out. Aim for two pages: what the thesis became as rules, how sourcing worked, how scoring and the
weights worked (including the backtest), what the blind second scorer changed, the top 10 table, the
pick and its price, and the pros and cons of using AI for the work.

If a section's table is omitted and the heading contains "top 10", a table is generated from the data.

Usage: python3 build_brief.py deals.json [--out <Fund>_Process_Brief.pdf]
"""
import argparse
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from _common import load, slug

NAVY = colors.HexColor("#1F3A5F")
LIGHT = colors.HexColor("#EEF2F7")
GRID = colors.HexColor("#C9D1DC")
base = ParagraphStyle("b", fontName="Helvetica", fontSize=9.4, leading=12.4, spaceAfter=5)
small = ParagraphStyle("sm", parent=base, fontSize=8.5, leading=11, spaceAfter=0)
headc = ParagraphStyle("hc", parent=small, fontName="Helvetica-Bold", textColor=colors.white)
title = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=NAVY, spaceAfter=2)
meta = ParagraphStyle("m", parent=base, fontSize=9, textColor=colors.HexColor("#555555"), spaceAfter=10)
h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=NAVY, spaceBefore=6, spaceAfter=3)


def table(rows, width):
    ncol = len(rows[0])
    data = [[Paragraph(str(c), headc if i == 0 else small) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[width / ncol] * ncol if ncol > 2 else None, repeatRows=1)
    st = [("GRID", (0, 0), (-1, -1), 0.4, GRID), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TOPPADDING", (0, 0), (-1, -1), 3),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]
    st += [("BACKGROUND", (0, r), (-1, r), LIGHT) for r in range(2, len(rows), 2)]
    t.setStyle(TableStyle(st))
    return t


def top10_table(data):
    comps = sorted(data.get("companies", []), key=lambda c: c.get("rank", 9999))[:10]
    rows = [["#", "Company", "HQ", "Score", "Why it is interesting"]]
    for c in comps:
        rows.append([c.get("rank", ""), c["name"], c.get("hq", ""), f"{c.get('weighted', 0):.2f}", c.get("why", "")])
    t = Table([[Paragraph(str(x), headc if i == 0 else small) for x in r] for i, r in enumerate(rows)],
              colWidths=[0.3 * inch, 1.1 * inch, 1.05 * inch, 0.5 * inch, 4.05 * inch], repeatRows=1)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, GRID), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("BACKGROUND", (0, 0), (-1, 0), NAVY)] +
                          [("BACKGROUND", (0, r), (-1, r), LIGHT) for r in range(2, len(rows), 2)]))
    return t


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deals")
    ap.add_argument("--out")
    a = ap.parse_args()
    data = load(a.deals)
    fund = data.get("fund") or {}
    br = data.get("brief") or {}
    out = a.out or f"{slug(fund.get('name'))}_Process_Brief.pdf"
    W = 7.0 * inch
    s = [Paragraph(br.get("title") or "How we built the top 10", title)]
    m = " | ".join(x for x in [data.get("prepared_by", ""), str(data.get("date", "")), fund.get("name", "")] if x)
    if m:
        s.append(Paragraph(m, meta))
    if br.get("summary"):
        box = Table([[Paragraph("<b>Bottom line.</b> " + br["summary"], base)]], colWidths=[W])
        box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("BOX", (0, 0), (-1, -1), 0.8, NAVY),
                                 ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                                 ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
        s.append(box)
    for sec in br.get("sections", []):
        parts = [Paragraph(sec.get("heading", ""), h2)]
        if sec.get("body"):
            for para in str(sec["body"]).split("\n\n"):
                parts.append(Paragraph(para, base))
        if sec.get("table"):
            parts += [table(sec["table"], W), Spacer(1, 4)]
        elif "top 10" in sec.get("heading", "").lower():
            parts += [top10_table(data), Spacer(1, 4)]
        s.append(KeepTogether(parts[:2]))
        s += parts[2:]

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.HexColor("#777777"))
        canvas.drawString(0.75 * inch, 0.5 * inch, " | ".join(x for x in [fund.get("name", ""), data.get("prepared_by", "")] if x))
        canvas.drawRightString(7.75 * inch, 0.5 * inch, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(out, pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                            topMargin=0.7 * inch, bottomMargin=0.75 * inch, title=br.get("title", "Process brief"),
                            author=data.get("prepared_by", ""))
    doc.build(s, onFirstPage=footer, onLaterPages=footer)
    print("saved", out)


if __name__ == "__main__":
    main()
