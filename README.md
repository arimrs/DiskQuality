**English** | [简体中文](README.zh-CN.md)

# DiskQuality

[![Version](https://img.shields.io/badge/version-v1.0.5-22c55e.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An ultra-lightweight, bilingual (**English / 简体中文**), purely objective Linux VPS benchmark suite built for **PT seedboxes, storage VPS, and backup servers**, paired with an ephemeral paginated query server.

- **Adaptive 50% Capacity Algorithm & >65% Disk Guard**: Automatically scales the endurance stress file to **50% of total disk capacity** (clamped to ≤ 80% of free space) within a **20-minute budget**. Runs a pre-test disk usage scan and **automatically cancels if disk usage exceeds 65%**.
- **Live Progress Bar & Thorough Pre/Post Cleanup**: Real-time visual progress bar with friendly kaomoji feedback, plus thorough environment cleanup before starting, after completion, and on `Ctrl+C` (`SIGINT`/`SIGTERM`/`EXIT` traps + `fstrim`).
- **Comprehensive PT / Storage / Backup Coverage (9 Dimensions)**: Covers Disk Topology, `ioping` latency, FIO 14-item Direct I/O matrix, **Small-Block High-Concurrency I/O** (PT seeding / piece hashing / multi-stream backup / 4K burst), production `fsync`, 50%-capacity endurance + per-minute `iostat`, 10k-file metadata + SMART/Ext4 lifetime, **Global Connectivity & Bulk Download Throughput**, and **IP Quality, Platform Access & Empirical Access Denial Probability**.
- **Pure Objective Metrics**: Zero subjective recommendations or tuning opinions — raw, reproducible numbers only.
- **Interactive Module Selection**: Choose language at startup (`zh` / `en`), pre-flight path & dependency check (exits cleanly if installation is declined), and NodeQuality-style `[y/n]` module toggles (skipped sections are rendered as bold red **`???`**).
- **Paginated Web Report & Enhanced Readability**: 6-page interactive paginated report viewer (`← Prev` / `Next →` buttons + keyboard `←`/`→` arrows + Full Panorama view) with enlarged high-contrast typography (`15.5px` / `26px` line height), zero-persistence `/tmp` storage with **1-hour TTL auto-destroy**, client-side Canvas PNG export, and one-click **Copy Text / NodeSeek  / Markdown / HD PNG / SVG** buttons.

---

## Quick Start

Run directly on any Linux VPS (Debian / Ubuntu / RHEL / Rocky / AlmaLinux):

```bash
bash <(curl -sL https://test.sakurado.top)
```

Optional CLI flags:
- `-m 20`: Total time budget in minutes (default: `20`)
- `-d /path`: Target mount directory (default: `/`)
- `-y`: Non-interactive mode (auto-accept all modules)

---

## Benchmark Dimensions

1. **System & Block Device Topology**: Virtualization, OS/kernel, CPU/RAM/Swap, disk model, capacity, `ROTA`, I/O scheduler, `write_cache`, `read_ahead_kb`, sector size, TRIM/Discard.
2. **Latency Baseline **: Direct random seek, Page Cache read, and `fsync` sync write (`min / avg / max / mdev`).
3. **FIO 14-Item Synthetic Matrix (`libaio`, `direct=1`)**: Sequential 1MB R/W (`QD=1`, `QD=32×4`), Random 4KB R/W (`QD=1`, `QD=16`, `QD=64×4`), Random 8K/16K 70/30, Sequential 128K 50/50, and Buffered 1M 50/50 (`direct=0`) with throughput, IOPS, p95, and p99 latency.
4. **Small-Block High-Concurrency I/O (PT / Backup)**:
   - `PT_SEED_16K_32T` (16KB 80/20 R/W, 32 threads, `QD=4`) — multi-peer PT seeding & downloading
   - `PT_HASH_256K_16T` (256KB random read, 16 threads, `QD=4`) — concurrent torrent piece hashing
   - `BACKUP_64K_16T` (64KB random write, 16 threads, `QD=4`) — parallel rsync / borg / restic streams
   - `BURST_4K_32T` (4KB 50/50 R/W, 32 threads, `QD=2`) — high-concurrency metadata & small-file bursts
5. **Production Workloads & `fsync` Commit**: OLTP 8K (`QD=32`), Web 16K (`QD=8`), WAL 4K (`fsync=1`, `QD=1`), Congested `fsync=4` (`QD=32`).
6. **50% Capacity Adaptive Endurance Stress + Per-Minute `iostat`**: Half budget continuous sequential write + half budget random mixed stress across a 50%-capacity file, sampled every 5 seconds and aggregated per minute (`r/s`, `w/s`, `rMB/s`, `wMB/s`, `w_await`, `%util`).
7. **Filesystem Metadata & Lifetime Diagnostics**: 10,000 × 4KB create/stat/read/unlink rates, `smartctl` SMART status, and Ext4 superblock creation time / mount count / lifetime writes.
8. **Global Connectivity & Bulk Download Throughput**: TCP handshake RTT & loss to 8 global hubs (Tokyo, Singapore, Hong Kong, Los Angeles, New York, Frankfurt, London, Amsterdam) + Cloudflare 50MB & CacheFly 100MB sustained download throughput.
9. **IP Quality, Platform Access & Empirical Denial Probability**: ASN/Org/Location/Hosting classification, HTTP reachability probes across 10 platforms (Cloudflare, Google, YouTube, Netflix, Disney+, TikTok, OpenAI, Reddit, GitHub, Steam), calculated **Access Denial Probability (%)** + risk tier, and outbound SMTP Port 25 check.

---

## Self-Hosting the Ephemeral Query Server

```bash
git clone https://github.com/arimrs/DiskQuality.git /opt/diskquality-server
cp /opt/diskquality-server/deploy/diskquality-web.service /etc/systemd/system/
# Edit DQ_SITE_URL in /etc/systemd/system/diskquality-web.service
systemctl daemon-reload && systemctl enable --now diskquality-web.service
```

Reverse proxy port `8765` with Nginx/Caddy (Cloudflare CDN can cache `/run.sh` and `/core.py` via `Cache-Control: public, max-age=300`).

---

## Acknowledgments & Upstream Tools

This project is built upon and inspired by the following outstanding open-source projects and public test endpoints:

- **fio** — https://github.com/axboe/fio *(Direct I/O & high-concurrency storage engine)*
- **ioping** — https://github.com/koct9i/ioping *(low-level disk latency probing)*
- **sysstat / iostat** — https://github.com/sysstat/sysstat *(per-minute block device telemetry)*
- **smartmontools** — https://www.smartmontools.org *(SMART health & power-on telemetry)*
- **e2fsprogs / tune2fs** — https://e2fsprogs.sourceforge.net *(Ext4 superblock lifetime inspection)*
- **curl** — https://curl.se *(HTTP platform reachability & download probes)*
- **Cloudflare Speed** — https://speed.cloudflare.com *(global CDN throughput test endpoint)*
- **CacheFly CDN** — https://cachefly.cachefly.net *(bulk download throughput endpoint)*
- **ip-api / ipinfo** — https://ip-api.com / https://ipinfo.io *(ASN & hosting classification metadata)*
- **NodeQuality** — https://github.com/LloydAsp/NodeQuality *(interactive workflow & web report UX inspiration)*
- **HardwareQuality** — https://github.com/xykt/HardwareQuality *(terminal ANSI layout inspiration)*
- **IPQuality** — https://github.com/xykt/IPQuality *(IP quality & platform access check inspiration)*

---

## Open-Source Usage Terms & Disclaimer

### 1. Free to Use & Modify — No Paid Derivatives
- This project is **100% free and open-source**.
- **Secondary development and modification are welcome** for personal learning, research, and free community sharing, provided original attribution and this notice are retained.
- **Strictly NO paid/commercial derivatives**: You may **NOT** sell this project or any modified/derivative version of it, charge fees for customized builds, licensing, paid benchmark services, or repackage it into any closed-source or profit-driven product.

### 2. Strict Legal Compliance
- **No Illegal Use**: It is **strictly prohibited** to use this project (or any derivative work) to violate any applicable local, national, or international laws and regulations — including, without limitation, unauthorized stress testing, maliciously exhausting third-party disk/bandwidth/compute resources, DoS/DDoS attacks, or interfering with computer information systems.
- Users must ensure they only run this tool on servers they legally own or have explicit written authorization to test. All legal responsibilities and consequences arising from misuse are borne solely by the user; the author assumes zero liability.

### 3. General Disclaimers
1. **Disk Wear, Heavy I/O & Provider ToS**: This benchmark performs sustained Direct I/O writes up to 50% of total disk capacity (with a >65% pre-scan abort guard and ≤80% free-space clamp). You are solely responsible for evaluating SSD TBW wear, hardware impact, and your VPS provider's Terms of Service (ToS); any throttling, suspension, or data loss is at your own risk.
2. **Zero Persistence & AS-IS Warranty**: The ephemeral query server provides **no permanent storage** — all uploaded reports and generated views are automatically destroyed after **1 hour**. This software is provided **"AS IS"** without warranty of any kind, express or implied (including merchantability, fitness for a particular purpose, or non-infringement). The author shall not be liable for any direct, indirect, incidental, special, or consequential damages.
3. **Objective Metrics & Third-Party Services**: All outputs are raw objective measurements and do not constitute purchasing advice or performance guarantees. Upstream open-source tools and public test endpoints belong to their respective owners, who are solely responsible for their availability and accuracy.
4. **Privacy**: Public IPv4/IPv6 addresses in reports are automatically masked (`x.x.*.*` / `xxxx:xxxx:*:*`) and hostnames are never uploaded. Do not manually attach sensitive personal or system information.
