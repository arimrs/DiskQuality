#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DiskQuality v1.0.4 — Bilingual Objective VPS Disk, Concurrency, Global Network & IP Quality Suite
- Tailored for PT / Storage / Backup VPS evaluation (pure objective data, zero subjective advice)
- Adaptive 50% capacity / 20-minute endurance algorithm with >65% disk usage safety guard
- Live visual progress bar, thorough pre/post environment cleanup, and friendly kaomoji UX
- Interactive module selection: skipped modules render as bold red "？？？" (zh) / "???" (en)
- Supports paginated web cards, full panorama SVG/PNG, NodeSeek multi-tab, and standard Markdown
"""

import os
import re
import sys
import json
import html
import time
import random
import signal
import atexit
import shlex
import socket
import shutil
import argparse
import subprocess
import unicodedata
import urllib.request
from datetime import datetime, timezone, timedelta

VERSION = "v1.0.5 (2026.11.23)"
DEFAULT_SITE_URL = os.environ.get("DQ_SITE_URL", "https://test.sakurado.top")

TOOL_CREDITS = [
    ("fio", "https://github.com/axboe/fio"),
    ("ioping", "https://github.com/koct9i/ioping"),
    ("sysstat / iostat", "https://github.com/sysstat/sysstat"),
    ("smartmontools", "https://www.smartmontools.org"),
    ("e2fsprogs / tune2fs", "https://e2fsprogs.sourceforge.net"),
    ("curl", "https://curl.se"),
    ("ipinfo.io", "https://ipinfo.io"),
    ("Cloudflare Speed", "https://speed.cloudflare.com"),
    ("CacheFly", "https://www.cachefly.com"),
    ("NodeQuality", "https://github.com/LloydAsp/NodeQuality"),
    ("HardwareQuality", "https://github.com/xykt/HardwareQuality"),
    ("IPQuality", "https://github.com/xykt/IPQuality"),
]

GLOBAL_TCP_TARGETS = [
    ("Tokyo (JP)",       "hnd-jp-ping.vultr.com", 80),
    ("Singapore (SG)",   "sgp-ping.vultr.com",    80),
    ("Hong Kong (HK)",   "speedtest.hkg12.hk.leaseweb.net", 80),
    ("Los Angeles (US)", "lax-ca-us-ping.vultr.com", 80),
    ("New York (US)",    "nj-us-ping.vultr.com",  80),
    ("Frankfurt (DE)",   "fra-de-ping.vultr.com", 80),
    ("London (UK)",      "lon-gb-ping.vultr.com", 80),
    ("Amsterdam (NL)",   "ams-nl-ping.vultr.com", 80),
]

UNLOCK_PROBES = [
    ("Cloudflare", "https://www.cloudflare.com/cdn-cgi/trace"),
    ("Google",     "https://www.google.com/generate_204"),
    ("YouTube",    "https://www.youtube.com/"),
    ("Netflix",    "https://www.netflix.com/title/80018499"),
    ("Disney+",    "https://www.disneyplus.com/"),
    ("TikTok",     "https://www.tiktok.com/"),
    ("OpenAI",     "https://api.openai.com/v1/models"),
    ("Reddit",     "https://www.reddit.com/"),
    ("GitHub",     "https://github.com/"),
    ("Steam",      "https://store.steampowered.com/"),
]

I18N = {
    "zh": {
        "title": "PT / 大盘 / 备份机 全维度客观测评报告",
        "algo_line": "自适应算法：50% 容量 ({gb} GB) · {mins:.0f} 分钟预算  |  实际耗时：{elapsed} 分钟",
        "time_ver": "报告时间：{t}  |  脚本版本：{v}",
        "credits_hdr": "致谢与检测工具原站：",
        "s1": "一、操作系统与块设备拓扑",
        "k_virt": "容器/虚拟化：           ", "k_os": "操作系统/内核：         ",
        "k_cpu": "CPU 型号：              ", "cpu_sub": "{cores}核心, {mhz}, 负载 {load}",
        "k_mem": "内存/交换：             ", "mem_val": "内存 {mem} | Swap {swap}",
        "k_disk": "存储介质：              ", "disk_val": "{model}  总容量 {tot}G, 已用 {used}G, 可用 {avail}G",
        "k_dev": "设备属性：              ", "dev_val": "{dev} ({fs}) | ROTA={rota} | 调度={sched}",
        "k_cache": "缓存与对齐：            ", "cache_val": "write_cache={wc} | RA={ra}KB | 扇区={sec} | TRIM={trim}",
        "trim_yes": "支持", "trim_no": "不支持",
        "k_spec": "压测文件规格：          ", "spec_val": "50% 自适应压测文件 = {sgb} GB (短矩阵 {mgb} GB, Direct I/O)",
        "s2": "二、底层访问与同步延迟基线 (ioping)",
        "k_res": "检测结果：              ",
        "k_seek": "Direct 随机寻道：       ", "k_cread": "Page Cache 缓存读：     ", "k_swrite": "持久化同步写 (fsync)：  ",
        "s3": "三、FIO 合成性能矩阵 (libaio, direct=1)",
        "th_item": "测试项目", "th_r": "读吞吐 / IOPS", "th_w": "写吞吐 / IOPS",
        "s4": "四、生产模型与 fsync 事务刷盘",
        "s5": "五、小量多并发 I/O 压测 (PT 做种 / 校验 / 并发备份)",
        "lbl_r": "读", "lbl_w": "写",
        "s6": "六、{gb}GB (50% 容量) 持久压测与逐分钟 iostat 时序",
        "k_seq": "阶段 A 顺序连续写：     ", "seq_val": "累计写入 {gb} GB | 均速 {bw} MB/s | p99={p99} ms",
        "k_mix": "阶段 B 随机混合重载：   ", "mix_val": "读 {rbw} MB/s({riops} IOPS) | 写 {wbw} MB/s({wiops} IOPS) | p99={p99} ms",
        "th_min": "分钟", "th_stg": "阶段", "th_rmb": "读MB/s", "th_wmb": "写MB/s",
        "stg_seq": "50%容量顺序写", "stg_mix": "50%容量随机混合", "min_fmt": "第{m:02d}分",
        "s7": "七、国际互联能力与大文件下行吞吐 (PT / 备份拉取)",
        "th_node": "国际节点", "th_rtt": "TCP 延迟 (min/avg/max)", "th_loss": "丢包率",
        "k_dl": "国际大文件实测：        ",
        "s8": "八、IP 质量、平台解锁与被拒绝访问概率",
        "k_asn": "ASN / 归属地：          ", "k_ipattr": "IP 属性标记：           ",
        "k_p25": "25 端口出站：           ", "p25_ok": "开放", "p25_no": "阻断/超时",
        "k_deny": "被拒绝访问概率：        ",
        "risk_low": "低风险", "risk_mid": "中风险", "risk_high": "高风险",
        "st_ok": "放行", "st_blk": "拦截/拒访",
        "s9": "九、文件系统元数据 (10,000 × 4KB) 与通电寿命溯源",
        "k_meta": "元数据吞吐：            ", "meta_val": "创建 {c} f/s | Stat {s} f/s | 读 {r} f/s | 删 {d} f/s",
        "k_smart": "SMART 寄存器：          ", "smart_poh": " (通电 {h} h)",
        "k_ext4": "Ext4 超级块记账：       ", "ext4_val": "创建于 {cr} | 挂载次数 {mc} | 累计写入 {lw}",
        "k_url": "在线结果页：            ",
        "skip_txt": "？？？",
        "ns_cmd": "一键复测命令", "ns_url": "在线报告",
        "done_msg": "测试完成，点击查看你的临时结果链接（1 小时后自动销毁）：",
        "res_link": "测试结果",
        "tabs": ["全部", "基本信息", "硬盘矩阵", "持久时序", "互联与IP", "元数据与寿命"],
    },
    "en": {
        "title": "PT / Storage / Backup VPS Objective Benchmark Report",
        "algo_line": "Adaptive Algorithm: 50% Capacity ({gb} GB) · {mins:.0f}-Min Budget  |  Elapsed: {elapsed} min",
        "time_ver": "Report Time: {t}  |  Version: {v}",
        "credits_hdr": "Acknowledgments & Upstream Tools:",
        "s1": "1. Operating System & Block Device Topology",
        "k_virt": "Virtualization:         ", "k_os": "OS / Kernel:            ",
        "k_cpu": "CPU Model:              ", "cpu_sub": "{cores} Core(s), {mhz}, Load {load}",
        "k_mem": "Memory / Swap:          ", "mem_val": "RAM {mem} | Swap {swap}",
        "k_disk": "Storage Media:          ", "disk_val": "{model}  Total {tot}G, Used {used}G, Avail {avail}G",
        "k_dev": "Block Device:           ", "dev_val": "{dev} ({fs}) | ROTA={rota} | Sched={sched}",
        "k_cache": "Cache & Alignment:      ", "cache_val": "write_cache={wc} | RA={ra}KB | Sector={sec} | TRIM={trim}",
        "trim_yes": "Supported", "trim_no": "Unsupported",
        "k_spec": "Benchmark File Size:    ", "spec_val": "50% Adaptive Stress File = {sgb} GB (Matrix {mgb} GB, Direct I/O)",
        "s2": "2. Latency Baseline (ioping)",
        "k_res": "Result:                 ",
        "k_seek": "Direct Random Seek:     ", "k_cread": "Page Cache Read:        ", "k_swrite": "Sync Write (fsync):     ",
        "s3": "3. FIO Synthetic Matrix (libaio, direct=1)",
        "th_item": "Workload", "th_r": "Read BW / IOPS", "th_w": "Write BW / IOPS",
        "s4": "4. Production Workloads & fsync Commit",
        "s5": "5. Small-Block High-Concurrency I/O (PT Seed / Hash / Backup)",
        "lbl_r": "R", "lbl_w": "W",
        "s6": "6. {gb}GB (50% Capacity) Endurance Stress & Per-Minute iostat",
        "k_seq": "Phase A Seq Write:      ", "seq_val": "Written {gb} GB | Avg {bw} MB/s | p99={p99} ms",
        "k_mix": "Phase B Rand Mixed:     ", "mix_val": "R {rbw} MB/s({riops} IOPS) | W {wbw} MB/s({wiops} IOPS) | p99={p99} ms",
        "th_min": "Min", "th_stg": "Phase", "th_rmb": "R MB/s", "th_wmb": "W MB/s",
        "stg_seq": "50% Seq Write", "stg_mix": "50% Rand Mix", "min_fmt": "M{m:02d}  ",
        "s7": "7. Global Connectivity & Bulk Download Throughput (PT / Backup)",
        "th_node": "Global Hub", "th_rtt": "TCP RTT (min/avg/max)", "th_loss": "Loss",
        "k_dl": "Bulk Download Speed:    ",
        "s8": "8. IP Quality, Platform Access & Denial Probability",
        "k_asn": "ASN / Location:         ", "k_ipattr": "IP Attributes:          ",
        "k_p25": "Port 25 Outbound:       ", "p25_ok": "OPEN", "p25_no": "BLOCKED",
        "k_deny": "Access Denial Prob:     ",
        "risk_low": "Low Risk", "risk_mid": "Medium Risk", "risk_high": "High Risk",
        "st_ok": "PASS", "st_blk": "DENIED",
        "s9": "9. Filesystem Metadata (10,000 x 4KB) & Lifetime Diagnostics",
        "k_meta": "Metadata Rate:          ", "meta_val": "Create {c} f/s | Stat {s} f/s | Read {r} f/s | Unlink {d} f/s",
        "k_smart": "SMART Status:           ", "smart_poh": " (Power-On {h} h)",
        "k_ext4": "Ext4 Superblock:        ", "ext4_val": "Created {cr} | Mounts {mc} | Lifetime Writes {lw}",
        "k_url": "Online Report:          ",
        "skip_txt": "???",
        "ns_cmd": "One-Click Command", "ns_url": "Online Report",
        "done_msg": "Benchmark complete! View temporary online report (auto-destroyed after 1h):",
        "res_link": "Test Result",
        "tabs": ["All", "Overview", "Disk Matrix", "Endurance", "Net & IP", "Meta & Life"],
    },
}

E = "\x1b"
C_RST, C_B, C_U = f"{E}[0m", f"{E}[1m", f"{E}[4m"
C_CYN, C_GRN, C_YEL, C_RED = f"{E}[36m", f"{E}[32m", f"{E}[33m", f"{E}[31m"
C_BRED = f"{E}[1m{E}[31m"
C_INV = f"{E}[1m{E}[47m{E}[30m"
C_BG_GRN = f"{E}[1m{E}[42m{E}[37m"
C_BG_RED = f"{E}[1m{E}[41m{E}[37m"
C_BG_YEL = f"{E}[1m{E}[43m{E}[30m"


def calc_adaptive_plan(target_dir="/", total_minutes=20.0):
    st = os.statvfs(target_dir)
    total_gb = (st.f_blocks * st.f_frsize) / (1024 ** 3)
    avail_gb = (st.f_bavail * st.f_frsize) / (1024 ** 3)
    used_gb = (st.f_blocks * st.f_frsize - st.f_bfree * st.f_frsize) / (1024 ** 3)
    raw_50_gb = total_gb * 0.50
    safe_cap_gb = avail_gb * 0.80
    stress_file_gb = max(1.0, round(min(raw_50_gb, safe_cap_gb), 2))
    matrix_file_gb = max(0.5, min(4.0, round(stress_file_gb * 0.15, 2)))
    total_sec = int(total_minutes * 60)
    matrix_item_sec = max(5, min(10, int(total_sec * 0.18 / 22)))
    sustained_total_sec = max(120, total_sec - matrix_item_sec * 22 - 90)
    return {
        "target_dir": target_dir, "disk_total_gb": round(total_gb, 2), "disk_used_gb": round(used_gb, 2),
        "disk_avail_gb": round(avail_gb, 2), "target_ratio_pct": 50.0, "stress_file_gb": stress_file_gb,
        "stress_file_clamped": raw_50_gb > safe_cap_gb, "matrix_file_gb": matrix_file_gb,
        "budget_total_min": total_minutes, "matrix_item_sec": matrix_item_sec,
        "sustained_seq_sec": sustained_total_sec // 2,
        "sustained_mix_sec": sustained_total_sec - sustained_total_sec // 2,
    }


_ACTIVE_PROCS = []


def _kill_all_active_procs():
    for p in list(_ACTIVE_PROCS):
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
        try:
            p.wait(timeout=2)
        except Exception:
            pass
    _ACTIVE_PROCS.clear()


def run_cmd(cmd, timeout=120):
    p = None
    try:
        p = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, start_new_session=True,
        )
        _ACTIVE_PROCS.append(p)
        out, err = p.communicate(timeout=timeout)
        return p.returncode, (out or "").strip(), (err or "").strip()
    except subprocess.TimeoutExpired:
        if p is not None:
            try: os.killpg(os.getpgid(p.pid), signal.SIGKILL)
            except Exception:
                try: p.kill()
                except Exception: pass
            try: p.communicate(timeout=2)
            except Exception: pass
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)
    finally:
        if p is not None and p in _ACTIVE_PROCS:
            _ACTIVE_PROCS.remove(p)


def collect_system_topology(target_dir="/"):
    _, virt, _ = run_cmd("systemd-detect-virt 2>/dev/null || echo unknown")
    _, os_rel, _ = run_cmd("grep '^PRETTY_NAME=' /etc/os-release 2>/dev/null | cut -d= -f2- | tr -d '\"'")
    _, kernel, _ = run_cmd("uname -r")
    _, arch, _ = run_cmd("uname -m")
    _, loadavg, _ = run_cmd("awk '{print $1\", \"$2\", \"$3}' /proc/loadavg")
    _, cpu_model, _ = run_cmd("lscpu 2>/dev/null | awk -F: '/Model name/{gsub(/^[ \\t]+/,\"\",$2); print $2; exit}'")
    _, cpu_cores, _ = run_cmd("nproc")
    _, cpu_mhz, _ = run_cmd("awk -F: '/cpu MHz/{gsub(/^[ \\t]+/,\"\",$2); printf \"%.3fMHz\", $2; exit}' /proc/cpuinfo")
    _, mem_line, _ = run_cmd("free -m | awk '/^Mem:/{printf \"%dM (Used %dM / Avail %dM)\", $2, $3, $7}'")
    _, swap_line, _ = run_cmd("free -m | awk '/^Swap:/{if($2>0) printf \"%dM (Used %dM)\", $2, $3; else print \"0M\"}'")
    _, pub_ip, _ = run_cmd("curl -s4m 4 https://api.ipify.org 2>/dev/null || hostname -I | awk '{print $1}'")
    raw_ip = pub_ip.strip() if pub_ip else ""
    if re.match(r'^\d+\.\d+\.\d+\.\d+$', raw_ip):
        masked_ip = re.sub(r'^(\d+\.\d+)\.\d+\.\d+$', r'\1.*.*', raw_ip)
    elif ":" in raw_ip:
        masked_ip = re.sub(r'^([0-9a-fA-F]*:[0-9a-fA-F]*):.*$', r'\1:*:*', raw_ip)
    else:
        masked_ip = "Unknown"

    q_target = shlex.quote(target_dir)
    _, dev_src, _ = run_cmd(f"findmnt -n -o SOURCE {q_target}")
    _, fs_type, _ = run_cmd(f"findmnt -n -o FSTYPE {q_target}")
    _, base_dev, _ = run_cmd(f"lsblk -no PKNAME {shlex.quote(dev_src)} 2>/dev/null | head -n1")
    if not base_dev: base_dev = os.path.basename(dev_src).rstrip("0123456789")
    sb = f"/sys/block/{base_dev}"
    _, model, _ = run_cmd(f"cat {sb}/device/model 2>/dev/null || echo 'Virtual Disk'")
    _, rota, _ = run_cmd(f"cat {sb}/queue/rotational 2>/dev/null || echo '?'")
    _, sched, _ = run_cmd(f"cat {sb}/queue/scheduler 2>/dev/null || echo '?'")
    _, ra_kb, _ = run_cmd(f"cat {sb}/queue/read_ahead_kb 2>/dev/null || echo '?'")
    _, wcache, _ = run_cmd(f"cat {sb}/queue/write_cache 2>/dev/null || echo '?'")
    _, log_s, _ = run_cmd(f"cat {sb}/queue/logical_block_size 2>/dev/null || echo '512'")
    _, phy_s, _ = run_cmd(f"cat {sb}/queue/physical_block_size 2>/dev/null || echo '512'")
    _, disc, _ = run_cmd(f"cat {sb}/queue/discard_granularity 2>/dev/null || echo '0'")

    return {
        "masked_ip": masked_ip, "virt": virt, "arch": arch,
        "os": f"{os_rel} {kernel}".strip(), "loadavg": loadavg,
        "cpu_model": cpu_model or "Unknown CPU", "cpu_cores": cpu_cores, "cpu_mhz": cpu_mhz,
        "mem": mem_line, "swap": swap_line, "mount_dev": dev_src, "base_dev": f"/dev/{base_dev}",
        "fs_type": fs_type, "disk_model": model.strip(), "rotational": rota, "scheduler": sched,
        "read_ahead_kb": ra_kb, "write_cache": wcache, "sector": f"{log_s}B / {phy_s}B",
        "trim_supported": int(disc or 0) > 0,
    }


def collect_poweron_lifetime(mount_dev, base_dev):
    _, smart_out, _ = run_cmd(f"smartctl -a {shlex.quote(base_dev)} 2>&1 | head -n 30")
    smart_avail = "Unavailable" not in smart_out and "failed" not in smart_out.lower() and bool(smart_out)
    poh = None
    if smart_avail:
        m = re.search(r'Power_On_Hours.*?(\d+)\s*$', smart_out, re.M)
        if m: poh = m.group(1)
    _, t2fs, _ = run_cmd(f"tune2fs -l {shlex.quote(mount_dev)} 2>/dev/null")
    cr = re.search(r'Filesystem created:\s*(.+)', t2fs)
    mc = re.search(r'Mount count:\s*(\d+)', t2fs)
    lw = re.search(r'Lifetime writes:\s*(.+)', t2fs)
    return {
        "smart_available": smart_avail, "smart_power_on_hours": poh,
        "smart_raw_status": "Available" if smart_avail else "Unavailable (Virtual/Shielded)",
        "fs_created": cr.group(1).strip() if cr else "N/A",
        "mount_count": mc.group(1).strip() if mc else "N/A",
        "lifetime_writes": lw.group(1).strip() if lw else "N/A",
    }


def run_ioping_tests(work_dir):
    res = {}
    q_dir = shlex.quote(work_dir)
    for key, flags in [("direct_seek", "-D -c 20 -i 0.05"), ("cached_read", "-C -c 20 -i 0.05"), ("sync_write", "-D -S -W -c 20 -i 0.05")]:
        _, out, _ = run_cmd(f"ioping {flags} {q_dir} 2>&1", timeout=60)
        m = re.search(r'min/avg/max/mdev\s*=\s*([^\n]+)', out)
        res[key] = m.group(1).strip() if m else "N/A"
    return res


def run_fio_job(name, filepath, size_gb, rw, bs, iodepth, numjobs, runtime, direct=1, rwmixread=None, fsync=None):
    cmd = (
        f"fio --name={shlex.quote(name)} --filename={shlex.quote(filepath)} --size={int(size_gb * 1024)}M "
        f"--ioengine=libaio --direct={direct} --rw={rw} --bs={bs} "
        f"--iodepth={iodepth} --numjobs={numjobs} --runtime={runtime} --time_based "
        f"--group_reporting --output-format=json"
    )
    if rwmixread is not None: cmd += f" --rwmixread={rwmixread}"
    if fsync is not None: cmd += f" --fsync={fsync}"
    rc, out, _ = run_cmd(cmd, timeout=runtime + 120)
    if rc != 0 or not out: return {"name": name, "error": True}
    try:
        j = json.loads(out)["jobs"][0]
        r, w = j["read"], j["write"]
        return {
            "name": name,
            "r_bw_mbs": round(r["bw_bytes"] / (1024 ** 2), 2), "r_iops": round(r["iops"], 1),
            "r_p95_ms": round(r.get("clat_ns", {}).get("percentile", {}).get("95.000000", 0) / 1e6, 2),
            "r_p99_ms": round(r.get("clat_ns", {}).get("percentile", {}).get("99.000000", 0) / 1e6, 2),
            "w_bw_mbs": round(w["bw_bytes"] / (1024 ** 2), 2), "w_iops": round(w["iops"], 1),
            "w_p95_ms": round(w.get("clat_ns", {}).get("percentile", {}).get("95.000000", 0) / 1e6, 2),
            "w_p99_ms": round(w.get("clat_ns", {}).get("percentile", {}).get("99.000000", 0) / 1e6, 2),
            "w_bytes": w.get("io_bytes", 0),
        }
    except Exception:
        return {"name": name, "error": True}


def run_global_network_tests():
    """Test TCP RTT + packet loss to 8 global hubs and bulk CDN download throughput."""
    hubs = []
    for label, host, port in GLOBAL_TCP_TARGETS:
        rtts = []
        tries = 4
        for _ in range(tries):
            t0 = time.perf_counter()
            try:
                s = socket.create_connection((host, port), timeout=2.5)
                rtts.append((time.perf_counter() - t0) * 1000.0)
                s.close()
            except Exception:
                pass
        loss = round((tries - len(rtts)) * 100.0 / tries, 0)
        if rtts:
            hubs.append({"hub": label, "min": round(min(rtts), 1), "avg": round(sum(rtts)/len(rtts), 1), "max": round(max(rtts), 1), "loss": loss})
        else:
            hubs.append({"hub": label, "min": -1, "avg": -1, "max": -1, "loss": 100.0})

    downloads = []
    for name, url in [
        ("Cloudflare 50MB", "https://speed.cloudflare.com/__down?bytes=52428800"),
        ("CacheFly 100MB",  "https://cachefly.cachefly.net/100mb.test"),
    ]:
        rc, out, _ = run_cmd(f"curl -4 -sS -L -m 15 -o /dev/null -w '%{{speed_download}}' '{url}'", timeout=20)
        try:
            mbs = round(float(out) / (1024 ** 2), 2)
            downloads.append({"name": name, "mbs": mbs, "mbps": round(mbs * 8, 1)})
        except Exception:
            downloads.append({"name": name, "mbs": 0.0, "mbps": 0.0})
    return {"hubs": hubs, "downloads": downloads}


def run_ip_quality_tests():
    """Objective ASN/geo lookup, 10-platform access probe, empirical denial probability, and port 25 test."""
    meta = {"asn": "Unknown", "org": "Unknown", "location": "Unknown", "hosting": "Unknown"}
    try:
        req = urllib.request.Request("https://ipinfo.io/json", headers={"User-Agent": "curl/8.0"})
        with urllib.request.urlopen(req, timeout=6) as r:
            d = json.loads(r.read().decode("utf-8", errors="ignore"))
            org_s = d.get("org", "")
            parts = org_s.split(" ", 1)
            meta["asn"] = parts[0] if parts else "Unknown"
            meta["org"] = parts[1] if len(parts) > 1 else org_s
            meta["location"] = ", ".join(x for x in [d.get("country", ""), d.get("region", ""), d.get("city", "")] if x)
    except Exception:
        pass
    try:
        req2 = urllib.request.Request("http://ip-api.com/json/?fields=hosting,proxy,mobile", headers={"User-Agent": "curl/8.0"})
        with urllib.request.urlopen(req2, timeout=5) as r2:
            d2 = json.loads(r2.read().decode("utf-8", errors="ignore"))
            flags = [k for k in ("hosting", "proxy", "mobile") if d2.get(k)]
            meta["hosting"] = "/".join(flags) if flags else "clean/residential"
    except Exception:
        pass

    probes = []
    denied = 0
    for name, url in UNLOCK_PROBES:
        rc, out, _ = run_cmd(f"curl -4 -sS -L -m 6 -A 'Mozilla/5.0' -o /dev/null -w '%{{http_code}}' '{url}'", timeout=10)
        code = int(out) if out.isdigit() else 0
        # OpenAI /v1/models returns 401 when accessible without API key (403/451/429 = geo/CF blocked)
        ok = (200 <= code < 400) or (name == "OpenAI" and code == 401)
        if not ok:
            denied += 1
        probes.append({"service": name, "code": code, "ok": ok})

    total_p = len(probes)
    denial_pct = round(denied * 100.0 / max(1, total_p), 1)
    risk = "low" if denial_pct < 15 else ("mid" if denial_pct <= 40 else "high")

    p25_open = False
    try:
        s = socket.create_connection(("gmail-smtp-in.l.google.com", 25), timeout=4)
        p25_open = True
        s.close()
    except Exception:
        pass

    return {
        "meta": meta, "probes": probes, "denied_count": denied, "total_probes": total_p,
        "denial_pct": denial_pct, "risk": risk, "port25_open": p25_open,
    }


def run_metadata_bench(work_dir):
    mdir = os.path.join(work_dir, "meta_10k")
    os.makedirs(mdir, exist_ok=True)
    payload, n = b"0" * 4096, 10000
    t0 = time.perf_counter()
    for i in range(n):
        with open(os.path.join(mdir, f"f{i}"), "wb") as f: f.write(payload)
    tc = time.perf_counter() - t0
    t0 = time.perf_counter()
    for i in range(n): os.stat(os.path.join(mdir, f"f{i}"))
    ts = time.perf_counter() - t0
    t0 = time.perf_counter()
    for i in range(n):
        with open(os.path.join(mdir, f"f{i}"), "rb") as f: _ = f.read()
    tr = time.perf_counter() - t0
    t0 = time.perf_counter()
    for i in range(n): os.unlink(os.path.join(mdir, f"f{i}"))
    td = time.perf_counter() - t0
    shutil.rmtree(mdir, ignore_errors=True)
    return {
        "files": n,
        "create_fps": round(n / max(tc, 1e-6), 1), "stat_fps": round(n / max(ts, 1e-6), 1),
        "read_fps": round(n / max(tr, 1e-6), 1), "delete_fps": round(n / max(td, 1e-6), 1),
    }


def parse_iostat_minutes(log_path, dev_short, seq_minutes):
    if not os.path.exists(log_path): return []
    samples = []
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 14 and parts[0] == dev_short:
                try: samples.append([float(x) for x in parts[1:]])
                except Exception: pass
    minutes = []
    for i in range(0, len(samples), 12):
        chunk = samples[i:i + 12]
        if not chunk: continue
        m_idx = len(minutes) + 1
        avg = [sum(row[c] for row in chunk) / len(chunk) for c in range(len(chunk[0]))]
        minutes.append({
            "min": m_idx, "is_seq": m_idx <= max(1, seq_minutes),
            "r_mb": round(avg[1], 2), "w_mb": round(avg[6], 2) if len(avg) > 6 else 0.0,
            "r_s": round(avg[0], 1), "w_s": round(avg[5], 1) if len(avg) > 6 else 0.0,
            "w_await": round(avg[10], 2) if len(avg) > 10 else 0.0, "util": round(avg[-1], 1),
        })
    return minutes


def _color_bw(mb):
    return C_GRN if mb >= 200 else (C_YEL if mb >= 20 else C_RED)


def build_sections(data, lang=None, site_url=None):
    """Build modular ANSI sections so both paginated web cards and full panorama share one source of truth."""
    lang = (lang or data.get("lang") or "zh").lower()
    if lang not in I18N: lang = "zh"
    L = I18N[lang]
    s_url = site_url or data.get("site_url") or DEFAULT_SITE_URL
    skip = f"{C_BRED}{L['skip_txt']}{C_RST}"
    t, p = data["topology"], data["plan"]
    sel = data.get("selected", {})

    # Page 0: Overview & Topology + ioping (clean HardwareQuality layout, zero credits wall)
    sec_overview = [
        "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++",
        f"               {C_B}{L['title']}: {C_CYN}{t['masked_ip']}{C_RST}",
        f"               {C_U}https://github.com/arimrs/DiskQuality{C_RST}",
        f"                bash <(curl -sL {s_url})",
        f"     {L['time_ver'].format(t=data['report_time'], v=data['version'])}",
        "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++",
        L["s1"],
        f"{C_CYN}{L['k_virt']}{C_GRN}{t['virt']} ({t['arch']}){C_RST}",
        f"{C_CYN}{L['k_os']}{C_GRN}{t['os']}{C_RST}",
        f"{C_CYN}{L['k_cpu']}{C_INV} {t['cpu_model']} {C_RST}",
        f"                        {C_INV} ╚═ {L['cpu_sub'].format(cores=t['cpu_cores'], mhz=t['cpu_mhz'], load=t['loadavg'])} {C_RST}",
        f"{C_CYN}{L['k_mem']}{C_INV} {L['mem_val'].format(mem=t['mem'], swap=t['swap'])} {C_RST}",
        f"{C_CYN}{L['k_disk']}{C_INV} {L['disk_val'].format(model=t['disk_model'], tot=p['disk_total_gb'], used=p['disk_used_gb'], avail=p['disk_avail_gb'])} {C_RST}",
        f"{C_CYN}{L['k_dev']}{C_GRN}{L['dev_val'].format(dev=t['mount_dev'], fs=t['fs_type'], rota=t['rotational'], sched=t['scheduler'])}{C_RST}",
        f"{C_CYN}{L['k_cache']}{C_GRN}{L['cache_val'].format(wc=t['write_cache'], ra=t['read_ahead_kb'], sec=t['sector'], trim=L['trim_yes'] if t['trim_supported'] else L['trim_no'])}{C_RST}",
        f"{C_CYN}{L['k_spec']}{C_YEL}{L['spec_val'].format(sgb=p['stress_file_gb'], mgb=p['matrix_file_gb'])}{C_RST}",
        "",
        L["s2"],
    ]
    io = data.get("ioping")
    if not sel.get("ioping", True) or not io:
        sec_overview.append(f"{C_CYN}{L['k_res']}{skip}")
    else:
        sec_overview += [
            f"{C_CYN}{L['k_seek']}{C_GRN}{io.get('direct_seek','N/A')}{C_RST}",
            f"{C_CYN}{L['k_cread']}{C_GRN}{io.get('cached_read','N/A')}{C_RST}",
            f"{C_CYN}{L['k_swrite']}{C_GRN}{io.get('sync_write','N/A')}{C_RST}",
        ]

    # Page 1: Disk Matrix + Production fsync + High-Concurrency Small-IO
    sec_disk = [L["s3"]]
    if not sel.get("matrix", True) or not data.get("matrix"):
        sec_disk.append(f"{C_CYN}{L['k_res']}{skip}")
    else:
        sec_disk.append(f"{C_CYN}{L['th_item']:<20} {L['th_r']:<22} {L['th_w']:<22} {'p95':>8} {'p99':>8}{C_RST}")
        for row in data["matrix"]:
            if row.get("error"): continue
            rs = f"{row['r_bw_mbs']:.2f}MB/s ({row['r_iops']:.0f})" if row["r_iops"] > 0 else "-"
            ws = f"{row['w_bw_mbs']:.2f}MB/s ({row['w_iops']:.0f})" if row["w_iops"] > 0 else "-"
            col = _color_bw(max(row["r_bw_mbs"], row["w_bw_mbs"]))
            sec_disk.append(f"{C_CYN}{row['name']:<20}{C_RST} {col}{rs:<22} {ws:<22}{C_RST} {max(row['r_p95_ms'],row['w_p95_ms']):>6.1f}ms {max(row['r_p99_ms'],row['w_p99_ms']):>6.1f}ms")

    sec_disk += ["", L["s4"]]
    if not sel.get("prod", True) or not data.get("production"):
        sec_disk.append(f"{C_CYN}{L['k_res']}{skip}")
    else:
        for row in data["production"]:
            if row.get("error"): continue
            rs = f"{L['lbl_r']} {row['r_bw_mbs']:.2f}MB/s({row['r_iops']:.0f})" if row["r_iops"] > 0 else f"{L['lbl_r']} -"
            ws = f"{L['lbl_w']} {row['w_bw_mbs']:.2f}MB/s({row['w_iops']:.0f})" if row["w_iops"] > 0 else f"{L['lbl_w']} -"
            sec_disk.append(f"{C_CYN}{row['name']:<18}{C_RST} {C_YEL}{rs:<22} {ws:<22}{C_RST} p99={max(row['r_p99_ms'],row['w_p99_ms']):.2f}ms")

    sec_disk += ["", L["s5"]]
    if not sel.get("concurrency", True) or not data.get("concurrency"):
        sec_disk.append(f"{C_CYN}{L['k_res']}{skip}")
    else:
        sec_disk.append(f"{C_CYN}{L['th_item']:<20} {L['th_r']:<22} {L['th_w']:<22} {'p95':>8} {'p99':>8}{C_RST}")
        for row in data["concurrency"]:
            if row.get("error"): continue
            rs = f"{row['r_bw_mbs']:.2f}MB/s ({row['r_iops']:.0f})" if row["r_iops"] > 0 else "-"
            ws = f"{row['w_bw_mbs']:.2f}MB/s ({row['w_iops']:.0f})" if row["w_iops"] > 0 else "-"
            col = _color_bw(max(row["r_bw_mbs"], row["w_bw_mbs"]))
            sec_disk.append(f"{C_CYN}{row['name']:<20}{C_RST} {col}{rs:<22} {ws:<22}{C_RST} {max(row['r_p95_ms'],row['w_p95_ms']):>6.1f}ms {max(row['r_p99_ms'],row['w_p99_ms']):>6.1f}ms")

    # Page 2: 50% Endurance & iostat Timeline
    sec_endurance = [L["s6"].format(gb=p["stress_file_gb"])]
    sus = data.get("sustained")
    if not sel.get("sustained", True) or not sus:
        sec_endurance.append(f"{C_CYN}{L['k_res']}{skip}")
    else:
        sw, ms = sus["seq_write"], sus["rand_mixed"]
        sec_endurance += [
            f"{C_CYN}{L['k_seq']}{C_GRN}{L['seq_val'].format(gb=round(sw.get('w_bytes',0)/(1024**3),2), bw=sw.get('w_bw_mbs',0), p99=sw.get('w_p99_ms',0))}{C_RST}",
            f"{C_CYN}{L['k_mix']}{C_YEL}{L['mix_val'].format(rbw=ms.get('r_bw_mbs',0), riops=ms.get('r_iops',0), wbw=ms.get('w_bw_mbs',0), wiops=ms.get('w_iops',0), p99=ms.get('w_p99_ms',0))}{C_RST}",
        ]
        if sus.get("timeline"):
            sec_endurance.append(f"{C_CYN}{L['th_min']:<6} {L['th_stg']:<14} {L['th_rmb']:>8} {L['th_wmb']:>9} {'r/s':>7} {'w/s':>7} {'w_await':>9} {'%util':>7}{C_RST}")
            for pt in sus["timeline"]:
                stg = L["stg_seq"] if pt.get("is_seq", True) else L["stg_mix"]
                col = C_GRN if pt["w_mb"] >= 50 else C_YEL
                sec_endurance.append(f"{L['min_fmt'].format(m=pt['min'])}  {stg:<13} {col}{pt['r_mb']:>8.2f} {pt['w_mb']:>9.2f}{C_RST} {pt['r_s']:>7.1f} {pt['w_s']:>7.1f} {pt['w_await']:>7.1f}ms {pt['util']:>6.1f}%")

    # Page 3: Global Network & IP Quality + Access Denial Probability
    sec_netip = [L["s7"]]
    net = data.get("network")
    if not sel.get("network", True) or not net:
        sec_netip.append(f"{C_CYN}{L['k_res']}{skip}")
    else:
        sec_netip.append(f"{C_CYN}{L['th_node']:<20} {L['th_rtt']:<28} {L['th_loss']:>8}{C_RST}")
        for h in net.get("hubs", []):
            rtt_s = f"{h['min']:.1f} / {h['avg']:.1f} / {h['max']:.1f} ms" if h["avg"] >= 0 else "Timeout"
            col = C_GRN if 0 <= h["avg"] < 120 else (C_YEL if h["avg"] >= 0 else C_RED)
            sec_netip.append(f"{C_CYN}{h['hub']:<20}{C_RST} {col}{rtt_s:<28}{C_RST} {h['loss']:>6.0f}%")
        dl_parts = [f"{d['name']}: {d['mbs']} MB/s ({d['mbps']} Mbps)" for d in net.get("downloads", [])]
        sec_netip.append(f"{C_CYN}{L['k_dl']}{C_GRN}{' | '.join(dl_parts)}{C_RST}")

    sec_netip += ["", L["s8"]]
    ipq = data.get("ip_quality")
    if not sel.get("ip_quality", True) or not ipq:
        sec_netip.append(f"{C_CYN}{L['k_res']}{skip}")
    else:
        im = ipq["meta"]
        rk_map = {"low": (C_BG_GRN, L["risk_low"]), "mid": (C_BG_YEL, L["risk_mid"]), "high": (C_BG_RED, L["risk_high"])}
        rk_col, rk_lbl = rk_map.get(ipq["risk"], (C_BG_YEL, ipq["risk"]))
        p25_badge = f"{C_BG_GRN} ✔ {L['p25_ok']} {C_RST}" if ipq["port25_open"] else f"{C_BG_RED} ✘ {L['p25_no']} {C_RST}"
        sec_netip += [
            f"{C_CYN}{L['k_asn']}{C_GRN}{im['asn']} ({im['org']}) · {im['location']}{C_RST}",
            f"{C_CYN}{L['k_ipattr']}{C_YEL}{im['hosting']}{C_RST}",
            f"{C_CYN}{L['k_p25']}{p25_badge}",
            f"{C_CYN}{L['k_deny']}{rk_col} {ipq['denial_pct']}% ({ipq['denied_count']}/{ipq['total_probes']}) {rk_lbl} {C_RST}",
        ]
        row_items = []
        for pr in ipq.get("probes", []):
            if pr["ok"]:
                row_items.append(f"{C_BG_GRN} ✔ {pr['service']} {C_RST}")
            else:
                row_items.append(f"{C_BG_RED} ✘ {pr['service']}({pr['code']}) {C_RST}")
        sec_netip.append("  " + "  ".join(row_items[:5]))
        sec_netip.append("  " + "  ".join(row_items[5:]))

    # Page 4: Metadata & Lifetime
    sec_meta = [L["s9"]]
    m, l = data.get("metadata"), data.get("lifetime")
    if not sel.get("meta", True) or not m or not l:
        sec_meta.append(f"{C_CYN}{L['k_res']}{skip}")
    else:
        poh_s = L["smart_poh"].format(h=l["smart_power_on_hours"]) if l.get("smart_power_on_hours") else ""
        sec_meta += [
            f"{C_CYN}{L['k_meta']}{C_GRN}{L['meta_val'].format(c=m['create_fps'], s=m['stat_fps'], r=m['read_fps'], d=m['delete_fps'])}{C_RST}",
            f"{C_CYN}{L['k_smart']}{C_YEL}{l['smart_raw_status']}{poh_s}{C_RST}",
            f"{C_CYN}{L['k_ext4']}{C_GRN}{L['ext4_val'].format(cr=l['fs_created'], mc=l['mount_count'], lw=l['lifetime_writes'])}{C_RST}",
        ]

    footer = ["================================================================================"]
    if data.get("report_url"):
        footer.append(f"{C_CYN}{L['k_url']}{C_U}{data['report_url']}{C_RST}")

    return {
        "overview": "\n".join(sec_overview),
        "disk": "\n".join(sec_disk),
        "endurance": "\n".join(sec_endurance),
        "netip": "\n".join(sec_netip),
        "meta": "\n".join(sec_meta),
        "full": "\n".join(sec_overview + [""] + sec_disk + [""] + sec_endurance + [""] + sec_netip + [""] + sec_meta + footer),
    }


def render_p2_ansi(data, lang=None, site_url=None):
    return build_sections(data, lang=lang, site_url=site_url)["full"]


def strip_ansi(s):
    return re.sub(r'\x1b\[[0-9;]*m', '', s)


ANSI_COLOR_MAP = {
    "30": "#18181b", "31": "#e05252", "32": "#52b758", "33": "#d4a017",
    "34": "#60a5fa", "35": "#c084fc", "36": "#3ba7a0", "37": "#f4f4f5",
}
ANSI_BG_MAP = {
    "41": "#c92a2a", "42": "#52a31c", "43": "#b45309", "46": "#0e7490", "47": "#d8d8d8",
}


def _disp_cells(s):
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in s)


def parse_ansi_spans(line):
    tokens = re.split(r'(\x1b\[[0-9;]*m)', line)
    fg, bg, bold, ul = "#e4e4e7", None, False, False
    spans = []
    for tok in tokens:
        if tok.startswith("\x1b[") and tok.endswith("m"):
            codes = [c for c in tok[2:-1].split(";") if c]
            if not codes or "0" in codes: fg, bg, bold, ul = "#e4e4e7", None, False, False
            for c in codes:
                if c == "1": bold = True
                elif c == "4": ul = True
                elif c in ANSI_COLOR_MAP: fg = ANSI_COLOR_MAP[c]
                elif c in ANSI_BG_MAP: bg = ANSI_BG_MAP[c]
        elif tok:
            spans.append((tok, fg, bg, bold, ul))
    return spans


def render_ansi_to_svg_str(ansi_text):
    """HardwareQuality / NodeQuality faithful charcoal terminal SVG renderer with real highlight bars & status badges."""
    lines = ansi_text.splitlines()
    line_height, pad_x, pad_y, char_w, width = 22, 26, 24, 8.4, 960
    height = pad_y * 2 + len(lines) * line_height + 10
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<defs><style>text { font-family: "JetBrains Mono","Cascadia Mono","Consolas","Microsoft YaHei","Noto Sans Mono CJK SC",monospace; font-size: 14px; white-space: pre; }</style></defs>',
        '<rect width="100%" height="100%" rx="8" fill="#1b1c1f"/>',
    ]
    for idx, line in enumerate(lines):
        y = pad_y + (idx + 1) * line_height - 5
        rects, els = [], []
        col_x = 0
        for txt, fg, bg, bold, ul in parse_ansi_spans(line):
            cells = _disp_cells(txt)
            if bg:
                rx_x = pad_x + col_x * char_w
                rx_w = max(cells * char_w + 2, 12)
                rects.append(f'<rect x="{rx_x:.1f}" y="{y - 14.5:.1f}" width="{rx_w:.1f}" height="18.5" rx="2" fill="{bg}"/>')
            fw = ' font-weight="700"' if bold else ''
            td = ' text-decoration="underline"' if ul else ''
            fill_c = "#18181b" if bg == "#d8d8d8" else ("#ffffff" if bg in ("#52a31c", "#c92a2a") else fg)
            els.append(f'<tspan fill="{fill_c}"{fw}{td}>{html.escape(txt)}</tspan>')
            col_x += cells
        svg.extend(rects)
        svg.append(f'<text x="{pad_x}" y="{y}" xml:space="preserve">{"".join(els)}</text>')
    svg.append("</svg>")
    return "\n".join(svg)


def render_nodeseek_md(data, lang=None, site_url=None):
    """Clean image-based NodeSeek multi-tab format (strict 4-colon outer, 3-colon inner, no credits wall)."""
    lang = (lang or data.get("lang") or "zh").lower()
    L = I18N.get(lang, I18N["zh"])
    s_url = (site_url or data.get("site_url") or DEFAULT_SITE_URL).rstrip("/")
    r_url = (data.get("report_url") or s_url).rstrip("/")
    tabs = L["tabs"]
    keys = ["full", "overview", "disk", "endurance", "netip", "meta"]
    blocks = []
    for lbl, key in zip(tabs, keys):
        blocks.append(f"::: tab-item {lbl}\n![{lbl}]({r_url}/{key}.svg)\n:::")
    return (
        f"{L['res_link']}：[{r_url}]({r_url})\n\n"
        f":::: tabs\n"
        + "\n\n".join(blocks)
        + "\n::::\n"
    )


def render_standard_md(data, lang=None, site_url=None):
    """Clean image-based Markdown format (report link + full SVG image, no credits wall)."""
    lang = (lang or data.get("lang") or "zh").lower()
    L = I18N.get(lang, I18N["zh"])
    s_url = (site_url or data.get("site_url") or DEFAULT_SITE_URL).rstrip("/")
    r_url = (data.get("report_url") or s_url).rstrip("/")
    return (
        f"{L['res_link']}：[{r_url}]({r_url})\n\n"
        f"![DiskQuality]({r_url}/full.svg)\n"
    )


def thorough_cleanup(work_dir, target_dir="/", do_trim=False):
    """Thoroughly terminate any lingering workers, remove all temporary files/dirs, and optionally TRIM."""
    _kill_all_active_procs()
    q_work = shlex.quote(work_dir)
    q_target = shlex.quote(target_dir)
    try:
        subprocess.run(f"pkill -9 -f {q_work} 2>/dev/null || true", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
    except Exception:
        pass
    for _ in range(3):
        if not os.path.exists(work_dir):
            break
        shutil.rmtree(work_dir, ignore_errors=True)
        if os.path.exists(work_dir):
            try:
                subprocess.run(f"rm -rf {q_work} 2>/dev/null || true", shell=True, timeout=10)
            except Exception:
                pass
            time.sleep(0.2)
    try:
        subprocess.run("sync 2>/dev/null || true", shell=True, timeout=10)
        if do_trim:
            subprocess.run(f"fstrim {q_target} 2>/dev/null || true", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
    except Exception:
        pass


def run_benchmark_cli(args):
    lang = args.lang.lower() if args.lang.lower() in ("zh", "en") else "zh"
    L = I18N[lang]
    work_dir = os.path.join(args.target.rstrip("/") or "/", ".diskquality_work")
    t_start = time.time()
    tz = timezone(timedelta(hours=8))
    start_str = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S (Taipei Time)")

    # 1. Thorough pre-test cleanup & signal/exit trap (ensures zero leftover files even on Ctrl+C)
    thorough_cleanup(work_dir, args.target, do_trim=False)
    cleaned_flag = {"done": False}

    def _emergency_cleanup(from_signal=False):
        if cleaned_flag["done"]:
            return
        cleaned_flag["done"] = True
        thorough_cleanup(work_dir, args.target, do_trim=from_signal)
        if from_signal:
            if lang == "en":
                print(f"\n{C_YEL}[Abort Cleanup] Interrupted — terminated all benchmark workers & thoroughly removed {work_dir} (´• ω •`){C_RST}", flush=True)
            else:
                print(f"\n{C_YEL}[中断清理] 检测到临时退出，已终止全部压测进程并彻底清理 {work_dir} 与积累文件 (´• ω •`){C_RST}", flush=True)

    atexit.register(_emergency_cleanup, False)
    for sig in (signal.SIGINT, signal.SIGTERM, getattr(signal, "SIGHUP", signal.SIGTERM)):
        try:
            signal.signal(sig, lambda s, f: (_emergency_cleanup(True), os._exit(130)))
        except Exception:
            pass

    # 2. Pre-test disk space scan (abort if usage > 65%)
    usage = shutil.disk_usage(args.target)
    used_pct = (usage.used * 100.0 / usage.total) if usage.total > 0 else 0.0
    if used_pct > 65.0:
        if lang == "en":
            print(f"{C_RED}[Abort] Disk usage is {used_pct:.1f}% (> 65%). Insufficient disk space, benchmark automatically cancelled (；′⌒`){C_RST}", flush=True)
        else:
            print(f"{C_RED}[终止] 当前硬盘占用 {used_pct:.1f}% (> 65%)，硬盘空间不足，已自动取消运行 (；′⌒`){C_RST}", flush=True)
        sys.exit(1)

    os.makedirs(work_dir, exist_ok=True)
    sel = {k: getattr(args, k).lower() == "y" for k in ("ioping", "matrix", "prod", "concurrency", "sustained", "network", "ip_quality", "meta")}

    # 3. Clean visual progress bar tracker (kaomoji reserved strictly for end completion)
    end_kaomojis = (
        "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧", "( •̀ ω •́ )✧", "(๑•̀ㅂ•́)و✧", "ヾ(•ω•`)o",
        "(o´ω`o)ﾉ", "٩(｡•́‿•̀｡)۶", "(*^▽^*)", "(☆▽☆)",
        "ヽ(✿ﾟ▽ﾟ)ノ", "(｡･ω･｡)ﾉ♡", "(*≧ω≦)", "(づ￣ 3￣)づ",
        "٩(ˊᗜˋ*)و", "✧*｡٩(ˊᗜˋ*)و✧*｡", "(￣▽￣)ノ", "o(*￣▽￣*)ブ",
        "(≧▽≦)/", "ヾ(≧▽≦*)o", "(●'◡'●)", "ヽ(•̀ω•́ )ゝ",
    )
    total_steps = (
        1  # topology
        + (1 if sel["ioping"] else 0)
        + (14 if sel["matrix"] else 0)
        + (4 if sel["prod"] else 0)
        + (4 if sel["concurrency"] else 0)
        + (2 if sel["sustained"] else 0)
        + (1 if sel["network"] else 0)
        + (1 if sel["ip_quality"] else 0)
        + (1 if sel["meta"] else 0)
        + 1  # final cleanup & report
    )
    step_state = {"cur": 0}

    def show_bar(msg_zh, msg_en, advance=1, suffix=""):
        step_state["cur"] = min(total_steps, step_state["cur"] + advance)
        pct = int(round(step_state["cur"] * 100.0 / max(1, total_steps)))
        filled = int(round(24 * pct / 100.0))
        bar = "█" * filled + "░" * (24 - filled)
        ts = datetime.now(tz).strftime("%H:%M:%S")
        msg = msg_en if lang == "en" else msg_zh
        tail = f" {suffix}" if suffix else ""
        print(f"{C_CYN}[{ts}]{C_RST} {C_GRN}[{bar}]{C_RST} {C_YEL}{pct:3d}%{C_RST} | {msg}{tail}", flush=True)

    show_bar("正在采集系统与块设备拓扑...", "Collecting system & block device topology...", advance=0)
    plan = calc_adaptive_plan(args.target, args.minutes)
    topo = collect_system_topology(args.target)
    show_bar(
        f"拓扑完成 · 目标盘 {plan['disk_total_gb']} GB (已用 {used_pct:.1f}%) · 50% 压测文件 {plan['stress_file_gb']} GB",
        f"Topology ready · Disk {plan['disk_total_gb']} GB (used {used_pct:.1f}%) · 50% Stress File {plan['stress_file_gb']} GB",
        advance=1,
    )

    ioping_res = None
    if sel["ioping"]:
        show_bar("正在运行底层延迟基线测试 (ioping)...", "Running latency baseline (ioping)...", advance=0)
        ioping_res = run_ioping_tests(work_dir)
        show_bar("底层延迟基线测试 (ioping) 完成", "Latency baseline (ioping) completed", advance=1)

    mfile, sfile = os.path.join(work_dir, "matrix.bin"), os.path.join(work_dir, "stress_50pct.bin")
    rt, msz = plan["matrix_item_sec"], plan["matrix_file_gb"]

    matrix_res = None
    if sel["matrix"]:
        specs = [
            ("SEQ1M_R_Q1", "read", "1M", 1, 1, 1, None, None), ("SEQ1M_R_Q32", "read", "1M", 32, 4, 1, None, None),
            ("SEQ1M_W_Q1", "write", "1M", 1, 1, 1, None, None), ("SEQ1M_W_Q32", "write", "1M", 32, 4, 1, None, None),
            ("RND4K_R_Q1", "randread", "4K", 1, 1, 1, None, None), ("RND4K_R_Q16", "randread", "4K", 16, 1, 1, None, None),
            ("RND4K_R_Q64", "randread", "4K", 64, 4, 1, None, None), ("RND4K_W_Q1", "randwrite", "4K", 1, 1, 1, None, None),
            ("RND4K_W_Q16", "randwrite", "4K", 16, 1, 1, None, None), ("RND4K_W_Q64", "randwrite", "4K", 64, 4, 1, None, None),
            ("RND8K_70_30", "randrw", "8K", 16, 2, 1, 70, None), ("RND16K_70_30", "randrw", "16K", 16, 2, 1, 70, None),
            ("SEQ128K_50_50", "rw", "128K", 16, 2, 1, 50, None), ("BUF1M_50_50", "rw", "1M", 16, 2, 0, 50, None),
        ]
        matrix_res = []
        for idx, (n, rw, bs, qd, nj, d, mix, fs) in enumerate(specs, 1):
            show_bar(f"FIO 矩阵 [{idx}/{len(specs)}] 正在测 {n}...", f"FIO Matrix [{idx}/{len(specs)}] {n}...", advance=0)
            matrix_res.append(run_fio_job(n, mfile, msz, rw, bs, qd, nj, rt, d, mix, fs))
            show_bar(f"FIO 矩阵 [{idx}/{len(specs)}] {n} 完成", f"FIO Matrix [{idx}/{len(specs)}] {n} done", advance=1)

    prod_res = None
    if sel["prod"]:
        pspecs = [
            ("OLTP_8K_Q32", "randrw", "8K", 32, 2, 1, 70, None), ("WEB_16K_Q8", "randrw", "16K", 8, 2, 1, 50, None),
            ("WAL_4K_FSYNC1", "write", "4K", 1, 1, 1, None, 1), ("CONG_4K_FSYNC4", "randwrite", "4K", 32, 2, 1, None, 4),
        ]
        prod_res = []
        for idx, (n, rw, bs, qd, nj, d, mix, fs) in enumerate(pspecs, 1):
            show_bar(f"生产模型 [{idx}/{len(pspecs)}] 正在测 {n}...", f"Production [{idx}/{len(pspecs)}] {n}...", advance=0)
            prod_res.append(run_fio_job(n, mfile, msz, rw, bs, qd, nj, rt, d, mix, fs))
            show_bar(f"生产模型 [{idx}/{len(pspecs)}] {n} 完成", f"Production [{idx}/{len(pspecs)}] {n} done", advance=1)

    conc_res = None
    if sel["concurrency"]:
        cspecs = [
            ("PT_SEED_16K_32T",  "randread", "16K",  4, 32, 1, None, None),
            ("PT_HASH_256K_16T", "read",     "256K", 4, 16, 1, None, None),
            ("BACKUP_64K_16T",   "randrw",   "64K",  4, 16, 1, 50,   None),
            ("BURST_4K_32T",     "randrw",   "4K",   1, 32, 1, 70,   None),
        ]
        conc_res = []
        for idx, (n, rw, bs, qd, nj, d, mix, fs) in enumerate(cspecs, 1):
            show_bar(f"小量多并发 [{idx}/{len(cspecs)}] 正在测 {n}...", f"Concurrency [{idx}/{len(cspecs)}] {n}...", advance=0)
            conc_res.append(run_fio_job(n, mfile, msz, rw, bs, qd, nj, rt, d, mix, fs))
            show_bar(f"小量多并发 [{idx}/{len(cspecs)}] {n} 完成", f"Concurrency [{idx}/{len(cspecs)}] {n} done", advance=1)

    try: os.remove(mfile)
    except Exception: pass

    sustained_res = None
    if sel["sustained"]:
        seq_m = round(plan["sustained_seq_sec"] / 60.0, 1)
        mix_m = round(plan["sustained_mix_sec"] / 60.0, 1)
        iostat_log = os.path.join(work_dir, "iostat_raw.log")
        dev_short = os.path.basename(topo["base_dev"])
        io_proc = subprocess.Popen(f"iostat -dxm {shlex.quote(dev_short)} 5 > {shlex.quote(iostat_log)} 2>&1", shell=True, start_new_session=True)
        _ACTIVE_PROCS.append(io_proc)
        try:
            show_bar(
                f"50% 容量持久压测 阶段 A 顺序写 ({plan['stress_file_gb']} GB, {seq_m} 分钟)...",
                f"50% Endurance Phase A Seq Write ({plan['stress_file_gb']} GB, {seq_m} min)...",
                advance=0,
            )
            sw = run_fio_job("SUSTAINED_50PCT_SEQ_W", sfile, plan["stress_file_gb"], "write", "1M", 16, 1, plan["sustained_seq_sec"], 1)
            show_bar("50% 容量持久压测 阶段 A 完成，进入阶段 B 随机混合...", "50% Endurance Phase A done, starting Phase B Mixed...", advance=1)
            ms = run_fio_job("SUSTAINED_50PCT_MIX", sfile, plan["stress_file_gb"], "randrw", "8K", 32, 2, plan["sustained_mix_sec"], 1, 30)
            show_bar("50% 容量持久压测 阶段 B 完成", "50% Endurance Phase B completed", advance=1)
        finally:
            try: os.killpg(os.getpgid(io_proc.pid), signal.SIGKILL)
            except Exception:
                try: io_proc.kill()
                except Exception: pass
            try: io_proc.wait(timeout=3)
            except Exception: pass
            if io_proc in _ACTIVE_PROCS: _ACTIVE_PROCS.remove(io_proc)
            try: os.remove(sfile)
            except Exception: pass
        sustained_res = {"seq_write": sw, "rand_mixed": ms, "timeline": parse_iostat_minutes(iostat_log, dev_short, plan["sustained_seq_sec"] // 60)}

    net_res = None
    if sel["network"]:
        show_bar("正在测试全球 8 大单播节点延迟与大文件下行...", "Running 8-hub global TCP latency & bulk download...", advance=0)
        net_res = run_global_network_tests()
        show_bar("国际互联与大文件下行测试完成", "Global connectivity & download tests completed", advance=1)

    ipq_res = None
    if sel["ip_quality"]:
        show_bar("正在探测 IP 质量、25 端口与 10 大平台可达性...", "Probing IP quality, Port 25 & 10-platform reachability...", advance=0)
        ipq_res = run_ip_quality_tests()
        show_bar("IP 质量与被拒访问概率评估完成", "IP quality & denial probability completed", advance=1)

    meta_res, life_res = None, None
    if sel["meta"]:
        show_bar("正在运行 10,000 小文件元数据与 SMART/Ext4 寿命读取...", "Running 10,000-file metadata & SMART/Ext4 lifetime...", advance=0)
        meta_res = run_metadata_bench(work_dir)
        life_res = collect_poweron_lifetime(topo["mount_dev"], topo["base_dev"])
        show_bar("元数据与介质寿命检测完成", "Metadata & lifetime diagnostics completed", advance=1)

    thorough_cleanup(work_dir, args.target, do_trim=True)
    end_emo = random.choice(end_kaomojis)
    show_bar("全部测试已完成，环境已彻底清理干净！", "All tests completed & environment thoroughly cleaned!", advance=1, suffix=end_emo)

    data = {
        "version": VERSION, "lang": lang, "site_url": args.site_url,
        "report_time": start_str, "elapsed_min": round((time.time() - t_start) / 60.0, 2),
        "selected": sel, "plan": plan, "topology": topo,
        "lifetime": life_res, "ioping": ioping_res, "matrix": matrix_res,
        "production": prod_res, "concurrency": conc_res, "sustained": sustained_res,
        "network": net_res, "ip_quality": ipq_res, "metadata": meta_res,
    }

    if args.upload_url:
        try:
            req = urllib.request.Request(
                args.upload_url, data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "DiskQuality-CLI/1.0.5"}, method="POST",
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                rj = json.loads(resp.read().decode("utf-8"))
                if rj.get("url"): data["report_url"] = rj["url"]
        except Exception as e:
            print(f"{C_YEL}[WARN] Upload failed: {e}{C_RST}", flush=True)

    print("\n" + render_p2_ansi(data, lang=lang, site_url=args.site_url))
    if data.get("report_url"):
        print(f"\n{C_GRN}{L['done_msg']}{C_RST}\n{C_B}{C_CYN}{data['report_url']}{C_RST}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="zh", choices=["zh", "en"])
    ap.add_argument("--target", default="/")
    ap.add_argument("--minutes", type=float, default=20.0)
    for mod in ("ioping", "matrix", "prod", "concurrency", "sustained", "network", "ip_quality", "meta"):
        ap.add_argument(f"--{mod}", default="y")
    ap.add_argument("--site-url", default=DEFAULT_SITE_URL)
    ap.add_argument("--upload-url", default="")
    run_benchmark_cli(ap.parse_args())


if __name__ == "__main__":
    main()
