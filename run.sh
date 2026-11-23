#!/usr/bin/env bash
# ==============================================================================
# DiskQuality v1.0.4 — Bilingual PT / Storage / Backup VPS Objective Benchmark
# ==============================================================================
set -euo pipefail

SITE_URL="${DQ_SITE_URL:-https://test.sakurado.top}"
SCRIPT_VERSION="v1.0.4"
SCRIPT_UPDATED="2026.11.23"
YELLOW='\033[1;33m'
GREEN='\033[1;32m'
CYAN='\033[1;36m'
RED='\033[1;31m'
RESET='\033[0m'

TARGET_DIR="/"
MINUTES="20"
AUTO_YES="0"
LANG_CODE=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        -y|--yes) AUTO_YES="1"; shift ;;
        -m|--minutes) MINUTES="$2"; shift 2 ;;
        -d|--dir) TARGET_DIR="$2"; shift 2 ;;
        -l|--lang) LANG_CODE="$2"; shift 2 ;;
        *) shift ;;
    esac
done

WORK_DIR="${TARGET_DIR%/}/.diskquality_work"
TMP_CORE="/tmp/diskquality_core_$$.py"

cleanup_env() {
    local code=$?
    pkill -9 -f "$WORK_DIR" 2>/dev/null || true
    rm -f "$TMP_CORE" 2>/dev/null || true
    rm -rf "$WORK_DIR" 2>/dev/null || true
    sync 2>/dev/null || true
    if [[ $code -eq 130 || $code -eq 143 ]]; then
        if [[ "${LANG_CODE:-zh}" == "en" ]]; then
            echo -e "\n${YELLOW}[Abort Cleanup] Cleaned up ${WORK_DIR} and temporary scripts safely (´• ω •\`)${RESET}" >&2
        else
            echo -e "\n${YELLOW}[中断清理] 已彻底清理临时路径 ${WORK_DIR} 与积累脚本文件 (´• ω •\`)${RESET}" >&2
        fi
    fi
}
trap cleanup_env EXIT
trap 'cleanup_env; exit 130' INT TERM HUP

read_tty() {
    local prompt="$1"
    local ans=""
    if (true </dev/tty) 2>/dev/null; then
        printf "${YELLOW}%s${RESET}" "$prompt" > /dev/tty
        IFS= read -r ans < /dev/tty || ans=""
    else
        printf "${YELLOW}%s${RESET}" "$prompt" >&2
        IFS= read -r ans || ans=""
    fi
    echo "$ans"
}

cat << 'BANNER'
██████╗ ██╗███████╗██╗  ██╗ ██████╗ ██╗   ██╗ █████╗ ██╗     ██╗████████╗██╗   ██╗
██╔══██╗██║██╔════╝██║ ██╔╝██╔═══██╗██║   ██║██╔══██╗██║     ██║╚══██╔══╝╚██╗ ██╔╝
██║  ██║██║███████╗█████╔╝ ██║   ██║██║   ██║███████║██║     ██║   ██║    ╚████╔╝ 
██║  ██║██║╚════██║██╔═██╗ ██║▄▄ ██║██║   ██║██╔══██║██║     ██║   ██║     ╚██╔╝  
██████╔╝██║███████║██║  ██╗╚██████╔╝╚██████╔╝██║  ██║███████╗██║   ██║      ██║   
╚═════╝ ╚═╝╚══════╝╚═╝  ╚═╝ ╚══▀▀═╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝      ╚═╝   
BANNER

# 1. Language Selection at Startup
if [[ -z "$LANG_CODE" ]]; then
    if [[ "$AUTO_YES" == "1" ]]; then
        LANG_CODE="zh"
    else
        LANG_ANS=$(read_tty "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ Select Language / 选择语言 [1=简体中文 (默认), 2=English]: ")
        if [[ "$LANG_ANS" == "2" || "$LANG_ANS" =~ ^[Ee][Nn]$ ]]; then
            LANG_CODE="en"
        else
            LANG_CODE="zh"
        fi
    fi
fi

if [[ "$LANG_CODE" == "en" ]]; then
    echo -e "${CYAN}PT / Storage / Backup VPS Objective Benchmark (50% Adaptive Capacity · 20-Min · 1h Ephemeral) ( •̀ ω •́ )✧${RESET}"
    echo -e "${GREEN}Version:${RESET} ${SCRIPT_VERSION} (${SCRIPT_UPDATED})   ${GREEN}Command:${RESET} bash <(curl -sL ${SITE_URL})"
else
    echo -e "${CYAN}PT / 大盘 / 备份机全维度客观测评（50% 容量自适应 · 20 分钟预算 · 报告 1 小时自动销毁）( •̀ ω •́ )✧${RESET}"
    echo -e "${GREEN}脚本版本：${RESET}${SCRIPT_VERSION} (${SCRIPT_UPDATED})   ${GREEN}一键命令：${RESET}bash <(curl -sL ${SITE_URL})"
fi

# Live Taipei Time & Run Counter (Total / Today)
TPE_TIME=$(TZ='Asia/Taipei' date '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date -u '+%Y-%m-%d %H:%M:%S')
TOTAL_RUNS="—"
TODAY_RUNS="—"
STATS_JSON=$(curl -fsSLm 3 "${SITE_URL}/api/v1/stats?hit=1" 2>/dev/null || true)
if [[ -n "$STATS_JSON" ]]; then
    _t=$(printf '%s' "$STATS_JSON" | sed -n 's/.*"taipei_time"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
    _tot=$(printf '%s' "$STATS_JSON" | sed -n 's/.*"total_runs"[[:space:]]*:[[:space:]]*\([0-9]*\).*/\1/p')
    _tod=$(printf '%s' "$STATS_JSON" | sed -n 's/.*"today_runs"[[:space:]]*:[[:space:]]*\([0-9]*\).*/\1/p')
    [[ -n "$_t" ]] && TPE_TIME="$_t"
    [[ -n "$_tot" ]] && TOTAL_RUNS="$_tot"
    [[ -n "$_tod" ]] && TODAY_RUNS="$_tod"
fi

if [[ "$LANG_CODE" == "en" ]]; then
    echo -e "${GREEN}Run Time (Taipei Time):${RESET} ${TPE_TIME}  |  ${GREEN}Total Runs:${RESET} ${TOTAL_RUNS}  |  ${GREEN}Today Runs:${RESET} ${TODAY_RUNS}"
    echo ""
    echo -e "${CYAN}[Acknowledgments & Upstream Tools]${RESET}"
    echo "  · fio (https://github.com/axboe/fio) | ioping (https://github.com/koct9i/ioping)"
    echo "  · sysstat (https://github.com/sysstat/sysstat) | smartmontools (https://www.smartmontools.org)"
    echo "  · e2fsprogs (https://e2fsprogs.sourceforge.net) | curl (https://curl.se) | ipinfo.io"
    echo "  · Cloudflare Speed (https://speed.cloudflare.com) | CacheFly (https://www.cachefly.com)"
    echo "  · Credits: NodeQuality (github.com/LloydAsp/NodeQuality) | HardwareQuality & IPQuality (github.com/xykt)"
else
    echo -e "${GREEN}运行时间 (Taipei Time)：${RESET}${TPE_TIME}  |  ${GREEN}累计运行：${RESET}${TOTAL_RUNS} 次  |  ${GREEN}今日运行：${RESET}${TODAY_RUNS} 次"
    echo ""
    echo -e "${CYAN}【致谢与底层检测工具原站】${RESET}"
    echo "  · fio (https://github.com/axboe/fio) | ioping (https://github.com/koct9i/ioping)"
    echo "  · sysstat (https://github.com/sysstat/sysstat) | smartmontools (https://www.smartmontools.org)"
    echo "  · e2fsprogs (https://e2fsprogs.sourceforge.net) | curl (https://curl.se) | ipinfo.io"
    echo "  · Cloudflare Speed (https://speed.cloudflare.com) | CacheFly (https://www.cachefly.com)"
    echo "  · 致敬项目：NodeQuality (github.com/LloydAsp/NodeQuality) | HardwareQuality & IPQuality (github.com/xykt)"
fi
echo ""

# 2. Pre-flight Path Check & Thorough Pre-Test Environment Cleanup
if [[ ! -d "$TARGET_DIR" || ! -w "$TARGET_DIR" ]]; then
    [[ "$LANG_CODE" == "en" ]] && echo -e "${RED}[Error] Target directory not writable: ${TARGET_DIR} (；′⌒\`)${RESET}" || echo -e "${RED}[错误] 目标测评路径不可访问或不可写：${TARGET_DIR} (；′⌒\`)${RESET}"
    exit 1
fi

if [[ "$LANG_CODE" == "en" ]]; then
    echo -e "${CYAN}[Cleanup] Sweeping stale temporary files before benchmark... (ง •̀_•́)ง${RESET}"
else
    echo -e "${CYAN}[环境清理] 正在彻底清理测试前残留临时文件... (ง •̀_•́)ง${RESET}"
fi
rm -rf "$WORK_DIR" 2>/dev/null || true
find /tmp -maxdepth 1 -name 'diskquality_core_*.py' ! -name "diskquality_core_$$.py" -delete 2>/dev/null || true
sync 2>/dev/null || true

# 3. Pre-Test Disk Usage Scan (Abort if > 65% used)
USED_PCT=$(df -Pk "$TARGET_DIR" | awk 'NR==2 { if ($2 > 0) printf "%.1f", ($3 * 100.0) / $2; else print "0.0" }')
IS_OVER=$(awk -v u="$USED_PCT" 'BEGIN { print (u > 65.0) ? 1 : 0 }')
if [[ "$IS_OVER" == "1" ]]; then
    if [[ "$LANG_CODE" == "en" ]]; then
        echo -e "${RED}[Abort] Disk usage is ${USED_PCT}% (> 65%). Insufficient disk space, benchmark automatically cancelled (；′⌒\`)${RESET}"
    else
        echo -e "${RED}[终止] 当前硬盘占用 ${USED_PCT}% (> 65%)，硬盘空间不足，已自动取消运行 (；′⌒\`)${RESET}"
    fi
    exit 1
else
    if [[ "$LANG_CODE" == "en" ]]; then
        echo -e "${GREEN}[✔] Disk pre-scan passed (used ${USED_PCT}% ≤ 65%) (๑•̀ㅂ•́)و✧${RESET}"
    else
        echo -e "${GREEN}[✔] 硬盘空间预检通过（当前占用 ${USED_PCT}% ≤ 65%）(๑•̀ㅂ•́)و✧${RESET}"
    fi
fi

# 4. Pre-flight Dependency Check
MISSING_CMDS=()
MISSING_PKGS=()
check_dep() {
    if ! command -v "$1" >/dev/null 2>&1; then
        MISSING_CMDS+=("$1"); MISSING_PKGS+=("$2")
    fi
}
check_dep "fio" "fio"; check_dep "ioping" "ioping"; check_dep "iostat" "sysstat"
check_dep "smartctl" "smartmontools"; check_dep "tune2fs" "e2fsprogs"
check_dep "python3" "python3"; check_dep "curl" "curl"

if [[ ${#MISSING_CMDS[@]} -gt 0 ]]; then
    if [[ "$LANG_CODE" == "en" ]]; then
        echo -e "${RED}[Dependencies] Missing tools: ${MISSING_CMDS[*]} (packages: ${MISSING_PKGS[*]})${RESET}"
        INSTALL_ANS=$( [[ "$AUTO_YES" == "1" ]] && echo "y" || read_tty "Allow automatic installation? (Declining exits cleanly) [y/N]: " )
    else
        echo -e "${RED}[依赖检查] 缺少必需工具：${MISSING_CMDS[*]}（安装包：${MISSING_PKGS[*]}）${RESET}"
        INSTALL_ANS=$( [[ "$AUTO_YES" == "1" ]] && echo "y" || read_tty "是否同意自动安装上述缺失依赖？(不同意将自动退出脚本) [y/N]：" )
    fi
    if [[ ! "$INSTALL_ANS" =~ ^[Yy]$ ]]; then
        [[ "$LANG_CODE" == "en" ]] && echo -e "${RED}[Exit] Installation declined. Exited safely (´• ω •\`).${RESET}" || echo -e "${RED}[退出] 用户未同意安装缺失依赖，脚本已安全退出 (´• ω •\`).${RESET}"
        exit 1
    fi
    if command -v apt-get >/dev/null 2>&1; then
        export DEBIAN_FRONTEND=noninteractive
        apt-get update -qq && apt-get install -y -qq "${MISSING_PKGS[@]}"
    elif command -v dnf >/dev/null 2>&1; then
        dnf install -y -q "${MISSING_PKGS[@]}"
    elif command -v yum >/dev/null 2>&1; then
        yum install -y -q "${MISSING_PKGS[@]}"
    else
        echo -e "${RED}[Error] Unsupported package manager: ${MISSING_PKGS[*]}${RESET}"
        exit 1
    fi
else
    [[ "$LANG_CODE" == "en" ]] && echo -e "${GREEN}[✔] Path & dependencies verified ヾ(•ω•\`)o${RESET}" || echo -e "${GREEN}[✔] 路径与全部测评依赖检查通过 ヾ(•ω•\`)o${RESET}"
fi
echo ""

# 5. Clean Interactive Module Selection (Default 'y')
ask_yn() {
    local prompt="$1"
    if [[ "$AUTO_YES" == "1" ]]; then
        echo -e "${YELLOW}${prompt}${RESET}y" >&2; echo "y"; return
    fi
    local ans
    ans=$(read_tty "$prompt"); ans="${ans:-y}"
    [[ "$ans" =~ ^[Nn]$ ]] && echo "n" || echo "y"
}

if [[ "$LANG_CODE" == "en" ]]; then
    RUN_IOPING=$(ask_yn "Run Latency Baseline (ioping)? [y/n]: ")
    RUN_MATRIX=$(ask_yn "Run FIO 14-Item Synthetic Matrix (Direct I/O)? [y/n]: ")
    RUN_PROD=$(ask_yn "Run Production Workloads & fsync Commit? [y/n]: ")
    RUN_CONC=$(ask_yn "Run Small-Block High-Concurrency I/O (PT Seed / Hash / Backup)? [y/n]: ")
    RUN_SUSTAINED=$(ask_yn "Run 50% Adaptive Capacity Endurance + iostat (20-min budget)? [y/n]: ")
    RUN_NET=$(ask_yn "Run Global Connectivity & Bulk Download Throughput? [y/n]: ")
    RUN_IPQ=$(ask_yn "Run IP Quality, Platform Unlock & Denial Probability? [y/n]: ")
    RUN_META=$(ask_yn "Run Filesystem Metadata (10,000 files) & Lifetime Diagnostics? [y/n]: ")
    echo -e "\n${CYAN}>>> All set! Launching DiskQuality benchmark engine... ٩(｡•́‿•̀｡)۶${RESET}"
else
    RUN_IOPING=$(ask_yn "运行 底层延迟基线测试 (ioping)？（回车默认 'y'）[y/n]：")
    RUN_MATRIX=$(ask_yn "运行 FIO 14项合成性能矩阵测试？（回车默认 'y'）[y/n]：")
    RUN_PROD=$(ask_yn "运行 生产模型与 fsync 事务刷盘测试？（回车默认 'y'）[y/n]：")
    RUN_CONC=$(ask_yn "运行 小量多并发 I/O 压测 (PT 做种/校验/并发备份)？（回车默认 'y'）[y/n]：")
    RUN_SUSTAINED=$(ask_yn "运行 50% 容量自适应持久压测 + iostat 时序 (20分钟预算)？（回车默认 'y'）[y/n]：")
    RUN_NET=$(ask_yn "运行 国际互联延迟与大文件下载吞吐测试？（回车默认 'y'）[y/n]：")
    RUN_IPQ=$(ask_yn "运行 IP 质量、平台解锁与被拒绝访问概率评估？（回车默认 'y'）[y/n]：")
    RUN_META=$(ask_yn "运行 文件系统元数据 (10,000 小文件) 与通电寿命溯源？（回车默认 'y'）[y/n]：")
    echo -e "\n${CYAN}>>> 选定完毕，正在启动 DiskQuality 测评引擎... ٩(｡•́‿•̀｡)۶${RESET}"
fi

curl -fsSL "${SITE_URL}/core.py" -o "$TMP_CORE"

python3 "$TMP_CORE" \
    --lang "$LANG_CODE" --target "$TARGET_DIR" --minutes "$MINUTES" \
    --ioping "$RUN_IOPING" --matrix "$RUN_MATRIX" --prod "$RUN_PROD" \
    --concurrency "$RUN_CONC" --sustained "$RUN_SUSTAINED" \
    --network "$RUN_NET" --ip_quality "$RUN_IPQ" --meta "$RUN_META" \
    --site-url "$SITE_URL" --upload-url "${SITE_URL}/api/v1/record"
