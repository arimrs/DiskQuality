"use strict";

const settings = JSON.parse(document.querySelector("#payload").textContent);
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
const bilingual = {
  language: ["页面语言", "Page language"], objective: ["Linux 存储与互联遥测", "LINUX STORAGE & NETWORK TELEMETRY"],
  intro: ["为 PT、大盘与备份服务器设计。测量硬盘稳态、并发 I/O、全球互联与 IP 质量。",
    "Built for PT seedboxes, storage VPS, and backup servers. Measure sustained disk performance, concurrent I/O, global connectivity, and IP quality."],
  taipei: ["台北时间", "Taipei time"], totalRuns: ["累计运行", "Total runs"], todayRuns: ["今日运行", "Today’s runs"],
  builder: ["一键命令生成器", "One-click command builder"], cliLang: ["报告语言", "Report language"], auto: ["自动", "Auto"],
  budget: ["时间预算", "Time budget"], budgetDefault: ["20m（默认）", "20m (Default)"], profile: ["平台", "Profile"],
  geekbench: ["CPU Geekbench", "CPU Geekbench"], autoYes: ["自动确认", "Auto-yes"], skip: ["跳过", "Skip"],
  copy: ["复制", "Copy"], copied: ["已复制 ✔", "Copied ✔"], copyFailed: ["复制失败", "Copy failed"],
  showcase: ["三视图报告", "Three report views"], dimensions: ["测评维度", "Benchmark dimensions"],
  credits: ["致谢与底层工具", "Acknowledgments & upstream tools"],
  privacy: ["报告默认长期保存。公网 IP 自动打码，主机名会被移除，报告页禁止搜索引擎索引。",
    "Reports are retained by default. Public IPs are masked, hostnames are removed, and report pages carry no-index directives."],
  dash: ["可视化看板", "Dashboard"], card: ["矢量战报图", "Visual Card"], terminal: ["极客终端卡", "Terminal"],
  dashDesc: ["查看硬盘雷达、可排序 FIO 矩阵和逐分钟双轴曲线。", "Explore the disk radar, sortable FIO matrix, and minute-by-minute timeline."],
  cardDesc: ["分享一张独立矢量图，支持 SVG 与 2× PNG。", "Share a standalone vector report as SVG or 2× PNG."],
  terminalDesc: ["六页终端报告，保留 ANSI 高亮与精确列对齐。", "Read six pages of ANSI highlights and aligned terminal columns."],
  text: ["复制文本", "Copy Text"], nodeseek: ["复制 NodeSeek", "Copy NodeSeek"], markdown: ["复制 Markdown", "Copy Markdown"],
  png: ["导出 PNG (2×)", "Export PNG (2×)"], svg: ["导出 SVG", "Export SVG"], json: ["下载 JSON", "Download JSON"],
  exported: ["已导出", "Exported"], exportFailed: ["导出失败", "Export failed"],
  persist: ["长期保存", "Persistent"], ttl: ["约 {n} 分钟后到期", "Expires in ~{n} min"],
  views: ["报告视图", "Report views"], terminalTabs: ["终端分页", "Terminal pages"], prev: ["上一页", "Previous page"], next: ["下一页", "Next page"],
  keyboard: ["V 切换视图 · ← / → 翻页 · 1–6 跳转终端页", "V cycles views · ← / → changes pages · 1–6 opens terminal pages"],
  hardware: ["硬件与设备拓扑", "HARDWARE & DEVICE TOPOLOGY"], diskCapacity: ["磁盘容量", "Disk capacity"],
  used: ["已用", "Used"], free: ["可用", "Available"], total: ["总计", "Total"], core: ["核", "core"], cores: ["核", "cores"],
  disk: ["硬盘综合评分", "Disk Composite Score"], oversell: ["超售指数 ↓", "Overselling Index ↓"], ip: ["IP 综合风控 ↓", "IP Composite Risk ↓"],
  grade: ["等级", "Grade"], ref: ["基准", "Ref"], sc: ["单核", "Single-Core"], mc: ["多核", "Multi-Core"],
  open: ["开放", "Open"], blocked: ["阻断/超时", "Blocked / timed out"], empty: ["未测 / 未包含", "Skipped / Not Included"],
  noSamples: ["无逐分钟采样", "No per-minute samples"], radar: ["六维硬盘雷达", "6-Axis Disk Radar"],
  endurance: ["50% 容量持久曲线", "50% Capacity Endurance"], minute: ["分钟", "Minute"],
  phaseA: ["阶段 A · 顺序写入", "Phase A · Sequential Write"], phaseB: ["阶段 B · 随机混合", "Phase B · Random Mix"],
  stage: ["阶段", "Stage"], written: ["已写入", "Written"], avg: ["均速", "Avg"],
  fio: ["FIO 读写性能", "FIO Read / Write Performance"], all: ["全部", "All"], seq: ["顺序", "Sequential"], rnd: ["随机", "Random"],
  prod: ["生产", "Production"], conc: ["并发", "Concurrency"], workload: ["测试项目", "Workload"], group: ["分组", "Group"],
  read: ["读", "Read"], write: ["写", "Write"], r99: ["读 p99", "Read p99"], w99: ["写 p99", "Write p99"],
  net: ["全球互联与 IP 质量", "Global Connectivity & IP Quality"], rtt: ["节点 RTT", "Hub RTT"],
  download: ["大文件下行", "Bulk download"], risk: ["多源 API 风控值", "Multi-API risk scores"],
  unlock: ["平台可达性", "Platform reachability"], timeout: ["超时", "Timeout"], pass: ["放行", "Reachable"], deny: ["拦截/拒访", "Denied"],
  meta: ["元数据与介质寿命", "Metadata & Media Lifetime"], create: ["创建", "Create"], stat: ["Stat", "Stat"],
  readOp: ["读取", "Read"], unlink: ["删除", "Unlink"], power: ["通电", "Power-on"], ext4: ["Ext4 超级块", "Ext4 superblock"],
  created: ["创建时间", "Created"], mounts: ["挂载次数", "Mount count"], lifetime: ["累计写入", "Lifetime writes"],
  sample: ["示例数据", "Sample Data"],
  tiers: [["极低/接近独服", "轻度共享", "中度超售", "重度超售"], ["Minimal / Near-Dedicated", "Light Sharing", "Moderate Overselling", "Heavy Overselling"]],
  riskLevels: [["极低/低风控", "中等风控", "高风控"], ["Low Risk", "Medium Risk", "High Risk"]],
  axes: [["顺序", "4K", "延迟", "并发", "持久", "元数据"], ["Seq", "4K", "Lat", "Conc", "Sust", "Meta"]],
  tabs: [["全部", "基本信息", "硬盘矩阵", "持久时序", "互联与 IP", "元数据与寿命"], ["All", "Overview", "Disk Matrix", "Endurance", "Net & IP", "Meta & Life"]],
  dim: [
    [
      ["系统与块设备", "CPU、系统、调度与对齐"], ["量化评分", "综合评分、超售与 Geekbench"], ["I/O 延迟", "ioping 与同步写入"],
      ["FIO 矩阵", "顺序、随机与尾延迟"], ["生产负载", "OLTP、Web 与 fsync"], ["并发 I/O", "PT 做种与并发备份"],
      ["容量耐久", "50% 容量与 iostat"], ["全球互联", "节点 RTT 与大文件下行"], ["IP 质量", "多源风控与平台可达性"],
      ["元数据与寿命", "文件操作、SMART 与 Ext4"]
    ], [
      ["System & block device", "CPU, OS, I/O scheduler"], ["Objective scores", "Disk, overselling, Geekbench"],
      ["I/O latency", "ioping and sync writes"], ["FIO matrix", "Sequential, random, tail latency"],
      ["Production I/O", "OLTP, web, fsync"], ["Concurrent I/O", "PT seeding and backup"],
      ["Capacity endurance", "50% capacity and iostat"], ["Global connectivity", "Hub RTT and downloads"],
      ["IP quality", "Multi-API risk and platform access"], ["Metadata & lifetime", "File ops, SMART, Ext4"]
    ]
  ]
};
let lang = settings.lang;
const L = {};
let toastTimer;

function localize() {
  const index = lang === "zh" ? 0 : 1;
  for (const [key, labels] of Object.entries(bilingual)) L[key] = labels[index];
  document.documentElement.lang = index ? "en" : "zh-CN";
  $$("[data-label]").forEach(node => { node.textContent = L[node.dataset.label]; });
  $$("[data-label-aria]").forEach(node => { node.setAttribute("aria-label", L[node.dataset.labelAria]); });
  $$("[data-lang]").forEach(button => { button.setAttribute("aria-pressed", button.dataset.lang === lang); });
}

function bindLanguage(render) {
  function update() {
    localize();
    render();
  }
  $$("[data-lang]").forEach(button => button.addEventListener("click", () => {
    lang = button.dataset.lang;
    update();
  }));
  update();
}

function el(tag, className, value) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (value !== undefined) node.textContent = value;
  return node;
}

function svg(tag, props = {}, value) {
  const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
  Object.entries(props).forEach(([key, val]) => node.setAttribute(key, val));
  if (value !== undefined) node.textContent = value;
  return node;
}

const obj = value => value && typeof value === "object" && !Array.isArray(value) ? value : {};
const rows = value => Array.isArray(value) ? value.filter(row => Object.keys(obj(row)).length) : [];
const text = value => value === undefined || value === null || value === "" ? "—" : String(value);
function num(value) {
  if (typeof value !== "number" && (typeof value !== "string" || !value.trim())) return null;
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}
const fmt = (value, digits = 1, suffix = "") => num(value) === null ? "—" : num(value).toFixed(digits) + suffix;
const ratio = (value, max) => value > 0 && max > 0 ? Math.min(value, max) / max : 0;
const empty = (label = L.empty) => el("p", "empty", label);
const pill = (label, color = "") => el("span", "pill " + color, label);
const hue = name => "var(--" + name + ")";
const svgInk = "#dce8f8", svgMuted = "#a6b5ca", svgGrid = "#304058";

function choose(host, options, selected, set) {
  host.replaceChildren(...options.map(([value, label]) => {
    const button = el("button", "chip", label);
    button.type = "button";
    button.setAttribute("aria-pressed", value === selected);
    button.addEventListener("click", () => set(value));
    return button;
  }));
}

function meter(value, max, color) {
  const track = el("div", "metric-track");
  const fill = el("span");
  fill.style.width = (ratio(value, max) * 100) + "%";
  fill.style.background = color;
  track.append(fill);
  return track;
}

function toast(message) {
  const box = $("#toast");
  clearTimeout(toastTimer);
  box.textContent = message;
  toastTimer = setTimeout(() => { box.textContent = ""; }, 2400);
}

async function copyToClipboard(value) {
  try {
    await navigator.clipboard.writeText(value);
    return true;
  } catch {
    const input = el("textarea");
    const focus = document.activeElement;
    input.value = value;
    input.setAttribute("readonly", "");
    input.style.cssText = "position:fixed;inset:0 auto auto -999px";
    document.body.append(input);
    input.select();
    try {
      return document.execCommand("copy");
    } finally {
      input.remove();
      focus?.focus();
    }
  }
}

function initHome() {
  const groups = [
    ["cliLang", "-l", [["", "auto"], ["zh"], ["en"]]],
    ["budget", "-m", [["", "budgetDefault"], ["10", null, "10m"], ["5", null, "5m"]]],
    ["profile", "-p", [["", null, "auto"], ["dedicated"], ["vds"], ["vps"], ["container"]]],
    ["geekbench", "--gb", [["", null, "gb5"], ["gb6"], ["skip", "skip"]]],
    ["autoYes", "-y", [["-y"]]]
  ];
  const choices = new Map(groups.map(([key]) => [key, ""]));
  const code = $("#command");
  const copyButton = $("#copy-command");
  function command() {
    code.textContent = settings.command + groups.map(([key, flag]) => {
      const value = choices.get(key);
      return value ? " " + flag + (flag === "-y" ? "" : " " + value) : "";
    }).join("");
  }
  function render() {
    const options = $("#command-options");
    options.replaceChildren();
    for (const [key, flag, values] of groups) {
      const row = el("div", "option-row");
      const buttons = el("div", "chips");
      buttons.setAttribute("role", "group");
      buttons.setAttribute("aria-label", L[key]);
      row.append(el("strong", "", L[key]), buttons);
      options.append(row);
      choose(buttons, values.map(([value, label, display]) => [value, L[label] || display || value]), choices.get(key), value => {
        choices.set(key, flag === "-y" && choices.get(key) ? "" : value);
        $$(".chip", buttons).forEach((button, index) => {
          button.setAttribute("aria-pressed", values[index][0] === choices.get(key));
        });
        command();
      });
    }
    $("#dimensions").replaceChildren(...L.dim.map(([title, detail]) => {
      const tile = el("article", "panel");
      tile.append(el("h3", "", title), el("p", "dim-detail", detail));
      return tile;
    }));
    command();
  }
  let copyTimer;
  copyButton.addEventListener("click", async () => {
    clearTimeout(copyTimer);
    try {
      copyButton.textContent = await copyToClipboard(code.textContent) ? L.copied : L.copyFailed;
    } catch {
      copyButton.textContent = L.copyFailed;
    }
    copyTimer = setTimeout(() => { copyButton.textContent = L.copy; }, 1800);
  });
  const start = Date.parse(settings.taipei.replace(" ", "T") + "+08:00");
  const loaded = performance.now();
  if (Number.isFinite(start)) {
    setInterval(() => {
      $("#taipei-clock").textContent = new Date(start + performance.now() - loaded + 28800000)
        .toISOString().slice(0, 19).replace("T", " ");
    }, 1000);
  }
  bindLanguage(render);
}

function initReport() {
  const data = settings.data;
  const t = obj(data.topology), plan = obj(data.plan), selected = obj(data.selected);
  const permitted = (key, flag = key) => !Object.hasOwn(selected, flag) || selected[flag] ? data[key] : null;
  const disk = obj(permitted("disk_score")), over = obj(permitted("overselling")), cpu = obj(permitted("geekbench"));
  const ip = obj(permitted("ip_quality")), sus = obj(permitted("sustained")), net = obj(permitted("network"));
  const metadata = obj(permitted("metadata", "meta")), life = obj(permitted("lifetime", "meta"));
  let mode = 0, page = 0, metric = "bw_mbs", group = "all", region = "All";
  let sort = { key: "", reverse: false };
  const tabs = $$("#terminal-tabs button");
  const modeButtons = $$("#mode-tabs button");

  function art(key, host) {
    if (host.dataset.current !== key) {
      host.replaceChildren($("#art-" + key).content.cloneNode(true));
      host.dataset.current = key;
    }
  }

  function goPage(index) {
    page = (index + tabs.length) % tabs.length;
    tabs.forEach((button, i) => button.setAttribute("aria-pressed", i === page));
    $("#terminal-index").textContent = (page + 1) + "/" + tabs.length;
    if (mode === 2) art(settings.pages[page], $("#terminal-art"));
  }

  function showMode(index) {
    mode = (index + modeButtons.length) % modeButtons.length;
    modeButtons.forEach((button, i) => {
      button.setAttribute("aria-pressed", i === mode);
      document.getElementById(button.getAttribute("aria-controls")).hidden = i !== mode;
    });
    if (mode === 1) art("card", $("#card-art"));
    if (mode === 2) goPage(page);
  }

  function gauge(score, color) {
    const label = score === null ? "N/A" : fmt(score);
    const graphic = svg("svg", {viewBox: "0 0 100 100", class: "gauge", role: "img", "aria-label": label + " / 100"});
    const ring = {cx: 50, cy: 50, r: 42, fill: "none", "stroke-width": 7};
    graphic.append(svg("circle", {...ring, stroke: svgGrid}));
    if (score > 0) {
      graphic.append(svg("circle", {...ring, stroke: color, transform: "rotate(-90 50 50)", "stroke-linecap": "round",
        pathLength: 100, "stroke-dasharray": "100 100", "stroke-dashoffset": 100 - ratio(score, 100) * 100, class: "gauge-arc"}));
    }
    graphic.append(svg("text", {x: 50, y: 57, "text-anchor": "middle",
      textLength: Math.min(65, label.length * 12), lengthAdjust: "spacingAndGlyphs"}, label));
    return graphic;
  }

  function detail(...children) {
    const box = el("div", "kpi-detail");
    box.append(...children.filter(Boolean));
    return box;
  }

  function renderKpis() {
    const specs = el("div");
    specs.append(el("span", "kicker", L.hardware), el("h2", "", text(t.cpu_model)));
    const cores = num(t.cpu_cores), coreLabel = cores === 1 ? L.core : L.cores;
    const values = [cores === null ? "" : cores + " " + coreLabel, t.disk_model, t.fs_type, t.os].filter(Boolean);
    specs.append(el("p", "specs", values.join(" · ") || L.empty));
    if (data.report_time) specs.append(el("p", "specs mono", data.report_time));
    const capacity = el("div", "capacity"), capTitle = el("div", "capacity-title");
    const capValues = el("div", "cap-values mono"), capTrack = el("div", "cap-track");
    const [used, avail, total] = ["used", "avail", "total"].map(key => num(plan["disk_" + key + "_gb"]));
    const usedPart = ratio(used, total), availPart = Math.min(1 - usedPart, ratio(avail, total));
    capTitle.append(el("b", "", L.diskCapacity), el("span", "mono", fmt(used === null || !total ? null : usedPart * 100, 1, "%")));
    for (const [label, value] of [[L.used, used], [L.free, avail], [L.total, total]]) {
      capValues.append(el("span", "", label + " " + fmt(value, 1, " GB")));
    }
    for (const [fraction, color] of [[usedPart, "green"], [availPart, "cyan"]]) {
      const fill = el("span");
      fill.style.width = (fraction * 100) + "%";
      fill.style.background = hue(color);
      capTrack.append(fill);
    }
    capacity.append(capTitle, capTrack, capValues);
    $("#hardware").replaceChildren(specs, capacity);

    const ds = num(disk.score), os = num(over.score), risk = num(ip.composite_risk);
    const oversellHue = os > 60 ? "rose" : os > 35 ? "amber" : "green";
    const riskHue = risk > 55 ? "rose" : risk > 25 ? "amber" : "green";
    const tier = /^t[0-3]$/.test(over.tier) ? L.tiers[Number(over.tier[1])] : text(over.tier);
    const riskTier = L.riskLevels[["low", "mid", "high"].indexOf(ip.composite_tier)];
    const cpuMetrics = el("div", "cpu-metrics");
    const cpuScores = [num(cpu.single_core), num(cpu.multi_core)];
    if (cpuScores.some(value => value !== null)) {
      cpuMetrics.append(pill(text(cpu.version || "Geekbench"), "violet"));
      cpuScores.forEach((value, i) => {
        const line = el("div", "metric-title");
        line.append(el("span", "", i === 0 ? L.sc : L.mc), el("b", "mono", fmt(value, 0)));
        const bar = svg("svg", {viewBox: "0 0 100 4", preserveAspectRatio: "none", class: "cpu-gauge", "aria-hidden": "true"});
        bar.append(svg("rect", {width: 100, height: 4, rx: 2, fill: svgGrid}),
          svg("rect", {width: 100 * ratio(value, Math.max(1, ...cpuScores)), height: 4, rx: 2,
            fill: hue(i === 0 ? "cyan" : "violet"), class: "cpu-gauge-fill"}));
        cpuMetrics.append(line, bar);
      });
    } else cpuMetrics.append(empty());
    const port = ip.port25_open;
    const dns = Array.isArray(ip.dnsbl_hits) ? ip.dnsbl_hits.length + "/" + text(ip.dnsbl_total ?? 3) : "—";
    const identity = [obj(ip.meta).native_type, obj(ip.meta).hosting].filter(Boolean).join(" · ");
    const cards = [
      [L.disk, gauge(ds, hue("green")), detail(el("span", "mono", "/ 100"), disk.grade && pill(L.grade + " " + disk.grade, "green"))],
      [L.oversell, gauge(os, hue(oversellHue)), detail(el("span", "", os === null ? "/ 100" : tier), over.media && pill(L.ref + " · " + over.media, "violet"))],
      [L.geekbench, cpuMetrics],
      [L.ip, ...(!Object.keys(ip).length ? [empty()] : [
        gauge(risk, hue(riskHue)), detail(el("span", "", [riskTier, identity].filter(Boolean).join(" · ") || "/ 100"),
          pill("Port 25 · " + (port === true ? L.open : port === false ? L.blocked : "—"), port === true ? "green" : port === false ? "rose" : ""),
          pill("DNSBL · " + dns, ip.dnsbl_hits?.length ? "rose" : ""))
      ])]
    ];
    $("#kpis").replaceChildren(...cards.map(([label, ...contents]) => {
      const article = el("article", "panel kpi");
      const body = el("div", "kpi-body");
      body.append(...contents);
      article.append(el("h3", "", label), body);
      return article;
    }));
  }

  function chart(host, box, label) {
    const graphic = svg("svg", {viewBox: box, class: "chart", role: "group", "aria-label": label});
    const tip = el("div", "chart-tip");
    tip.hidden = true;
    tip.setAttribute("aria-hidden", "true");
    host.replaceChildren(graphic, tip);
    return [graphic, tip];
  }

  function tipTarget(host, tip, target, label) {
    target.setAttribute("tabindex", "0");
    target.setAttribute("aria-label", label.replaceAll("\n", ", "));
    const show = event => {
      tip.textContent = label;
      tip.hidden = false;
      const box = host.getBoundingClientRect(), targetBox = target.getBoundingClientRect();
      const x = event.type === "focus" ? targetBox.left + targetBox.width / 2 : event.clientX;
      const y = event.type === "focus" ? targetBox.top + Math.min(targetBox.height / 2, 45) : event.clientY;
      const left = Math.max(0, Math.min(host.clientWidth - tip.offsetWidth, x - box.left + 9));
      const top = Math.max(0, Math.min(host.clientHeight - tip.offsetHeight, y - box.top + 10));
      tip.style.left = left + host.scrollLeft + "px";
      tip.style.top = top + host.scrollTop + "px";
    };
    target.addEventListener("pointerenter", show);
    target.addEventListener("pointermove", show);
    target.addEventListener("focus", show);
    target.addEventListener("pointerleave", () => { if (document.activeElement !== target) tip.hidden = true; });
    target.addEventListener("blur", () => { tip.hidden = true; });
  }

  function renderRadar() {
    const host = $("#radar");
    const scores = ["s_seq", "s_4k", "s_lat", "s_conc", "s_sust", "s_meta"].map(key => num(disk[key]));
    if (scores.every(value => value === null)) {
      host.replaceChildren(empty());
      return;
    }
    const [chartSvg, tip] = chart(host, "0 0 410 300", L.radar);
    const point = (i, fraction) => {
      const angle = (i / 3 - .5) * Math.PI;
      return [205 + Math.cos(angle) * 106 * fraction, 150 + Math.sin(angle) * 106 * fraction];
    };
    const coords = points => points.map(pair => pair.join(",")).join(" ");
    for (const f of [.25, .50, .75, 1]) {
      chartSvg.append(svg("polygon", {points: coords(scores.map((_, i) => point(i, f))), stroke: svgGrid, fill: "none"}),
        svg("text", {x: 211, y: 150 - 106 * f + 9, fill: svgMuted, "font-size": 9}, f * 100 + "%"));
    }
    const vertices = scores.map((v, i) => v === null ? null : point(i, ratio(v, 100)));
    scores.forEach((score, i) => {
      const [x, y] = point(i, 1), [lx, ly] = point(i, 1.25);
      chartSvg.append(svg("line", {x1: 205, y1: 150, x2: x, y2: y, stroke: svgGrid}),
        svg("text", {x: lx, y: ly + 4, fill: svgInk, "font-size": 12,
          "text-anchor": i % 3 === 0 ? "middle" : i < 3 ? "start" : "end"}, L.axes[i] + " " + text(score)));
    });
    if (vertices.every(Boolean)) {
      chartSvg.append(svg("polygon", {points: coords(vertices), fill: "#44eab1", "fill-opacity": .23,
        stroke: "#5fe2e7", "stroke-width": 2}));
    } else {
      vertices.forEach((a, i) => {
        const b = vertices[(i + 1) % vertices.length];
        if (a && b) chartSvg.append(svg("line", {x1: a[0], y1: a[1], x2: b[0], y2: b[1], stroke: "#5fe2e7", "stroke-width": 2}));
      });
    }
    vertices.forEach((vertex, i) => {
      if (!vertex) return;
      const [cx, cy] = vertex;
      chartSvg.append(svg("circle", {cx, cy, r: 4, fill: "#7cf2bb", "pointer-events": "none"}));
      const target = svg("circle", {cx, cy, r: 10, fill: "transparent", class: "hover-target"});
      tipTarget(host, tip, target, L.axes[i] + " · " + scores[i] + " / 100");
      chartSvg.append(target);
    });
  }

  function seriesRuns(values, project) {
    const runs = [];
    let run = [];
    values.forEach((value, index) => {
      if (value !== null) {
        run.push(project(value, index));
      } else if (run.length) {
        runs.push(run);
        run = [];
      }
    });
    if (run.length) runs.push(run);
    return runs;
  }

  function renderEndurance() {
    const summary = $("#endurance-summary"), host = $("#endurance"), seq = obj(sus.seq_write);
    summary.replaceChildren();
    if (Object.keys(seq).length && !seq.error) {
      const bytes = num(seq.w_bytes);
      summary.append(pill(L.written + " " + fmt(bytes === null ? null : bytes / 1024 ** 3, 1, " GB"), "green"),
        pill(L.avg + " " + fmt(seq.w_bw_mbs, 1, " MB/s"), "cyan"), pill("p99 " + fmt(seq.w_p99_ms, 1, " ms")));
    }
    const points = rows(sus.timeline);
    const values = ["w_mb", "w_await"].map(key => points.map(point => num(point[key])));
    if (values.every(series => series.every(value => value === null))) {
      host.replaceChildren(empty(Object.keys(sus).length ? L.noSamples : L.empty));
      return;
    }
    summary.append(pill(L.phaseA, "green"), pill(L.phaseB, "violet"));
    const [chartSvg, tip] = chart(host, "0 0 670 274", L.endurance);
    const scales = values.map(series => series.reduce((max, v) => Math.max(max, v ?? 0), 1));
    const left = 56, right = 607, top = 34, bottom = 235, slot = (right - left) / points.length;
    const xAt = i => left + slot * (i + .5);
    const yAt = (v, idx) => bottom - (bottom - top) * ratio(v, scales[idx]);
    const green = "#55e898", amber = "#fbbf56";
    const defs = svg("defs"), fade = svg("linearGradient", {id: "endurance-area", x2: "0", y2: "1"});
    fade.append(svg("stop", {"stop-color": green, "stop-opacity": .37}),
      svg("stop", {offset: 1, "stop-color": green, "stop-opacity": .03}));
    defs.append(fade);
    chartSvg.append(defs);
    points.forEach((point, i) => chartSvg.append(svg("rect", {x: left + i * slot,
      y: top, width: slot + .1, height: bottom - top, fill: settings.phases[i] ? "#173232" : "#262741"})));
    for (let i = 0; i <= 4; i++) {
      const y = bottom - (bottom - top) * i / 4;
      chartSvg.append(svg("line", {x1: left, y1: y, x2: right, y2: y, stroke: svgGrid}),
        svg("text", {x: left - 7, y: y + 4, "text-anchor": "end", fill: svgMuted, "font-size": 11}, fmt(scales[0] * (i / 4))),
        svg("text", {x: right + 7, y: y + 4, fill: svgMuted, "font-size": 11}, fmt(scales[1] * (i / 4))));
    }
    chartSvg.append(svg("text", {x: left, y: 20, fill: green, "font-size": 12}, "wMB/s"),
      svg("text", {x: right, y: 20, fill: amber, "font-size": 12, "text-anchor": "end"}, "w_await · ms"),
      svg("text", {x: 331, y: 271, fill: svgMuted, "font-size": 11, "text-anchor": "middle"}, L.minute));
    const ticks = new Set(Array.from({length: 8}, (_, i) => Math.round(i * (points.length - 1) / 7)));
    points.forEach((point, i) => {
      if (ticks.has(i) && num(point.min) !== null) {
        chartSvg.append(svg("text", {x: xAt(i), y: 253, fill: svgMuted, "font-size": 11, "text-anchor": "middle"}, point.min));
      }
    });
    values.forEach((series, idx) => {
      const color = idx === 0 ? green : amber;
      for (const run of seriesRuns(series, (v, i) => [xAt(i), yAt(v, idx)])) {
        if (run.length === 1) {
          chartSvg.append(svg("circle", {cx: run[0][0], cy: run[0][1], r: 3, fill: color}));
          continue;
        }
        const coords = run.map(point => point.join(",")).join(" ");
        if (idx === 0) {
          chartSvg.append(svg("polygon", {points: run[0][0] + "," + bottom + " " + coords + " " + run.at(-1)[0] + "," + bottom,
            fill: "url(#endurance-area)"}));
        }
        const props = {points: coords, stroke: color, "stroke-width": 2, fill: "none"};
        if (idx === 1) props["stroke-dasharray"] = "6 5";
        chartSvg.append(svg("polyline", props));
      }
    });
    points.forEach((point, i) => {
      const target = svg("rect", {x: left + slot * i, y: top, width: slot,
        height: bottom - top, fill: "transparent", class: "minute-target"});
      const stage = settings.phases[i] ? L.phaseA : L.phaseB;
      tipTarget(host, tip, target, [
        L.minute + " " + text(point.min), L.stage + " · " + stage,
        "rMB/s  " + text(point.r_mb), "wMB/s  " + text(point.w_mb), "r/s    " + text(point.r_s),
        "w/s    " + text(point.w_s), "w_await  " + text(point.w_await) + " ms", "%util  " + text(point.util)
      ].join("\n"));
      chartSvg.append(target);
    });
  }

  const fioRows = [
    ...rows(permitted("matrix")).map(row => ({row, group: /^RND/.test(row.name) ? "rnd" : "seq"})),
    ...rows(permitted("production", "prod")).map(row => ({row, group: "prod"})),
    ...rows(permitted("concurrency")).map(row => ({row, group: "conc"}))
  ].filter(({row}) => row.name && !row.error);

  function fioValue(row, direction, kind) {
    const value = num(row[direction + "_" + kind]), iops = num(row[direction + "_iops"]);
    return value === 0 && iops === 0 ? null : value;
  }

  function renderFio() {
    const filters = $("#fio-controls"), content = $("#fio-content");
    filters.replaceChildren();
    const filtered = fioRows.filter(item => group === "all" || item.group === group);
    if (!fioRows.length) {
      content.replaceChildren(empty());
      return;
    }
    const metricButtons = el("div", "chips"), groupButtons = el("div", "chips");
    filters.append(metricButtons, groupButtons);
    const change = (setting, value) => {
      if (setting === "metric") {
        metric = value;
        sort = {key: "", reverse: false};
      } else group = value;
      renderFio();
      $$(".chip[aria-pressed='true']", filters)[setting === "metric" ? 0 : 1]?.focus();
    };
    choose(metricButtons, [["bw_mbs", "MB/s"], ["iops", "IOPS"], ["p99_ms", "p99 ms"]], metric, value => change("metric", value));
    choose(groupButtons, ["all", "seq", "rnd", "prod", "conc"].map(key => [key, L[key]]), group, value => change("group", value));
    if (!filtered.length) {
      content.replaceChildren(empty());
      return;
    }
    const digits = metric === "iops" ? 0 : 2;
    const maximum = filtered.reduce((max, {row}) => Math.max(max, fioValue(row, "r", metric), fioValue(row, "w", metric)), 1);
    const columns = [
      ["name", L.workload, item => String(item.row.name)], ["group", L.group, item => L[item.group]],
      ["r", L.read, item => fioValue(item.row, "r", metric)], ["w", L.write, item => fioValue(item.row, "w", metric)]
    ];
    if (metric !== "p99_ms") {
      columns.push(["r99", L.r99, item => fioValue(item.row, "r", "p99_ms")],
        ["w99", L.w99, item => fioValue(item.row, "w", "p99_ms")]);
    }
    const host = el("div", "fio-scroll"), table = el("table", "fio-table");
    const thead = el("thead"), header = el("tr"), body = el("tbody");
    columns.forEach(([key, label, get]) => {
      const current = sort.key === key, th = el("th");
      th.setAttribute("scope", "col");
      if (current) {
        th.setAttribute("aria-sort", sort.reverse ? "descending" : "ascending");
        filtered.sort((a, b) => {
          const x = get(a), y = get(b);
          if (x === null || y === null) return x === y ? 0 : x === null ? 1 : -1;
          return (typeof x === "string" ? x.localeCompare(y, lang) : x - y) * (sort.reverse ? -1 : 1);
        });
      }
      const button = el("button", "", label + (current ? sort.reverse ? " ↓" : " ↑" : ""));
      button.value = key;
      button.addEventListener("click", () => {
        sort = {key, reverse: current ? !sort.reverse : key !== "name" && key !== "group"};
        renderFio();
        $$("th button", content).find(b => b.value === key)?.focus();
      });
      th.append(button);
      header.append(th);
    });
    filtered.forEach(item => {
      const tr = el("tr");
      for (const [key, , get] of columns) {
        const td = el("td", key === "name" ? "mono" : ""), value = get(item);
        if ((key === "r" || key === "w") && value !== null) {
          const line = el("div", "fio-value");
          line.append(el("span", "", fmt(value, digits)), meter(value, maximum, hue(key === "r" ? "cyan" : "green")));
          td.append(line);
        } else td.textContent = key === "r99" || key === "w99" ? fmt(value, 2) : text(value);
        tr.append(td);
      }
      body.append(tr);
    });
    thead.append(header);
    table.append(thead, body);
    host.append(table);
    content.replaceChildren(host);
  }

  const regionColors = {APAC: "#61d4ff", US: "#c3a5ff", EU: "#55e898"};
  const hubs = rows(net.hubs).map(hub => {
    const country = String(hub.hub).match(/\(([A-Z]{2})\)/)?.[1];
    return {hub, region: settings.regions[country]};
  });
  const riskSources = rows(ip.risk_sources);
  const probes = new Map(rows(ip.probes).map(row => [row.service, row]));
  function renderNet() {
    const host = $("#net-content");
    if (!hubs.length && !rows(net.downloads).length && !riskSources.length && !probes.size && !Object.keys(ip).length) {
      host.replaceChildren(empty());
      return;
    }
    const left = el("div"), right = el("div"), netList = el("div", "net-list");
    const filters = el("div", "chips"), controls = el("div", "section-head");
    const maximum = hubs.reduce((max, {hub}) => Math.max(max, num(hub.max), num(hub.avg)), 1);
    const drawHubs = () => {
      const visible = hubs.filter(h => region === "All" || h.region === region);
      netList.replaceChildren();
      if (!visible.length) netList.append(empty());
      visible.forEach(({hub, region}) => {
        const line = el("div", "rtt-line");
        const color = regionColors[region] || svgMuted;
        const a = num(hub.min), b = num(hub.avg), c = num(hub.max);
        const [minX, avgX, maxX] = [a, b, c].map(v => 5 + ratio(v, maximum) * 150);
        const graphic = svg("svg", {viewBox: "0 0 160 16", preserveAspectRatio: "none", "aria-hidden": "true"});
        graphic.append(svg("line", {x1: 5, x2: 155, y1: 8, y2: 8, stroke: svgGrid, "stroke-width": 2}));
        if (b !== null && b >= 0) {
          if (a !== null && c !== null && a >= 0 && c >= 0) {
            graphic.append(svg("line", {x1: minX, x2: maxX, y1: 8, y2: 8, stroke: color, "stroke-width": 2}));
            for (const x of [minX, maxX]) graphic.append(svg("line", {x1: x, x2: x, y1: 4, y2: 12, stroke: color}));
          }
          graphic.append(svg("line", {x1: avgX, x2: avgX, y1: 3, y2: 13, stroke: color, "stroke-width": 3}));
        }
        const name = el("span", "", text(hub.hub));
        name.style.color = color;
        line.append(name, graphic, el("span", "mono", b === null ? "—" : b < 0 ? L.timeout : [a, b, c].map(v => fmt(v)).join(" / ")));
        netList.append(line);
      });
    };
    const regions = [["All", L.all], ...Object.keys(regionColors).map(value => [value, value])];
    choose(filters, regions, region, value => {
      region = value;
      $$(".chip", filters).forEach((button, i) => button.setAttribute("aria-pressed", regions[i][0] === region));
      drawHubs();
    });
    controls.append(el("h3", "", L.rtt + " · ms"), filters);
    left.append(controls, netList);
    drawHubs();
    const downloads = el("div", "downloads");
    rows(net.downloads).forEach(row => {
      const card = el("article", "inset");
      card.append(el("h3", "", text(row.name)), el("span", "value", fmt(row.mbs, 2, " MB/s")),
        el("p", "", fmt(row.mbps, 1, " Mbps")));
      downloads.append(card);
    });
    left.append(el("h3", "subheading home-section", L.download), downloads.children.length ? downloads : empty());

    right.append(el("h3", "subheading", L.risk));
    for (const source of riskSources) {
      const r = el("div", "risk-row"), value = num(source.score);
      const color = value > 55 ? "rose" : value > 25 ? "amber" : "green";
      const reading = el("span", "", fmt(value, 0, " / 100"));
      if (source.raw !== undefined && String(source.raw) !== String(value)) {
        reading.append(document.createTextNode(" · " + text(source.raw)));
      }
      r.append(el("span", "", text(source.api)), meter(value, 100, hue(color)), reading);
      right.append(r);
    }
    if (!riskSources.length) right.append(empty());
    right.append(el("h3", "subheading home-section", L.unlock));
    if (probes.size) {
      const grid = el("div", "unlock");
      for (const service of settings.services) {
        const probe = probes.get(service), ok = probe?.ok;
        const status = ok === true ? ["✔", "green", L.pass] : ok === false ? ["✘", "rose", L.deny] : ["—", "", L.empty];
        const badge = pill(status[0] + " " + service, status[1]);
        badge.title = status[2] + (probe?.code ? " · HTTP " + probe.code : "");
        grid.append(badge);
      }
      right.append(grid);
    } else right.append(empty());
    host.replaceChildren(left, right);
  }

  function renderMeta() {
    const host = $("#meta-content");
    if (!Object.keys(metadata).length && !Object.keys(life).length) {
      host.replaceChildren(empty());
      return;
    }
    const bars = el("div", "meta-bars");
    const metrics = [["create", "create_fps"], ["stat", "stat_fps"], ["readOp", "read_fps"], ["unlink", "delete_fps"]];
    const max = Math.max(1, ...metrics.map(([, key]) => num(metadata[key])));
    if (Object.keys(metadata).length) {
      for (const [label, key] of metrics) {
        const line = el("div"), title = el("div", "metric-title");
        title.append(el("span", "", L[label]), el("b", "mono", fmt(metadata[key], 0, " f/s")));
        line.append(title, meter(num(metadata[key]), max, hue("green")));
        bars.append(line);
      }
    } else bars.append(empty());
    const boxes = el("div", "lifetime");
    if (Object.keys(life).length) {
      const smart = el("article", "inset"), ext4 = el("article", "inset");
      smart.append(el("h3", "", "SMART"), el("p", "", text(life.smart_raw_status)),
        el("p", "", L.power + " · " + fmt(life.smart_power_on_hours, 0, " h")));
      ext4.append(el("h3", "", L.ext4));
      for (const [label, key] of [["created", "fs_created"], ["mounts", "mount_count"], ["lifetime", "lifetime_writes"]]) {
        ext4.append(el("p", "", L[label] + " · " + text(life[key])));
      }
      boxes.append(smart, ext4);
    } else boxes.append(empty());
    host.replaceChildren(bars, boxes);
  }

  function download(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = el("a");
    link.href = url;
    link.download = filename;
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10000);
  }

  async function save(format) {
    const key = mode === 2 ? settings.pages[page] : "card";
    const filename = "diskquality_" + settings.rid + "_" + key;
    if (format === "json") {
      download(new Blob([JSON.stringify(data, null, 2)], {type: "application/json"}), "diskquality_" + settings.rid + ".json");
      return;
    }
    const vector = $("#art-" + key).content.querySelector("svg");
    const bytes = new Blob([new XMLSerializer().serializeToString(vector)], {type: "image/svg+xml;charset=utf-8"});
    if (format === "svg") {
      download(bytes, filename + ".svg");
      return;
    }
    const image = new Image(), url = URL.createObjectURL(bytes);
    try {
      image.src = url;
      await image.decode();
      const canvas = el("canvas");
      canvas.width = 2 * Number(vector.getAttribute("width"));
      canvas.height = 2 * Number(vector.getAttribute("height"));
      canvas.getContext("2d").drawImage(image, 0, 0, canvas.width, canvas.height);
      const png = await new Promise(resolve => canvas.toBlob(resolve, "image/png"));
      if (!png) throw new Error("Canvas export failed");
      download(png, filename + "@2x.png");
    } finally {
      URL.revokeObjectURL(url);
    }
  }

  modeButtons.forEach((button, index) => button.addEventListener("click", () => showMode(index)));
  tabs.forEach((button, index) => button.addEventListener("click", () => goPage(index)));
  $("#terminal-prev").addEventListener("click", () => goPage(page - 1));
  $("#terminal-next").addEventListener("click", () => goPage(page + 1));
  $$(".viewport").forEach(box => box.addEventListener("pointermove", event => {
    const rect = box.getBoundingClientRect();
    box.style.setProperty("--mx", event.clientX - rect.left + "px");
    box.style.setProperty("--my", event.clientY - rect.top + "px");
  }));
  document.addEventListener("keydown", event => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.defaultPrevented ||
        event.target.matches("input,textarea,select,[contenteditable]")) return;
    if (event.key.toLowerCase() === "v") {
      showMode(mode + 1);
    } else if (/^[1-6]$/.test(event.key)) {
      goPage(Number(event.key) - 1);
      showMode(2);
    } else if (mode === 2 && (event.key === "ArrowLeft" || event.key === "ArrowRight")) {
      goPage(page + (event.key === "ArrowLeft" ? -1 : 1));
    } else return;
    event.preventDefault();
  });
  $$("[data-action]").forEach(button => button.addEventListener("click", async () => {
    const kind = button.dataset.action;
    const exporting = ["svg", "png", "json"].includes(kind);
    try {
      if (exporting) {
        await save(kind);
        toast(L.exported + " · " + kind.toUpperCase());
      } else {
        toast(await copyToClipboard(settings.exports[kind]) ? L.copied + " · " + L[kind] : L.copyFailed);
      }
    } catch {
      toast(exporting ? L.exportFailed : L.copyFailed);
    }
  }));

  bindLanguage(() => {
    $("#retention").textContent = settings.ttl === null ? L.persist : L.ttl.replace("{n}", settings.ttl);
    tabs.forEach((button, index) => { button.textContent = L.tabs[index]; });
    renderKpis();
    renderRadar();
    renderEndurance();
    renderFio();
    renderNet();
    renderMeta();
  });
  showMode(0);
}

if (settings.data) initReport();
else initHome();
