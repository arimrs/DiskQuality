#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DiskQuality v1.0.5 — Hardened Paginated Ephemeral Web & API Server (Bilingual zh/en)
- Paginated report viewer (6 interactive pages + Prev/Next + Arrow-Key navigation)
- Hardened against Stored XSS, search-engine indexing, referrer leakage, and unmasked IP storage
- Zero persistence (/tmp storage, strict 1h TTL auto-destroy, 410 Gone after expiry)
"""

import os
import re
import sys
import time
import json
import html
import secrets
import threading
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DQ_DATA_DIR", "/tmp/diskquality_ephemeral")
STATS_FILE = os.environ.get("DQ_STATS_FILE", os.path.join(APP_DIR, "run_stats.json"))
SITE_URL = os.environ.get("DQ_SITE_URL", "https://test.sakurado.top")
PORT = int(os.environ.get("DQ_PORT", "8765"))
TTL_SECONDS = int(os.environ.get("DQ_TTL_SECONDS", "3600"))
MAX_REPORTS = 200
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
    now = time.time()
    try:
        entries = []
        for fn in os.listdir(DATA_DIR):
            if not fn.endswith(".json"): continue
            fp = os.path.join(DATA_DIR, fn)
            try:
                mt = os.path.getmtime(fp)
                if now - mt >= TTL_SECONDS: os.unlink(fp)
                else: entries.append((mt, fp))
            except OSError: pass
        if len(entries) > MAX_REPORTS:
            entries.sort(key=lambda x: x[0])
            for _, fp in entries[: len(entries) - MAX_REPORTS]:
                try: os.unlink(fp)
                except OSError: pass
    except Exception: pass


def _janitor():
    while True:
        time.sleep(60)
        cleanup_expired()


threading.Thread(target=_janitor, daemon=True).start()


def load_valid_report(rid):
    fp = os.path.join(DATA_DIR, f"{rid}.json")
    if not os.path.exists(fp): return None, 0
    age = time.time() - os.path.getmtime(fp)
    if age >= TTL_SECONDS:
        try: os.unlink(fp)
        except OSError: pass
        return None, 0
    with open(fp, "r", encoding="utf-8") as f:
        return json.load(f), max(0, int(TTL_SECONDS - age))


def render_home_html():
    st = get_or_hit_stats(hit=False)
    credits_html = "".join(
        f'<li><a href="{u}" target="_blank" rel="noopener">{html.escape(n)}</a> — <span>{html.escape(u)}</span></li>'
        for n, u in core.TOOL_CREDITS
    )
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>DiskQuality {core.VERSION}</title>
<style>
  *{{box-sizing:border-box}} body{{margin:0;padding:38px 20px;background:#0a0d12;color:#f1f5f9;font-family:system-ui,-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;line-height:1.65}}
  .wrap{{max-width:960px;margin:0 auto}} .brand{{display:flex;align-items:center;justify-content:center;gap:12px;margin-bottom:14px}}
  .stats{{text-align:center;font-size:14px;color:#94a3b8;font-family:"JetBrains Mono",Consolas,monospace;margin-bottom:24px}}
  .stats b{{color:#4ade80}}
  .bar{{width:4px;height:36px;background:#22c55e;border-radius:2px}} .title{{font-size:34px;font-weight:700;color:#fff}}
  .ver{{font-size:13px;color:#4ade80;background:#14532d66;border:1px solid #22c55e77;padding:4px 12px;border-radius:999px;font-family:monospace}}
  .cmd{{background:#151b26;border:1px solid #2b3548;border-radius:12px;padding:20px 24px;display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:22px}}
  .code{{font-family:"JetBrains Mono","Cascadia Mono",Consolas,monospace;font-size:18px;color:#f8fafc;word-break:break-all}}
  .prompt{{color:#ec4899;font-weight:700;margin-right:10px}}
  .btn{{cursor:pointer;background:#1f2937;color:#f8fafc;border:1px solid #4b5563;border-radius:7px;padding:9px 18px;font-size:14px;font-weight:600}}
  .notice{{background:#1c1917;border:1px solid #854d0e;color:#fde047;border-radius:10px;padding:14px 18px;font-size:14.5px;margin-bottom:22px}}
  .panel{{background:#111622;border:1px solid #232c3f;border-radius:12px;padding:22px 26px;margin-bottom:20px}}
  .panel h3{{margin:0 0 12px 0;font-size:17px;color:#38bdf8}} .panel li{{margin:7px 0;font-size:14.5px;color:#cbd5e1}} .panel a{{color:#4ade80;text-decoration:none;font-weight:600}}
</style></head><body><div class="wrap">
  <div class="brand"><div class="bar"></div><div class="title">DiskQuality</div><span class="ver">{core.VERSION}</span></div>
  <div class="stats">Taipei Time: <b>{st['taipei_time']}</b> &nbsp;|&nbsp; 累计运行 / Total Runs: <b>{st['total_runs']}</b> &nbsp;|&nbsp; 今日运行 / Today Runs: <b>{st['today_runs']}</b></div>
  <div class="cmd"><div class="code"><span class="prompt">&gt;</span>bash &lt;(curl -sL {SITE_URL})</div><button class="btn" id="cpBtn" onclick="copyCmd()">Copy / 复制命令</button></div>
  <div class="notice">⚠️ <strong>Zero Persistence / 零持久化声明</strong>: Ephemeral query only — all reports &amp; images are permanently destroyed after <strong>1 hour</strong>. 仅提供测试与 1 小时临时查询，到期自动销毁。</div>
  <div class="panel"><h3>Acknowledgments &amp; Upstream Tools / 致谢与原站</h3><ul>{credits_html}</ul></div>
</div><script>
function copyCmd(){{navigator.clipboard.writeText("bash <(curl -sL {SITE_URL})").then(()=>{{const b=document.getElementById('cpBtn');b.textContent='Copied ✔';setTimeout(()=>b.textContent='Copy / 复制命令',2000);}});}}
</script></body></html>"""


HOME_HTML_BYTES = render_home_html().encode("utf-8")


def render_report_html(rid, data, rem_sec):
    lang = (data.get("lang") or "zh").lower()
    if lang not in ("zh", "en"): lang = "zh"
    L = core.I18N[lang]
    data["report_url"] = f"{SITE_URL}/r/{rid}"
    secs = core.build_sections(data, lang=lang, site_url=SITE_URL)
    plain_txt = core.strip_ansi(secs["full"])
    ns_md = core.render_nodeseek_md(data, lang=lang, site_url=SITE_URL)
    std_md = core.render_standard_md(data, lang=lang, site_url=SITE_URL)

    page_keys = ["full", "overview", "disk", "endurance", "netip", "meta"]
    page_svgs = [core.render_ansi_to_svg_str(secs[k]) for k in page_keys]
    tab_labels = L["tabs"]
    rem_min = max(1, (rem_sec + 59) // 60)

    if lang == "en":
        ttl_txt = f"{html.escape(data.get('version', core.VERSION))} · Ephemeral (auto-destroyed in ~{rem_min} min) · ← / → keys to switch"
        b_txt, b_ns, b_md, b_png, b_svg = "Copy Text", "Copy NodeSeek Format", "Copy Markdown", "Export PNG", "SVG"
    else:
        ttl_txt = f"{html.escape(data.get('version', core.VERSION))} · 临时页面（剩余约 {rem_min} 分钟自动销毁）· 键盘 ← / → 切换"
        b_txt, b_ns, b_md, b_png, b_svg = "复制文本", "复制为NodeSeek格式", "复制为通用Markdown", "导出PNG", "SVG"

    tabs_html = "".join(
        f'<button class="tab{" active" if i==0 else ""}" id="tab-{i}" onclick="goPage({i})">{html.escape(lbl)}</button>'
        for i, lbl in enumerate(tab_labels)
    )
    pages_html = "".join(
        f'<div class="pane{" active" if i==0 else ""}" id="pane-{i}">{svg}</div>'
        for i, svg in enumerate(page_svgs)
    )

    return f"""<!DOCTYPE html>
<html lang="{lang}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="robots" content="noindex, nofollow, noarchive">
<meta name="referrer" content="no-referrer">
<title>DiskQuality — {html.escape(data['topology']['masked_ip'])}</title>
<style>
  *{{box-sizing:border-box}}
  body{{margin:0;padding:24px 16px 48px;background:#0f0f13;color:#d4d4d8;font-family:system-ui,-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;line-height:1.5}}
  .wrap{{max-width:1040px;margin:0 auto}}
  .brand{{display:flex;align-items:center;justify-content:center;gap:10px;margin-bottom:22px;text-decoration:none}}
  .bar{{width:4px;height:34px;background:#22c55e}}
  .title{{font-size:32px;font-weight:600;color:#f4f4f5;letter-spacing:0.3px}}
  .toolbar{{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:8px;margin-bottom:12px}}
  .grp{{display:flex;flex-wrap:wrap;gap:8px}}
  .btn{{cursor:pointer;background:transparent;color:#d4d4d8;border:1px solid #4a4d57;border-radius:3px;padding:5px 12px;font-size:13px;transition:0.12s}}
  .btn:hover{{background:#272930;border-color:#717584;color:#fff}}
  .card{{background:#1b1c1f;border:1px solid #2b2d33;border-radius:8px;overflow:hidden}}
  .tabbar{{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:10px 14px 4px;background:#1b1c1f}}
  .tabs{{display:inline-flex;flex-wrap:wrap;gap:4px;background:#141518;padding:4px;border-radius:5px;border:1px solid #26282e}}
  .tab{{cursor:pointer;background:transparent;color:#3fb950;border:none;border-radius:4px;padding:5px 13px;font-size:13px;font-weight:500;transition:0.12s}}
  .tab:hover{{color:#86efac;background:#22242a}}
  .tab.active{{background:#3a3d45;color:#f4f4f5}}
  .nav{{display:flex;align-items:center;gap:6px}}
  .nav-btn{{cursor:pointer;background:#141518;color:#a1a1aa;border:1px solid #2b2d33;border-radius:4px;padding:3px 9px;font-size:13px}}
  .nav-btn:hover{{color:#fff;border-color:#52525b}}
  .pind{{font-size:12px;color:#71717a;font-family:monospace;min-width:34px;text-align:center}}
  .viewport{{overflow-x:auto;padding:4px 0 8px}}
  .pane{{display:none}} .pane.active{{display:block}}
  svg{{display:block;max-width:100%;height:auto}}
  .foot{{display:flex;justify-content:space-between;align-items:center;margin-top:10px;font-size:12px;color:#71717a}}
  .toast{{color:#4ade80;font-size:12.5px;min-height:18px}}
</style></head><body><div class="wrap">
  <a class="brand" href="/"><div class="bar"></div><div class="title">DiskQuality</div></a>
  <div class="toolbar">
    <div class="grp"><button class="btn" onclick="cp('txt','{b_txt}')">{b_txt}</button><button class="btn" onclick="cp('ns','{b_ns}')">{b_ns}</button></div>
    <div class="grp"><button class="btn" onclick="cp('md','{b_md}')">{b_md}</button><button class="btn" onclick="dlPNG()">{b_png}</button><button class="btn" onclick="dlSVG()">{b_svg}</button></div>
  </div>
  <div class="card">
    <div class="tabbar">
      <div class="tabs">{tabs_html}</div>
      <div class="nav">
        <button class="nav-btn" onclick="stepPage(-1)">‹</button>
        <span class="pind" id="pind">1/{len(page_keys)}</span>
        <button class="nav-btn" onclick="stepPage(1)">›</button>
      </div>
    </div>
    <div class="viewport">{pages_html}</div>
  </div>
  <div class="foot"><span>{ttl_txt}</span><span class="toast" id="toast"></span></div>
</div><script>
const P={{txt:{safe_json_for_script(plain_txt)},ns:{safe_json_for_script(ns_md)},md:{safe_json_for_script(std_md)},svgs:{safe_json_for_script(page_svgs)}}};
let cur=0, total={len(page_keys)};
function goPage(i){{
  cur=(i+total)%total;
  for(let k=0;k<total;k++){{
    document.getElementById('tab-'+k).classList.toggle('active',k===cur);
    document.getElementById('pane-'+k).classList.toggle('active',k===cur);
  }}
  document.getElementById('pind').textContent=(cur+1)+'/'+total;
}}
function stepPage(d){{goPage(cur+d);}}
document.addEventListener('keydown',e=>{{if(e.key==='ArrowLeft')stepPage(-1);if(e.key==='ArrowRight')stepPage(1);}});
function tip(m){{const e=document.getElementById('toast');e.textContent='Copied: '+m;setTimeout(()=>e.textContent='',2200);}}
async function cp(k,n){{try{{await navigator.clipboard.writeText(P[k]);tip(n);}}catch(e){{const t=document.createElement('textarea');t.value=P[k];document.body.appendChild(t);t.select();document.execCommand('copy');t.remove();tip(n);}}}}
function dlSVG(){{const svg=P.svgs[cur];const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([svg],{{type:'image/svg+xml'}}));a.download='diskquality_{rid}_p'+(cur+1)+'.svg';a.click();tip('SVG');}}
function dlPNG(){{const svg=P.svgs[cur];const s=document.querySelector('#pane-'+cur+' svg'),w=parseInt(s.getAttribute('width')),h=parseInt(s.getAttribute('height')),img=new Image(),u=URL.createObjectURL(new Blob([svg],{{type:'image/svg+xml;charset=utf-8'}}));img.onload=()=>{{const c=document.createElement('canvas');c.width=w*2;c.height=h*2;const x=c.getContext('2d');x.scale(2,2);x.drawImage(img,0,0);URL.revokeObjectURL(u);const a=document.createElement('a');a.href=c.toDataURL('image/png');a.download='diskquality_{rid}_p'+(cur+1)+'.png';a.click();tip('PNG');}};img.src=u;}}
</script></body></html>"""


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
        m_psvg = re.match(r"^/r/([A-Za-z0-9_-]+)/(full|overview|disk|endurance|netip|meta)\.svg$", path)
        if m_psvg:
            rid, sec_key = m_psvg.group(1), m_psvg.group(2)
            d, rem = load_valid_report(rid)
            if not d: return self._send(410, "Report expired and destroyed (1h TTL).", "text/plain; charset=utf-8", extra_headers=priv_hdrs)
            d["report_url"] = f"{SITE_URL}/r/{rid}"
            secs = core.build_sections(d, lang=d.get("lang", "zh"), site_url=SITE_URL)
            return self._send(200, core.render_ansi_to_svg_str(secs[sec_key]), "image/svg+xml; charset=utf-8", cache="no-store, no-cache, must-revalidate", extra_headers=priv_hdrs)

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
