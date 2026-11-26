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

VERSION = "v1.0.8 (2026.11.26)"
DEFAULT_SITE_URL = os.environ.get("DQ_SITE_URL", "https://test.sakurado.top")

TOOL_CREDITS = [
    ("fio", "https://github.com/axboe/fio"),
    ("ioping", "https://github.com/koct9i/ioping"),
    ("Geekbench 5/6", "https://www.geekbench.com"),
    ("sysstat / iostat", "https://github.com/sysstat/sysstat"),
    ("smartmontools", "https://www.smartmontools.org"),
    ("e2fsprogs / tune2fs", "https://e2fsprogs.sourceforge.net"),
    ("curl", "https://curl.se"),
    ("IPPure", "https://ippure.com"),
    ("IP2Location", "https://www.ip2location.io"),
    ("ping0.cc", "https://ping0.cc"),
    ("ProxyCheck / Scamalytics", "https://proxycheck.io"),
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
        "k_spec": "压测文件规格：          ", "spec_val": "50% 自适应压测文件 = {sgb} GB (短矩阵 {mgb} GB, {ioe} direct={dir})",
        "k_gb": "CPU 跑分 ({ver})：   ", "k_gb_skip": "CPU 跑分 (Geekbench)：  ", "k_gb_url": "跑分详情：              ",
        "gb_sc": "单核", "gb_mc": "多核",
        "k_oscore": "超售指数 (越低越好)：   ",
        "os_sub": "基准: 独服 {media} (0=独服水平, 100=极重超售) · 吞吐落差 {d_bw} | 4K落差 {d_4k} | 尾延迟 {d_lat} | 缓外掉速 {d_drop}",
        "os_t0": "极低/接近独服", "os_t1": "轻度共享", "os_t2": "中度超售", "os_t3": "重度超售",
        "k_dscore": "硬盘综合评分 (越高越好)：",
        "ds_sub": "顺序 {s_seq} | 4K随机 {s_4k} | 延迟 {s_lat} | 高并发 {s_conc} | 持久稳态 {s_sust} | 元数据 {s_meta}",
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
        "k_asn": "ASN / 归属地：          ", "k_ipattr": "IP 属性与类型：         ",
        "k_ping0": "ping0.cc 归属校验：     ",
        "k_risk": "综合风控值 (越低越净)： ",
        "k_risk_src": "风控分项构成 (各API)：  ",
        "k_dnsbl": "黑名单 (DNSBL 3库)：    ",
        "k_p25": "25 端口出站：           ", "p25_ok": "开放", "p25_no": "阻断/超时",
        "k_deny": "主流平台被拒概率：      ",
        "risk_low": "极低/低风控", "risk_mid": "中等风控", "risk_high": "高风控",
        "st_ok": "放行", "st_blk": "拦截/拒访",
        "grp_hw": "── [硬件与系统拓扑] ──", "grp_eval": "── [综合量化评估] ──",
        "grp_seq": "── [顺序大块吞吐 · Sequential] ──", "grp_rnd": "── [随机小块 IOPS · Random 4K/8K/16K] ──",
        "grp_ip_base": "── [IP 基础画像] ──", "grp_ip_risk": "── [多源 API 风控测算与构成] ──", "grp_ip_plat": "── [主流平台可达性] ──",
        "reg_ap": "亚太", "reg_us": "美洲", "reg_eu": "欧洲",
        "s9": "九、文件系统元数据 (10,000 × 4KB) 与通电寿命溯源",
        "k_meta": "元数据吞吐：            ", "meta_val": "创建 {c} f/s | Stat {s} f/s | 读 {r} f/s | 删 {d} f/s",
        "k_smart": "SMART 寄存器：          ", "smart_poh": " (通电 {h} h)",
        "k_ext4": "Ext4 超级块记账：       ", "ext4_val": "创建于 {cr} | 挂载次数 {mc} | 累计写入 {lw}",
        "k_url": "在线结果页：            ",
        "skip_txt": "？？？",
        "ns_cmd": "一键复测命令", "ns_url": "在线报告",
        "done_msg": "测试完成，点击查看你的在线测评报告：",
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
        "k_spec": "Benchmark File Size:    ", "spec_val": "50% Adaptive Stress File = {sgb} GB (Matrix {mgb} GB, {ioe} direct={dir})",
        "k_gb": "CPU Score ({ver}): ", "k_gb_skip": "CPU Score (Geekbench):  ", "k_gb_url": "Score Details:          ",
        "gb_sc": "Single-Core", "gb_mc": "Multi-Core",
        "k_oscore": "Oversell Index (Lower↓):",
        "os_sub": "Ref: Dedicated {media} (0=Dedicated, 100=Severe) · BW {d_bw} | 4K {d_4k} | TailLat {d_lat} | Drop {d_drop}",
        "os_t0": "Minimal / Near-Dedicated", "os_t1": "Light Sharing", "os_t2": "Moderate Overselling", "os_t3": "Heavy Overselling",
        "k_dscore": "Disk Score (Higher↑):   ",
        "ds_sub": "Seq {s_seq} | 4K {s_4k} | Lat {s_lat} | Conc {s_conc} | Sust {s_sust} | Meta {s_meta}",
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
        "k_asn": "ASN / Location:         ", "k_ipattr": "IP Type / Flags:        ",
        "k_ping0": "ping0.cc Geo Check:     ",
        "k_risk": "Composite Risk (Lower↓):",
        "k_risk_src": "Risk API Breakdown:     ",
        "k_dnsbl": "Blacklist (3 DNSBLs):   ",
        "k_p25": "Port 25 Outbound:       ", "p25_ok": "OPEN", "p25_no": "BLOCKED",
        "k_deny": "Platform Denial Prob:   ",
        "risk_low": "Low Risk", "risk_mid": "Medium Risk", "risk_high": "High Risk",
        "st_ok": "PASS", "st_blk": "DENIED",
        "grp_hw": "── [Hardware & Topology] ──", "grp_eval": "── [Quantifiable Scores] ──",
        "grp_seq": "── [Sequential Throughput] ──", "grp_rnd": "── [Random 4K/8K/16K IOPS] ──",
        "grp_ip_base": "── [IP Identity & Type] ──", "grp_ip_risk": "── [Multi-API Risk Score & Breakdown] ──", "grp_ip_plat": "── [Platform Reachability] ──",
        "reg_ap": "APAC", "reg_us": "US", "reg_eu": "EU",
        "s9": "9. Filesystem Metadata (10,000 x 4KB) & Lifetime Diagnostics",
        "k_meta": "Metadata Rate:          ", "meta_val": "Create {c} f/s | Stat {s} f/s | Read {r} f/s | Unlink {d} f/s",
        "k_smart": "SMART Status:           ", "smart_poh": " (Power-On {h} h)",
        "k_ext4": "Ext4 Superblock:        ", "ext4_val": "Created {cr} | Mounts {mc} | Lifetime Writes {lw}",
        "k_url": "Online Report:          ",
        "skip_txt": "???",
        "ns_cmd": "One-Click Command", "ns_url": "Online Report",
        "done_msg": "Benchmark complete! View your online report:",
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


def detect_platform_profile(virt_raw, cpu_model, cpu_cores, mem_mb):
    """Auto-classify server platform: dedicated (Bare-Metal), vds, container (LXC/OpenVZ/Docker), or vps."""
    v = (virt_raw or "unknown").strip().lower()
    if os.path.exists("/.dockerenv"):
        return "container", "docker"
    if os.path.exists("/proc/vz") and not os.path.exists("/proc/bc"):
        return "container", "openvz"
    if any(k in v for k in ("lxc", "openvz", "docker", "podman", "systemd-nspawn", "wsl", "vz")):
        return "container", v
    _, hv_flag, _ = run_cmd("grep -q ' hypervisor' /proc/cpuinfo 2>/dev/null && echo 1 || echo 0")
    if v in ("none", "", "unknown") and hv_flag != "1":
        return "dedicated", "bare-metal"
    # Distinguish VDS (dedicated CPU passthrough / high-spec physical model) from standard shared VPS
    cm = (cpu_model or "").lower()
    is_passthrough = bool(cm) and ("qemu" not in cm) and ("virtual" not in cm) and ("common kvm" not in cm)
    if v in ("kvm", "xen", "vmware", "microsoft", "bhyve", "qemu") and is_passthrough and int(cpu_cores or 1) >= 2 and int(mem_mb or 0) >= 3500:
        return "vds", f"{v} (VDS)"
    return "vps", v or "unknown"


def probe_fio_capabilities(work_dir):
    """Auto-probe FIO ioengine & O_DIRECT support for LXC/OpenVZ/ZFS/OverlayFS/Dedicated compatibility."""
    test_f = os.path.join(work_dir, ".probe.bin")
    q_f = shlex.quote(test_f)
    for ioe, direct in (("libaio", 1), ("psync", 1), ("psync", 0)):
        rc, _, _ = run_cmd(f"fio --name=probe --filename={q_f} --size=1M --ioengine={ioe} --direct={direct} --rw=write --bs=4k --runtime=1 --output-format=json", timeout=15)
        try: os.remove(test_f)
        except Exception: pass
        if rc == 0:
            return ioe, direct
    return "psync", 0


def calc_overselling_index(topo, matrix_res, prod_res, sustained_res):
    """
    Objective 0-100 Overselling Index (Lower is better; 0 = Dedicated Server reference baseline).
    Anchored to standard Dedicated Server NVMe / SATA SSD / Enterprise HDD baselines.
    """
    rota = str(topo.get("rotational", "0")).strip()
    bdev = (topo.get("base_dev", "") + " " + topo.get("disk_model", "")).lower()
    if rota == "1":
        media = "HDD"
        ref_bw, ref_4k, ref_p99 = 160.0, 180.0, 35.0
    elif "nvme" in bdev:
        media = "NVMe"
        ref_bw, ref_4k, ref_p99 = 1500.0, 60000.0, 2.0
    else:
        media = "SSD"
        ref_bw, ref_4k, ref_p99 = 450.0, 25000.0, 4.0

    # Extract measured metrics
    burst_seq_bw, rnd4k_iops, p99_vals = None, None, []
    if matrix_res:
        by_name = {r.get("name"): r for r in matrix_res if not r.get("error")}
        for k in ("SEQ1M_W_Q32", "SEQ1M_R_Q32", "SEQ1M_W_Q1"):
            if k in by_name:
                val = max(by_name[k].get("w_bw_mbs", 0), by_name[k].get("r_bw_mbs", 0))
                if val > 0:
                    burst_seq_bw = max(burst_seq_bw or 0.0, val)
        for k in ("RND4K_W_Q64", "RND4K_R_Q64", "RND4K_W_Q16", "RND4K_R_Q16"):
            if k in by_name:
                iv = max(by_name[k].get("w_iops", 0), by_name[k].get("r_iops", 0))
                if iv > 0:
                    rnd4k_iops = max(rnd4k_iops or 0.0, iv)
        for k in ("RND4K_W_Q16", "RND4K_R_Q16", "RND8K_70_30"):
            if k in by_name:
                pv = max(by_name[k].get("w_p99_ms", 0), by_name[k].get("r_p99_ms", 0))
                if pv > 0: p99_vals.append(pv)

    if prod_res:
        for r in prod_res:
            if not r.get("error"):
                pv = max(r.get("w_p99_ms", 0), r.get("r_p99_ms", 0))
                if pv > 0: p99_vals.append(pv)

    sust_bw = None
    if sustained_res and isinstance(sustained_res.get("seq_write"), dict) and not sustained_res["seq_write"].get("error"):
        sust_bw = sustained_res["seq_write"].get("w_bw_mbs", 0) or None

    parts = []
    d_bw = d_4k = d_lat = d_drop = "N/A"

    if burst_seq_bw is not None:
        s_bw = max(0.0, min(100.0, (1.0 - burst_seq_bw / ref_bw) * 100.0))
        parts.append((0.30, s_bw))
        d_bw = f"{s_bw:.0f}"
    if rnd4k_iops is not None:
        s_4k = max(0.0, min(100.0, (1.0 - rnd4k_iops / ref_4k) * 100.0))
        parts.append((0.25, s_4k))
        d_4k = f"{s_4k:.0f}"
    if p99_vals:
        avg_p99 = sum(p99_vals) / len(p99_vals)
        s_lat = max(0.0, min(100.0, ((avg_p99 - ref_p99) / (ref_p99 * 8.0)) * 100.0))
        parts.append((0.20, s_lat))
        d_lat = f"{s_lat:.0f}"
    if sust_bw is not None:
        base_cmp = burst_seq_bw if (burst_seq_bw and burst_seq_bw > 0) else ref_bw
        s_drop = max(0.0, min(100.0, (1.0 - sust_bw / max(1.0, base_cmp)) * 100.0))
        parts.append((0.25, s_drop))
        d_drop = f"{s_drop:.0f}"

    if not parts or (not matrix_res and not sustained_res):
        return None

    w_sum = sum(w for w, _ in parts)
    score = round(sum(w * v for w, v in parts) / w_sum, 1)
    tier = "t0" if score <= 15.0 else ("t1" if score <= 35.0 else ("t2" if score <= 60.0 else "t3"))
    return {
        "score": score, "tier": tier, "media": media,
        "d_bw": d_bw, "d_4k": d_4k, "d_lat": d_lat, "d_drop": d_drop,
    }


def calc_disk_score(topo, ioping_res, matrix_res, prod_res, conc_res, sustained_res, meta_res):
    """
    Objective 0-100 comprehensive Disk Quality Score (Higher is better) across all executed dimensions:
    Sequential throughput (20%), Random 4K IOPS (25%), Latency & fsync (15%),
    High-Concurrency PT/Backup (15%), 50% Sustained Endurance (15%), Metadata (10%).
    """
    parts = []
    subs = {"s_seq": "-", "s_4k": "-", "s_lat": "-", "s_conc": "-", "s_sust": "-", "s_meta": "-"}

    if matrix_res:
        by_n = {r.get("name"): r for r in matrix_res if not r.get("error")}
        seq_bws = [max(by_n[k].get("r_bw_mbs", 0), by_n[k].get("w_bw_mbs", 0)) for k in ("SEQ1M_R_Q32", "SEQ1M_W_Q32", "SEQ1M_W_Q1") if k in by_n]
        if seq_bws:
            avg_seq = sum(seq_bws) / len(seq_bws)
            s_seq = min(100.0, (avg_seq / 2000.0) ** 0.55 * 100.0)
            parts.append((0.20, s_seq)); subs["s_seq"] = f"{s_seq:.0f}"
        iops_4k = [max(by_n[k].get("r_iops", 0), by_n[k].get("w_iops", 0)) for k in ("RND4K_R_Q64", "RND4K_W_Q64", "RND4K_R_Q16", "RND4K_W_Q16") if k in by_n]
        if iops_4k:
            avg_4k = sum(iops_4k) / len(iops_4k)
            s_4k = min(100.0, (avg_4k / 80000.0) ** 0.42 * 100.0)
            parts.append((0.25, s_4k)); subs["s_4k"] = f"{s_4k:.0f}"

    lat_vals = []
    if matrix_res:
        for r in matrix_res:
            if not r.get("error") and r.get("name") in ("RND4K_R_Q16", "RND4K_W_Q16", "RND8K_70_30"):
                pv = max(r.get("r_p99_ms", 0), r.get("w_p99_ms", 0))
                if pv > 0: lat_vals.append(pv)
    if prod_res:
        for r in prod_res:
            if not r.get("error"):
                pv = max(r.get("r_p99_ms", 0), r.get("w_p99_ms", 0))
                if pv > 0: lat_vals.append(pv)
    if lat_vals:
        avg_lat = sum(lat_vals) / len(lat_vals)
        s_lat = max(5.0, min(100.0, 100.0 / (1.0 + (avg_lat / 15.0) ** 0.85)))
        parts.append((0.15, s_lat)); subs["s_lat"] = f"{s_lat:.0f}"
    elif ioping_res and ioping_res.get("direct_seek", "N/A") != "N/A":
        m_u = re.search(r"([0-9.]+)\s*(us|ms)", ioping_res["direct_seek"])
        if m_u:
            ms_v = float(m_u.group(1)) / (1000.0 if m_u.group(2) == "us" else 1.0)
            s_lat = max(5.0, min(100.0, 100.0 / (1.0 + (ms_v / 3.0) ** 0.75)))
            parts.append((0.15, s_lat)); subs["s_lat"] = f"{s_lat:.0f}"

    if conc_res:
        cbws = [r.get("r_bw_mbs", 0) + r.get("w_bw_mbs", 0) for r in conc_res if not r.get("error")]
        if cbws:
            avg_c = sum(cbws) / len(cbws)
            s_conc = min(100.0, (avg_c / 800.0) ** 0.50 * 100.0)
            parts.append((0.15, s_conc)); subs["s_conc"] = f"{s_conc:.0f}"

    if sustained_res and isinstance(sustained_res.get("seq_write"), dict) and not sustained_res["seq_write"].get("error"):
        sw_bw = sustained_res["seq_write"].get("w_bw_mbs", 0)
        s_sust = min(100.0, (sw_bw / 1000.0) ** 0.52 * 100.0)
        parts.append((0.15, s_sust)); subs["s_sust"] = f"{s_sust:.0f}"

    if meta_res and meta_res.get("create_fps", 0) > 0:
        avg_m = (meta_res.get("create_fps", 0) + meta_res.get("read_fps", 0) + meta_res.get("delete_fps", 0)) / 3.0
        s_meta = min(100.0, (avg_m / 60000.0) ** 0.45 * 100.0)
        parts.append((0.10, s_meta)); subs["s_meta"] = f"{s_meta:.0f}"

    if not parts or (not matrix_res and not sustained_res):
        return None

    score = round(sum(w * v for w, v in parts) / sum(w for w, _ in parts), 1)
    grade = "S+" if score >= 90 else ("S" if score >= 80 else ("A" if score >= 70 else ("B" if score >= 55 else ("C" if score >= 40 else "D"))))
    return {"score": score, "grade": grade, **subs}


def collect_system_topology(target_dir="/", forced_profile="auto"):
    _, virt_raw, _ = run_cmd("systemd-detect-virt 2>/dev/null || echo unknown")
    _, os_rel, _ = run_cmd("grep '^PRETTY_NAME=' /etc/os-release 2>/dev/null | cut -d= -f2- | tr -d '\"'")
    _, kernel, _ = run_cmd("uname -r")
    _, arch, _ = run_cmd("uname -m")
    _, loadavg, _ = run_cmd("awk '{print $1\", \"$2\", \"$3}' /proc/loadavg")
    _, cpu_model, _ = run_cmd("lscpu 2>/dev/null | awk -F: '/Model name/{gsub(/^[ \\t]+/,\"\",$2); print $2; exit}' || awk -F: '/model name|Hardware/{gsub(/^[ \\t]+/,\"\",$2); print $2; exit}' /proc/cpuinfo")
    _, cpu_cores, _ = run_cmd("nproc 2>/dev/null || grep -c ^processor /proc/cpuinfo")
    _, cpu_mhz, _ = run_cmd("awk -F: '/cpu MHz/{gsub(/^[ \\t]+/,\"\",$2); printf \"%.3fMHz\", $2; exit}' /proc/cpuinfo")
    _, mem_total_mb, _ = run_cmd("free -m | awk '/^Mem:/{print $2}'")
    _, mem_line, _ = run_cmd("free -m | awk '/^Mem:/{printf \"%dM (Used %dM / Avail %dM)\", $2, $3, $7}'")
    _, swap_line, _ = run_cmd("free -m | awk '/^Swap:/{if($2>0) printf \"%dM (Used %dM)\", $2, $3; else print \"0M\"}'")
    _, pub_ip, _ = run_cmd("curl -s4m 4 https://api.ipify.org 2>/dev/null || curl -s6m 4 https://api64.ipify.org 2>/dev/null || hostname -I | awk '{print $1}'")
    raw_ip = pub_ip.strip() if pub_ip else ""
    if re.match(r'^\d+\.\d+\.\d+\.\d+$', raw_ip):
        masked_ip = re.sub(r'^(\d+\.\d+)\.\d+\.\d+$', r'\1.*.*', raw_ip)
    elif ":" in raw_ip:
        masked_ip = re.sub(r'^([0-9a-fA-F]*:[0-9a-fA-F]*):.*$', r'\1:*:*', raw_ip)
    else:
        masked_ip = "Unknown"

    profile, virt_disp = detect_platform_profile(virt_raw, cpu_model, cpu_cores, mem_total_mb or 0)
    if forced_profile in ("dedicated", "vds", "vps", "container"):
        profile = forced_profile

    q_target = shlex.quote(target_dir)
    _, dev_src, _ = run_cmd(f"findmnt -n -o SOURCE {q_target} 2>/dev/null || df -P {q_target} | awk 'NR==2{{print $1}}'")
    _, fs_type, _ = run_cmd(f"findmnt -n -o FSTYPE {q_target} 2>/dev/null || df -T {q_target} | awk 'NR==2{{print $2}}'")
    _, base_dev, _ = run_cmd(f"lsblk -no PKNAME {shlex.quote(dev_src)} 2>/dev/null | head -n1")
    if not base_dev and dev_src.startswith("/dev/"):
        bn = os.path.basename(dev_src)
        if re.match(r'^(nvme\d+n\d+|mmcblk\d+|loop\d+)p\d+$', bn):
            base_dev = re.sub(r'p\d+$', '', bn)
        else:
            base_dev = bn.rstrip("0123456789")
    sb = f"/sys/block/{base_dev}" if base_dev and os.path.exists(f"/sys/block/{base_dev}") else ""
    if sb:
        _, model, _ = run_cmd(f"cat {sb}/device/model 2>/dev/null || echo 'Physical/Virtual Disk'")
        _, rota, _ = run_cmd(f"cat {sb}/queue/rotational 2>/dev/null || echo '?'")
        _, sched, _ = run_cmd(f"cat {sb}/queue/scheduler 2>/dev/null || echo '?'")
        _, ra_kb, _ = run_cmd(f"cat {sb}/queue/read_ahead_kb 2>/dev/null || echo '?'")
        _, wcache, _ = run_cmd(f"cat {sb}/queue/write_cache 2>/dev/null || echo '?'")
        _, log_s, _ = run_cmd(f"cat {sb}/queue/logical_block_size 2>/dev/null || echo '512'")
        _, phy_s, _ = run_cmd(f"cat {sb}/queue/physical_block_size 2>/dev/null || echo '512'")
        _, disc, _ = run_cmd(f"cat {sb}/queue/discard_granularity 2>/dev/null || echo '0'")
    else:
        model, rota, sched, ra_kb, wcache, log_s, phy_s, disc = (
            f"Container/Virtual ({fs_type or 'fs'})", "?", "host-managed", "?", "?", "512", "512", "0"
        )

    return {
        "masked_ip": masked_ip, "virt": virt_disp, "profile": profile, "arch": arch,
        "os": f"{os_rel} {kernel}".strip(), "loadavg": loadavg,
        "cpu_model": cpu_model or f"{arch} CPU", "cpu_cores": cpu_cores or "1", "cpu_mhz": cpu_mhz or "N/A",
        "mem": mem_line, "swap": swap_line, "mount_dev": dev_src or "unknown",
        "base_dev": f"/dev/{base_dev}" if base_dev else "virtual", "has_block_dev": bool(sb),
        "fs_type": fs_type or "unknown", "disk_model": model.strip(), "rotational": rota, "scheduler": sched,
        "read_ahead_kb": ra_kb, "write_cache": wcache, "sector": f"{log_s}B / {phy_s}B",
        "trim_supported": int(disc or 0) > 0,
    }


def collect_poweron_lifetime(mount_dev, base_dev, fs_type="ext4"):
    smart_avail, poh, smart_status = False, None, "Unavailable (Virtual/Container/Shielded)"
    if base_dev and base_dev.startswith("/dev/") and os.path.exists(base_dev):
        _, smart_out, _ = run_cmd(f"smartctl -a {shlex.quote(base_dev)} 2>&1 | head -n 60")
        if smart_out and "Unavailable" not in smart_out and "failed" not in smart_out.lower() and "Permission denied" not in smart_out:
            smart_avail = True
            smart_status = "Available"
            m = re.search(r'(?:Power_On_Hours|Power On Hours).*?([\d,]+)\s*$', smart_out, re.M)
            if m: poh = m.group(1).replace(",", "")
    cr_s = mc_s = lw_s = f"N/A ({fs_type})"
    if (fs_type or "").startswith("ext") and mount_dev.startswith("/dev/"):
        _, t2fs, _ = run_cmd(f"tune2fs -l {shlex.quote(mount_dev)} 2>/dev/null")
        cr = re.search(r'Filesystem created:\s*(.+)', t2fs)
        mc = re.search(r'Mount count:\s*(\d+)', t2fs)
        lw = re.search(r'Lifetime writes:\s*(.+)', t2fs)
        cr_s = cr.group(1).strip() if cr else "N/A"
        mc_s = mc.group(1).strip() if mc else "N/A"
        lw_s = lw.group(1).strip() if lw else "N/A"
    return {
        "smart_available": smart_avail, "smart_power_on_hours": poh,
        "smart_raw_status": smart_status,
        "fs_created": cr_s, "mount_count": mc_s, "lifetime_writes": lw_s,
    }


def run_geekbench(mode, work_dir):
    """Run full Geekbench 5 or Geekbench 6 CPU benchmark (Single-Core & Multi-Core) inside work_dir."""
    mode = (mode or "skip").lower()
    if mode not in ("gb5", "gb6"):
        return None
    _, arch, _ = run_cmd("uname -m")
    if arch not in ("x86_64", "amd64", "aarch64", "arm64"):
        ver_label = "Geekbench 5" if mode == "gb5" else "Geekbench 6"
        return {"version": ver_label, "single_core": f"Unsupported({arch})", "multi_core": f"Unsupported({arch})", "url": ""}
    is_arm = arch in ("aarch64", "arm64")
    if mode == "gb5":
        ver_label = "Geekbench 5"
        url = (
            "https://cdn.geekbench.com/Geekbench-5.5.1-LinuxARMPreview.tar.gz"
            if is_arm else
            "https://cdn.geekbench.com/Geekbench-5.5.1-Linux.tar.gz"
        )
        bin_name = "geekbench5"
    else:
        ver_label = "Geekbench 6"
        url = (
            "https://cdn.geekbench.com/Geekbench-6.3.0-LinuxARMPreview.tar.gz"
            if is_arm else
            "https://cdn.geekbench.com/Geekbench-6.3.0-Linux.tar.gz"
        )
        bin_name = "geekbench6"

    gb_dir = os.path.join(work_dir, f"_{mode}")
    os.makedirs(gb_dir, exist_ok=True)
    tgz = os.path.join(gb_dir, "gb.tar.gz")
    q_tgz, q_dir = shlex.quote(tgz), shlex.quote(gb_dir)

    rc, _, err = run_cmd(f"curl -fsSLm 120 {shlex.quote(url)} -o {q_tgz} && tar -xzf {q_tgz} -C {q_dir} --strip-components=1", timeout=150)
    if rc != 0:
        return {"version": ver_label, "single_core": "N/A", "multi_core": "N/A", "url": "", "error": "download_failed"}

    bin_path = os.path.join(gb_dir, bin_name)
    if not os.path.exists(bin_path):
        # Fallback search inside extracted dir
        for root_d, _, files in os.walk(gb_dir):
            if bin_name in files:
                bin_path = os.path.join(root_d, bin_name)
                break
    if not os.path.exists(bin_path):
        return {"version": ver_label, "single_core": "N/A", "multi_core": "N/A", "url": "", "error": "binary_missing"}

    rc, out, err = run_cmd(f"chmod +x {shlex.quote(bin_path)} && {shlex.quote(bin_path)} --upload 2>&1", timeout=600)
    combined = (out or "") + "\n" + (err or "")
    m_url = re.search(r"https://browser\.geekbench\.com/v[56]/cpu/\d+", combined)
    res_url = m_url.group(0) if m_url else ""

    sc, mc = "N/A", "N/A"
    # Try parsing directly from CLI output first
    m_sc = re.search(r"Single-Core Score\s+(\d+)", combined, re.I)
    m_mc = re.search(r"Multi-Core Score\s+(\d+)", combined, re.I)
    if m_sc: sc = m_sc.group(1)
    if m_mc: mc = m_mc.group(1)

    # If CLI output only gave the upload URL (standard for Geekbench 5/6 free CLI), fetch official result page
    if (sc == "N/A" or mc == "N/A") and res_url:
        try:
            req = urllib.request.Request(res_url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                page = resp.read().decode("utf-8", errors="ignore")
            scores = re.findall(r"class=['\"][^'\"]*\bscore\b[^'\"]*['\"][^>]*>\s*(\d+)\s*<", page, re.S | re.I)
            if len(scores) >= 2:
                sc, mc = scores[0], scores[1]
            else:
                m1 = re.search(r"Single-Core Score.*?(\d{2,6})", page, re.S | re.I)
                m2 = re.search(r"Multi-Core Score.*?(\d{2,6})", page, re.S | re.I)
                if m1: sc = m1.group(1)
                if m2: mc = m2.group(1)
        except Exception:
            pass

    shutil.rmtree(gb_dir, ignore_errors=True)
    return {"version": ver_label, "single_core": sc, "multi_core": mc, "url": res_url}


def run_ioping_tests(work_dir):
    res = {}
    q_dir = shlex.quote(work_dir)
    for key, flags_list in [
        ("direct_seek", ["-D -c 20 -i 0.05", "-c 20 -i 0.05"]),
        ("cached_read", ["-C -c 20 -i 0.05"]),
        ("sync_write",  ["-D -S -W -c 20 -i 0.05", "-S -W -c 20 -i 0.05"]),
    ]:
        val = "N/A"
        for flags in flags_list:
            _, out, _ = run_cmd(f"ioping {flags} {q_dir} 2>&1", timeout=60)
            m = re.search(r'min/avg/max/mdev\s*=\s*([^\n]+)', out)
            if m:
                val = m.group(1).strip()
                break
        res[key] = val
    return res


def run_fio_job(name, filepath, size_gb, rw, bs, iodepth, numjobs, runtime, direct=1, rwmixread=None, fsync=None, ioengine="libaio"):
    cmd = (
        f"fio --name={shlex.quote(name)} --filename={shlex.quote(filepath)} --size={int(size_gb * 1024)}M "
        f"--ioengine={shlex.quote(ioengine)} --direct={direct} --rw={rw} --bs={bs} "
        f"--iodepth={iodepth} --numjobs={numjobs} --runtime={runtime} --time_based "
        f"--group_reporting --output-format=json"
    )
    if rwmixread is not None: cmd += f" --rwmixread={rwmixread}"
    if fsync is not None: cmd += f" --fsync={fsync}"
    rc, out, _ = run_cmd(cmd, timeout=runtime + 120)
    if rc != 0 or not out: return {"name": name, "error": True}
    try:
        s_idx, e_idx = out.find("{"), out.rfind("}")
        if s_idx < 0 or e_idx <= s_idx:
            return {"name": name, "error": True}
        j = json.loads(out[s_idx:e_idx + 1])["jobs"][0]
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
    """Test TCP RTT + packet loss to 8 global hubs and bulk CDN download throughput (IPv4/IPv6 safe)."""
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
        rc, out, _ = run_cmd(f"curl -sS -L -m 15 -o /dev/null -w '%{{speed_download}}' {shlex.quote(url)}", timeout=20)
        try:
            mbs = round(float(out) / (1024 ** 2), 2)
            downloads.append({"name": name, "mbs": mbs, "mbps": round(mbs * 8, 1)})
        except Exception:
            downloads.append({"name": name, "mbs": 0.0, "mbps": 0.0})
    return {"hubs": hubs, "downloads": downloads}


def _http_get_text(url, timeout=7, ua="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0"):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": ua})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""


def run_ip_quality_tests():
    """
    Multi-source IP quality & composite risk evaluation:
    Queries IPPure, IP2Location.io, ping0.cc, ProxyCheck.io, Scamalytics, ip-api.com, ipinfo.io,
    3-zone DNSBL, 10 platform reachability probes, and SMTP Port 25. Never persists raw IP.
    """
    meta = {"asn": "Unknown", "org": "Unknown", "location": "Unknown", "hosting": "Unknown", "native_type": "Unknown", "ping0_geo": "N/A"}
    raw_ip = ""
    risk_sources = []  # Each item: {"api": str, "raw": str, "score": int (0-100), "weight": float}

    # 1. IPPure (my.ippure.com/v1/info) — direct fraudScore (0-100) + isResidential + isBroadcast
    ipp_txt = _http_get_text("https://my.ippure.com/v1/info", timeout=7)
    ipp_cc = ""
    if ipp_txt:
        try:
            d = json.loads(ipp_txt)
            raw_ip = str(d.get("ip", "")).strip() or raw_ip
            if d.get("asn"): meta["asn"] = f"AS{d['asn']}"
            if d.get("asOrganization"): meta["org"] = str(d["asOrganization"])
            ipp_cc = str(d.get("countryCode", "")).upper()
            loc_s = ", ".join(x for x in [d.get("countryCode", ""), d.get("region", ""), d.get("city", "")] if x)
            if loc_s: meta["location"] = loc_s
            is_res = bool(d.get("isResidential", False))
            is_bc = bool(d.get("isBroadcast", False))
            meta["native_type"] = ("住宅/Residential" if is_res else "机房/Datacenter") + " · " + ("广播/Broadcast" if is_bc else "原生/Native")
            if "fraudScore" in d and d["fraudScore"] is not None:
                fs = max(0, min(100, int(d["fraudScore"])))
                risk_sources.append({"api": "IPPure", "raw": f"{fs} ({'Res' if is_res else 'DC'}/{'BC' if is_bc else 'Native'})", "score": fs, "weight": 0.25})
        except Exception:
            pass

    # Fallback ASN/IP from ipinfo if IPPure missed
    if not raw_ip or meta["asn"] == "Unknown":
        ipi_txt = _http_get_text("https://ipinfo.io/json", timeout=6, ua="curl/8.0")
        if ipi_txt:
            try:
                d = json.loads(ipi_txt)
                raw_ip = str(d.get("ip", "")).strip() or raw_ip
                org_s = d.get("org", "")
                parts = org_s.split(" ", 1)
                if meta["asn"] == "Unknown" and parts: meta["asn"] = parts[0]
                if meta["org"] == "Unknown" and len(parts) > 1: meta["org"] = parts[1]
                if meta["location"] == "Unknown":
                    meta["location"] = ", ".join(x for x in [d.get("country", ""), d.get("region", ""), d.get("city", "")] if x)
            except Exception:
                pass

    # 2. IP2Location.io (api.ip2location.io) — proxy detection & country verification
    ip2_txt = _http_get_text("https://api.ip2location.io/", timeout=7)
    ip2_cc = ""
    if ip2_txt:
        try:
            d = json.loads(ip2_txt)
            raw_ip = str(d.get("ip", "")).strip() or raw_ip
            ip2_cc = str(d.get("country_code", "")).upper()
            is_px = bool(d.get("is_proxy", False))
            sc2 = 75 if is_px else 0
            risk_sources.append({"api": "IP2Location", "raw": "Proxy" if is_px else "Clean(0)", "score": sc2, "weight": 0.15})
        except Exception:
            pass

    # 3. ping0.cc (geo/jsonp/check) — Chinese geo/ASN check & cross-database consistency
    p0_txt = _http_get_text("https://ping0.cc/geo/jsonp/check", timeout=7, ua="curl/8.0")
    if p0_txt:
        m = re.findall(r'"([^"]*)"', p0_txt)
        if len(m) >= 5:
            p0_ip, p0_geo, p0_asn, p0_org, p0_cc = m[0], m[1], m[2], m[3], m[4].upper()
            raw_ip = raw_ip or p0_ip
            meta["ping0_geo"] = f"{p0_geo} ({p0_asn} · {p0_cc})"
            cc_ref = ipp_cc or ip2_cc
            mismatch = bool(cc_ref and p0_cc and cc_ref != p0_cc)
            sc_p0 = 45 if mismatch else 10
            risk_sources.append({"api": "ping0.cc", "raw": f"{p0_cc}/{'广播偏差' if mismatch else '归属一致'}({sc_p0})", "score": sc_p0, "weight": 0.10})

    # 4. ProxyCheck.io (risk 0-100 + proxy/VPN type)
    if raw_ip and re.match(r'^[0-9a-fA-F.:]+$', raw_ip):
        pc_txt = _http_get_text(f"https://proxycheck.io/v2/{raw_ip}?vpn=1&asn=1&risk=1", timeout=7)
        if pc_txt:
            try:
                d = json.loads(pc_txt)
                info = d.get(raw_ip, {})
                if isinstance(info, dict) and "risk" in info:
                    pc_r = max(0, min(100, int(info["risk"])))
                    pc_t = str(info.get("type", "Clean"))
                    risk_sources.append({"api": "ProxyCheck", "raw": f"{pc_r} ({pc_t})", "score": pc_r, "weight": 0.20})
            except Exception:
                pass

    # 5. Scamalytics (fraud score 0-100)
    if raw_ip and re.match(r'^[0-9a-fA-F.:]+$', raw_ip):
        sc_txt = _http_get_text(f"https://scamalytics.com/ip/{raw_ip}", timeout=7)
        if sc_txt:
            ms = re.search(r'"score"\s*:\s*"(\d+)"', sc_txt)
            mr = re.search(r'"risk"\s*:\s*"([^"]+)"', sc_txt)
            if ms:
                sc_v = max(0, min(100, int(ms.group(1))))
                sc_r = mr.group(1) if mr else ""
                risk_sources.append({"api": "Scamalytics", "raw": f"{sc_v} ({sc_r})", "score": sc_v, "weight": 0.15})

    # 6. ip-api.com (hosting / proxy / mobile flags)
    ia_txt = _http_get_text("http://ip-api.com/json/?fields=hosting,proxy,mobile", timeout=6, ua="curl/8.0")
    if ia_txt:
        try:
            d2 = json.loads(ia_txt)
            flags = [k for k in ("hosting", "proxy", "mobile") if d2.get(k)]
            meta["hosting"] = "/".join(flags) if flags else "clean/residential"
            sc_ia = 80 if d2.get("proxy") else (30 if d2.get("hosting") else 5)
            risk_sources.append({"api": "ip-api", "raw": f"{meta['hosting']}({sc_ia})", "score": sc_ia, "weight": 0.10})
        except Exception:
            pass

    # 7. 3-Zone DNSBL blacklist check (IPv4 only, fast local resolver)
    dnsbl_hits = []
    dnsbl_zones = [("Spamhaus", "zen.spamhaus.org"), ("Barracuda", "b.barracudacentral.org"), ("SpamCop", "bl.spamcop.net")]
    if raw_ip and re.match(r'^\d+\.\d+\.\d+\.\d+$', raw_ip):
        rev = ".".join(reversed(raw_ip.split(".")))
        for z_lbl, zone in dnsbl_zones:
            try:
                socket.setdefaulttimeout(2.5)
                socket.gethostbyname(f"{rev}.{zone}")
                dnsbl_hits.append(z_lbl)
            except Exception:
                pass
        sc_bl = min(100, len(dnsbl_hits) * 35)
        risk_sources.append({"api": "DNSBL", "raw": f"{len(dnsbl_hits)}/3({sc_bl})", "score": sc_bl, "weight": 0.05})

    # Compute weighted composite risk score (0-100, lower is cleaner)
    if risk_sources:
        w_sum = sum(x["weight"] for x in risk_sources)
        comp_risk = round(sum(x["score"] * x["weight"] for x in risk_sources) / max(1e-6, w_sum), 1)
    else:
        comp_risk = 0.0
    comp_tier = "low" if comp_risk <= 25 else ("mid" if comp_risk <= 55 else "high")

    # Platform HTTP reachability probes
    probes = []
    denied = 0
    for name, url in UNLOCK_PROBES:
        rc, out, _ = run_cmd(f"curl -sS -L -m 6 -A 'Mozilla/5.0' -o /dev/null -w '%{{http_code}}' {shlex.quote(url)}", timeout=10)
        code = int(out) if out.isdigit() else 0
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
        "composite_risk": comp_risk, "composite_tier": comp_tier,
        "risk_sources": [{"api": x["api"], "raw": x["raw"], "score": x["score"]} for x in risk_sources],
        "dnsbl_hits": dnsbl_hits, "dnsbl_total": len(dnsbl_zones),
    }


def run_metadata_bench(work_dir):
    mdir = os.path.join(work_dir, "meta_10k")
    os.makedirs(mdir, exist_ok=True)
    payload, n = b"0" * 4096, 10000
    try:
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
    finally:
        shutil.rmtree(mdir, ignore_errors=True)
    return {
        "files": n,
        "create_fps": round(n / max(tc, 1e-6), 1), "stat_fps": round(n / max(ts, 1e-6), 1),
        "read_fps": round(n / max(tr, 1e-6), 1), "delete_fps": round(n / max(td, 1e-6), 1),
    }


def parse_iostat_minutes(log_path, dev_short, seq_minutes):
    """Header-aware iostat -dxm parser compatible with both sysstat 11.x and 12.x."""
    if not os.path.exists(log_path): return []
    col_map = {}
    samples = []
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.split()
            if not parts: continue
            if parts[0] == "Device" or parts[0] == "Device:":
                for idx, h in enumerate(parts[1:]):
                    col_map[h.lower()] = idx
                continue
            if len(parts) >= 12 and parts[0] == dev_short:
                try:
                    vals = [float(x) for x in parts[1:]]
                    i_rs = col_map.get("r/s", 0)
                    i_rmb = col_map.get("rmb/s", col_map.get("rkB/s".lower(), 1))
                    i_ws = col_map.get("w/s", 5)
                    i_wmb = col_map.get("wmb/s", col_map.get("wkB/s".lower(), 6))
                    i_wa = col_map.get("w_await", col_map.get("await", 10))
                    i_ut = col_map.get("%util", len(vals) - 1)
                    samples.append((
                        vals[i_rs] if i_rs < len(vals) else 0.0,
                        vals[i_rmb] if i_rmb < len(vals) else 0.0,
                        vals[i_ws] if i_ws < len(vals) else 0.0,
                        vals[i_wmb] if i_wmb < len(vals) else 0.0,
                        vals[i_wa] if i_wa < len(vals) else 0.0,
                        vals[i_ut] if i_ut < len(vals) else 0.0,
                    ))
                except Exception:
                    pass
    minutes = []
    for i in range(0, len(samples), 12):
        chunk = samples[i:i + 12]
        if not chunk: continue
        m_idx = len(minutes) + 1
        n = len(chunk)
        minutes.append({
            "min": m_idx, "is_seq": m_idx <= max(1, seq_minutes),
            "r_s": round(sum(r[0] for r in chunk) / n, 1),
            "r_mb": round(sum(r[1] for r in chunk) / n, 2),
            "w_s": round(sum(r[2] for r in chunk) / n, 1),
            "w_mb": round(sum(r[3] for r in chunk) / n, 2),
            "w_await": round(sum(r[4] for r in chunk) / n, 2),
            "util": round(sum(r[5] for r in chunk) / n, 1),
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

    # Page 0: Overview & Topology + Quantifiable Scores + ioping (clean categorized layout)
    sec_overview = [
        "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++",
        f"               {C_B}{L['title']}: {C_CYN}{t['masked_ip']}{C_RST}",
        f"               {C_U}https://github.com/arimrs/DiskQuality{C_RST}",
        f"                bash <(curl -sL {s_url})",
        f"     {L['time_ver'].format(t=data['report_time'], v=data['version'])}",
        "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++",
        L["s1"],
        f"{C_YEL}{L['grp_hw']}{C_RST}",
        f"{C_CYN}{L['k_virt']}{C_GRN}{t['virt']} · {t.get('profile','vps').upper()} ({t['arch']}){C_RST}",
        f"{C_CYN}{L['k_os']}{C_GRN}{t['os']}{C_RST}",
        f"{C_CYN}{L['k_cpu']}{C_INV} {t['cpu_model']} {C_RST}",
        f"                        {C_INV} ╚═ {L['cpu_sub'].format(cores=t['cpu_cores'], mhz=t['cpu_mhz'], load=t['loadavg'])} {C_RST}",
        f"{C_CYN}{L['k_mem']}{C_INV} {L['mem_val'].format(mem=t['mem'], swap=t['swap'])} {C_RST}",
        f"{C_CYN}{L['k_disk']}{C_INV} {L['disk_val'].format(model=t['disk_model'], tot=p['disk_total_gb'], used=p['disk_used_gb'], avail=p['disk_avail_gb'])} {C_RST}",
        f"{C_CYN}{L['k_dev']}{C_GRN}{L['dev_val'].format(dev=t['mount_dev'], fs=t['fs_type'], rota=t['rotational'], sched=t['scheduler'])}{C_RST}",
        f"{C_CYN}{L['k_cache']}{C_GRN}{L['cache_val'].format(wc=t['write_cache'], ra=t['read_ahead_kb'], sec=t['sector'], trim=L['trim_yes'] if t['trim_supported'] else L['trim_no'])}{C_RST}",
        f"{C_CYN}{L['k_spec']}{C_YEL}{L['spec_val'].format(sgb=p['stress_file_gb'], mgb=p['matrix_file_gb'], ioe=p.get('ioengine','libaio'), dir=p.get('direct',1))}{C_RST}",
        "",
        f"{C_YEL}{L['grp_eval']}{C_RST}",
    ]
    d_sc = data.get("disk_score")
    if d_sc:
        ds_col = C_BG_GRN if d_sc["score"] >= 70 else (C_BG_YEL if d_sc["score"] >= 45 else C_BG_RED)
        sec_overview.append(
            f"{C_CYN}{L['k_dscore']}{ds_col} {d_sc['score']:.1f} / 100 · {d_sc['grade']} {C_RST}"
        )
        sec_overview.append(
            f"                        {C_GRN}╚═ {L['ds_sub'].format(s_seq=d_sc['s_seq'], s_4k=d_sc['s_4k'], s_lat=d_sc['s_lat'], s_conc=d_sc['s_conc'], s_sust=d_sc['s_sust'], s_meta=d_sc['s_meta'])}{C_RST}"
        )
    os_idx = data.get("overselling")
    if os_idx:
        t_col = {"t0": C_BG_GRN, "t1": C_BG_GRN, "t2": C_BG_YEL, "t3": C_BG_RED}.get(os_idx["tier"], C_BG_YEL)
        t_lbl = L.get(f"os_{os_idx['tier']}", os_idx["tier"])
        sec_overview.append(
            f"{C_CYN}{L['k_oscore']}{t_col} {os_idx['score']:.1f} / 100 · {t_lbl} {C_RST}"
        )
        sec_overview.append(
            f"                        {C_GRN}╚═ {L['os_sub'].format(media=os_idx['media'], d_bw=os_idx['d_bw'], d_4k=os_idx['d_4k'], d_lat=os_idx['d_lat'], d_drop=os_idx['d_drop'])}{C_RST}"
        )
    gb = data.get("geekbench")
    if not gb:
        sec_overview.append(f"{C_CYN}{L['k_gb_skip']}{skip}")
    else:
        sc_v, mc_v = gb.get("single_core", "N/A"), gb.get("multi_core", "N/A")
        gb_ver = gb.get("version", "Geekbench")
        sec_overview.append(
            f"{C_CYN}{L['k_gb'].format(ver=gb_ver)}"
            f"{C_BG_GRN} {L['gb_sc']}: {sc_v} {C_RST}  {C_BG_GRN} {L['gb_mc']}: {mc_v} {C_RST}"
        )
        if gb.get("url"):
            sec_overview.append(f"{C_CYN}{L['k_gb_url']}{C_GRN}{C_U}{gb['url']}{C_RST}")
    sec_overview += ["", L["s2"]]
    io = data.get("ioping")
    if not sel.get("ioping", True) or not io:
        sec_overview.append(f"{C_CYN}{L['k_res']}{skip}")
    else:
        sec_overview += [
            f"{C_CYN}{L['k_seek']}{C_GRN}{io.get('direct_seek','N/A')}{C_RST}",
            f"{C_CYN}{L['k_cread']}{C_GRN}{io.get('cached_read','N/A')}{C_RST}",
            f"{C_CYN}{L['k_swrite']}{C_GRN}{io.get('sync_write','N/A')}{C_RST}",
        ]

    # Page 1: Disk Matrix (grouped into Sequential vs Random) + Production fsync + High-Concurrency
    sec_disk = [L["s3"]]
    if not sel.get("matrix", True) or not data.get("matrix"):
        sec_disk.append(f"{C_CYN}{L['k_res']}{skip}")
    else:
        seq_rows = [r for r in data["matrix"] if not r.get("error") and r["name"].startswith(("SEQ", "BUF"))]
        rnd_rows = [r for r in data["matrix"] if not r.get("error") and r["name"].startswith("RND")]
        hdr = f"{C_CYN}{L['th_item']:<20} {L['th_r']:<22} {L['th_w']:<22} {'p95':>8} {'p99':>8}{C_RST}"
        for grp_lbl, rows in ((L["grp_seq"], seq_rows), (L["grp_rnd"], rnd_rows)):
            if not rows: continue
            sec_disk.append(f"{C_YEL}{grp_lbl}{C_RST}")
            sec_disk.append(hdr)
            for row in rows:
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

    # Page 3: Global Network (grouped by region) & Multi-Source IP Quality + Risk Breakdown
    sec_netip = [L["s7"]]
    net = data.get("network")
    if not sel.get("network", True) or not net:
        sec_netip.append(f"{C_CYN}{L['k_res']}{skip}")
    else:
        sec_netip.append(f"{C_CYN}{L['th_node']:<24} {L['th_rtt']:<28} {L['th_loss']:>8}{C_RST}")
        reg_tags = {"(JP)": L["reg_ap"], "(SG)": L["reg_ap"], "(HK)": L["reg_ap"], "(US)": L["reg_us"], "(DE)": L["reg_eu"], "(UK)": L["reg_eu"], "(NL)": L["reg_eu"]}
        for h in net.get("hubs", []):
            rtag = next((v for k, v in reg_tags.items() if k in h["hub"]), "")
            h_lbl = f"[{rtag}] {h['hub']}" if rtag else h["hub"]
            rtt_s = f"{h['min']:.1f} / {h['avg']:.1f} / {h['max']:.1f} ms" if h["avg"] >= 0 else "Timeout"
            col = C_GRN if 0 <= h["avg"] < 120 else (C_YEL if h["avg"] >= 0 else C_RED)
            sec_netip.append(f"{C_CYN}{h_lbl:<24}{C_RST} {col}{rtt_s:<28}{C_RST} {h['loss']:>6.0f}%")
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
        cr_col, cr_lbl = rk_map.get(ipq.get("composite_tier", "mid"), (C_BG_YEL, ""))
        p25_badge = f"{C_BG_GRN} ✔ {L['p25_ok']} {C_RST}" if ipq["port25_open"] else f"{C_BG_RED} ✘ {L['p25_no']} {C_RST}"
        bl_hits = ipq.get("dnsbl_hits", [])
        bl_tot = ipq.get("dnsbl_total", 3)
        bl_badge = f"{C_BG_GRN} ✔ 0/{bl_tot} Clean {C_RST}" if not bl_hits else f"{C_BG_RED} ✘ {len(bl_hits)}/{bl_tot} ({','.join(bl_hits)}) {C_RST}"

        sec_netip += [
            f"{C_YEL}{L['grp_ip_base']}{C_RST}",
            f"{C_CYN}{L['k_asn']}{C_GRN}{im['asn']} ({im['org']}) · {im['location']}{C_RST}",
            f"{C_CYN}{L['k_ipattr']}{C_YEL}{im.get('native_type', 'Unknown')} · ip-api: {im['hosting']}{C_RST}",
            f"{C_CYN}{L['k_ping0']}{C_GRN}{im.get('ping0_geo', 'N/A')}{C_RST}",
            f"{C_CYN}{L['k_p25']}{p25_badge}   {C_CYN}{L['k_dnsbl']}{bl_badge}",
            "",
            f"{C_YEL}{L['grp_ip_risk']}{C_RST}",
            f"{C_CYN}{L['k_risk']}{cr_col} {ipq.get('composite_risk', 0):.1f} / 100 · {cr_lbl} {C_RST}",
        ]
        srcs = ipq.get("risk_sources", [])
        if srcs:
            src_strs = [f"{x['api']}: {x['raw']}" for x in srcs]
            sec_netip.append(f"{C_CYN}{L['k_risk_src']}{C_GRN}{' | '.join(src_strs[:3])}{C_RST}")
            if len(src_strs) > 3:
                sec_netip.append(f"                        {C_GRN}{' | '.join(src_strs[3:])}{C_RST}")
        sec_netip += [
            "",
            f"{C_YEL}{L['grp_ip_plat']}{C_RST}",
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


def _span_px_width(s, ascii_w=10.5, cjk_w=17.6):
    """Calculate accurate pixel width for larger 17.5px mixed ASCII + CJK monospace text."""
    total = 0.0
    for ch in s:
        total += cjk_w if unicodedata.east_asian_width(ch) in ("W", "F") else ascii_w
    return total


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
    """Crisp, larger-font (17.5px) HardwareQuality-style SVG renderer with dynamic width & zero clipping."""
    lines = ansi_text.splitlines()
    line_height, pad_x, pad_y = 29, 34, 32
    parsed = [parse_ansi_spans(ln) for ln in lines]
    max_line_w = 0.0
    for spans in parsed:
        w_line = sum(_span_px_width(t) + (6.0 if bg else 0.0) for t, _, bg, _, _ in spans)
        if w_line > max_line_w:
            max_line_w = w_line
    width = max(1140, int(max_line_w + pad_x * 2 + 28))
    height = pad_y * 2 + len(lines) * line_height + 20
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<defs><style>text { font-family: "JetBrains Mono","Fira Code","Cascadia Code","Sarasa Mono SC","LXGW WenKai Mono","PingFang SC","Microsoft YaHei",monospace; font-size: 17.5px; letter-spacing: 0.25px; text-rendering: geometricPrecision; white-space: pre; }</style></defs>',
        '<rect width="100%" height="100%" rx="10" fill="#1b1c1f"/>',
    ]
    for idx, spans in enumerate(parsed):
        y = pad_y + (idx + 1) * line_height - 7
        rects, texts = [], []
        cur_x = float(pad_x)
        for txt, fg, bg, bold, ul in spans:
            px_w = _span_px_width(txt)
            if bg:
                rx_w = max(px_w + 6.0, 18.0)
                rects.append(f'<rect x="{cur_x:.1f}" y="{y - 18.5:.1f}" width="{rx_w:.1f}" height="24" rx="3" fill="{bg}"/>')
            fw = ' font-weight="700"' if bold else ''
            td = ' text-decoration="underline"' if ul else ''
            fill_c = "#18181b" if bg == "#d8d8d8" else ("#ffffff" if bg in ("#52a31c", "#c92a2a") else fg)
            texts.append(f'<text x="{cur_x:.1f}" y="{y}" fill="{fill_c}"{fw}{td} xml:space="preserve">{html.escape(txt)}</text>')
            cur_x += px_w + (6.0 if bg else 0.0)
        svg.extend(rects)
        svg.extend(texts)
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
    gb_mode = (getattr(args, "geekbench", "gb5") or "skip").lower()
    if gb_mode not in ("gb5", "gb6"):
        gb_mode = "skip"

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
        + (1 if gb_mode != "skip" else 0)
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
    topo = collect_system_topology(args.target, forced_profile=getattr(args, "profile", "auto"))
    ioe, io_direct = probe_fio_capabilities(work_dir)
    plan["ioengine"] = ioe
    plan["direct"] = io_direct
    # Platform-specific adaptive scheduling: cap huge dedicated arrays cleanly & protect container pids/ulimit
    prof = topo.get("profile", "vps")
    if prof == "dedicated":
        plan["matrix_file_gb"] = min(8.0, max(plan["matrix_file_gb"], 4.0))
        plan["stress_file_gb"] = min(plan["stress_file_gb"], 2000.0)
    elif prof == "container":
        plan["matrix_file_gb"] = min(plan["matrix_file_gb"], 2.0)
    show_bar(
        f"拓扑完成 · {prof.upper()} ({topo['virt']}/{topo['arch']}) · {plan['disk_total_gb']} GB · {ioe} direct={io_direct}",
        f"Topology ready · {prof.upper()} ({topo['virt']}/{topo['arch']}) · {plan['disk_total_gb']} GB · {ioe} direct={io_direct}",
        advance=1,
    )

    ioping_res = None
    if sel["ioping"]:
        show_bar("正在运行底层延迟基线测试 (ioping)...", "Running latency baseline (ioping)...", advance=0)
        ioping_res = run_ioping_tests(work_dir)
        show_bar("底层延迟基线测试 (ioping) 完成", "Latency baseline (ioping) completed", advance=1)

    mfile, sfile = os.path.join(work_dir, "matrix.bin"), os.path.join(work_dir, "stress_50pct.bin")
    rt, msz = plan["matrix_item_sec"], plan["matrix_file_gb"]
    max_jobs = 16 if prof == "container" else 32

    matrix_res = None
    if sel["matrix"]:
        specs = [
            ("SEQ1M_R_Q1", "read", "1M", 1, 1, io_direct, None, None), ("SEQ1M_R_Q32", "read", "1M", 32, 4, io_direct, None, None),
            ("SEQ1M_W_Q1", "write", "1M", 1, 1, io_direct, None, None), ("SEQ1M_W_Q32", "write", "1M", 32, 4, io_direct, None, None),
            ("RND4K_R_Q1", "randread", "4K", 1, 1, io_direct, None, None), ("RND4K_R_Q16", "randread", "4K", 16, 1, io_direct, None, None),
            ("RND4K_R_Q64", "randread", "4K", 64, 4, io_direct, None, None), ("RND4K_W_Q1", "randwrite", "4K", 1, 1, io_direct, None, None),
            ("RND4K_W_Q16", "randwrite", "4K", 16, 1, io_direct, None, None), ("RND4K_W_Q64", "randwrite", "4K", 64, 4, io_direct, None, None),
            ("RND8K_70_30", "randrw", "8K", 16, 2, io_direct, 70, None), ("RND16K_70_30", "randrw", "16K", 16, 2, io_direct, 70, None),
            ("SEQ128K_50_50", "rw", "128K", 16, 2, io_direct, 50, None), ("BUF1M_50_50", "rw", "1M", 16, 2, 0, 50, None),
        ]
        matrix_res = []
        for idx, (n, rw, bs, qd, nj, d, mix, fs) in enumerate(specs, 1):
            show_bar(f"FIO 矩阵 [{idx}/{len(specs)}] 正在测 {n}...", f"FIO Matrix [{idx}/{len(specs)}] {n}...", advance=0)
            matrix_res.append(run_fio_job(n, mfile, msz, rw, bs, qd, nj, rt, d, mix, fs, ioengine=ioe))
            show_bar(f"FIO 矩阵 [{idx}/{len(specs)}] {n} 完成", f"FIO Matrix [{idx}/{len(specs)}] {n} done", advance=1)

    prod_res = None
    if sel["prod"]:
        pspecs = [
            ("OLTP_8K_Q32", "randrw", "8K", 32, 2, io_direct, 70, None), ("WEB_16K_Q8", "randrw", "16K", 8, 2, io_direct, 50, None),
            ("WAL_4K_FSYNC1", "write", "4K", 1, 1, io_direct, None, 1), ("CONG_4K_FSYNC4", "randwrite", "4K", 32, 2, io_direct, None, 4),
        ]
        prod_res = []
        for idx, (n, rw, bs, qd, nj, d, mix, fs) in enumerate(pspecs, 1):
            show_bar(f"生产模型 [{idx}/{len(pspecs)}] 正在测 {n}...", f"Production [{idx}/{len(pspecs)}] {n}...", advance=0)
            prod_res.append(run_fio_job(n, mfile, msz, rw, bs, qd, nj, rt, d, mix, fs, ioengine=ioe))
            show_bar(f"生产模型 [{idx}/{len(pspecs)}] {n} 完成", f"Production [{idx}/{len(pspecs)}] {n} done", advance=1)

    conc_res = None
    if sel["concurrency"]:
        cspecs = [
            ("PT_SEED_16K_32T",  "randread", "16K",  4, min(32, max_jobs), io_direct, None, None),
            ("PT_HASH_256K_16T", "read",     "256K", 4, min(16, max_jobs), io_direct, None, None),
            ("BACKUP_64K_16T",   "randrw",   "64K",  4, min(16, max_jobs), io_direct, 50,   None),
            ("BURST_4K_32T",     "randrw",   "4K",   1, min(32, max_jobs), io_direct, 70,   None),
        ]
        conc_res = []
        for idx, (n, rw, bs, qd, nj, d, mix, fs) in enumerate(cspecs, 1):
            show_bar(f"小量多并发 [{idx}/{len(cspecs)}] 正在测 {n}...", f"Concurrency [{idx}/{len(cspecs)}] {n}...", advance=0)
            conc_res.append(run_fio_job(n, mfile, msz, rw, bs, qd, nj, rt, d, mix, fs, ioengine=ioe))
            show_bar(f"小量多并发 [{idx}/{len(cspecs)}] {n} 完成", f"Concurrency [{idx}/{len(cspecs)}] {n} done", advance=1)

    try: os.remove(mfile)
    except Exception: pass

    sustained_res = None
    if sel["sustained"]:
        seq_m = round(plan["sustained_seq_sec"] / 60.0, 1)
        mix_m = round(plan["sustained_mix_sec"] / 60.0, 1)
        iostat_log = os.path.join(work_dir, "iostat_raw.log")
        dev_short = os.path.basename(topo["base_dev"]) if topo.get("has_block_dev") else ""
        io_proc = None
        if dev_short:
            io_proc = subprocess.Popen(f"iostat -dxm {shlex.quote(dev_short)} 5 > {shlex.quote(iostat_log)} 2>&1", shell=True, start_new_session=True)
            _ACTIVE_PROCS.append(io_proc)
        try:
            show_bar(
                f"50% 容量持久压测 阶段 A 顺序写 ({plan['stress_file_gb']} GB, {seq_m} 分钟)...",
                f"50% Endurance Phase A Seq Write ({plan['stress_file_gb']} GB, {seq_m} min)...",
                advance=0,
            )
            sw = run_fio_job("SUSTAINED_50PCT_SEQ_W", sfile, plan["stress_file_gb"], "write", "1M", 16, 1, plan["sustained_seq_sec"], io_direct, ioengine=ioe)
            show_bar("50% 容量持久压测 阶段 A 完成，进入阶段 B 随机混合...", "50% Endurance Phase A done, starting Phase B Mixed...", advance=1)
            ms = run_fio_job("SUSTAINED_50PCT_MIX", sfile, plan["stress_file_gb"], "randrw", "8K", 32, 2, plan["sustained_mix_sec"], io_direct, 30, ioengine=ioe)
            show_bar("50% 容量持久压测 阶段 B 完成", "50% Endurance Phase B completed", advance=1)
        finally:
            if io_proc is not None:
                try: os.killpg(os.getpgid(io_proc.pid), signal.SIGKILL)
                except Exception:
                    try: io_proc.kill()
                    except Exception: pass
                try: io_proc.wait(timeout=3)
                except Exception: pass
                if io_proc in _ACTIVE_PROCS: _ACTIVE_PROCS.remove(io_proc)
            try: os.remove(sfile)
            except Exception: pass
        tl = parse_iostat_minutes(iostat_log, dev_short, plan["sustained_seq_sec"] // 60) if dev_short else []
        sustained_res = {"seq_write": sw, "rand_mixed": ms, "timeline": tl}

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
        life_res = collect_poweron_lifetime(topo["mount_dev"], topo["base_dev"], fs_type=topo.get("fs_type", "ext4"))
        show_bar("元数据与介质寿命检测完成", "Metadata & lifetime diagnostics completed", advance=1)

    gb_res = None
    if gb_mode != "skip":
        gb_lbl = "Geekbench 5" if gb_mode == "gb5" else "Geekbench 6"
        show_bar(f"正在运行完整 {gb_lbl} CPU 单核/多核跑分（约 2–4 分钟）...", f"Running full {gb_lbl} CPU Single/Multi-Core benchmark (~2–4m)...", advance=0)
        gb_res = run_geekbench(gb_mode, work_dir)
        show_bar(f"{gb_lbl} CPU 跑分完成", f"{gb_lbl} CPU benchmark completed", advance=1)

    overselling_res = calc_overselling_index(topo, matrix_res, prod_res, sustained_res)
    disk_score_res = calc_disk_score(topo, ioping_res, matrix_res, prod_res, conc_res, sustained_res, meta_res)

    thorough_cleanup(work_dir, args.target, do_trim=True)
    end_emo = random.choice(end_kaomojis)
    show_bar("全部测试已完成，环境已彻底清理干净！", "All tests completed & environment thoroughly cleaned!", advance=1, suffix=end_emo)

    data = {
        "version": VERSION, "lang": lang, "site_url": args.site_url,
        "report_time": start_str, "elapsed_min": round((time.time() - t_start) / 60.0, 2),
        "selected": sel, "plan": plan, "topology": topo, "geekbench": gb_res,
        "overselling": overselling_res, "disk_score": disk_score_res,
        "lifetime": life_res, "ioping": ioping_res, "matrix": matrix_res,
        "production": prod_res, "concurrency": conc_res, "sustained": sustained_res,
        "network": net_res, "ip_quality": ipq_res, "metadata": meta_res,
    }

    if args.upload_url:
        try:
            req = urllib.request.Request(
                args.upload_url, data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "DiskQuality-CLI/1.0.8"}, method="POST",
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
    ap.add_argument("--geekbench", default="gb5", choices=["gb5", "gb6", "skip"])
    ap.add_argument("--profile", default="auto", choices=["auto", "dedicated", "vds", "vps", "container"])
    ap.add_argument("--site-url", default=DEFAULT_SITE_URL)
    ap.add_argument("--upload-url", default="")
    run_benchmark_cli(ap.parse_args())


if __name__ == "__main__":
    main()
