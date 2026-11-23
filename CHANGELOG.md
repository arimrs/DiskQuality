# Changelog / 更新日志

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
