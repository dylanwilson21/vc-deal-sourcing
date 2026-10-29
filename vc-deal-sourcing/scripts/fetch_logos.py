#!/usr/bin/env python3
"""Download a square logo for each top-N company (and the fund) into logos/.

For each website it tries, in order: an apple-touch-icon, other <link rel=icon> files, an <img> whose
tag mentions "logo", and finally Google's favicon service. Wordmarks are cropped to their left
square (usually the icon). White-on-transparent logos are darkened so they show on white paper.
Check the results by eye (logos/_contact_sheet.png) and replace any that look wrong.

Usage: python3 fetch_logos.py deals.json [--top 10] [--outdir logos]
"""
import argparse
import io
import os
import re
import urllib.parse
import urllib.request
from PIL import Image, ImageDraw
from _common import load

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 Chrome/120 Safari/537.36"}


def get(u):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20)
    return r.geturl(), r.read(), r.headers.get("Content-Type", "")


def to_image(data, ct, url):
    if b"<svg" in data[:3000] or url.lower().split("?")[0].endswith(".svg") or "svg" in ct:
        try:
            import cairosvg
        except ImportError:
            return None
        data = cairosvg.svg2png(bytestring=data, output_width=512)
    im = Image.open(io.BytesIO(data))
    im.load()
    return im.convert("RGBA")


def darken_white(im):
    """Darken white-on-transparent logos (made for dark sites) so they show on white paper."""
    px = im.load()
    total = im.width * im.height
    opaque = [px[x, y] for x in range(im.width) for y in range(im.height) if px[x, y][3] > 0]
    transparent_share = 1 - len(opaque) / total if total else 0
    if opaque and transparent_share > 0.2 and sum(1 for p in opaque if min(p[:3]) > 200) > 0.6 * len(opaque):
        for x in range(im.width):
            for y in range(im.height):
                r, g, b, a = px[x, y]
                if a > 0 and min(r, g, b) > 200:
                    px[x, y] = (40, 40, 40, a)
    return im


def squarify(im, keep_wide=False):
    bb = im.getbbox()
    if bb:
        im = im.crop(bb)
    if not keep_wide and im.width / max(im.height, 1) > 1.6:
        im = im.crop((0, 0, int(im.height * 1.1), im.height))
        if im.getbbox():
            im = im.crop(im.getbbox())
    if keep_wide:
        return im
    s = max(im.size)
    c = Image.new("RGBA", (s, s), (255, 255, 255, 0))
    c.paste(im, ((s - im.width) // 2, (s - im.height) // 2), im)
    return c.resize((256, 256), Image.LANCZOS)


def candidates(site):
    out = []
    try:
        base, html, _ = get(site)
        html = html.decode("utf-8", "ignore")
        icons = []
        for m in re.finditer(r"<link[^>]+>", html, re.I):
            tag = m.group(0)
            if re.search(r'rel=["\'][^"\']*icon[^"\']*["\']', tag, re.I):
                h = re.search(r'href=["\']([^"\']+)["\']', tag)
                if h and not h.group(1).startswith("data:"):
                    icons.append((0 if "apple" in tag.lower() else 1, urllib.parse.urljoin(base, h.group(1))))
        out += [u for _, u in sorted(icons)]
        for m in re.finditer(r"<img[^>]+>", html, re.I):
            tag = m.group(0)
            if re.search(r"logo", tag, re.I):
                src = re.search(r'src=["\']([^"\']+)["\']', tag)
                if src and not src.group(1).startswith("data:"):
                    out.append(urllib.parse.urljoin(base, src.group(1)))
                    break
    except Exception:
        pass
    dom = urllib.parse.urlparse(site).netloc or site
    out.append(f"https://www.google.com/s2/favicons?domain={dom}&sz=256")
    return out


def fetch(site, keep_wide=False):
    best = None
    for u in candidates(site):
        try:
            _, data, ct = get(u)
            im = to_image(data, ct, u)
            if im is None or min(im.size) < 24:
                continue
            im = darken_white(im)
            if min(im.size) >= 96 or keep_wide:
                return squarify(im, keep_wide), u
            if best is None or min(im.size) > min(best[0].size):
                best = (im, u)
        except Exception:
            continue
    if best:
        return squarify(best[0], keep_wide), best[1]
    return None, None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deals")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--outdir", default="logos")
    a = ap.parse_args()
    data = load(a.deals)
    os.makedirs(a.outdir, exist_ok=True)
    jobs = [(c["name"], c.get("website")) for c in data.get("companies", [])[:a.top] if c.get("website")]
    saved = []
    for name, site in jobs:
        im, src = fetch(site)
        if im:
            p = os.path.join(a.outdir, f"{name}.png")
            im.save(p)
            saved.append(p)
            print(f"{name}: {src}")
        else:
            print(f"{name}: no logo found")
    fsite = (data.get("fund") or {}).get("website")
    if fsite:
        im, src = fetch(fsite, keep_wide=True)
        if im:
            im.save(os.path.join(a.outdir, "_fund.png"))
            print(f"fund: {src}")
    if saved:
        sheet = Image.new("RGB", (120 * len(saved), 150), "white")
        d = ImageDraw.Draw(sheet)
        for i, p in enumerate(saved):
            im = Image.open(p)
            im.thumbnail((100, 100))
            sheet.paste(im, (10 + 120 * i, 10), im)
            d.text((10 + 120 * i, 120), os.path.basename(p)[:16], fill="black")
        sheet.save(os.path.join(a.outdir, "_contact_sheet.png"))
        print(f"Check {a.outdir}/_contact_sheet.png")


if __name__ == "__main__":
    main()
