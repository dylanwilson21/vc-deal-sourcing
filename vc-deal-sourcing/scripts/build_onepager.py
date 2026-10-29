#!/usr/bin/env python3
"""Build the one-page top-10 PDF from deals.json.

The #1 company (or the pick) is featured with fit, why, valuation and why it won; the other nine get
one line each for fit and why. Company names link to websites and founder names to their LinkedIn
profiles (only URLs present in deals.json). Logos come from logos/<name>.png and logos/_fund.png.

Usage: python3 build_onepager.py deals.json [--out <Fund>_Top10.pdf] [--logos logos]
"""
import argparse
import os
from html import escape
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from PIL import Image as PILImage
from _common import load, slug

NAVY = colors.HexColor("#1F3A5F")
LINK = "#1F5FAD"
LIGHT = colors.HexColor("#EEF2F7")
GRID = colors.HexColor("#D5DCE6")


def style(**k):
    base = dict(fontName="Helvetica", fontSize=8.3, leading=10.2)
    base.update(k)
    return ParagraphStyle("s", **base)


body = style()
small = style(fontSize=7.2, leading=8.8, textColor=colors.HexColor("#555555"))
name_s = style(fontName="Helvetica-Bold", fontSize=9.2, leading=11)
big = style(fontName="Helvetica-Bold", fontSize=13, leading=15)
title = style(fontName="Helvetica-Bold", fontSize=14, leading=17, textColor=NAVY)
sub = style(fontSize=8, leading=10, textColor=colors.HexColor("#555555"))
num = style(fontName="Helvetica-Bold", fontSize=10, leading=12, textColor=NAVY, alignment=1)


def e(t):
    return escape(t or "", quote=False)


def link(text, url):
    return f'<a href="{escape(url)}" color="{LINK}">{e(text)}</a>' if url else e(text)


def founders(fs):
    return ", ".join(link(f.get("name", ""), f.get("linkedin")) for f in fs or [])


def logo(dirpath, name, size):
    p = os.path.join(dirpath, f"{name}.png")
    return Image(p, width=size, height=size) if os.path.exists(p) else ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deals")
    ap.add_argument("--out")
    ap.add_argument("--logos", default="logos")
    a = ap.parse_args()
    data = load(a.deals)
    fund = data.get("fund") or {}
    out = a.out or f"{slug(fund.get('name'))}_Top10.pdf"
    comps = sorted(data.get("companies", []), key=lambda c: c.get("rank", 9999))[:10]
    pick = data.get("pick") or {}
    if pick.get("name"):
        top = next((c for c in comps if c["name"] == pick["name"]), comps[0])
        rest = [c for c in comps if c is not top]
    else:
        top, rest = comps[0], comps[1:]
    W = 7.5 * inch
    s = []

    left = [Paragraph("Top 10 deals", title)]
    meta = " | ".join(x for x in [("Prepared by " + data["prepared_by"]) if data.get("prepared_by") else "", data.get("date", "")] if x)
    if meta:
        left.append(Paragraph(e(meta), sub))
    fl = os.path.join(a.logos, "_fund.png")
    if os.path.exists(fl):
        w0, h0 = PILImage.open(fl).size
        lw = min(1.9 * inch, 0.55 * inch * w0 / h0)
        hdr = Table([[left, Image(fl, width=lw, height=lw * h0 / w0)]], colWidths=[W - lw - 0.1 * inch, lw + 0.1 * inch])
    else:
        hdr = Table([[left]], colWidths=[W])
    hdr.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (-1, 0), (-1, 0), "RIGHT"),
                             ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    s += [hdr, Spacer(1, 7)]

    deal = " | ".join(x for x in [
        f"{top.get('last_round', '')} ${top['last_round_m']:.1f}M, {top.get('last_round_date', '')}" if top.get("last_round_m") else "",
        f"${top['post_money_m']:.0f}M post" if top.get("post_money_m") else "",
        f"${top['total_raised_m']:.1f}M raised" if top.get("total_raised_m") else ""] if x)
    head = Table([[logo(a.logos, top["name"], 0.55 * inch),
                   [Paragraph(f'<font color="#1F3A5F">1.</font> {link(top["name"], top.get("website"))} '
                              f'<font size="9" color="#555555">  {e(top.get("hq"))}</font>', big),
                    Paragraph(f"Founders: {founders(top.get('founders'))}" + (f" &nbsp;|&nbsp; {e(deal)}" if deal else ""), body)]]],
                 colWidths=[0.7 * inch, W - 1.0 * inch])
    head.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    rows = [[head]] + [[Paragraph(f"<b>{lab}:</b> {e(top.get(k))}", body)]
                       for lab, k in (("Fit", "fit"), ("Why interesting", "why")) if top.get(k)]
    if pick.get("valuation_text"):
        rows.append([Paragraph(f"<b>Valuation:</b> {pick['valuation_text']}", body)])
    if pick.get("why_won"):
        rows.append([Paragraph(f"<b>Why it won:</b> {e(pick['why_won'])}", body)])
    feat = Table(rows, colWidths=[W - 0.3 * inch])
    feat.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("BOX", (0, 0), (-1, -1), 1, NAVY),
                              ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                              ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
                              ("TOPPADDING", (0, 0), (0, 0), 7), ("BOTTOMPADDING", (0, -1), (-1, -1), 7)]))
    s += [feat, Spacer(1, 8)]

    data_rows = []
    for i, c in enumerate(rest, start=2):
        leftcol = [Paragraph(link(c["name"], c.get("website")), name_s), Paragraph(e(c.get("hq")), small),
                   Paragraph(founders(c.get("founders")), small)]
        rightcol = [Paragraph(f"<b>{lab}:</b> {e(c.get(k))}", body) for lab, k in (("Fit", "fit"), ("Why interesting", "why")) if c.get(k)]
        data_rows.append([Paragraph(str(i), num), logo(a.logos, c["name"], 0.36 * inch), leftcol, rightcol])
    if data_rows:
        t = Table(data_rows, colWidths=[0.3 * inch, 0.5 * inch, 1.55 * inch, W - 2.35 * inch])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LINEBELOW", (0, 0), (-1, -2), 0.5, GRID),
                               ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                               ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]))
        s.append(t)

    doc = SimpleDocTemplate(out, pagesize=letter, leftMargin=0.5 * inch, rightMargin=0.5 * inch,
                            topMargin=0.45 * inch, bottomMargin=0.4 * inch,
                            title=f"Top 10 deals for {fund.get('name', '')}", author=data.get("prepared_by", ""))
    doc.build(s)
    try:
        from pypdf import PdfReader
        pages = len(PdfReader(out).pages)
        print(f"saved {out} ({pages} page{'s' if pages != 1 else ''})")
        if pages > 1:
            print("Over one page: shorten the fit/why sentences in deals.json and rebuild.")
    except ImportError:
        print("saved", out)


if __name__ == "__main__":
    main()
