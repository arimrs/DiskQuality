[English](README.md) | **简体中文**

# DiskQuality

[![Version](https://img.shields.io/badge/version-v1.0.4-22c55e.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

超轻量、中英双语（**简体中文 / English**）、纯客观数据的 Linux VPS 深度测评套件，专为 **PT 刷流机、大盘存储机与备份服务器** 打造，并配套零持久化可翻页临时在线查询服务端。

- **自适应 50% 容量算法 + 65% 空间安全熔断**：自动按目标硬盘总容量的 **50%** 动态调节持久压测文件体积（安全钳制 ≤ 可用空间的 80%），全流程收敛至 **20 分钟**。启动前自动扫描硬盘占用，**若占用高于 65% 则自动提示“硬盘空间不足，已自动取消运行”**。
- **实时可视化进度条与彻底环境清理**：全程展示实时终端进度条与多样颜文字交互，测试前、测试后以及 `Ctrl+C` 中断时均自动彻底清理所有临时文件与残留进程并执行 `fstrim`。
- **PT / 大盘 / 备份机全维度覆盖**：涵盖硬件拓扑、`ioping` 延迟基线、FIO 14 项合成矩阵、**小量多并发 I/O**（PT 做种 / 校验 / 多线程备份 / 4K 突发）、生产 `fsync`、50% 容量持久压测 + 逐分钟 `iostat`、10,000 小文件元数据与 SMART/Ext4 寿命、**国际互联与大文件下载吞吐**，以及 **IP 质量、平台访问与被拒概率估算**。
- **纯客观数据呈现**：彻底去除任何主观建议与调优文案，仅输出可复现的原始客观指标。
- **交互式体验**：启动开头即选语言（中/英）；运行前自动检查路径与工具依赖，缺失时询问同意安装，**不同意即安全退出**；支持 NodeQuality 同款 `[y/n]` 分模块选择，跳过项在报告及图片中统一以加粗标红 **`？？？`** 展示。
- **网页端可翻页报告与增强可读性**：6 页交互式翻页结果页（`← 上一页` / `下一页 →` + 键盘左右方向键切换 + 全景大图页），大字号高对比暗色终端卡片（`15.5px` 字体 / `26px` 行高），严格零持久化 `/tmp` 暂存与 **1 小时自动物理销毁**，浏览器本地 Canvas 导出高清 PNG，内置 **复制文本 / 复制为NodeSeek格式/ 复制为通用Markdown / 导出高清PNG / 下载SVG** 按钮。

---

## 快速开始

在任意 Linux VPS（Debian / Ubuntu / RHEL / Rocky / AlmaLinux）上直接运行：

```bash
bash <(curl -sL https://test.sakurado.top)
```

可选参数：
- `-l zh` / `-l en`：预设简体中文或英文
- `-m 20`：总测评时长预算（单位：分钟，默认 `20`）
- `-d /path`：指定测评挂载路径（默认 `/`）
- `-y`：非交互自动模式（全部模块默认选 `y`）

---

## 测评维度

1. **系统与块设备拓扑**：虚拟化、操作系统与内核、CPU/内存/Swap、磁盘型号、容量、`ROTA`、I/O 调度器、`write_cache`、`read_ahead_kb`、扇区规格、TRIM/Discard 支持。
2. **底层延迟基线（`ioping`）**：Direct I/O 原生随机寻道、Page Cache 缓存读、`fsync` 持久化同步写（`min / avg / max / mdev`）。
3. **FIO 14 项合成性能矩阵（`libaio`, `direct=1`）**：顺序 1MB 读/写（`QD=1`, `QD=32×4`）、随机 4KB 读/写（`QD=1`, `QD=16`, `QD=64×4`）、随机 8K/16K 70/30、顺序 128K 50/50、Buffered 1M 50/50（`direct=0`），输出吞吐、IOPS、p95 与 p99。
4. **小量多并发 I/O**：
   - `PT_SEED_16K_32T`（16KB 80/20 读写，32 并发线程，`QD=4`）— 多 Peer PT 做种/下载混合模型
   - `PT_HASH_256K_16T`（256KB 随机读，16 并发线程，`QD=4`）— 多任务种子分片 Hash 校验
   - `BACKUP_64K_16T`（64KB 随机写，16 并发线程，`QD=4`）— rsync / borg / restic 多流备份写入
   - `BURST_4K_32T`（4KB 50/50 混合，32 并发线程，`QD=2`）— 高并发小文件突发压力
5. **生产场景模型与 `fsync` 事务刷盘**：OLTP 8K（`QD=32`）、Web 16K（`QD=8`）、WAL 4K（`fsync=1`, `QD=1`）、高并发拥塞 `fsync=4`（`QD=32`）。
6. **50% 容量自适应持久压测 + 逐分钟 `iostat` 时序**：前半段连续大文件顺序写 + 后半段随机混合重载，后台每 5 秒高频采样聚合逐分钟 `r/s`、`w/s`、`rMB/s`、`wMB/s`、`w_await`、`%util`。
7. **文件系统元数据与介质通电寿命溯源**：10,000 × 4KB 小文件创建/Stat/读/删速率、`smartctl` SMART 寄存器状态及 Ext4 超级块创建时间/挂载次数/累计写入量。
8. **国际互联能力与大文件下载吞吐**：全球 8 大核心枢纽（东京、新加坡、香港、洛杉矶、纽约、法兰克福、伦敦、阿姆斯特丹）TCP 握手延迟与丢包率 + Cloudflare 50MB / CacheFly 100MB 实测下载速度。
9. **IP 质量、平台访问与被拒绝访问概率估算**：ASN/运营商/归属地/机房属性识别、10 大常见平台（Cloudflare、Google、YouTube、Netflix、Disney+、TikTok、OpenAI、Reddit、GitHub、Steam）HTTP 探测、综合估算 **被拒绝访问概率（%）** 与风险等级，以及出站 SMTP 25 端口连通性检测。

---

## 自建临时查询服务端

```bash
git clone https://github.com/arimrs/DiskQuality.git /opt/diskquality-server
cp /opt/diskquality-server/deploy/diskquality-web.service /etc/systemd/system/
# 修改 /etc/systemd/system/diskquality-web.service 中的 DQ_SITE_URL 为你的域名
systemctl daemon-reload && systemctl enable --now diskquality-web.service
```

使用 Nginx / Caddy 反向代理本地 `8765` 端口即可（脚本响应带 `Cache-Control: public, max-age=300`，挂接 CDN 后几乎零回源）。

---

## 致谢与底层检测工具原站

本项目基于以下优秀开源项目与公共测速节点构建，并致敬其设计理念：

- **fio** — https://github.com/axboe/fio *（Direct I/O 与高并发存储压测引擎）*
- **ioping** — https://github.com/koct9i/ioping *（底层磁盘延迟基准探测）*
- **sysstat / iostat** — https://github.com/sysstat/sysstat *（逐分钟块设备时序采样）*
- **smartmontools** — https://www.smartmontools.org *（SMART 健康与通电寿命读取）*
- **e2fsprogs / tune2fs** — https://e2fsprogs.sourceforge.net *（Ext4 超级块寿命与写入量溯源）*
- **curl** — https://curl.se *（HTTP 平台可达性与大文件下载探测）*
- **Cloudflare Speed** — https://speed.cloudflare.com *（全球 CDN 下载吞吐测速节点）*
- **CacheFly CDN** — https://cachefly.cachefly.net *（国际大文件下载吞吐节点）*
- **ip-api / ipinfo** — https://ip-api.com / https://ipinfo.io *（ASN 与机房属性元数据查询）*
- **NodeQuality** — https://github.com/LloydAsp/NodeQuality *（致敬交互流程与在线结果页体验）*
- **HardwareQuality** — https://github.com/xykt/HardwareQuality *（致敬终端 ANSI 报告排版风格）*
- **IPQuality** — https://github.com/xykt/IPQuality *（致敬 IP 质量与平台可达性检测理念）*

---

## 免责声明

1. **磁盘写入损耗与高负载提示**：本工具会在目标挂载点产生最高达硬盘总容量 50%（安全钳制 ≤ 可用空间 80%）的持续 Direct I/O 写入。请仅在拥有合法权限的设备上运行，并自行评估 SSD TBW 写入寿命及云服务商 ToS 条款。
2. **零持久化与无担保声明**：临时在线查询服务**不提供任何长期保存功能**，所有上传的测评结果与页面均在 **1 小时后自动物理销毁**。本开源项目基于 MIT 协议按“现状”提供，作者不对任何直接或间接损失承担责任。
3. **隐私保护**：测评报告中的公网 IP 默认自动打码（`x.x.*.*`），请勿在报告中主动附加敏感隐私数据。
