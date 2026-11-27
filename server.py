#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DiskQuality v1.0.9 — Telemetry Studio & API Server (Bilingual zh/en)
- Interactive dashboard, shareable infographic, and six-page paginated terminal report
- Hardened against Stored XSS, search-engine indexing, referrer leakage, and unmasked IP storage
- Persistent report storage by default (DQ_TTL_SECONDS=0; optional TTL if > 0)
"""

import os
import re
import sys
import time
import json
import html
import shlex
import secrets
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DQ_DATA_DIR", os.path.join(APP_DIR, "data"))
STATS_FILE = os.environ.get("DQ_STATS_FILE", os.path.join(APP_DIR, "run_stats.json"))
SITE_URL = os.environ.get("DQ_SITE_URL", "https://test.sakurado.top")
PORT = int(os.environ.get("DQ_PORT", "8765"))
TTL_SECONDS = int(os.environ.get("DQ_TTL_SECONDS", "0"))
MAX_REPORTS = int(os.environ.get("DQ_MAX_REPORTS", "0"))
MAX_BODY_BYTES = 256 * 1024
TAIPEI_TZ = timezone(timedelta(hours=8))

os.makedirs(DATA_DIR, exist_ok=True)
sys.path.insert(0, APP_DIR)
import disk_bench_core as core

_RATE_LOCK = threading.Lock()
_RATE_MAP = {}
_STATS_RATE_MAP = {}
_STATS_LOCK = threading.Lock()


def safe_json_for_script(obj):
    """Prevent </script> breakout / Stored XSS when embedding JSON inside <script>."""
    return (
        json.dumps(obj, ensure_ascii=False)
        .replace("</", "<\\/")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def _mask_ip_str(val):
    s = str(val or "").strip()
    if re.match(r"^\d+\.\d+\.\d+\.\d+$", s):
        return re.sub(r"^(\d+\.\d+)\.\d+\.\d+$", r"\1.*.*", s)
    if ":" in s and not s.endswith(":*:*"):
        return re.sub(r"^([0-9a-fA-F]*:[0-9a-fA-F]*):.*$", r"\1:*:*", s)
    return s or "Unknown"


def sanitize_report_payload(data):
    """Enforce server-side privacy sanitization so no hostname or unmasked IP is ever stored/served."""
    if not isinstance(data, dict):
        return None
    topo = data.get("topology")
    if not isinstance(topo, dict):
        return None
    for k in ("hostname", "ip", "real_ip", "public_ip", "client_ip"):
        data.pop(k, None)
        topo.pop(k, None)
    topo["masked_ip"] = _mask_ip_str(topo.get("masked_ip", "Unknown"))
    if "version" in data:
        data["version"] = str(data["version"])[:64]
    return data


def get_or_hit_stats(hit=False):
    now_tpe = datetime.now(TAIPEI_TZ)
    today_str = now_tpe.strftime("%Y-%m-%d")
    time_str = now_tpe.strftime("%Y-%m-%d %H:%M:%S")
    with _STATS_LOCK:
        st = {"total": 0, "today_date": today_str, "today": 0}
        target_file = STATS_FILE
        for cand in (STATS_FILE, "/tmp/diskquality_run_stats.json"):
            if os.path.exists(cand):
                try:
                    with open(cand, "r", encoding="utf-8") as f:
                        d = json.load(f)
                    st["total"] = int(d.get("total", 0))
                    st["today_date"] = str(d.get("today_date", today_str))
                    st["today"] = int(d.get("today", 0))
                    target_file = cand
                    break
                except Exception:
                    pass
        if st["today_date"] != today_str:
            st["today_date"] = today_str
            st["today"] = 0
        if hit:
            st["total"] += 1
            st["today"] += 1
            for cand in (target_file, "/tmp/diskquality_run_stats.json"):
                try:
                    with open(cand, "w", encoding="utf-8") as f:
                        json.dump(st, f)
                    break
                except OSError:
                    continue
        return {
            "taipei_time": time_str,
            "today_date": st["today_date"],
            "total_runs": st["total"],
            "today_runs": st["today"],
        }

with open(os.path.join(APP_DIR, "run.sh"), "rb") as _f:
    RUN_SH_BYTES = _f.read().replace(b"https://your-domain.example", SITE_URL.encode("utf-8"))
with open(os.path.join(APP_DIR, "disk_bench_core.py"), "rb") as _f:
    CORE_PY_BYTES = _f.read()


def cleanup_expired():
    if TTL_SECONDS <= 0 and MAX_REPORTS <= 0:
        return
    now = time.time()
    try:
        entries = []
        for fn in os.listdir(DATA_DIR):
            if not fn.endswith(".json"): continue
            fp = os.path.join(DATA_DIR, fn)
            try:
                mt = os.path.getmtime(fp)
                if TTL_SECONDS > 0 and now - mt >= TTL_SECONDS: os.unlink(fp)
                else: entries.append((mt, fp))
            except OSError: pass
        if MAX_REPORTS > 0 and len(entries) > MAX_REPORTS:
            entries.sort(key=lambda x: x[0])
            for _, fp in entries[: len(entries) - MAX_REPORTS]:
                try: os.unlink(fp)
                except OSError: pass
    except Exception: pass


def _janitor():
    while True:
        time.sleep(60)
        cleanup_expired()


if TTL_SECONDS > 0 or MAX_REPORTS > 0:
    threading.Thread(target=_janitor, daemon=True).start()


def load_valid_report(rid):
    fp = os.path.join(DATA_DIR, f"{rid}.json")
    if not os.path.exists(fp): return None, 0
    if TTL_SECONDS > 0:
        age = time.time() - os.path.getmtime(fp)
        if age >= TTL_SECONDS:
            try: os.unlink(fp)
            except OSError: pass
            return None, 0
        rem = max(0, int(TTL_SECONDS - age))
    else:
        rem = 0
    with open(fp, "r", encoding="utf-8") as f:
        return sanitize_report_payload(json.load(f)), rem


_WEB_DIR = Path(APP_DIR) / "web"
_WEB_CSS = (_WEB_DIR / "telemetry.css").read_text(encoding="utf-8")
_WEB_JS = (_WEB_DIR / "telemetry.js").read_text(encoding="utf-8")
_LANGUAGE_PICKER = """
<div class="chips lang-switch" role="group" data-label-aria="language">
  <button type="button" class="chip" data-lang="zh" lang="zh-CN">中</button>
  <button type="button" class="chip" data-lang="en" lang="en">EN</button>
</div>"""
_BRAND = '<a class="brand" href="/"><span class="brand-mark" aria-hidden="true"></span>DiskQuality</a>'
_REPO_LINK = '<a href="https://github.com/arimrs/DiskQuality" rel="noreferrer">github.com/arimrs/DiskQuality</a>'
_FAVICON = "data:image/svg+xml," + quote(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
    '<rect width="32" height="32" rx="8" fill="#163530"/>'
    '<path d="M5 17h5l4-7 5 12 4-7h4" fill="none" stroke="#79ecc6" stroke-width="2" stroke-linejoin="round"/>'
    '</svg>'
)


def _studio_html(lang, title, body, payload, private=False):
    privacy = ('<meta name="robots" content="noindex, nofollow, noarchive">\n'
               '<meta name="referrer" content="no-referrer">') if private else ""
    # Legacy uploads may contain non-finite numbers from Python's JSON encoder.
    # Convert them to null, and prevent HTML script tokenizer state changes on any '<'.
    serial = safe_json_for_script(payload)
    if re.search(r"NaN|Infinity", serial):
        serial = safe_json_for_script(json.loads(serial, parse_constant=lambda _: None))
    serial = serial.replace("<", r"\u003c").encode("utf-8", "backslashreplace").decode("utf-8")
    return f"""<!DOCTYPE html>
<html lang="{'zh-CN' if lang == 'zh' else 'en'}">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
{privacy}
<title>{core._svg_escape(title)}</title>
<link rel="icon" type="image/svg+xml" href="{_FAVICON}">
<style>{_WEB_CSS}</style>
</head>
<body>{body}
<div class="toast" id="toast" role="status"></div>
<script id="payload" type="application/json">{serial}</script>
<script>{_WEB_JS}</script>
</body></html>"""


_HOME_FEATURES = (
    ("dash", """<path d="M13 52H247M13 36H247M13 20H247" stroke="#26384d"/>
<path d="M14 53L39 42 60 47 81 29 101 33 128 18 148 23 169 13 189 28 217 20 246 15V60H14Z" fill="#173a38"/>
<path d="M14 53L39 42 60 47 81 29 101 33 128 18 148 23 169 13 189 28 217 20 246 15" stroke="#5df0b5" stroke-width="2" fill="none"/>
<path d="M14 52L39 50 60 55 81 53 101 51 128 48 148 51 169 42 189 46 217 32 246 35" stroke="#eeb359" stroke-dasharray="4 3" fill="none"/>"""),
    ("card", """<rect x="13" y="10" width="234" height="50" rx="6" fill="#172131" stroke="#33455c"/>
<circle cx="46" cy="35" r="15" fill="none" stroke="#314157" stroke-width="4"/>
<path d="M46 20a15 15 0 1 1-15 15" fill="none" stroke="#67e6b4" stroke-width="4" stroke-linecap="round"/>
<path d="M77 25h32m-32 10h23m-23 10h37" stroke="#769bb1" stroke-width="2" stroke-linecap="round"/>
<path d="m140 34 12-14 23 0 9 14-13 16h-19Z" fill="#264b56" stroke="#6bd7f1"/>
<path d="M203 44h27m-27-10h21m-21-10h12" stroke="#b7a2fa" stroke-width="3" stroke-linecap="round"/>"""),
    ("terminal", """<rect x="13" y="10" width="234" height="50" rx="6" fill="#161d29" stroke="#33455c"/>
<path d="M13 23H247" stroke="#33455c"/>
<circle cx="23" cy="17" r="2" fill="#c78696"/><circle cx="31" cy="17" r="2" fill="#d1a775"/><circle cx="39" cy="17" r="2" fill="#78aa9a"/>
<path d="m24 33 5 4-5 4m9 1h9" fill="none" stroke="#6ee7b7" stroke-width="1.6"/>
<path d="M53 34h82m-82 9h62m-62 9h98" stroke="#738aa5" stroke-width="2" stroke-linecap="round"/>
<rect x="187" y="29" width="42" height="9" rx="3" fill="#265f53"/><rect x="176" y="43" width="53" height="9" rx="3" fill="#384c6e"/>"""),
)


def render_home_html():
    st = get_or_hit_stats(hit=False)
    command = f"bash <(curl -sL {shlex.quote(SITE_URL)})"
    version = html.escape(core.VERSION)
    features = "".join(
        f'<article class="panel view-feature"><h3 data-label="{key}"></h3>'
        f'<svg viewBox="0 0 260 70" aria-hidden="true">{graphic}</svg>'
        f'<p data-label="{key}Desc"></p></article>' for key, graphic in _HOME_FEATURES
    )
    credits = "".join(
        f'<a class="tag-link" href="{html.escape(url)}" target="_blank" rel="noopener noreferrer">{html.escape(name)}</a>'
        for name, url in core.TOOL_CREDITS
    )
    languages = _LANGUAGE_PICKER.replace(">中<", ">ZH<")
    body = f"""
<div class="wrap">
<header class="site-head">{_BRAND}<span class="pill green mono">{version}</span>{languages}</header>
<main>
  <section class="home-hero">
    <div class="home-intro">
      <p class="kicker" data-label="objective"></p>
      <h1>DiskQuality</h1>
      <p class="lede" data-label="intro"></p>
      <div class="stats">
        <div class="stat"><span data-label="taipei"></span><b id="taipei-clock">{st['taipei_time']}</b></div>
        <div class="stat"><span data-label="totalRuns"></span><b>{st['total_runs']}</b></div>
        <div class="stat"><span data-label="todayRuns"></span><b>{st['today_runs']}</b></div>
      </div>
    </div>
    <div class="panel builder">
      <div class="section-head"><h2 data-label="builder"></h2></div>
      <div class="command"><code id="command">{html.escape(command)}</code>
        <button class="button primary" id="copy-command" type="button" data-label="copy">复制</button></div>
      <div class="builder-groups" id="command-options"></div>
    </div>
  </section>
  <section class="home-section">
    <div class="section-head"><h2 data-label="showcase"></h2></div>
    <div class="home-views">{features}</div>
  </section>
  <section class="home-section">
    <div class="section-head"><h2 data-label="dimensions"></h2></div>
    <div class="bento" id="dimensions"></div>
  </section>
  <section class="home-section">
    <div class="section-head"><h2 data-label="credits"></h2></div>
    <div class="tags">{credits}</div>
  </section>
  <p class="privacy" data-label="privacy"></p>
</main>
<footer>{_REPO_LINK}</footer>
</div>"""
    return _studio_html("zh", f"DiskQuality {core.VERSION}", body, {
        "lang": "zh", "command": command, "taipei": st["taipei_time"],
    })


def render_report_html(rid, data, rem_sec):
    # Reports rendered directly and old files on disk share the same privacy boundary as uploads.
    topo = core._mapping(data.get("topology"))
    data = sanitize_report_payload({**data, "topology": dict(topo)})
    lang = core._report_lang(data, None)
    data["report_url"] = f"{SITE_URL}/r/{rid}"
    sections = core.build_sections(data, lang=lang, site_url=SITE_URL)
    pages = core.REPORT_PAGES
    artwork = "".join(
        f'<template id="art-{key}">{core.render_ansi_to_svg_str(sections[key], title=label)}</template>'
        for key, label in zip(pages, core.I18N[lang]["tabs"])
    )
    card = core.render_visual_card_svg(data, lang=lang, site_url=SITE_URL)
    topo = data["topology"]
    masked_ip = topo["masked_ip"]
    platform = " · ".join(str(topo[key]) for key in ("profile", "virt", "arch") if topo.get(key))
    version = data.get("version") or core.VERSION
    sample = '<span class="pill cyan" data-label="sample"></span>' if data.get("sample_preview") is True else ""
    mode_tabs = "".join(
        f'<button class="chip" type="button" aria-controls="{target}"><span class="view-icon" aria-hidden="true">{icon}</span>'
        f'<span data-label="{label}"></span></button>'
        for target, icon, label in (("dashboard", "✦", "dash"), ("card-view", "▧", "card"), ("terminal-view", "⌘", "terminal"))
    )
    actions = "".join(
        f'<button type="button" class="button{" primary" if key == "png" else ""}" data-action="{key}" data-label="{key}"></button>'
        for key in ("text", "nodeseek", "markdown", "png", "svg", "json")
    )
    terminal_tabs = "".join('<button type="button" class="chip"></button>' for _ in pages)
    body = f"""
<div class="wrap">
<header class="site-head report-head">
  {_BRAND}
  <div class="identity">
    <span class="pill green mono">{core._svg_escape(masked_ip)}</span>
    <span class="pill violet">{core._svg_escape(platform or "—")}</span>
    <span class="pill mono">{core._svg_escape(version)}</span>
    <span class="pill" id="retention"></span>{sample}
  </div>{_LANGUAGE_PICKER}
</header>
<main>
  <div class="studio-nav">
    <nav class="views" id="mode-tabs" data-label-aria="views">{mode_tabs}</nav>
    <div class="actions">{actions}</div>
  </div>
  <div class="dashboard" id="dashboard">
    <section class="panel hardware" id="hardware"></section>
    <section class="kpis" id="kpis"></section>
    <div class="analytics">
      <section class="panel">
        <div class="section-head"><h2 data-label="radar"></h2></div>
        <div class="chart-host radar-chart" id="radar"></div>
      </section>
      <section class="panel">
        <div class="section-head"><h2 data-label="endurance"></h2></div>
        <div class="chart-summary tags" id="endurance-summary"></div>
        <div class="chart-host endurance-chart" id="endurance"></div>
      </section>
    </div>
    <section class="panel">
      <div class="section-head"><h2 data-label="fio"></h2></div>
      <div class="fio-controls" id="fio-controls"></div><div id="fio-content"></div>
    </section>
    <section class="panel">
      <div class="section-head"><h2 data-label="net"></h2></div><div class="net-layout" id="net-content"></div>
    </section>
    <section class="panel">
      <div class="section-head"><h2 data-label="meta"></h2></div><div class="meta-layout" id="meta-content"></div>
    </section>
  </div>
  <section class="panel art-panel" id="card-view" hidden><div class="viewport" id="card-art"></div></section>
  <section class="panel art-panel" id="terminal-view" hidden>
    <div class="terminal-nav">
      <nav class="chips" id="terminal-tabs" data-label-aria="terminalTabs">{terminal_tabs}</nav>
      <div>
        <button type="button" class="button" id="terminal-prev" data-label-aria="prev">‹</button>
        <span class="terminal-index mono" id="terminal-index"></span>
        <button type="button" class="button" id="terminal-next" data-label-aria="next">›</button>
      </div>
    </div>
    <div class="viewport terminal-art" id="terminal-art"></div>
  </section>
</main>
<footer>{_REPO_LINK}<span data-label="keyboard"></span></footer>
</div>
<template id="art-card">{card}</template>{artwork}"""
    plan = core._mapping(data.get("plan"))
    sustained = core._mapping(core._module(data, "sustained"))
    phases = [core._sequential(point, plan) for point in core._rows(sustained.get("timeline"))]
    payload = {
        "lang": lang, "data": data, "rid": rid, "pages": pages, "phases": phases,
        "regions": {country: core.I18N["en"][region] for country, region in core._HUB_REGIONS.items()},
        "services": [name for name, _ in core.UNLOCK_PROBES],
        "ttl": max(1, (rem_sec + 59) // 60) if TTL_SECONDS > 0 else None,
        "exports": {
            "text": core.strip_ansi(sections["full"]),
            "nodeseek": core.render_nodeseek_md(data, lang=lang, site_url=SITE_URL),
            "markdown": core.render_standard_md(data, lang=lang, site_url=SITE_URL),
        },
    }
    return _studio_html(lang, f"DiskQuality · {masked_ip}", body, payload, private=True)


EXPIRED_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>410 Gone</title>
<style>body{background:#0a0d12;color:#f1f5f9;font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}
.box{background:#111622;border:1px solid #232c3f;border-radius:12px;padding:30px 36px;text-align:center;max-width:520px}h2{color:#f87171;margin-top:0}a{color:#38bdf8}</style></head>
<body><div class="box"><h2>Report Expired &amp; Destroyed / 报告已过期销毁</h2>
<p>Reports are automatically destroyed after 1 hour. / 所有临时报告均在 1 小时后自动销毁。</p><p><a href="/">Home / 返回首页</a></p></div></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def _send(self, code, body, ctype="text/html; charset=utf-8", cache="no-store", extra_headers=None):
        b = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", cache)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        if ctype.startswith("text/html"):
            self.send_header(
                "Content-Security-Policy",
                "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src blob: data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
            )
        if extra_headers:
            for hk, hv in extra_headers.items():
                self.send_header(hk, hv)
        self.end_headers()
        if self.command != "HEAD": self.wfile.write(b)

    def do_HEAD(self): self.do_GET()

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        ua = (self.headers.get("User-Agent") or "").lower()
        if path == "/robots.txt":
            return self._send(200, "User-agent: *\nDisallow: /r/\nDisallow: /api/\n", "text/plain; charset=utf-8", cache="public, max-age=3600")
        if path == "/" and ("curl" in ua or "wget" in ua or "raw=1" in self.path):
            return self._send(200, RUN_SH_BYTES, "text/plain; charset=utf-8", cache="public, max-age=300")
        if path == "/run.sh": return self._send(200, RUN_SH_BYTES, "text/plain; charset=utf-8", cache="public, max-age=300")
        if path == "/core.py": return self._send(200, CORE_PY_BYTES, "text/plain; charset=utf-8", cache="public, max-age=300")
        if path == "/api/v1/stats":
            hit = "hit=1" in self.path
            if hit:
                ip = (self.headers.get("X-Real-IP") or self.client_address[0] or "unknown").split(",")[0].strip()
                now = time.time()
                with _RATE_LOCK:
                    hist = [t for t in _STATS_RATE_MAP.get(ip, []) if now - t < 60]
                    if len(hist) >= 10:
                        hit = False
                    else:
                        hist.append(now)
                        _STATS_RATE_MAP[ip] = hist
            return self._send(200, json.dumps(get_or_hit_stats(hit=hit)), "application/json", cache="no-store")
        if path == "/": return self._send(200, render_home_html(), "text/html; charset=utf-8", cache="no-store")

        priv_hdrs = {"X-Robots-Tag": "noindex, nofollow, noarchive"}
        m_psvg = re.match(r"^/r/([A-Za-z0-9_-]+)/(card|full|overview|disk|endurance|netip|meta)\.svg$", path)
        if m_psvg:
            rid, sec_key = m_psvg.group(1), m_psvg.group(2)
            d, rem = load_valid_report(rid)
            if not d: return self._send(410, "Report expired and destroyed (1h TTL).", "text/plain; charset=utf-8", extra_headers=priv_hdrs)
            d["report_url"] = f"{SITE_URL}/r/{rid}"
            if sec_key == "card":
                svg = core.render_visual_card_svg(d, lang=d.get("lang", "zh"), site_url=SITE_URL)
            else:
                secs = core.build_sections(d, lang=d.get("lang", "zh"), site_url=SITE_URL)
                svg = core.render_ansi_to_svg_str(secs[sec_key])
            return self._send(200, svg, "image/svg+xml; charset=utf-8", cache="no-store, no-cache, must-revalidate", extra_headers=priv_hdrs)

        m_svg = re.match(r"^/r/([A-Za-z0-9_-]+)\.svg$", path)
        if m_svg:
            rid = m_svg.group(1)
            d, rem = load_valid_report(rid)
            if not d: return self._send(410, "Report expired and destroyed (1h TTL).", "text/plain; charset=utf-8", extra_headers=priv_hdrs)
            d["report_url"] = f"{SITE_URL}/r/{rid}"
            return self._send(200, core.render_ansi_to_svg_str(core.render_p2_ansi(d, site_url=SITE_URL)), "image/svg+xml; charset=utf-8", cache="no-store, no-cache, must-revalidate", extra_headers=priv_hdrs)

        m_r = re.match(r"^/r/([A-Za-z0-9_-]+)$", path)
        if m_r:
            rid = m_r.group(1)
            d, rem = load_valid_report(rid)
            if not d: return self._send(410, EXPIRED_HTML, extra_headers=priv_hdrs)
            return self._send(200, render_report_html(rid, d, rem), cache="no-store, no-cache, must-revalidate", extra_headers=priv_hdrs)
        return self._send(404, "Not Found", "text/plain")

    def do_POST(self):
        if self.path.split("?", 1)[0] == "/api/v1/record":
            ip = (self.headers.get("X-Real-IP") or self.client_address[0] or "unknown").split(",")[0].strip()
            now = time.time()
            with _RATE_LOCK:
                hist = [t for t in _RATE_MAP.get(ip, []) if now - t < 60]
                if len(hist) >= 5: return self._send(429, json.dumps({"ok": False, "error": "rate limit"}), "application/json")
                hist.append(now); _RATE_MAP[ip] = hist
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                return self._send(400, json.dumps({"ok": False, "error": "invalid content-length"}), "application/json")
            if length <= 0 or length > MAX_BODY_BYTES: return self._send(400, json.dumps({"ok": False, "error": "invalid size"}), "application/json")
            try:
                raw_data = json.loads(self.rfile.read(length).decode("utf-8"))
            except Exception:
                return self._send(400, json.dumps({"ok": False, "error": "invalid json"}), "application/json")
            data = sanitize_report_payload(raw_data)
            if not data:
                return self._send(400, json.dumps({"ok": False, "error": "invalid schema"}), "application/json")
            cleanup_expired()
            rid = secrets.token_urlsafe(12)
            with open(os.path.join(DATA_DIR, f"{rid}.json"), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            return self._send(200, json.dumps({"ok": True, "id": rid, "ttl_seconds": TTL_SECONDS, "url": f"{SITE_URL}/r/{rid}"}), "application/json")
        return self._send(404, "Not Found", "text/plain")


if __name__ == "__main__":
    cleanup_expired()
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
