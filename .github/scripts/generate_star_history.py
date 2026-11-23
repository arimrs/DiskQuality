#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zero-dependency GitHub Star History SVG generator (Light + Dark themes).
Fetches stargazer timestamps via GitHub REST API and renders crisp SVGs.
"""

import json
import os
import urllib.request
from datetime import datetime, timezone, timedelta

REPO = os.environ.get("GITHUB_REPOSITORY", "arimrs/DiskQuality")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets")
TAIPEI_TZ = timezone(timedelta(hours=8))


def fetch_stars():
    dates = []
    page = 1
    headers = {
        "Accept": "application/vnd.github.star+json",
        "User-Agent": "DiskQuality-StarHistory",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    while page <= 400:
        url = f"https://api.github.com/repos/{REPO}/stargazers?per_page=100&page={page}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                items = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"[WARN] Page {page} fetch failed: {e}")
            break
        if not items:
            break
        for it in items:
            ts = it.get("starred_at")
            if ts:
                dates.append(ts[:10])
        if len(items) < 100:
            break
        page += 1
    dates.sort()
    return dates


def build_series(dates):
    today = datetime.now(TAIPEI_TZ).strftime("%Y-%m-%d")
    if not dates:
        return [(today, 0)]
    counts = {}
    for d in dates:
        counts[d] = counts.get(d, 0) + 1
    pts = []
    cum = 0
    for d in sorted(counts.keys()):
        cum += counts[d]
        pts.append((d, cum))
    if pts[-1][0] != today:
        pts.append((today, cum))
    return pts


def render_svg(pts, theme="dark"):
    w, h = 820, 380
    pl, pr, pt, pb = 64, 34, 58, 56
    cw, ch = w - pl - pr, h - pt - pb

    if theme == "dark":
        bg, border, fg, muted, grid, line_c, fill_c = (
            "#1b1c1f", "#2b2d33", "#f4f4f5", "#9ca3af", "#2d3038", "#3fb950", "#3fb95026"
        )
    else:
        bg, border, fg, muted, grid, line_c, fill_c = (
            "#ffffff", "#e5e7eb", "#111827", "#6b7280", "#f3f4f6", "#16a34a", "#16a34a20"
        )

    total = pts[-1][1]
    max_y = max(total, 5)
    # Nice rounded Y ceiling
    step = max(1, (max_y + 4) // 5)
    y_top = step * 5

    n = len(pts)
    coords = []
    for i, (d, v) in enumerate(pts):
        x = pl + (cw * i / max(1, n - 1)) if n > 1 else pl + cw / 2
        y = pt + ch - (ch * v / max(1, y_top))
        coords.append((x, y, d, v))

    now_tpe = datetime.now(TAIPEI_TZ).strftime("%Y-%m-%d %H:%M Taipei")
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'<rect width="100%" height="100%" rx="8" fill="{bg}" stroke="{border}" stroke-width="1"/>',
        f'<text x="{pl}" y="34" fill="{fg}" font-family="system-ui,-apple-system,Segoe UI,sans-serif" font-size="16" font-weight="600">{REPO} — Star History</text>',
        f'<text x="{w - pr}" y="34" text-anchor="end" fill="{muted}" font-family="ui-monospace,Consolas,monospace" font-size="12">★ {total}  ·  Updated {now_tpe}</text>',
    ]

    # Horizontal gridlines + Y labels
    for k in range(6):
        val = k * step
        yy = pt + ch - (ch * val / y_top)
        svg.append(f'<line x1="{pl}" y1="{yy:.1f}" x2="{w - pr}" y2="{yy:.1f}" stroke="{grid}" stroke-width="1"/>')
        svg.append(f'<text x="{pl - 10}" y="{yy + 4:.1f}" text-anchor="end" fill="{muted}" font-family="ui-monospace,Consolas,monospace" font-size="11">{val}</text>')

    # Area + polyline
    if len(coords) >= 2:
        poly = " ".join(f"{x:.1f},{y:.1f}" for x, y, _, _ in coords)
        area = f"{pl:.1f},{pt + ch:.1f} {poly} {coords[-1][0]:.1f},{pt + ch:.1f}"
        svg.append(f'<polygon points="{area}" fill="{fill_c}"/>')
        svg.append(f'<polyline fill="none" stroke="{line_c}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round" points="{poly}"/>')
    else:
        x, y, _, _ = coords[0]
        svg.append(f'<line x1="{pl}" y1="{y:.1f}" x2="{w - pr}" y2="{y:.1f}" stroke="{line_c}" stroke-width="2" stroke-dasharray="4 4"/>')

    # Endpoint dot
    lx, ly, _, lv = coords[-1]
    svg.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="4.5" fill="{line_c}"/>')

    # X axis labels (up to 5 evenly spaced)
    idxs = sorted(set([0, len(coords) // 2, len(coords) - 1])) if len(coords) > 2 else list(range(len(coords)))
    for i in idxs:
        x, _, d, _ = coords[i]
        svg.append(f'<text x="{x:.1f}" y="{h - 22}" text-anchor="middle" fill="{muted}" font-family="ui-monospace,Consolas,monospace" font-size="11">{d}</text>')

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    pts = build_series(fetch_stars())
    for theme in ("light", "dark"):
        out_path = os.path.join(OUT_DIR, f"star-history-{theme}.svg")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(render_svg(pts, theme=theme))
        print(f"[OK] Wrote {out_path} ({pts[-1][1]} stars)")


if __name__ == "__main__":
    main()
