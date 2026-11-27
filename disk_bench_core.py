#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DiskQuality v1.0.9 — Bilingual Objective VPS Disk, Concurrency, Global Network & IP Quality Suite
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
import math
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

VERSION = "v1.0.9 (2026.11.27)"
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
        "card_tab": "可视化战报",
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
        "card_tab": "Visual Card",
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


_ANSI_ESCAPE = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07\x1b]*(?:\x07|\x1b\\)|[@-_])")
_SGR = re.compile(r"(\x1b\[[0-9;]*m)")
_XML_INVALID = re.compile(r"[\x00-\x08\x0a-\x1f\x7f-\x9f\ud800-\udfff\ufffe\uffff]")
REPORT_PAGES = ("full", "overview", "disk", "endurance", "netip", "meta")
_RADAR_KEYS = ("s_seq", "s_4k", "s_lat", "s_conc", "s_sust", "s_meta")


def strip_ansi(s):
    return _ANSI_ESCAPE.sub("", s)


def _vis_width(s):
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in strip_ansi(s))


def _pad_vis(s, width, align="left"):
    padding = " " * max(0, width - _vis_width(s))
    return padding + s if align == "right" else s + padding


def _num(value):
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (ValueError, TypeError, OverflowError):
        return None
    return result if math.isfinite(result) else None


def _fmt(value, digits=1, suffix=""):
    value = _num(value)
    return f"{value:.{digits}f}{suffix}" if value is not None else "—"


def _sparkline(values):
    values = [v for v in map(_num, values) if v is not None]
    if not values:
        return ""
    lo, hi = min(values), max(values)
    if hi == lo:
        return "▄" * len(values)
    # Scale before subtracting so opposite finite extremes cannot overflow.
    scale = max(abs(lo), abs(hi))
    lo, hi = lo / scale, hi / scale
    return "".join("▁▂▃▄▅▆▇█"[round((v / scale - lo) * 7 / (hi - lo))] for v in values)


def _mini_bar(score, max_val=100.0, width=14):
    score, max_val = _num(score), _num(max_val)
    ratio = min(max(0, score), max_val) / max_val if score is not None and max_val and max_val > 0 else 0
    filled = round(ratio * width)
    return "█" * filled + "░" * (width - filled)


def _mapping(value):
    return value if isinstance(value, dict) else {}


def _rows(value):
    return [row for row in value if isinstance(row, dict)] if isinstance(value, list) else []


def _enabled(data, key):
    # Legacy reports omit the selection map. An explicit false or null flag skips that module.
    return bool(_mapping(data.get("selected")).get(key, True))


def _module(data, key, selection=None):
    return data.get(key) if _enabled(data, selection or key) else None


def _report_lang(data, lang):
    value = str(lang or data.get("lang") or "zh").lower()
    return value if value in I18N else "zh"


def _shown(value):
    return "—" if value is None or value == "" else str(value)


def _sequential(point, plan):
    if isinstance(point.get("is_seq"), bool):
        return point["is_seq"]
    stage = str(point.get("stage") or "").lower()
    if "随机" in stage or "mix" in stage or "rand" in stage:
        return False
    if "顺序" in stage or "seq" in stage:
        return True
    minute, seconds = _num(point.get("min")), _num(plan.get("sustained_seq_sec"))
    return minute is None or seconds is None or minute <= max(1, seconds // 60)


def _color_bw(mb):
    return C_GRN if mb >= 200 else (C_YEL if mb >= 20 else C_RED)


def _fio_rows(value):
    return [r for r in _rows(value) if r.get("name") and not r.get("error")]


def build_sections(data, lang=None, site_url=None):
    """Build shared ANSI sections for the CLI and terminal SVG exports."""
    lang = _report_lang(data, lang)
    L = I18N[lang]
    s_url = site_url or data.get("site_url") or DEFAULT_SITE_URL
    skip = f"{C_BRED}{L['skip_txt']}{C_RST}"
    t, p = _mapping(data.get("topology")), _mapping(data.get("plan"))
    continuation = " " * 32

    def label(key, **kwargs):
        return _pad_vis(L[key].format(**kwargs).rstrip(), 32)

    def kv(key, value, color=C_GRN, **kwargs):
        return f"{C_CYN}{label(key, **kwargs)}{color}{value}{C_RST}"

    def fields(template, values, **keys):
        return L[template].format(**{name: _shown(values.get(key)) for name, key in keys.items()})

    def disk_table(rows):
        lines = [f"{C_CYN}{_pad_vis(L['th_item'], 22)} {_pad_vis(L['th_r'], 24)} {_pad_vis(L['th_w'], 24)} {'p95':>9} {'p99':>9}{C_RST}"]
        for row in rows:
            r, w = (_num(row.get(k)) for k in ("r_iops", "w_iops"))
            bw_r, bw_w = (_num(row.get(k)) for k in ("r_bw_mbs", "w_bw_mbs"))
            rs = f"{_fmt(bw_r, 2, 'MB/s')} ({r:.0f})" if r else "—"
            ws = f"{_fmt(bw_w, 2, 'MB/s')} ({w:.0f})" if w else "—"
            tails = []
            for percentile in ("p95", "p99"):
                vals = [_num(row.get(f"{direction}_{percentile}_ms")) for direction in ("r", "w")]
                tails.append(_pad_vis(_fmt(max((v for v in vals if v is not None), default=None), 2, "ms"), 9, "right"))
            col = _color_bw(max(bw_r or 0, bw_w or 0))
            lines.append(f"{C_CYN}{_pad_vis(str(row['name']), 22)}{C_RST} {col}{_pad_vis(rs, 24)} {_pad_vis(ws, 24)}{C_RST} {' '.join(tails)}")
        return lines

    sec_overview = [
        "+" * 80,
        f"               {C_B}{L['title']}: {C_CYN}{_shown(t.get('masked_ip'))}{C_RST}",
        f"               {C_U}https://github.com/arimrs/DiskQuality{C_RST}",
        f"                bash <(curl -sL {s_url})",
        f"     {L['time_ver'].format(t=_shown(data.get('report_time')), v=_shown(data.get('version')))}",
        "+" * 80, L["s1"], f"{C_YEL}{L['grp_hw']}{C_RST}",
        kv("k_virt", f"{_shown(t.get('virt'))} · {str(t.get('profile') or 'vps').upper()} ({_shown(t.get('arch'))})"),
        kv("k_os", _shown(t.get("os"))),
        kv("k_cpu", f" {_shown(t.get('cpu_model'))} ", C_INV),
        f"{continuation}{C_INV} ╚═ {fields('cpu_sub', t, cores='cpu_cores', mhz='cpu_mhz', load='loadavg')} {C_RST}",
        kv("k_mem", f" {fields('mem_val', t, mem='mem', swap='swap')} ", C_INV),
        kv("k_disk", f" {fields('disk_val', {**p, **t}, model='disk_model', tot='disk_total_gb', used='disk_used_gb', avail='disk_avail_gb')} ", C_INV),
        kv("k_dev", fields("dev_val", t, dev="mount_dev", fs="fs_type", rota="rotational", sched="scheduler")),
        kv("k_cache", fields("cache_val", {**t, "trim": L["trim_yes"] if t.get("trim_supported") else L["trim_no"] if "trim_supported" in t else "—"}, wc="write_cache", ra="read_ahead_kb", sec="sector", trim="trim")),
        kv("k_spec", fields("spec_val", {"ioengine": "libaio", "direct": 1, **p}, sgb="stress_file_gb", mgb="matrix_file_gb", ioe="ioengine", dir="direct"), C_YEL),
        "", f"{C_YEL}{L['grp_eval']}{C_RST}",
    ]
    d_sc = _mapping(_module(data, "disk_score"))
    ds = _num(d_sc.get("score"))
    if ds is not None:
        ds_col = C_BG_GRN if ds >= 70 else C_BG_YEL if ds >= 45 else C_BG_RED
        sec_overview += [
            kv("k_dscore", f" {ds:.1f} / 100 · {_shown(d_sc.get('grade'))} {C_RST} {C_GRN}{_mini_bar(ds)}", ds_col),
            f"{continuation}{C_GRN}╚═ {fields('ds_sub', d_sc, **{k: k for k in _RADAR_KEYS})}{C_RST}",
        ]
    os_idx = _mapping(_module(data, "overselling"))
    score = _num(os_idx.get("score"))
    if score is not None:
        tier = _shown(os_idx.get("tier"))
        col = {"t0": C_BG_GRN, "t1": C_BG_GRN, "t2": C_BG_YEL, "t3": C_BG_RED}.get(tier, C_BG_YEL)
        sub = fields("os_sub", os_idx, media="media", d_bw="d_bw", d_4k="d_4k", d_lat="d_lat", d_drop="d_drop")
        sec_overview += [
            kv("k_oscore", f" {score:.1f} / 100 · {L.get(f'os_{tier}', tier)} {C_RST} {C_YEL}{_mini_bar(score)}", col),
            f"{continuation}{C_GRN}╚═ {sub}{C_RST}",
        ]
    gb = _mapping(_module(data, "geekbench"))
    if gb:
        scores = "  ".join(f"{C_BG_GRN} {L[lbl]}: {_shown(gb.get(key))} {C_RST}" for lbl, key in (("gb_sc", "single_core"), ("gb_mc", "multi_core")))
        sec_overview.append(kv("k_gb", scores, ver=gb.get("version") or "Geekbench"))
        if gb.get("url"):
            sec_overview.append(kv("k_gb_url", f"{C_U}{gb['url']}"))
    else:
        sec_overview.append(kv("k_gb_skip", skip))
    sec_overview += ["", L["s2"]]
    io = _mapping(_module(data, "ioping"))
    if io:
        sec_overview.extend(kv(lbl, _shown(io.get(key))) for lbl, key in (
            ("k_seek", "direct_seek"), ("k_cread", "cached_read"), ("k_swrite", "sync_write")))
    else:
        sec_overview.append(kv("k_res", skip))

    sec_disk = [L["s3"]]
    matrix = _fio_rows(_module(data, "matrix"))
    seq_rows = [r for r in matrix if str(r["name"]).startswith(("SEQ", "BUF"))]
    rnd_rows = [r for r in matrix if str(r["name"]).startswith("RND")]
    for grp, rows in (("grp_seq", seq_rows), ("grp_rnd", rnd_rows)):
        if rows:
            sec_disk += [f"{C_YEL}{L[grp]}{C_RST}"] + disk_table(rows)
    if not seq_rows and not rnd_rows:
        sec_disk.append(kv("k_res", skip))
    for heading, rows in (("s4", _fio_rows(_module(data, "production", "prod"))),
                          ("s5", _fio_rows(_module(data, "concurrency")))):
        sec_disk += ["", L[heading]] + (disk_table(rows) if rows else [kv("k_res", skip)])

    sec_endurance = [L["s6"].format(gb=_shown(p.get("stress_file_gb")))]
    sus = _mapping(_module(data, "sustained"))
    sw, ms = _mapping(sus.get("seq_write")), _mapping(sus.get("rand_mixed"))
    if sw and not sw.get("error"):
        written = _num(sw.get("w_bytes"))
        sec_endurance.append(kv("k_seq", L["seq_val"].format(
            gb=_fmt(written / 1024**3 if written is not None else None, 2),
            bw=_shown(sw.get("w_bw_mbs")), p99=_shown(sw.get("w_p99_ms")))))
    if ms and not ms.get("error"):
        sec_endurance.append(kv("k_mix", fields("mix_val", ms, rbw="r_bw_mbs", riops="r_iops",
                                               wbw="w_bw_mbs", wiops="w_iops", p99="w_p99_ms"), C_YEL))
    timeline = _rows(sus.get("timeline"))
    if timeline:
        write_rates = (_num(pt.get("w_mb")) for pt in timeline)
        values = [v for v in write_rates if v is not None]
        if values:
            scale = max(map(abs, values)) or 1
            avg = scale * (math.fsum(v / scale for v in values) / len(values))
            desc = "写入 最低 / 平均 / 峰值" if lang == "zh" else "Write min / avg / peak"
            sec_endurance.append(f"{C_CYN}{desc}  {C_GRN}{_sparkline(values)}{C_RST}  {min(values):.2f} / {avg:.2f} / {max(values):.2f} MB/s")
        columns = (("min", L["th_min"], 6, 0, ""), ("stage", L["th_stg"], 18, 0, ""),
                   ("r_mb", L["th_rmb"], 9, 2, ""), ("w_mb", L["th_wmb"], 9, 2, ""),
                   ("r_s", "r/s", 8, 1, ""), ("w_s", "w/s", 8, 1, ""),
                   ("w_await", "w_await", 10, 2, "ms"), ("util", "%util", 8, 1, "%"))
        sec_endurance.append(C_CYN + " ".join(_pad_vis(h, w, "left" if k in ("min", "stage") else "right")
                                             for k, h, w, _, _ in columns) + C_RST)
        for pt in timeline:
            stage = L["stg_seq"] if _sequential(pt, p) else L["stg_mix"]
            minute = _num(pt.get("min"))
            minute = L["min_fmt"].format(m=int(minute)).rstrip() if minute is not None else "—"
            cells = [_pad_vis(minute, 6), _pad_vis(stage, 18)]
            cells.extend(_pad_vis(_fmt(pt.get(k), digits, unit), width, "right")
                         for k, _, width, digits, unit in columns[2:])
            col = C_GRN if (_num(pt.get("w_mb")) or 0) >= 50 else C_YEL
            sec_endurance.append(f"{' '.join(cells[:2])} {col}{' '.join(cells[2:4])}{C_RST} {' '.join(cells[4:])}")
    if len(sec_endurance) == 1:
        sec_endurance.append(kv("k_res", skip))

    sec_netip = [L["s7"]]
    net = _mapping(_module(data, "network"))
    hubs = _rows(net.get("hubs"))
    if hubs:
        sec_netip.append(f"{C_CYN}{_pad_vis(L['th_node'], 28)} {_pad_vis(L['th_rtt'], 29)} {_pad_vis(L['th_loss'], 8, 'right')}{C_RST}")
        for h in hubs:
            name = _shown(h.get("hub"))
            reg = _hub_region(name)
            h_lbl = f"[{L[reg]}] {name}" if reg else name
            avg = _num(h.get("avg"))
            rtt = " / ".join(_fmt(h.get(k)) for k in ("min", "avg", "max")) + " ms" if avg is not None and avg >= 0 else ("超时" if lang == "zh" else "Timeout") if avg is not None else "—"
            col = C_GRN if avg is not None and 0 <= avg < 120 else C_YEL if avg is not None and avg >= 0 else C_RED
            sec_netip.append(f"{C_CYN}{_pad_vis(h_lbl, 28)}{C_RST} {col}{_pad_vis(rtt, 29)}{C_RST} {_pad_vis(_fmt(h.get('loss'), 0, '%'), 8, 'right')}")
    dl = _rows(net.get("downloads"))
    if dl:
        sec_netip.append(kv("k_dl", " | ".join(f"{_shown(d.get('name'))}: {_shown(d.get('mbs'))} MB/s ({_shown(d.get('mbps'))} Mbps)" for d in dl)))
    if not hubs and not dl:
        sec_netip.append(kv("k_res", skip))

    sec_netip += ["", L["s8"]]
    ipq = _mapping(_module(data, "ip_quality"))
    if ipq:
        im = _mapping(ipq.get("meta"))
        risk_colors = {"low": C_BG_GRN, "mid": C_BG_YEL, "high": C_BG_RED}
        tier, risk = _shown(ipq.get("composite_tier")), _shown(ipq.get("risk"))
        port25, bl_hits = ipq.get("port25_open"), ipq.get("dnsbl_hits")
        bl_tot = _shown(ipq.get("dnsbl_total", 3))
        p25 = (f"{C_BG_GRN} ✔ {L['p25_ok']} " if port25 is True else
               f"{C_BG_RED} ✘ {L['p25_no']} " if port25 is False else "—") + C_RST
        dnsbl = "—"
        if isinstance(bl_hits, list):
            dnsbl = (f"{C_BG_RED} ✘ {len(bl_hits)}/{bl_tot} ({','.join(map(str, bl_hits))}) " if bl_hits else
                     f"{C_BG_GRN} ✔ 0/{bl_tot} {'无命中' if lang == 'zh' else 'Clean'} ") + C_RST
        sec_netip += [
            f"{C_YEL}{L['grp_ip_base']}{C_RST}",
            kv("k_asn", f"{_shown(im.get('asn'))} ({_shown(im.get('org'))}) · {_shown(im.get('location'))}"),
            kv("k_ipattr", f"{_shown(im.get('native_type'))} · ip-api: {_shown(im.get('hosting'))}", C_YEL),
            kv("k_ping0", _shown(im.get("ping0_geo"))),
            kv("k_p25", p25), kv("k_dnsbl", dnsbl),
            "", f"{C_YEL}{L['grp_ip_risk']}{C_RST}",
        ]
        comp = _num(ipq.get("composite_risk"))
        if comp is not None:
            sec_netip.append(kv("k_risk", f" {comp:.1f} / 100 · {L.get(f'risk_{tier}', tier)} {C_RST} {C_YEL}{_mini_bar(comp)}", risk_colors.get(tier, C_BG_YEL)))
        srcs = [f"{_shown(x.get('api'))}: {_shown(x.get('raw'))}" for x in _rows(ipq.get("risk_sources"))]
        for i in range(0, len(srcs), 3):
            part = " | ".join(srcs[i:i + 3])
            sec_netip.append(kv("k_risk_src", part) if i == 0 else f"{continuation}{C_GRN}{part}{C_RST}")
        sec_netip += ["", f"{C_YEL}{L['grp_ip_plat']}{C_RST}",
                      kv("k_deny", f" {_fmt(ipq.get('denial_pct'), 1, '%')} ({_shown(ipq.get('denied_count'))}/{_shown(ipq.get('total_probes'))}) {L.get(f'risk_{risk}', risk)} ", risk_colors.get(risk, C_BG_YEL))]
        probes = []
        for pr in _rows(ipq.get("probes")):
            name, ok = _shown(pr.get("service")), pr.get("ok")
            probes.append(f"{C_BG_GRN} ✔ {name} {C_RST}" if ok is True else
                          f"{C_BG_RED} ✘ {name}({_shown(pr.get('code'))}) {C_RST}" if ok is False else
                          f" — {name} ")
        sec_netip.extend("  " + "  ".join(probes[i:i + 5]) for i in range(0, len(probes), 5))
    else:
        sec_netip.append(kv("k_res", skip))

    sec_meta = [L["s9"]]
    m = _mapping(_module(data, "metadata", "meta"))
    life = _mapping(_module(data, "lifetime", "meta"))
    if m:
        sec_meta.append(kv("k_meta", fields("meta_val", m, c="create_fps", s="stat_fps", r="read_fps", d="delete_fps")))
    if life:
        poh = life.get("smart_power_on_hours")
        hours = L["smart_poh"].format(h=poh) if poh is not None else ""
        sec_meta += [kv("k_smart", f"{_shown(life.get('smart_raw_status'))}{hours}", C_YEL),
                     kv("k_ext4", fields("ext4_val", life, cr="fs_created", mc="mount_count", lw="lifetime_writes"))]
    if not m and not life:
        sec_meta.append(kv("k_res", skip))

    footer = ["=" * 80]
    if data.get("report_url"):
        footer.append(kv("k_url", f"{C_U}{data['report_url']}"))
    parts = (sec_overview, sec_disk, sec_endurance, sec_netip, sec_meta)
    return {
        "full": "\n\n".join("\n".join(part) for part in parts) + "\n" + "\n".join(footer),
        **{key: "\n".join(part) for key, part in zip(REPORT_PAGES[1:], parts)},
    }


def render_p2_ansi(data, lang=None, site_url=None):
    return build_sections(data, lang=lang, site_url=site_url)["full"]


ANSI_COLOR_MAP = {
    "30": "#0f172a", "31": "#fb7185", "32": "#6ee7a1", "33": "#fcd34d",
    "34": "#60a5fa", "35": "#c084fc", "36": "#67d8ed", "37": "#f8fafc",
}
ANSI_BG_MAP = {
    "41": "#dc2626", "42": "#16a34a", "43": "#d97706", "46": "#0891b2", "47": "#e2e8f0",
}


def _xml_text(value):
    return _XML_INVALID.sub("", strip_ansi(str(value)))


def _svg_escape(value):
    return html.escape(_xml_text(value))


def parse_ansi_spans(line):
    default = "#e2e8f0"
    fg, bg, bold, ul = default, None, False, False
    spans = []
    for i, token in enumerate(_SGR.split(line)):
        if i % 2:
            for code in token[2:-1].split(";"):
                if code in ("", "0"):
                    fg, bg, bold, ul = default, None, False, False
                elif code in ANSI_COLOR_MAP:
                    fg = ANSI_COLOR_MAP[code]
                elif code in ANSI_BG_MAP:
                    bg = ANSI_BG_MAP[code]
                elif code == "1":
                    bold = True
                elif code == "4":
                    ul = True
                elif code == "22":
                    bold = False
                elif code == "24":
                    ul = False
                elif code == "39":
                    fg = default
                elif code == "49":
                    bg = None
        elif token:
            clean = _xml_text(token)
            if clean:
                spans.append((clean, fg, bg, bold, ul))
    return spans


def render_ansi_to_svg_str(ansi_text, title=None):
    """Render aligned 17px terminal cells independently of installed font metrics."""
    lines = str(ansi_text).split("\n")
    cell, line_height, pad_x, first_y = 10.5, 29, 28, 62
    parsed = []
    for line in lines:
        spans = []
        column = 0
        for txt, fg, bg, bold, ul in parse_ansi_spans(line):
            expanded = []
            for ch in txt:
                if ch == "\t":
                    count = 8 - column % 8
                    expanded.append(" " * count)
                    column += count
                else:
                    expanded.append(ch)
                    column += _vis_width(ch)
            spans.append(("".join(expanded), fg, bg, bold, ul))
        parsed.append((spans, column))

    width = max(1140, math.ceil(max(n for _, n in parsed) * cell + pad_x * 2 + 12))
    height = first_y + (len(lines) - 1) * line_height + 27
    badge = "DiskQuality · Objective Telemetry"
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="terminal-title">',
        f'<title id="terminal-title">{_svg_escape(title or badge)}</title>',
        '<defs><linearGradient id="terminal-bg" x2="0" y2="1"><stop stop-color="#12151c"/><stop offset="1" stop-color="#171b24"/></linearGradient>',
        '<linearGradient id="terminal-accent"><stop stop-color="#22c55e"/><stop offset=".5" stop-color="#06b6d4"/><stop offset="1" stop-color="#6366f1"/></linearGradient>',
        f'<clipPath id="terminal-frame"><rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="12"/></clipPath></defs>',
        f'<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="12" fill="url(#terminal-bg)" stroke="#2a3244"/>',
        '<rect y="1" width="100%" height="3" fill="url(#terminal-accent)" clip-path="url(#terminal-frame)"/>',
        f'<line x1="1" x2="{width - 1}" y1="39.5" y2="39.5" stroke="#2a3244"/>',
        '<circle cx="23" cy="22" r="3.5" fill="#a36879"/><circle cx="37" cy="22" r="3.5" fill="#a89267"/><circle cx="51" cy="22" r="3.5" fill="#689083"/>',
        f'<rect x="{width - 253}" y="11" width="230" height="22" rx="11" fill="#1d2431" stroke="#2a3244"/>',
        f'<text x="{width - 138}" y="26" text-anchor="middle" fill="#a9b8ce" font-family="system-ui,sans-serif" font-size="11">{_svg_escape(badge)}</text>',
        '<g font-family="Sarasa Mono SC,Cascadia Mono,Consolas,Microsoft YaHei,PingFang SC,Noto Sans Mono CJK SC,monospace" font-size="17" xml:space="preserve" style="white-space:pre">',
    ]
    for idx, (spans, _) in enumerate(parsed):
        y = first_y + idx * line_height
        label = "".join(t for t, *_ in spans).strip()
        if re.fullmatch(r"\+{4,}|={4,}", label):
            svg.append(f'<line x1="{pad_x}" x2="{width - pad_x}" y1="{y - 5.5}" y2="{y - 5.5}" stroke="#344055"/>')
            continue
        cur_x = pad_x
        for txt, fg, bg, bold, ul in spans:
            px_w = _vis_width(txt) * cell
            if bg:
                svg.append(f'<rect x="{cur_x - 2:.1f}" y="{y - 17}" width="{px_w + 4:.1f}" height="24" rx="4.5" fill="{bg}"/>')
                if bg == "#e2e8f0":
                    fg = "#0f172a"
                elif bg == "#16a34a":
                    fg = "#08170f"
                elif bg == "#d97706":
                    fg = "#10131c"
                else:
                    fg = "#ffffff"
            # Place padded columns explicitly for SVG engines that use their own
            # font metrics for textLength or trim leading and trailing whitespace.
            text_x = cur_x
            for part in re.split(r"( {2,})", txt):
                visible = part.strip(" ")
                lead = len(part) - len(part.lstrip(" "))
                text_w = _vis_width(visible) * cell
                if visible:
                    weight = ' font-weight="700"' if bold else ''
                    decoration = ' text-decoration="underline"' if ul else ''
                    svg.append(f'<text x="{text_x + lead * cell:.1f}" y="{y}" textLength="{text_w:.1f}" lengthAdjust="spacingAndGlyphs" fill="{fg}"{weight}{decoration}>{_svg_escape(visible)}</text>')
                text_x += _vis_width(part) * cell
            cur_x += px_w
    svg.append("</g></svg>")
    return "\n".join(svg)


def render_nodeseek_md(data, lang=None, site_url=None):
    """Render the NodeSeek image tabs with the visual summary first."""
    L = I18N[_report_lang(data, lang)]
    s_url = str(site_url or data.get("site_url") or DEFAULT_SITE_URL).rstrip("/")
    r_url = str(data.get("report_url") or s_url).rstrip("/")
    tabs = [L["card_tab"], *L["tabs"]]
    keys = ("card", *REPORT_PAGES)
    blocks = [f"::: tab-item {label}\n![{label}]({r_url}/{key}.svg)\n:::" for label, key in zip(tabs, keys)]
    return f"{L['res_link']}：[{r_url}]({r_url})\n\n:::: tabs\n" + "\n\n".join(blocks) + "\n::::\n"


def render_standard_md(data, lang=None, site_url=None):
    """Render the visual summary and a collapsible full terminal report."""
    lang = _report_lang(data, lang)
    L = I18N[lang]
    s_url = str(site_url or data.get("site_url") or DEFAULT_SITE_URL).rstrip("/")
    r_url = str(data.get("report_url") or s_url).rstrip("/")
    summary = "完整终端报告" if lang == "zh" else "Full Terminal Report"
    return (
        f"{L['res_link']}：[{r_url}]({r_url})\n\n"
        f"![DiskQuality Visual Card]({r_url}/card.svg)\n\n"
        f"<details>\n<summary>{summary}</summary>\n\n"
        f"![DiskQuality Full Report]({r_url}/full.svg)\n\n</details>\n"
    )


_CARD_INK = "#edf4ff"
_CARD_MUTED = "#a2b2c9"
_CARD_LINE = "#26344a"
_CARD_GREEN, _CARD_CYAN = "#22c55e", "#38bdf8"
_CARD_AMBER, _CARD_ROSE, _CARD_VIOLET = "#f59e0b", "#f43f5e", "#a78bfa"
_REGION_COLORS = {"reg_ap": _CARD_CYAN, "reg_us": _CARD_VIOLET, "reg_eu": _CARD_GREEN}
_HUB_REGIONS = {"JP": "reg_ap", "SG": "reg_ap", "HK": "reg_ap", "US": "reg_us",
                "DE": "reg_eu", "UK": "reg_eu", "NL": "reg_eu"}


def _hub_region(name):
    match = re.search(r"\(([A-Z]{2})\)", name)
    return _HUB_REGIONS.get(match[1]) if match else None


def _fit_svg_text(value, width, size):
    """Fit a conservative local-font budget, allowing for CJK and wide fallback glyphs."""
    value = " ".join(_xml_text(_shown(value)).split())
    widths = [size * (1.12 if _vis_width(ch) == 2 or ord(ch) > 127 else
                      0.98 if ch in "MW@%&#" else 0.72 if ch.isupper() else
                      0.67 if ch.isdigit() or ch.islower() else 0.57) for ch in value]
    if sum(widths) <= width:
        return value
    used = size
    for i, advance in enumerate(widths):
        used += advance
        if used > width:
            return value[:i].rstrip() + "…"
    return value


class _VisualSVG:
    def __init__(self):
        self.parts = []

    def rect(self, x, y, w, h, fill, radius=0, stroke="none"):
        self.parts.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{radius:g}" fill="{fill}" stroke="{stroke}"/>')

    def line(self, x1, y1, x2, y2, color=_CARD_LINE, width=1):
        self.parts.append(f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{color}" stroke-width="{width:g}" stroke-linecap="round"/>')

    def circle(self, x, y, r, fill):
        self.parts.append(f'<circle cx="{x:g}" cy="{y:g}" r="{r:g}" fill="{fill}"/>')

    def text(self, x, y, value, width, size=14, color=_CARD_MUTED, weight=500, anchor="start"):
        value = _fit_svg_text(value, width, size)
        self.parts.append(f'<text x="{x:g}" y="{y:g}" fill="{color}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(value)}</text>')

    def panel(self, x, y, w, h):
        self.rect(x, y, w, h, "#131926", 16, "#232d42")

    def pill(self, x, y, w, value, color=_CARD_CYAN, size=11):
        self.rect(x, y, w, 24, "#192437", 12, "#2a3b53")
        self.text(x + w / 2, y + 16, value, w - 12, size, color, 700, "middle")

    def bar(self, x, y, w, fraction, color=_CARD_GREEN, height=5):
        self.rect(x, y, w, height, "#26344a", height / 2)
        if fraction is not None and fraction > 0:
            self.rect(x, y, w * min(fraction, 1), height, color, height / 2)

    def ring(self, x, y, score, color):
        radius = 42
        length = 2 * math.pi * radius
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="none" stroke="#26344a" stroke-width="7"/>')
        if score is not None and score > 0:
            offset = length * (1 - min(score, 100) / 100)
            self.parts.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="none" stroke="{color}" stroke-width="7" stroke-linecap="round" stroke-dasharray="{length:.4f} {length:.4f}" stroke-dashoffset="{offset:.4f}" transform="rotate(-90 {x} {y})"/>')
        self.text(x, y + 7, "N/A" if score is None else _fmt(score), 77, 23, _CARD_INK, 760, "middle")


def _scale_fraction(value, maximum):
    return min(value, maximum) / maximum if value is not None and value > 0 and maximum > 0 else 0


def _runs(points):
    run = []
    for point in points:
        if point is not None:
            run.append(point)
        elif run:
            yield run
            run = []
    if run:
        yield run


def _card_radar(svg, x, y, disk, zh):
    labels = ("顺序", "4K", "延迟", "并发", "持久", "元数据") if zh else ("Seq", "4K", "Lat", "Conc", "Sust", "Meta")
    vals = [_num(disk.get(k)) for k in _RADAR_KEYS]
    cx, cy, radius = x + 217, y + 202, 110

    def point(i, ratio):
        angle = math.pi * (i / 3 - 0.5)
        return cx + math.cos(angle) * radius * ratio, cy + math.sin(angle) * radius * ratio

    def coords(points):
        return " ".join(f"{px:.1f},{py:.1f}" for px, py in points)

    for ratio in (.25, .50, .75, 1):
        svg.parts.append(f'<polygon points="{coords(point(i, ratio) for i in range(6))}" fill="none" stroke="{_CARD_LINE}"/>')
        svg.text(cx + 6, cy - radius * ratio + 11, f"{ratio:.0%}", 42, 9, "#879ab5")
    for i, label in enumerate(labels):
        px, py = point(i, 1)
        svg.line(cx, cy, px, py)
        lx, ly = point(i, 1.28)
        anchor = "middle" if i in (0, 3) else "start" if i < 3 else "end"
        svg.text(lx, ly + 5, f"{label} {_shown(disk.get(_RADAR_KEYS[i]))}", 86, 12, _CARD_INK, 650, anchor)
    vertices = [point(i, _scale_fraction(value, 100)) if value is not None else None for i, value in enumerate(vals)]
    if all(p is not None for p in vertices):
        svg.parts.append(f'<polygon points="{coords(vertices)}" fill="#22c55e" fill-opacity=".20" stroke="#45dacc" stroke-width="2"/>')
    else:
        for a, b in zip(vertices, vertices[1:] + vertices[:1]):
            if a is not None and b is not None:
                svg.line(*a, *b, "#45dacc", 2)
    for vertex in vertices:
        if vertex is not None:
            svg.circle(*vertex, 3.5, "#6ee7b7")


def _card_endurance(svg, x, y, sus, plan, zh):
    seq = _mapping(sus.get("seq_write"))
    if seq.get("error"):
        seq = {}
    written = _num(seq.get("w_bytes"))
    badges = (
        (("已写入 " if zh else "Written ") + _fmt(written / 1024**3 if written is not None else None, 1, " GB"), _CARD_GREEN),
        (("均速 " if zh else "Avg ") + _fmt(seq.get("w_bw_mbs"), 1, " MB/s"), _CARD_CYAN),
        ("p99 " + _fmt(seq.get("w_p99_ms"), 1, " ms"), _CARD_AMBER),
    )
    for i, (label, color) in enumerate(badges):
        svg.pill(x + 19 + i * 150, y + 47, 142, label, color)

    points = _rows(sus.get("timeline"))
    series = [[_num(p.get(key)) for p in points] for key in ("w_mb", "w_await")]
    if not any(v is not None for values in series for v in values):
        svg.text(x + 20, y + 118, "无逐分钟采样" if zh else "No per-minute samples", 580)
        return
    left, top, w, h = x + 61, y + 137, 574, 171
    bottom = top + h
    scales = [max(1, max((v for v in values if v is not None), default=0)) for values in series]
    slot = w / len(points)
    phase = [_sequential(pt, plan) for pt in points]
    for i, is_seq in enumerate(phase):
        svg.rect(left + slot * i, top, slot + .1, h, "#152b2c" if is_seq else "#22273e")
    svg.text(left, top - 10, "wMB/s", 76, 11, _CARD_GREEN)
    svg.text(left + w, top - 10, "w_await · ms", 110, 11, _CARD_AMBER, anchor="end")
    svg.pill(x + 20, y + 83, 165, "A · 顺序写入" if zh else "A · Sequential write", _CARD_GREEN)
    svg.pill(x + 195, y + 83, 165, "B · 随机混合" if zh else "B · Random mix", _CARD_VIOLET)
    for i in range(5):
        gy = bottom - h * i / 4
        svg.line(left, gy, left + w, gy)
        svg.text(left - 8, gy + 4, _fmt(scales[0] * (i / 4)), 47, 10, anchor="end")
        svg.text(left + w + 8, gy + 4, _fmt(scales[1] * (i / 4)), 46, 10)

    for idx, values in enumerate(series):
        color = (_CARD_GREEN, _CARD_AMBER)[idx]
        plot = [(left + slot * (i + .5), bottom - h * _scale_fraction(v, scales[idx]))
                if v is not None else None for i, v in enumerate(values)]
        for run in _runs(plot):
            if idx == 0 and len(run) > 1:
                # Horizontal tangents at each real sample smooth the area without overshoot.
                x0, y0 = run[0]
                path = [f"M{x0:.2f},{y0:.2f}"]
                for (xa, ya), (xb, yb) in zip(run, run[1:]):
                    mid = (xa + xb) / 2
                    path.append(f"C{mid:.2f},{ya:.2f} {mid:.2f},{yb:.2f} {xb:.2f},{yb:.2f}")
                curve = " ".join(path)
                svg.parts.append(f'<path d="{curve} V{bottom} H{x0:.2f} Z" fill="url(#card-area)"/>')
                svg.parts.append(f'<path d="{curve}" fill="none" stroke="{color}" stroke-width="2"/>')
            elif len(run) == 1:
                svg.circle(*run[0], 3, color)
            else:
                coords = " ".join(f"{px:.2f},{py:.2f}" for px, py in run)
                svg.parts.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="2" stroke-dasharray="6 5"/>')
    tick_ids = {round(i * (len(points) - 1) / 6) for i in range(7)}
    for i in sorted(tick_ids):
        minute = _num(points[i].get("min"))
        if minute is not None:
            svg.text(left + slot * (i + .5), bottom + 20, _fmt(minute, 0) + (" 分" if zh else "m"),
                     50, 11, anchor="middle")


def _card_workloads(svg, x, y, rows, zh):
    svg.text(x + 38, y, "负载 / 方向" if zh else "WORKLOAD / DIRECTION", 190, 11)
    svg.text(x + 275, y, "MB/s", 60, 11)
    svg.text(x + 394, y, "IOPS", 50, 11)
    svg.text(x + 489, y, "p99 ms", 85, 11)
    maximum = max((bw for _, _, bw, _, _ in rows if bw is not None), default=1)
    for i, (label, direction, bw, iops, tail) in enumerate(rows):
        cy = y + 27 + i * 25
        color = _CARD_CYAN if direction == "R" else _CARD_GREEN
        if i % 2 == 0:
            svg.rect(x + 12, cy - 16, 565, 24, "#172131", 5)
        svg.text(x + 20, cy, direction, 16, 11, color, 700)
        svg.text(x + 38, cy, label, 170, 11, _CARD_INK, 650)
        svg.bar(x + 205, cy - 7, 62, _scale_fraction(bw, maximum), color)
        svg.text(x + 275, cy, _fmt(bw, 2), 86, 12, _CARD_INK)
        svg.text(x + 394, cy, _fmt(iops, 0), 85, 12, _CARD_INK)
        svg.text(x + 489, cy, _fmt(tail, 2), 82, 12, _CARD_AMBER)


def _preview_workloads(data):
    matrix = {str(r["name"]): r for r in _fio_rows(_module(data, "matrix"))}
    conc = {str(r["name"]): r for r in _fio_rows(_module(data, "concurrency"))}
    jobs = [(matrix, f"{name}_{direction}_{depth}", f"{name} {depth}", (direction,))
            for name, depths in (("SEQ1M", ("Q32", "Q1")), ("RND4K", ("Q1", "Q64")))
            for depth in depths for direction in ("R", "W")]
    jobs.extend((conc, name, name, directions) for name, directions in (
        ("PT_SEED_16K_32T", ("R",)), ("BACKUP_64K_16T", ("R", "W"))))
    rows = []
    for source, key, label, directions in jobs:
        row = source.get(key, {})
        for direction in directions:
            prefix = direction.lower()
            values = tuple(_num(row.get(f"{prefix}_{metric}")) for metric in ("bw_mbs", "iops", "p99_ms"))
            if any(v is not None and v > 0 for v in values):
                rows.append((label, direction, *values))
    return rows


def _card_connectivity(svg, x, y, hubs, downloads, ipq, zh):
    if hubs:
        maximum = max(1, max((_num(h.get("max")) or 0 for h in hubs), default=0))
        for i, hub in enumerate(hubs):
            cy = y + i * 23
            label = _shown(hub.get("hub"))
            color = _REGION_COLORS.get(_hub_region(label), _CARD_MUTED)
            svg.circle(x + 20, cy - 4, 3, color)
            svg.text(x + 30, cy, label, 141, 11, _CARD_INK, 620)
            a, mid, b = (_num(hub.get(key)) for key in ("min", "avg", "max"))
            start, length = x + 173, 139
            svg.line(start, cy - 4, start + length, cy - 4, "#293951", 3)
            if mid is not None and mid >= 0:
                if a is not None and b is not None and a >= 0 and b >= 0:
                    svg.line(start + length * _scale_fraction(a, maximum), cy - 4,
                             start + length * _scale_fraction(b, maximum), cy - 4, color, 4)
                svg.circle(start + length * _scale_fraction(mid, maximum), cy - 4, 4, color)
                value = " / ".join(_fmt(v) for v in (a, mid, b))
            else:
                value = ("超时" if zh else "Timeout") if mid is not None else "—"
            svg.text(x + 325, cy, value, 170, 11)
        y += len(hubs) * 23 + 10
    if downloads:
        svg.text(x + 20, y, "大文件下行" if zh else "BULK DOWNLOAD", 145, 11)
        for i, dl in enumerate(downloads):
            svg.pill(x + 20 + i * 250, y + 8, 238,
                     f"{_shown(dl.get('name'))} · {_fmt(dl.get('mbs'), 2, ' MB/s')}")
        y += 59
    probes = {str(p.get("service")): p.get("ok") for p in _rows(ipq.get("probes"))}
    if probes:
        svg.text(x + 20, y, "平台可达性" if zh else "PLATFORM REACHABILITY", 250, 11)
        for i, (service, _) in enumerate(UNLOCK_PROBES):
            state = probes.get(service)
            mark, color = ("✔", "#6ee7a1") if state is True else ("✘", "#fb7185") if state is False else ("—", _CARD_MUTED)
            svg.pill(x + 18 + (i % 5) * 101, y + 10 + (i // 5) * 29, 96,
                     f"{mark} {service}", color, 9.5)
    if not hubs and not downloads and not probes:
        svg.text(x + 20, y, "未测 / 未包含" if zh else "Skipped / Not Included", 500)


def render_visual_card_svg(data, lang=None, site_url=None):
    """Render a standalone 1200-pixel telemetry infographic from available report fields."""
    lang = _report_lang(data, lang)
    zh = lang == "zh"
    L = I18N[lang]
    t, plan = _mapping(data.get("topology")), _mapping(data.get("plan"))
    disk, over, gb, ipq, sus, net = (_mapping(_module(data, key)) for key in
                                     ("disk_score", "overselling", "geekbench", "ip_quality", "sustained", "network"))
    meta, life = (_mapping(_module(data, key, "meta")) for key in ("metadata", "lifetime"))
    hubs = _rows(net.get("hubs"))[:8]
    downloads = _rows(net.get("downloads"))[:2]
    rows = _preview_workloads(data)
    has_radar = any(_num(disk.get(k)) is not None for k in _RADAR_KEYS)
    analytics_h = 360 if has_radar or _rows(sus.get("timeline")) else 142 if sus else 108
    perf_h = max(111, 92 + 25 * len(rows),
                 90 + 23 * len(hubs) + (10 if hubs else 0) + (59 if downloads else 0)
                 + (64 if _rows(ipq.get("probes")) else 0))
    analytics_y = 409
    perf_y = analytics_y + analytics_h + 16
    meta_y = perf_y + perf_h + 16
    meta_h = (105 if meta and life else 83) if meta or life else 0
    foot_y = meta_y + meta_h + (16 if meta_h else 0)
    height = foot_y + (82 if data.get("report_url") else 56)
    svg = _VisualSVG()
    svg.parts.extend([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-labelledby="card-title">',
        f'<title id="card-title">DiskQuality · {_svg_escape(L["card_tab"])}</title>',
        '<defs><linearGradient id="card-hero"><stop stop-color="#11282c"/><stop offset="1" stop-color="#151c31"/></linearGradient>',
        '<linearGradient id="card-accent"><stop stop-color="#22c55e"/><stop offset="1" stop-color="#38bdf8"/></linearGradient>',
        '<linearGradient id="card-area" x2="0" y2="1"><stop stop-color="#22c55e" stop-opacity=".42"/><stop offset="1" stop-color="#22c55e" stop-opacity=".03"/></linearGradient>',
        '<pattern id="card-grid" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#7ba4bf" opacity=".18"/></pattern></defs>',
        '<g font-family="system-ui,Segoe UI,Microsoft YaHei,PingFang SC,Noto Sans CJK SC,sans-serif">',
    ])
    svg.rect(0, 0, 1200, height, "#0b0f17", 22)
    svg.rect(1, 1, 1198, height - 2, "none", 21, "#232d42")
    svg.rect(24, 24, 1152, 166, "url(#card-hero)", 17, "#2a3c51")
    svg.rect(25, 25, 1150, 164, "url(#card-grid)", 16)
    svg.rect(44, 46, 32, 5, "url(#card-accent)", 2.5)
    identity = ("客观存储遥测" if zh else "OBJECTIVE STORAGE TELEMETRY")
    if data.get("sample_preview") is True:
        identity += " · " + ("示例数据" if zh else "SAMPLE DATA")
    svg.text(86, 53, identity, 460, 12, "#92e7da", 750)
    svg.text(42, 113, "DiskQuality", 505, 59, _CARD_INK, 790)
    svg.pill(44, 135, 164, data.get("version") or VERSION, _CARD_GREEN)
    svg.pill(216, 135, 117, t.get("masked_ip"))
    platform = " / ".join(str(t[k]) for k in ("profile", "virt", "arch") if t.get(k))
    svg.pill(341, 135, 206, platform or "—", _CARD_VIOLET)
    svg.line(570, 46, 570, 167, "#33475c")
    svg.text(595, 54, "CPU", 55, 11, "#92e7da", 700)
    svg.text(651, 54, t.get("cpu_model"), 391, 13, _CARD_INK, 650)
    cores = _shown(t.get("cpu_cores"))
    core_unit = "核" if zh else "core" if _num(cores) == 1 else "cores"
    svg.text(1154, 54, f"{cores} {core_unit}", 105, 12, anchor="end")
    svg.text(595, 80, "磁盘" if zh else "DISK", 56, 11, "#92e7da", 700)
    svg.text(651, 80, t.get("disk_model"), 500, 13, _CARD_INK, 650)
    total, used, avail = (_num(plan.get(f"disk_{key}_gb")) for key in ("total", "used", "avail"))
    cap_labels = ("已用", "可用", "总容量") if zh else ("Used", "Avail", "Total")
    for i, (label, value) in enumerate(zip(cap_labels, (used, avail, total))):
        svg.text(595 + i * 185, 112, f"{label} {_fmt(value, 1, ' GB')}", 178, 12, _CARD_INK)
    fractions = [_scale_fraction(v, total or 0) for v in (used, avail)]
    svg.bar(595, 122, 558, 0, _CARD_CYAN, 7)
    if fractions[0]:
        svg.rect(595, 122, 558 * fractions[0], 7, _CARD_GREEN, 3.5)
    free_fraction = min(fractions[1], 1 - fractions[0])
    if free_fraction > 0:
        svg.rect(595 + 558 * fractions[0], 122, 558 * free_fraction, 7, _CARD_CYAN, 3.5)
    svg.text(595, 159, data.get("report_time"), 550, 12)

    labels = ("硬盘综合评分", "超售指数 ↓", "CPU Geekbench", "IP 综合风控 ↓") if zh else (
        "Disk Composite Score", "Overselling Index ↓", "CPU Geekbench", "IP Composite Risk ↓")
    for i, label in enumerate(labels):
        x = 24 + i * 292
        svg.panel(x, 206, 276, 187)
        color = (_CARD_GREEN, _CARD_AMBER, _CARD_VIOLET, _CARD_CYAN)[i]
        svg.rect(x + 18, 226, 3, 14, color, 1.5)
        svg.text(x + 29, 238, label, 232, 15, _CARD_INK, 740)
    ds = _num(disk.get("score"))
    svg.ring(94, 312, ds, _CARD_GREEN)
    svg.text(151, 311, "/ 100", 90, 17)
    if ds is not None and disk.get("grade"):
        svg.pill(151, 326, 86, f"{'等级' if zh else 'Grade'} {disk['grade']}", _CARD_GREEN)
    score = _num(over.get("score"))
    tier = _shown(over.get("tier"))
    short_tiers = {"t0": "Near-Dedicated", "t1": "Light Sharing",
                   "t2": "Moderate Oversell", "t3": "Heavy Oversell"}
    tier_label = L.get(f"os_{tier}", tier) if zh else short_tiers.get(tier, tier)
    over_color = _CARD_ROSE if score is not None and score > 60 else _CARD_AMBER if score is not None and score > 35 else _CARD_GREEN
    svg.ring(386, 312, score, over_color)
    svg.text(444, 300, tier_label if score is not None else "/ 100", 132, 12, _CARD_INK, 670)
    if over.get("media"):
        svg.pill(442, 316, 130, f"{'基准' if zh else 'Ref'} · {_shown(over['media'])}", over_color)
    gb_scores = [_num(gb.get(k)) for k in ("single_core", "multi_core")]
    skipped = "未测 / 未包含" if zh else "Skipped / Not Included"
    if any(value is not None for value in gb_scores):
        svg.pill(626, 251, 230, gb.get("version") or "Geekbench", _CARD_VIOLET)
        for i, (label, value, color) in enumerate(zip((L["gb_sc"], L["gb_mc"]), gb_scores, (_CARD_CYAN, _CARD_VIOLET))):
            y = 300 + i * 40
            svg.text(628, y, label, 135, 12, _CARD_INK, 700)
            svg.text(865, y, _fmt(value, 0), 95, 15, _CARD_INK, 720, "end")
            svg.bar(628, y + 7, 237, _scale_fraction(value, max(1, *(v or 0 for v in gb_scores))), color)
    else:
        svg.text(628, 299, skipped, 236)
    risk = _num(ipq.get("composite_risk"))
    risk_color = _CARD_ROSE if risk is not None and risk > 55 else _CARD_AMBER if risk is not None and risk > 25 else _CARD_GREEN
    if ipq:
        svg.ring(971, 312, risk, risk_color)
        ip_meta = _mapping(ipq.get("meta"))
        native = str(ip_meta.get("native_type") or "")
        for label, local in (("机房/Datacenter", "机房" if zh else "DC"),
                             ("住宅/Residential", "住宅" if zh else "Residential"),
                             ("原生/Native", "原生" if zh else "Native"),
                             ("广播/Broadcast", "广播" if zh else "Broadcast")):
            native = native.replace(label, local)
        hosting = str(ip_meta.get("hosting") or "")
        if hosting.lower() in ("datacenter", "hosting"):
            hosting = "机房" if zh else "DC"
        identity = native
        if hosting and hosting not in native:
            identity = " · ".join(part for part in (native, hosting) if part)
        if identity:
            svg.pill(1025, 256, 137, identity, _CARD_VIOLET, 10)
        tier = ipq.get("composite_tier")
        svg.text(1028, 297, L.get(f"risk_{tier}", tier), 136, 11)
        port = ipq.get("port25_open")
        port_label = L["p25_ok"] if port is True else ("未开放" if zh else "Blocked") if port is False else "—"
        svg.pill(1025, 306, 137, f"Port 25 · {port_label}",
                 _CARD_ROSE if port is False else _CARD_GREEN if port is True else _CARD_MUTED, 10)
        hits = ipq.get("dnsbl_hits")
        dns = f"{len(hits)}/{_shown(ipq.get('dnsbl_total', 3))}" if isinstance(hits, list) else "—"
        svg.pill(1025, 336, 137, f"DNSBL · {dns}", _CARD_ROSE if hits else _CARD_MUTED)
    else:
        svg.text(920, 299, skipped, 236)

    svg.panel(24, analytics_y, 432, analytics_h)
    svg.text(44, analytics_y + 32, "六维硬盘雷达" if zh else "6-Axis Disk Radar", 382, 17, _CARD_INK, 750)
    if has_radar:
        _card_radar(svg, 24, analytics_y, disk, zh)
    else:
        svg.text(44, analytics_y + 71, skipped, 382)
    svg.panel(472, analytics_y, 704, analytics_h)
    svg.text(492, analytics_y + 32, "50% 容量持久曲线" if zh else "50% Capacity Endurance", 656, 17, _CARD_INK, 750)
    if sus:
        _card_endurance(svg, 472, analytics_y, sus, plan, zh)
    else:
        svg.text(492, analytics_y + 71, skipped, 656)

    svg.panel(24, perf_y, 589, perf_h)
    svg.text(44, perf_y + 30, "FIO 矩阵与 PT / 备份" if zh else "FIO Matrix & PT / Backup", 544, 17, _CARD_INK, 750)
    if rows:
        _card_workloads(svg, 24, perf_y + 56, rows, zh)
    else:
        svg.text(44, perf_y + 67, skipped, 544)
    svg.panel(629, perf_y, 547, perf_h)
    svg.text(649, perf_y + 30, "全球延迟与平台可达性" if zh else "Global RTT & Platform Access", 504, 17, _CARD_INK, 750)
    if hubs:
        svg.text(649, perf_y + 49, "TCP RTT · ms", 100, 10)
        for i, (key, color) in enumerate(_REGION_COLORS.items()):
            svg.text(760 + 49 * i, perf_y + 49, L[key], 44, 10, color, 650)
        svg.text(1131, perf_y + 49, "min / avg / max", 105, 10, anchor="end")
    _card_connectivity(svg, 629, perf_y + 70, hubs, downloads, ipq, zh)

    if meta_h:
        svg.panel(24, meta_y, 1152, meta_h)
        svg.text(44, meta_y + 27, "元数据与介质寿命" if zh else "Metadata & Media Lifetime", 1107, 16, _CARD_INK, 750)
        if meta:
            metrics = ("创建", "Stat", "读取", "删除") if zh else ("Create", "Stat", "Read", "Unlink")
            for i, (label, key) in enumerate(zip(metrics, ("create_fps", "stat_fps", "read_fps", "delete_fps"))):
                svg.pill(44 + i * 279, meta_y + 37, 266, f"{label} · {_fmt(meta.get(key), 0, ' f/s')}", _CARD_GREEN)
        if life:
            ly = meta_y + (83 if meta else 56)
            hours = life.get("smart_power_on_hours")
            smart = f"SMART · {_shown(life.get('smart_raw_status'))}"
            if hours is not None:
                smart += f" · {_shown(hours)} h"
            ext = L["ext4_val"].format(cr=_shown(life.get("fs_created")), mc=_shown(life.get("mount_count")),
                                       lw=_shown(life.get("lifetime_writes")))
            svg.text(44, ly, smart, 386, 12)
            svg.text(438, ly, f"Ext4 · {ext}", 713, 12)
    svg.line(25, foot_y, 1175, foot_y)
    svg.text(32, foot_y + 29, "github.com/arimrs/DiskQuality", 330, 13, _CARD_CYAN, 680)
    s_url = site_url or data.get("site_url") or DEFAULT_SITE_URL
    svg.text(1168, foot_y + 29, f"bash <(curl -sL {s_url})", 730, 13, _CARD_INK, 620, "end")
    if data.get("report_url"):
        svg.text(32, foot_y + 55, data["report_url"], 1135, 12)
    svg.parts.append("</g></svg>")
    return "\n".join(svg.parts)


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

    # 3. Time-weighted visual progress bar with live speed-calibrated ETA (kaomoji only at 100% end)
    end_kaomojis = (
        "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧", "( •̀ ω •́ )✧", "(๑•̀ㅂ•́)و✧", "ヾ(•ω•`)o",
        "(o´ω`o)ﾉ", "٩(｡•́‿•̀｡)۶", "(*^▽^*)", "(☆▽☆)",
        "ヽ(✿ﾟ▽ﾟ)ノ", "(｡･ω･｡)ﾉ♡", "(*≧ω≦)", "(づ￣ 3￣)づ",
        "٩(ˊᗜˋ*)و", "✧*｡٩(ˊᗜˋ*)و✧*｡", "(￣▽￣)ノ", "o(*￣▽￣*)ブ",
        "(≧▽≦)/", "ヾ(≧▽≦*)o", "(●'◡'●)", "ヽ(•̀ω•́ )ゝ",
    )

    plan = calc_adaptive_plan(args.target, args.minutes)
    topo = collect_system_topology(args.target, forced_profile=getattr(args, "profile", "auto"))
    ioe, io_direct = probe_fio_capabilities(work_dir)
    plan["ioengine"] = ioe
    plan["direct"] = io_direct
    prof = topo.get("profile", "vps")
    if prof == "dedicated":
        plan["matrix_file_gb"] = min(8.0, max(plan["matrix_file_gb"], 4.0))
        plan["stress_file_gb"] = min(plan["stress_file_gb"], 2000.0)
    elif prof == "container":
        plan["matrix_file_gb"] = min(plan["matrix_file_gb"], 2.0)

    rt, msz = plan["matrix_item_sec"], plan["matrix_file_gb"]
    probe_w = float(getattr(args, "probe_write_mbs", 0.0) or 0.0)
    if probe_w <= 0.0:
        # Fast 1s 64MB fallback write probe if invoked directly without run.sh
        pf = os.path.join(work_dir, ".py_probe.bin")
        t0_p = time.perf_counter()
        try:
            blk = b"\x00" * (1024 * 1024)
            with open(pf, "wb") as f:
                for _ in range(64): f.write(blk)
                f.flush(); os.fsync(f.fileno())
            probe_w = round(64.0 / max(time.perf_counter() - t0_p, 0.01), 1)
        except Exception:
            probe_w = 150.0
        finally:
            try: os.remove(pf)
            except Exception: pass

    def _calc_phase_secs(w_mbs):
        w = max(10.0, float(w_mbs or 150.0))
        m_alloc = min(150.0, (msz * 1024.0) / w)
        s_alloc = min(120.0, ((plan["stress_file_gb"] * 1024.0) / w) * 0.12)
        return {
            "topo": 3.0,
            "ioping": 12.0 if sel["ioping"] else 0.0,
            "matrix_first": (rt + m_alloc) if sel["matrix"] else 0.0,
            "matrix_each": float(rt) if sel["matrix"] else 0.0,
            "prod_each": float(rt) if sel["prod"] else 0.0,
            "conc_each": float(rt) if sel["concurrency"] else 0.0,
            "sust_a": (plan["sustained_seq_sec"] + s_alloc) if sel["sustained"] else 0.0,
            "sust_b": float(plan["sustained_mix_sec"]) if sel["sustained"] else 0.0,
            "network": 22.0 if sel["network"] else 0.0,
            "ip_quality": 18.0 if sel["ip_quality"] else 0.0,
            "meta": (35.0 if w < 120.0 else 12.0) if sel["meta"] else 0.0,
            "geekbench": 180.0 if gb_mode != "skip" else 0.0,
            "cleanup": 4.0,
        }

    psec = _calc_phase_secs(probe_w)
    total_est_sec = (
        psec["topo"] + psec["ioping"]
        + (psec["matrix_first"] + psec["matrix_each"] * 13 if sel["matrix"] else 0.0)
        + (psec["prod_each"] * 4 if sel["prod"] else 0.0)
        + (psec["conc_each"] * 4 if sel["concurrency"] else 0.0)
        + psec["sust_a"] + psec["sust_b"]
        + psec["network"] + psec["ip_quality"] + psec["meta"] + psec["geekbench"] + psec["cleanup"]
    )
    eta_state = {"done_sec": 0.0, "total_sec": max(1.0, total_est_sec), "w_mbs": probe_w}

    def _fmt_eta(rem_s):
        rem_s = max(0, int(round(rem_s)))
        if rem_s == 0:
            return "0s"
        mm, ss = divmod(rem_s, 60)
        return f"{mm}m{ss:02d}s" if mm > 0 else f"{ss}s"

    def show_bar(msg_zh, msg_en, advance_sec=0.0, suffix="", force_100=False):
        eta_state["done_sec"] = min(eta_state["total_sec"], eta_state["done_sec"] + max(0.0, float(advance_sec)))
        if force_100:
            pct = 100
            rem_s = 0.0
        else:
            pct = min(99, int(round(eta_state["done_sec"] * 100.0 / max(1.0, eta_state["total_sec"]))))
            rem_s = max(0.0, eta_state["total_sec"] - eta_state["done_sec"])
        filled = int(round(24 * pct / 100.0))
        bar = "█" * filled + "░" * (24 - filled)
        ts = datetime.now(tz).strftime("%H:%M:%S")
        msg = msg_en if lang == "en" else msg_zh
        tail = f" {suffix}" if suffix else ""
        eta_str = f" · ETA ~{_fmt_eta(rem_s)}" if not force_100 else " · ETA 0s"
        print(f"{C_CYN}[{ts}]{C_RST} {C_GRN}[{bar}]{C_RST} {C_YEL}{pct:3d}%{C_RST}{C_CYN}{eta_str:<15}{C_RST} | {msg}{tail}", flush=True)

    show_bar(
        f"预热测速 {probe_w:.1f} MB/s · {prof.upper()} ({topo['virt']}/{topo['arch']}) · 总预计 ~{_fmt_eta(eta_state['total_sec'])}",
        f"Probe {probe_w:.1f} MB/s · {prof.upper()} ({topo['virt']}/{topo['arch']}) · Total ETA ~{_fmt_eta(eta_state['total_sec'])}",
        advance_sec=psec["topo"],
    )

    ioping_res = None
    if sel["ioping"]:
        show_bar("正在运行底层延迟基线测试 (ioping)...", "Running latency baseline (ioping)...", advance_sec=0)
        ioping_res = run_ioping_tests(work_dir)
        show_bar("底层延迟基线测试 (ioping) 完成", "Latency baseline (ioping) completed", advance_sec=psec["ioping"])

    mfile, sfile = os.path.join(work_dir, "matrix.bin"), os.path.join(work_dir, "stress_50pct.bin")
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
            step_w = psec["matrix_first"] if idx == 1 else psec["matrix_each"]
            show_bar(f"FIO 矩阵 [{idx}/{len(specs)}] 正在测 {n}...", f"FIO Matrix [{idx}/{len(specs)}] {n}...", advance_sec=0)
            res_j = run_fio_job(n, mfile, msz, rw, bs, qd, nj, rt, d, mix, fs, ioengine=ioe)
            matrix_res.append(res_j)
            # Re-calibrate remaining sustained ETA right after real SEQ1M_W_Q32 write speed is measured
            if n == "SEQ1M_W_Q32" and not res_j.get("error") and res_j.get("w_bw_mbs", 0) > 5:
                real_w = res_j["w_bw_mbs"]
                new_p = _calc_phase_secs(real_w)
                delta_s = (new_p["sust_a"] - psec["sust_a"]) + (new_p["meta"] - psec["meta"])
                psec["sust_a"], psec["meta"] = new_p["sust_a"], new_p["meta"]
                eta_state["total_sec"] = max(eta_state["done_sec"] + 10.0, eta_state["total_sec"] + delta_s)
            show_bar(f"FIO 矩阵 [{idx}/{len(specs)}] {n} 完成", f"FIO Matrix [{idx}/{len(specs)}] {n} done", advance_sec=step_w)

    prod_res = None
    if sel["prod"]:
        pspecs = [
            ("OLTP_8K_Q32", "randrw", "8K", 32, 2, io_direct, 70, None), ("WEB_16K_Q8", "randrw", "16K", 8, 2, io_direct, 50, None),
            ("WAL_4K_FSYNC1", "write", "4K", 1, 1, io_direct, None, 1), ("CONG_4K_FSYNC4", "randwrite", "4K", 32, 2, io_direct, None, 4),
        ]
        prod_res = []
        for idx, (n, rw, bs, qd, nj, d, mix, fs) in enumerate(pspecs, 1):
            show_bar(f"生产模型 [{idx}/{len(pspecs)}] 正在测 {n}...", f"Production [{idx}/{len(pspecs)}] {n}...", advance_sec=0)
            prod_res.append(run_fio_job(n, mfile, msz, rw, bs, qd, nj, rt, d, mix, fs, ioengine=ioe))
            show_bar(f"生产模型 [{idx}/{len(pspecs)}] {n} 完成", f"Production [{idx}/{len(pspecs)}] {n} done", advance_sec=psec["prod_each"])

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
            show_bar(f"小量多并发 [{idx}/{len(cspecs)}] 正在测 {n}...", f"Concurrency [{idx}/{len(cspecs)}] {n}...", advance_sec=0)
            conc_res.append(run_fio_job(n, mfile, msz, rw, bs, qd, nj, rt, d, mix, fs, ioengine=ioe))
            show_bar(f"小量多并发 [{idx}/{len(cspecs)}] {n} 完成", f"Concurrency [{idx}/{len(cspecs)}] {n} done", advance_sec=psec["conc_each"])

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
                advance_sec=0,
            )
            sw = run_fio_job("SUSTAINED_50PCT_SEQ_W", sfile, plan["stress_file_gb"], "write", "1M", 16, 1, plan["sustained_seq_sec"], io_direct, ioengine=ioe)
            show_bar("50% 容量持久压测 阶段 A 完成，进入阶段 B 随机混合...", "50% Endurance Phase A done, starting Phase B Mixed...", advance_sec=psec["sust_a"])
            ms = run_fio_job("SUSTAINED_50PCT_MIX", sfile, plan["stress_file_gb"], "randrw", "8K", 32, 2, plan["sustained_mix_sec"], io_direct, 30, ioengine=ioe)
            show_bar("50% 容量持久压测 阶段 B 完成", "50% Endurance Phase B completed", advance_sec=psec["sust_b"])
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
        show_bar("正在测试全球 8 大单播节点延迟与大文件下行...", "Running 8-hub global TCP latency & bulk download...", advance_sec=0)
        net_res = run_global_network_tests()
        show_bar("国际互联与大文件下行测试完成", "Global connectivity & download tests completed", advance_sec=psec["network"])

    ipq_res = None
    if sel["ip_quality"]:
        show_bar("正在探测 IP 质量、25 端口与 10 大平台可达性...", "Probing IP quality, Port 25 & 10-platform reachability...", advance_sec=0)
        ipq_res = run_ip_quality_tests()
        show_bar("IP 质量与被拒访问概率评估完成", "IP quality & denial probability completed", advance_sec=psec["ip_quality"])

    meta_res, life_res = None, None
    if sel["meta"]:
        show_bar("正在运行 10,000 小文件元数据与 SMART/Ext4 寿命读取...", "Running 10,000-file metadata & SMART/Ext4 lifetime...", advance_sec=0)
        meta_res = run_metadata_bench(work_dir)
        life_res = collect_poweron_lifetime(topo["mount_dev"], topo["base_dev"], fs_type=topo.get("fs_type", "ext4"))
        show_bar("元数据与介质寿命检测完成", "Metadata & lifetime diagnostics completed", advance_sec=psec["meta"])

    gb_res = None
    if gb_mode != "skip":
        gb_lbl = "Geekbench 5" if gb_mode == "gb5" else "Geekbench 6"
        show_bar(f"正在运行完整 {gb_lbl} CPU 单核/多核跑分（约 2–4 分钟）...", f"Running full {gb_lbl} CPU Single/Multi-Core benchmark (~2–4m)...", advance_sec=0)
        gb_res = run_geekbench(gb_mode, work_dir)
        show_bar(f"{gb_lbl} CPU 跑分完成", f"{gb_lbl} CPU benchmark completed", advance_sec=psec["geekbench"])

    overselling_res = calc_overselling_index(topo, matrix_res, prod_res, sustained_res)
    disk_score_res = calc_disk_score(topo, ioping_res, matrix_res, prod_res, conc_res, sustained_res, meta_res)

    thorough_cleanup(work_dir, args.target, do_trim=True)
    end_emo = random.choice(end_kaomojis)
    show_bar("全部测试已完成，环境已彻底清理干净！", "All tests completed & environment thoroughly cleaned!", advance_sec=psec["cleanup"], suffix=end_emo, force_100=True)

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
                headers={"Content-Type": "application/json", "User-Agent": "DiskQuality-CLI/1.0.9"}, method="POST",
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
    ap.add_argument("--probe-write-mbs", type=float, default=0.0)
    ap.add_argument("--site-url", default=DEFAULT_SITE_URL)
    ap.add_argument("--upload-url", default="")
    run_benchmark_cli(ap.parse_args())


if __name__ == "__main__":
    main()
