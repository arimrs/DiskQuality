# Changelog / 更新日志

## v1.0.8 (2026.11.26)
### English
- **Bug Fixes & Stability**:
  - Fixed `iostat` column misalignment on newer Linux distros (`sysstat 12.x`) by reading column headers dynamically.
  - Fixed FIO output parsing failures when warnings appear before JSON, added `ioping` `fsync` fallback when `-D` is unsupported, improved IPv6-only compatibility, and prevented inflated disk scores when FIO is skipped.
- **Cleaner Categorized Layout**:
  - Grouped metrics into clear visual blocks (Hardware vs Scores, Sequential vs Random I/O, Regional network hubs, IP identity / multi-API risk / platform unlock) instead of flat walls of numbers.
- **Multi-Source IP Risk Score with Full Breakdown**:
  - Added **IPPure, IP2Location, ping0.cc, ProxyCheck, Scamalytics, ip-api, and 3 DNSBL blacklists** to calculate a single 0–100 composite risk score — and prints each API's exact individual score so you can see where the number came from.

### 简体中文
- **修了一批影响实际跑分的 Bug**：
  - 修复了 Debian 12/13 等新系统（`sysstat 12.x`）下 `iostat` 读写列错位的问题，现在按表头自动认列，不再写死列号。
  - 修复了 FIO 带警告信息时解析报错、`ioping` 同步写在某些虚拟盘报 `N/A`、纯 IPv6 小鸡测速失败，以及跳过 FIO 时硬盘综合分虚高的问题。
- **报告排版重新按类别归拢**：
  - 不再把一堆数字平铺到底，把硬件拓扑与评分、顺序读写与 4K 随机、亚太/美洲/欧洲互联、IP 画像与平台解锁都拆成清晰的小块，扫一眼就能看懂重点。
- **IP 质量检测升级 + 风控构成全透明**：
  - 接入 **IPPure、IP2Location、ping0.cc、ProxyCheck、Scamalytics、ip-api 与 3 个主流黑名单（DNSBL）** 综合算出 0–100 风控值（越低越干净），并把每个 API 单独给的分原原本本列在下面，不再黑盒打分。

---

## v1.0.7 (2026.11.25)
### English
- **Comprehensive Quantifiable Disk Score (`0–100` & Grade `S+`–`D`)**:
  - Added weighted composite scoring across Sequential Throughput (20%), Random 4K IOPS (25%), Tail Latency & `fsync` (15%), High-Concurrency PT/Backup I/O (15%), 50% Sustained Endurance (15%), and Filesystem Metadata (10%), alongside the Dedicated-baseline Overselling Index (`0–100`, lower is better).
- **Speed-Probe Calibrated ETA**:
  - Added a quick 64 MB Direct I/O write/read pre-probe before module selection to calibrate estimated execution time based on actual measured disk speed and target capacity.
- **Dedicated / VDS / Non-KVM & Multi-Arch Auto-Scheduling**:
  - Added automatic platform classification (`Dedicated`, `VDS`, `VPS`, `LXC/OpenVZ/Docker`), FIO `ioengine`/`O_DIRECT` auto-fallback, NVMe/RAID/non-ext4 compatibility, and `apk`/`pacman`/`zypper` package manager support.
- **Larger Dynamic-Width SVG Typography & Web-Only Specular Sheen**:
  - Upgraded SVG report rendering to `17.5px` font (`29px` line-height) with dynamic auto-expanding width (`≥ 1140px`) and refined monospace/CJK typography so NodeSeek image embeds stay crisp and unclipped.
  - Added a subtle cursor-reactive specular light effect exclusively on the web report viewer (zero effect on exported SVG/PNG images).
  - Hardened Geekbench 5/6 HTML score parsing to reliably extract Single-Core and Multi-Core scores.

### 简体中文
- **新增硬盘综合量化评分（`0–100` 分与 `S+`–`D` 等级）**：
  - 综合顺序吞吐（20%）、随机 4K IOPS（25%）、尾延迟与 `fsync`（15%）、高并发 PT/备份 I/O（15%）、50% 容量持久稳态（15%）及元数据吞吐（10%）输出客观加权总分与各分项指标，并与独立服务器基准超售指数（越低越好）并列展示。
- **预热测速校准预计耗时**：
  - 在交互选测前新增 64 MB 快速直写/读预热探测，结合实测读写速度与目标盘容量动态核算各模块与总执行时间。
- **独立服务器 / VDS / 非 KVM 与多架构自适应调度**：
  - 支持裸金属独服、VDS、KVM/Xen/VMware、LXC/OpenVZ/Docker 与多架构自动识别，内置 FIO 引擎与 `O_DIRECT` 自动降级、NVMe/非 ext4 兼容及 `apk`/`pacman`/`zypper` 包管理器支持。
- **大字号自适应宽度图片渲染与网页端动态光影**：
  - SVG 报告升级为 `17.5px` 大字号（`29px` 行高）、灵动等宽字体栈与动态自适应画布宽度（`≥ 1140px`），确保 NodeSeek 图片排版清晰完整无截断。
  - 在线报告页新增随鼠标移动的柔和光影动态效果（仅网页端生效，不影响导出的 SVG/PNG 图片）。
  - 增强 Geekbench 5/6 官方结果页解析正则，修复部分场景下单多核分数显示 `N/A` 的问题。

---

## v1.0.6 (2026.11.23)
### English
- **Full Geekbench 5 / Geekbench 6 CPU Benchmark (`Single-Core` & `Multi-Core`)**:
  - Added interactive CPU benchmark selector (`[1=GB5 (default), 2=GB6, 3=Skip]`) supporting both `x86_64` and `aarch64`, with unified Single-Core / Multi-Core badge display and official Geekbench result URLs (skipped renders as bold red `???`).
- **Fixed SVG Highlight-Bar Left-Edge Text Clipping Bug**:
  - Locked every SVG `<text>` and `<rect>` span to identical pixel coordinates (`x`) with accurate CJK (`14.2px`) vs ASCII (`8.4px`) width math, completely eliminating left-edge truncation on `Intel(R)`, `╚═`, `内存`, and `Virtual Disk` highlight bars across all browsers and OSes.
- **Persistent Report Storage**:
  - Removed the 1-hour auto-destroy limit by default (`DQ_TTL_SECONDS=0`) so published report links and NodeSeek image embeds remain permanently accessible.

### 简体中文
- **新增完整 Geekbench 5 / Geekbench 6 CPU 单核与多核跑分**：
  - 启动交互新增 `5/5` 选项，支持按 `1 / 2 / 3` 选择 **Geekbench 5（默认）/ Geekbench 6 / 跳过**，兼容 `x86_64` 与 `aarch64`，统一输出单核 / 多核分数徽章与官方详情链接（跳过时标红 `？？？`）。
- **彻底修复 SVG 高亮条左侧文字截断 / 错位 Bug**：
  - 重写 SVG 渲染器坐标计算，将每个高亮 `<rect>` 与对应 `<text>` 锁定在同一精确像素 `x` 坐标，并按中英文实际字宽（CJK `14.2px` / ASCII `8.4px`）独立核算背景条宽度，彻底根治跨浏览器/跨系统下 `Intel(R)`、`内存`、`Virtual Disk` 左侧被吞字的问题。
- **报告永久保存升级**：
  - 默认移除 1 小时销毁限制（`DQ_TTL_SECONDS=0`），已生成的报告链接与 NodeSeek 多图帖子长期有效不再裂图。

---

## v1.0.5 (2026.11.23)
### English
- **Security & Privacy Vulnerability Fixes**:
  - Fixed a **Stored XSS** vulnerability in `/r/<id>` where unescaped `</script>` sequences inside uploaded JSON fields could break out of inline `<script>` blocks (`safe_json_for_script` escaping).
  - Enforced **server-side privacy sanitization** on `POST /api/v1/record` (strips any `hostname`/`ip`/`real_ip` fields and re-masks IPv4/IPv6 addresses before persistence in `/tmp`).
  - Hardened web report privacy & security headers: added `X-Robots-Tag: noindex, nofollow, noarchive`, `<meta name="robots" content="noindex, nofollow, noarchive">`, `Referrer-Policy: no-referrer`, strict `Content-Security-Policy`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Cache-Control: no-store` on `/r/<id>` and `.svg`, plus `/robots.txt` disallowing `/r/` and `/api/`.
  - Hardened CLI subprocess commands with `shlex.quote()` against shell argument injection and added rate-limiting on `/api/v1/stats?hit=1`.
- **UX Improvements**:
  - Merged 8 interactive `[y/n]` prompts into **4 intuitive groups** (Disk Performance Suite, 50% Endurance Stress, Global Network & IP Quality, Metadata & Lifetime).
  - Added **disk-aware estimated execution time** (calculated from target disk capacity and SSD/NVMe vs HDD media type before launching).

### 简体中文
- **安全与隐私漏洞修复**：
  - 修复 `/r/<id>` 网页端因内联 `<script>` 未转义 `</script>` 导致的 **存储型 XSS 漏洞**（新增 `safe_json_for_script` 安全转义）。
  - 在服务端 `POST /api/v1/record` 强制实施**服务端隐私脱敏校验**，入库前自动剥离 `hostname` / `ip` / `real_ip` 等敏感字段并对 IPv4/IPv6 二次打码，杜绝旧客户端或异常载荷泄露隐私。
  - 全面加固网页端隐私保护响应头：新增 `X-Robots-Tag: noindex, nofollow, noarchive`、`<meta name="robots" ...>`、`Referrer-Policy: no-referrer`、严格 `CSP`、`X-Frame-Options: DENY`、`X-Content-Type-Options: nosniff`、`/r/` 与 `.svg` 强制 `Cache-Control: no-store` 及 `/robots.txt` 禁止收录 `/r/` 与 `/api/`。
  - 对底层脚本全部动态路径与设备参数补充 `shlex.quote()` 防命令注入加固，并为 `/api/v1/stats?hit=1` 增加防刷频控。
- **交互体验优化**：
  - 将原本 8 次 `[y/n]` 确认合并精简为 **4 大同类测试组**，显著减少按键次数。
  - 新增**基于硬盘容量与介质类型（SSD/NVMe vs HDD）的预计执行时间粗略估算**，启动前一目了然。

---

## v1.0.4 (2026.11.23)
### English
- **Live Visual Progress Bar & Friendly Kaomoji UX**: Added a real-time 24-block terminal progress bar (`[████████░░░░░░░░░░░░]  42%`) with timestamped per-step updates and varied kaomoji across interactive prompts and execution phases (keeping objective report outputs 100% clean).
- **Pre-Test Disk Space Guard (> 65% Abort)**: Added automatic disk usage pre-scanning on the target mount point; if usage exceeds **65%**, the benchmark immediately aborts with an insufficient disk space notice.
- **Thorough Pre-Test & Post-Test Environment Cleanup**: Automatically sweeps stale `.diskquality_work` directories and temporary scripts before starting, cleans up and runs `sync` + `fstrim` after completion, and installs `EXIT`/`SIGINT`/`SIGTERM` signal traps so even `Ctrl+C` aborts leave zero leftover files or orphan child processes.

### 简体中文
- **实时可视化进度条与多样颜文字交互**：新增终端实时可视化进度条（`[████████░░░░░░░░░░░░]  42%`）与带时间戳的逐项执行回显，在交互提示与执行阶段加入多样颜文字提升体验（客观报告正文与导出图片保持纯净无干扰）。
- **测试前硬盘空间预检熔断（> 65% 自动取消）**：开始测试前自动扫描目标挂载盘占用率，若占用高于 **65%** 则直接提示“硬盘空间不足，已自动取消运行”并安全退出。
- **测试前/后及中断时彻底环境清理**：开始前自动清扫残留的 `.diskquality_work` 与历史临时脚本，测试结束后彻底删除全部临时文件并执行 `sync` + `fstrim`，同时挂载 `EXIT`/`SIGINT`/`SIGTERM` 信号捕获，即使中途 `Ctrl+C` 也不会留下垃圾文件或僵尸进程。

---

## v1.0.3 (2026.11.22)
### English
- **Expanded PT / Storage / Backup Benchmark Coverage**:
  - Added **Small-Block High-Concurrency I/O** (`PT_SEED_16K_32T`, `PT_HASH_256K_16T`, `BACKUP_64K_16T`, `BURST_4K_32T`) tailored for PT seedboxes and multi-stream backup servers.
  - Added **Global Connectivity & Bulk Download Throughput** (8-hub global TCP handshake RTT/loss + Cloudflare 50MB & CacheFly 100MB download speed).
  - Added **IP Quality, Platform Access & Empirical Denial Probability** (ASN/Hosting metadata, 10-platform HTTP reachability matrix, empirical Access Denial Probability %, and outbound Port 25 check).
- **Paginated Web Report UI & Enhanced Readability**:
  - Upgraded `/r/<id>` to a 6-page interactive paginated viewer with tab bar, `← Prev` / `Next →` controls, `ArrowLeft`/`ArrowRight` keyboard navigation, and a Full Panorama page.
  - Enhanced SVG/PNG and web typography (`15.5px` font, `26px` line height, `#111318` high-contrast dark card) for crisp legibility.
- **Strict Syntax & Synchronized Credits**:
  - Enforced strict 4-colon outer `:::: tabs` / 3-colon inner `::: tab-item` NodeSeek multi-tab Markdown syntax.
  - Synchronized all 12 upstream tools & inspiration credits across CLI banner, SVG/Markdown reports, web UI, and bilingual READMEs.

### 简体中文
- **全面拓展 PT / 大盘 / 备份机核心测评维度**：
  - 新增 **小量多并发 I/O 测试**（`PT_SEED_16K_32T`、`PT_HASH_256K_16T`、`BACKUP_64K_16T`、`BURST_4K_32T`），直击 PT 做种/校验与多线程备份真实场景。
  - 新增 **国际互联能力与大文件下载吞吐测试**（全球 8 大核心枢纽 TCP 延迟/丢包 + Cloudflare 50MB / CacheFly 100MB 实测速度）。
  - 新增 **IP 质量、平台访问与被拒绝访问概率估算**（ASN/机房属性、10 大平台 HTTP 探测、被拒访问概率百分比估算及 25 端口出站检测）。
- **网页端可翻页报告与文字可读性增强**：
  - 在线报告页 `/r/<id>` 升级为 6 页交互式翻页展示，支持顶部页签、底部 `上一页 / 下一页` 按钮、键盘左右方向键翻页与全景大图切换。
  - 全面增强 SVG/PNG 图片及网页排版字号与对比度（`15.5px` 字体、`26px` 行高、`#111318` 高对比深色卡片），各项指标一目了然。
- **严格输出语法规范与全量致谢同步**：
  - NodeSeek 导出严格遵循外层 4 冒号 `:::: tabs`、内层 3 冒号 `::: tab-item` 标准多标签语法。
  - 将全部 12 个底层检测工具原站与致敬名单全量同步至终端启动头、测评报告、网页端与中英文 README。

---

## v1.0.2 (2026.11.22)
### English
- Added full bilingual support (**Simplified Chinese & English**) with interactive language selection at startup (`-l zh` / `-l en`).
- Translated all CLI prompts, ANSI terminal reports, SVG/PNG image outputs, NodeSeek tabs, Markdown tables, and web UI buttons 1-to-1 between Chinese and English.
- Added strict zero-persistence ephemeral server mode (`/tmp` storage, 1-hour auto-destroy TTL, `HTTP 410 Gone` after expiry, systemd `MemoryMax=64M` / `CPUQuota=10%`).
- Added pre-flight path & dependency checks with explicit user consent (`[y/N]`; declining exits safely without modifying the system).
- Sanitized repository for public open-source release with bilingual README, Acknowledgments, and Disclaimer.

### 简体中文
- 新增完整中英双语支持，脚本启动开头即让用户选择语言（支持 `-l zh` / `-l en`）。
- 终端提示、ANSI 报告、SVG/PNG 图片、NodeSeek 格式、通用 Markdown 与在线网页按钮全量中英文一一对应翻译。
- 落地零持久化临时查询服务端（`/tmp` 暂存、严格 1 小时自动物理销毁、过期返回 `410 Gone`、systemd 硬限制 `64M` 内存 / `10%` CPU）。
- 新增运行前路径与工具依赖检查，缺失时征求同意安装，不同意即安全退出不改动系统。
- 整理发布开源仓库结构，补全中英双语 README、致谢原站与免责声明。

---

## v1.0.1 (2026.11.22)
### English
- Simplified interactive `[y/n]` module prompts (removed redundant skipped-format hint text from prompts; skipped items continue to render as bold red `???` in outputs).
- Added prominent version & update date display (`v1.0.1 (2026.11.22)`) across CLI banner, report headers, and web homepage.

### 简体中文
- 精简交互式 `[y/n]` 提示文案，去除提示语中冗余的跳过说明，仅在最终输出结果中保留标红 `？？？`。
- 在脚本启动头、测评报告与首页显眼标注脚本版本号与更新时间。

---

## v1.0.0 (2026.11.22)
### English
- Initial release of DiskQuality: 6-dimension objective VPS disk benchmark suite (`ioping`, FIO 14-item matrix, production `fsync`, adaptive 50%-capacity / 20-minute endurance stress with per-minute `iostat`, 10,000-file metadata, and SMART/Ext4 lifetime diagnostics).
- Pure objective output (zero subjective recommendations) with NodeQuality-style dark terminal ANSI/SVG/PNG rendering and one-click NodeSeek / Markdown export buttons.

### 简体中文
- 首个正式版本发布：包含 6 大客观硬盘测评维度（`ioping` 延迟基线、FIO 14 项合成矩阵、生产 `fsync`、50% 容量自适应 / 20 分钟持久压测与逐分钟 `iostat`、10,000 小文件元数据、SMART/Ext4 通电寿命溯源）。
- 纯客观数据输出（去除主观建议），支持 NodeQuality 风格深色终端 ANSI/SVG/PNG 渲染与一键复制 NodeSeek / Markdown 格式。
