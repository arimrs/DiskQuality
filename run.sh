#!/usr/bin/env bash
# ==============================================================================
# DiskQuality v1.0.6 — Bilingual PT / Storage / Backup VPS Objective Benchmark
# ==============================================================================
set -euo pipefail

SITE_URL="${DQ_SITE_URL:-https://test.sakurado.top}"
SCRIPT_VERSION="v1.0.6"
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
PROFILE_MODE="auto"
GB_CLI=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        -y|--yes) AUTO_YES="1"; shift ;;
        -m|--minutes) MINUTES="$2"; shift 2 ;;
        -d|--dir) TARGET_DIR="$2"; shift 2 ;;
        -l|--lang) LANG_CODE="$2"; shift 2 ;;
        -p|--profile) PROFILE_MODE="$2"; shift 2 ;;
        --gb|--geekbench) GB_CLI="$2"; shift 2 ;;
        -h|--help)
            cat << 'HELP'
DiskQuality Usage:
  bash <(curl -sL https://test.sakurado.top) [options]

Options:
  -l, --lang <zh|en>                         Language (zh or en)
  -d, --dir <path>                           Target mount directory (default: /)
  -m, --minutes <N>                          Total time budget in minutes (default: 20)
  -p, --profile <auto|dedicated|vds|vps|container>  Server architecture scheduling profile (default: auto)
  --gb <gb5|gb6|skip>                        CPU benchmark mode (default: gb5)
  -y, --yes                                  Non-interactive mode (accept defaults)
HELP
            exit 0
            ;;
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

START_KAOMOJIS=(
    '(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧' '( •̀ ω •́ )✧' '(๑•̀ㅂ•́)و✧' 'ヾ(•ω•`)o'
    '(o´ω`o)ﾉ' '٩(｡•́‿•̀｡)۶' '(*^▽^*)' '(☆▽☆)'
    'ヽ(✿ﾟ▽ﾟ)ノ' '(｡･ω･｡)ﾉ♡' '(*≧ω≦)' '(づ￣ 3￣)づ'
    '٩(ˊᗜˋ*)و' '✧*｡٩(ˊᗜˋ*)و✧*｡' '(￣▽￣)ノ' 'o(*￣▽￣*)ブ'
    '(≧▽≦)/' 'ヾ(≧▽≦*)o' "(●'◡'●)" 'ヽ(•̀ω•́ )ゝ'
)
START_EMO="${START_KAOMOJIS[$((RANDOM % ${#START_KAOMOJIS[@]}))]}"

# 1. Language Selection at Startup
if [[ -z "$LANG_CODE" ]]; then
    if [[ "$AUTO_YES" == "1" ]]; then
        LANG_CODE="zh"
    else
        LANG_ANS=$(read_tty "Select Language / 选择语言 [1=简体中文 (默认), 2=English]: ")
        if [[ "$LANG_ANS" == "2" || "$LANG_ANS" =~ ^[Ee][Nn]$ ]]; then
            LANG_CODE="en"
        else
            LANG_CODE="zh"
        fi
    fi
fi

if [[ "$LANG_CODE" == "en" ]]; then
    echo -e "${CYAN}PT / Storage / Backup VPS Objective Benchmark (50% Adaptive Capacity · 20-Min Budget) ${START_EMO}${RESET}"
    echo -e "${GREEN}Version:${RESET} ${SCRIPT_VERSION} (${SCRIPT_UPDATED})   ${GREEN}Command:${RESET} bash <(curl -sL ${SITE_URL})"
else
    echo -e "${CYAN}PT / 大盘 / 备份机全维度客观测评（50% 容量自适应 · 20 分钟预算）${START_EMO}${RESET}"
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
    echo -e "${CYAN}[Cleanup] Sweeping stale temporary files before benchmark...${RESET}"
else
    echo -e "${CYAN}[环境清理] 正在彻底清理测试前残留临时文件...${RESET}"
fi
rm -rf "$WORK_DIR" 2>/dev/null || true
find /tmp -maxdepth 1 -name 'diskquality_core_*.py' ! -name "diskquality_core_$$.py" -delete 2>/dev/null || true
sync 2>/dev/null || true

# 3. Pre-Test Disk Usage Scan (Abort if > 65% used)
USED_PCT=$(df -Pk "$TARGET_DIR" | awk 'NR==2 { if ($2 > 0) printf "%.1f", ($3 * 100.0) / $2; else print "0.0" }')
IS_OVER=$(awk -v u="$USED_PCT" 'BEGIN { print (u > 65.0) ? 1 : 0 }')
if [[ "$IS_OVER" == "1" ]]; then
    if [[ "$LANG_CODE" == "en" ]]; then
        echo -e "${RED}[Abort] Disk usage is ${USED_PCT}% (> 65%). Insufficient disk space, benchmark automatically cancelled.${RESET}"
    else
        echo -e "${RED}[终止] 当前硬盘占用 ${USED_PCT}% (> 65%)，硬盘空间不足，已自动取消运行${RESET}"
    fi
    exit 1
else
    if [[ "$LANG_CODE" == "en" ]]; then
        echo -e "${GREEN}[✔] Disk pre-scan passed (used ${USED_PCT}% ≤ 65%)${RESET}"
    else
        echo -e "${GREEN}[✔] 硬盘空间预检通过（当前占用 ${USED_PCT}% ≤ 65%）${RESET}"
    fi
fi

# 4. Platform Detection & Pre-flight Dependency Check (Dedicated / VDS / KVM / LXC / OpenVZ / Multi-Arch)
ARCH_NAME=$(uname -m 2>/dev/null || echo "unknown")
VIRT_RAW=$(systemd-detect-virt 2>/dev/null || echo "unknown")
IS_CONTAINER="0"
if [[ -f /.dockerenv ]] || [[ -d /proc/vz && ! -d /proc/bc ]] || [[ "$VIRT_RAW" =~ ^(lxc|openvz|docker|podman|systemd-nspawn|wsl)$ ]]; then
    IS_CONTAINER="1"
    PLAT_TAG="CONTAINER (${VIRT_RAW}/${ARCH_NAME})"
elif [[ "$VIRT_RAW" == "none" ]] && ! grep -q ' hypervisor' /proc/cpuinfo 2>/dev/null; then
    PLAT_TAG="DEDICATED (Bare-Metal/${ARCH_NAME})"
else
    PLAT_TAG="VM (${VIRT_RAW}/${ARCH_NAME})"
fi

MISSING_CMDS=()
MISSING_PKGS=()
check_dep() {
    if ! command -v "$1" >/dev/null 2>&1; then
        MISSING_CMDS+=("$1"); MISSING_PKGS+=("$2")
    fi
}
check_dep "fio" "fio"; check_dep "ioping" "ioping"
check_dep "python3" "python3"; check_dep "curl" "curl"
if [[ "$IS_CONTAINER" == "0" ]]; then
    check_dep "iostat" "sysstat"; check_dep "smartctl" "smartmontools"; check_dep "tune2fs" "e2fsprogs"
fi

if [[ ${#MISSING_CMDS[@]} -gt 0 ]]; then
    if [[ "$LANG_CODE" == "en" ]]; then
        echo -e "${RED}[Dependencies] Missing tools: ${MISSING_CMDS[*]} (packages: ${MISSING_PKGS[*]})${RESET}"
        INSTALL_ANS=$( [[ "$AUTO_YES" == "1" ]] && echo "y" || read_tty "Allow automatic installation? (Declining exits cleanly) [y/N]: " )
    else
        echo -e "${RED}[依赖检查] 缺少必需工具：${MISSING_CMDS[*]}（安装包：${MISSING_PKGS[*]}）${RESET}"
        INSTALL_ANS=$( [[ "$AUTO_YES" == "1" ]] && echo "y" || read_tty "是否同意自动安装上述缺失依赖？(不同意将自动退出脚本) [y/N]：" )
    fi
    if [[ ! "$INSTALL_ANS" =~ ^[Yy]$ ]]; then
        [[ "$LANG_CODE" == "en" ]] && echo -e "${RED}[Exit] Installation declined. Exited safely.${RESET}" || echo -e "${RED}[退出] 用户未同意安装缺失依赖，脚本已安全退出。${RESET}"
        exit 1
    fi
    if command -v apt-get >/dev/null 2>&1; then
        export DEBIAN_FRONTEND=noninteractive
        apt-get update -qq && apt-get install -y -qq "${MISSING_PKGS[@]}"
    elif command -v dnf >/dev/null 2>&1; then
        dnf install -y -q "${MISSING_PKGS[@]}"
    elif command -v yum >/dev/null 2>&1; then
        yum install -y -q "${MISSING_PKGS[@]}"
    elif command -v apk >/dev/null 2>&1; then
        apk add --no-cache "${MISSING_PKGS[@]}"
    elif command -v pacman >/dev/null 2>&1; then
        pacman -Sy --noconfirm "${MISSING_PKGS[@]}"
    elif command -v zypper >/dev/null 2>&1; then
        zypper -n install "${MISSING_PKGS[@]}"
    else
        echo -e "${RED}[Error] Unsupported package manager. Please install manually: ${MISSING_PKGS[*]}${RESET}"
        exit 1
    fi
else
    [[ "$LANG_CODE" == "en" ]] && echo -e "${GREEN}[✔] Path & dependencies verified (${PLAT_TAG})${RESET}" || echo -e "${GREEN}[✔] 路径与全部测评依赖检查通过（${PLAT_TAG}）${RESET}"
fi
echo ""

# 5. Disk-Aware Time Estimation & 5 Merged Interactive Module Groups (Default 'y' / GB5)
DISK_TOTAL_GB=$(df -Pk "$TARGET_DIR" | awk 'NR==2 { printf "%.1f", $2 / 1048576.0 }')
DISK_AVAIL_GB=$(df -Pk "$TARGET_DIR" | awk 'NR==2 { printf "%.1f", $4 / 1048576.0 }')
STRESS_EST_GB=$(awk -v t="$DISK_TOTAL_GB" -v a="$DISK_AVAIL_GB" 'BEGIN { r=t*0.5; c=a*0.8; g=(r<c?r:c); if(g>2000) g=2000; if(g<1) g=1; printf "%.1f", g }')
DEV_SRC=$(findmnt -n -o SOURCE "$TARGET_DIR" 2>/dev/null || df -P "$TARGET_DIR" | awk 'NR==2{print $1}')
BASE_DEV=$(lsblk -no PKNAME "$DEV_SRC" 2>/dev/null | head -n1 || true)
if [[ -z "$BASE_DEV" && "$DEV_SRC" == /dev/* ]]; then
    BASE_DEV=$(basename "$DEV_SRC" | sed -E 's/^(nvme[0-9]+n[0-9]+|mmcblk[0-9]+|loop[0-9]+)p[0-9]+$/\1/; s/[0-9]+$//')
fi
ROTA_VAL=$(cat "/sys/block/${BASE_DEV}/queue/rotational" 2>/dev/null || echo "0")
if [[ "$ROTA_VAL" == "1" ]]; then
    MEDIA_ZH="HDD/机械盘"; MEDIA_EN="HDD"
    EST_CORE_MIN=5; EST_META_MIN=1
else
    MEDIA_ZH="SSD/NVMe"; MEDIA_EN="SSD/NVMe"
    EST_CORE_MIN=3; EST_META_MIN=0
fi
EST_SUST_MIN=$(awk -v m="$MINUTES" 'BEGIN { s=int(m*0.75); if(s<2) s=2; print s }')

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
    echo -e "${CYAN}[Disk Profile] Capacity ${DISK_TOTAL_GB} GB (${MEDIA_EN}) · 50% Stress File ≈ ${STRESS_EST_GB} GB${RESET}"
    RUN_CORE=$(ask_yn "1/5 Run Disk Performance Suite (ioping + FIO 14-item + fsync + PT/Backup Concurrency, ~${EST_CORE_MIN}m) (default y) [Y/n]: ")
    RUN_SUSTAINED=$(ask_yn "2/5 Run 50% Adaptive Capacity Endurance (${STRESS_EST_GB} GB) + iostat (~${EST_SUST_MIN}m) (default y) [Y/n]: ")
    RUN_NETIP=$(ask_yn "3/5 Run Global Connectivity, Bulk Download & IP Quality / Denial Risk (~0.5m) (default y) [Y/n]: ")
    RUN_META=$(ask_yn "4/5 Run Filesystem Metadata (10,000 files) & SMART / Ext4 Lifetime (~0.3m) (default y) [Y/n]: ")
    if [[ "$AUTO_YES" == "1" ]]; then
        GB_ANS="1"
    else
        GB_ANS=$(read_tty "5/5 CPU Benchmark (Geekbench Full Single/Multi-Core, ~3m) [1=GB5 (default), 2=GB6, 3=Skip]: ")
        GB_ANS="${GB_ANS:-1}"
    fi
else
    echo -e "${CYAN}[硬盘画像] 容量 ${DISK_TOTAL_GB} GB（${MEDIA_ZH}）· 50% 自适应压测文件 ≈ ${STRESS_EST_GB} GB${RESET}"
    RUN_CORE=$(ask_yn "1/5 运行 综合硬盘性能组（ioping 延迟 + FIO 14项 + 生产 fsync + PT/备份多并发，约 ${EST_CORE_MIN} 分钟）（回车默认 y）[Y/n]：")
    RUN_SUSTAINED=$(ask_yn "2/5 运行 50% 容量自适应持久压测（${STRESS_EST_GB} GB）+ 逐分钟 iostat（约 ${EST_SUST_MIN} 分钟）（回车默认 y）[Y/n]：")
    RUN_NETIP=$(ask_yn "3/5 运行 国际互联延迟、大文件下行与 IP 质量 / 被拒访问概率（约 30 秒）（回车默认 y）[Y/n]：")
    RUN_META=$(ask_yn "4/5 运行 文件系统元数据（10,000 小文件）与 SMART / Ext4 通电寿命（约 20 秒）（回车默认 y）[Y/n]：")
    if [[ "$AUTO_YES" == "1" ]]; then
        GB_ANS="1"
    else
        GB_ANS=$(read_tty "5/5 CPU 性能测试（Geekbench 完整单核/多核跑分，约 3 分钟）[1=GB5 (回车默认), 2=GB6, 3=跳过]：")
        GB_ANS="${GB_ANS:-1}"
    fi
fi

[[ -n "$GB_CLI" ]] && GB_ANS="$GB_CLI"
case "$GB_ANS" in
    2|gb6|GB6) GB_MODE="gb6" ;;
    3|n|N|skip|SKIP|0) GB_MODE="skip" ;;
    *) GB_MODE="gb5" ;;
esac

RUN_IOPING="$RUN_CORE"; RUN_MATRIX="$RUN_CORE"; RUN_PROD="$RUN_CORE"; RUN_CONC="$RUN_CORE"
RUN_NET="$RUN_NETIP"; RUN_IPQ="$RUN_NETIP"

EST_LOW=$(awk -v c="$RUN_CORE" -v cm="$EST_CORE_MIN" -v s="$RUN_SUSTAINED" -v sm="$EST_SUST_MIN" -v n="$RUN_NETIP" -v m="$RUN_META" -v mm="$EST_META_MIN" -v g="$GB_MODE" 'BEGIN { t=0.2; if(c=="y") t+=cm; if(s=="y") t+=sm; if(n=="y") t+=0.5; if(m=="y") t+=(mm>0?mm:0.3); if(g!="skip") t+=3.0; printf "%.1f", t }')
EST_HIGH=$(awk -v lo="$EST_LOW" -v r="$ROTA_VAL" 'BEGIN { f=(r=="1"?1.35:1.2); hi=lo*f; if(hi<lo+0.5) hi=lo+0.5; printf "%.1f", hi }')

if [[ "$LANG_CODE" == "en" ]]; then
    echo -e "\n${CYAN}>>> Estimated Total Runtime: ~${EST_LOW}–${EST_HIGH} min (${PLAT_TAG} · ${DISK_TOTAL_GB} GB ${MEDIA_EN} · CPU: ${GB_MODE}). Launching engine...${RESET}"
else
    echo -e "\n${CYAN}>>> 预计总执行时间：约 ${EST_LOW}–${EST_HIGH} 分钟（${PLAT_TAG} · ${DISK_TOTAL_GB} GB ${MEDIA_ZH} · CPU: ${GB_MODE}），正在启动测评引擎...${RESET}"
fi

curl -fsSL "${SITE_URL}/core.py" -o "$TMP_CORE"

python3 "$TMP_CORE" \
    --lang "$LANG_CODE" --target "$TARGET_DIR" --minutes "$MINUTES" \
    --ioping "$RUN_IOPING" --matrix "$RUN_MATRIX" --prod "$RUN_PROD" \
    --concurrency "$RUN_CONC" --sustained "$RUN_SUSTAINED" \
    --network "$RUN_NET" --ip_quality "$RUN_IPQ" --meta "$RUN_META" \
    --geekbench "$GB_MODE" --profile "$PROFILE_MODE" \
    --site-url "$SITE_URL" --upload-url "${SITE_URL}/api/v1/record"
