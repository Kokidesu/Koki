const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const {
  FaUniversity, FaUserTie, FaChartLine, FaBalanceScale, FaGavel, FaShieldAlt,
  FaCogs, FaGlobeAsia, FaHandshake, FaCoins, FaLayerGroup, FaExchangeAlt,
  FaBuilding, FaArrowRight, FaTrophy, FaChartPie, FaCrosshairs, FaSyncAlt,
  FaCubes, FaGem, FaWaveSquare, FaCheckCircle, FaTimesCircle,
  FaBriefcase, FaUsers, FaBookOpen, FaFlagCheckered, FaRedo, FaSitemap, FaMoneyBillWave
} = require("react-icons/fa");

// ---------- palette ----------
const NAVY = "0A1A3F";       // dark background
const NAVY2 = "122B5C";      // panel navy
const NAVY3 = "1C3D72";      // lighter navy
const GOLD = "C9A227";       // accent gold
const GOLDL = "E8B84B";      // light gold
const INK = "1B2436";        // body text dark
const SLATE = "5A6678";      // muted
const LINEC = "D8DEE8";      // light divider
const CARDBG = "F4F6FA";     // light card bg
const WHITE = "FFFFFF";

const HF = "Georgia";        // header font
const BF = "Calibri";        // body font

async function iconPng(IconComponent, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}
const makeShadow = () => ({ type: "outer", color: "000000", blur: 7, offset: 3, angle: 135, opacity: 0.16 });

let pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
pres.author = "就活企業研究";
pres.title = "Goldman Sachs 企業研究";
const W = 13.3, H = 7.5;

// ---------- helpers ----------
function pageHeader(slide, kicker, title, opt = {}) {
  // light content slide header (left aligned, no accent line under title)
  slide.addText(kicker, {
    x: 0.6, y: 0.42, w: 11, h: 0.3, fontFace: BF, fontSize: 12.5, bold: true,
    color: GOLD, charSpacing: 2, align: "left", margin: 0
  });
  slide.addText(title, {
    x: 0.6, y: 0.72, w: 12.1, h: 0.85, fontFace: HF, fontSize: opt.size || 29, bold: true,
    color: NAVY, align: "left", margin: 0, valign: "top"
  });
  // small gold square as motif (top-right), not a line under title
  slide.addShape(pres.shapes.RECTANGLE, { x: 12.55, y: 0.5, w: 0.16, h: 0.16, fill: { color: GOLD } });
}
function pageNum(slide, n) {
  slide.addText(String(n).padStart(2, "0"), {
    x: 12.5, y: 7.02, w: 0.5, h: 0.3, fontFace: BF, fontSize: 10, color: SLATE, align: "right", margin: 0
  });
}
function statCard(slide, x, y, w, h, big, label, sub, opt = {}) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h, fill: { color: opt.bg || WHITE }, line: { color: opt.line || LINEC, width: 1 },
    shadow: makeShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.09, h, fill: { color: opt.accent || GOLD } });
  slide.addText(big, {
    x: x + 0.2, y: y + 0.14, w: w - 0.35, h: h * 0.45, fontFace: HF, fontSize: opt.bigSize || 40,
    bold: true, color: opt.bigColor || NAVY, align: "left", valign: "middle", margin: 0
  });
  slide.addText(label, {
    x: x + 0.22, y: y + h * 0.55, w: w - 0.4, h: 0.32, fontFace: BF, fontSize: 13, bold: true,
    color: opt.labelColor || INK, align: "left", margin: 0
  });
  if (sub) slide.addText(sub, {
    x: x + 0.22, y: y + h * 0.55 + 0.32, w: w - 0.4, h: h * 0.3, fontFace: BF, fontSize: 10.5,
    color: opt.subColor || SLATE, align: "left", margin: 0, valign: "top"
  });
}

// ============================================================ MAIN
(async () => {
  // preload icons
  const ic = {};
  const need = [
    ["history", FaUniversity, GOLD], ["ceo", FaUserTie, NAVY],
    ["chart", FaChartLine, GOLD], ["scale", FaBalanceScale, GOLD],
    ["gavel", FaGavel, GOLD], ["shield", FaShieldAlt, GOLD],
    ["cogs", FaCogs, GOLD], ["globe", FaGlobeAsia, NAVY],
    ["hand", FaHandshake, NAVY], ["coins", FaCoins, NAVY],
    ["layer", FaLayerGroup, NAVY], ["swap", FaExchangeAlt, GOLD],
    ["bldg", FaBuilding, NAVY], ["arrow", FaArrowRight, GOLD],
    ["trophy", FaTrophy, GOLD], ["pie", FaChartPie, NAVY],
    ["target", FaCrosshairs, NAVY], ["sync", FaSyncAlt, GOLD],
    ["cubes", FaCubes, NAVY], ["gem", FaGem, NAVY],
    ["wave", FaWaveSquare, GOLD], ["check", FaCheckCircle, "2E7D5B"],
    ["times", FaTimesCircle, "B5453C"], ["brief", FaBriefcase, NAVY],
    ["users", FaUsers, NAVY], ["book", FaBookOpen, NAVY],
    ["flag", FaFlagCheckered, GOLD], ["redo", FaRedo, GOLD],
    ["sitemap", FaSitemap, NAVY], ["money", FaMoneyBillWave, NAVY],
    ["arrowW", FaArrowRight, GOLDL], ["checkG", FaCheckCircle, GOLDL]
  ];
  for (const [k, comp, col] of need) ic[k] = await iconPng(comp, "#" + col);

  // ============================================================ SLIDE 1 — Cover (dark)
  {
    const s = pres.addSlide();
    s.background = { color: NAVY };
    // subtle abstract graph motif on right
    const pts = [6.2, 5.4, 5.8, 4.6, 4.9, 3.6, 3.9, 2.7];
    for (let i = 0; i < pts.length; i++) {
      s.addShape(pres.shapes.RECTANGLE, {
        x: 8.4 + i * 0.62, y: pts[i], w: 0.42, h: 7.0 - pts[i],
        fill: { color: i % 2 ? NAVY3 : NAVY2 }, line: { color: NAVY3, width: 0.5 }
      });
    }
    // rising line over bars
    s.addShape(pres.shapes.LINE, { x: 8.55, y: 6.0, w: 4.35, h: -3.55, line: { color: GOLD, width: 2.5 } });

    s.addText("GS", {
      x: 0.85, y: 0.65, w: 3.2, h: 1.6, fontFace: HF, fontSize: 86, bold: true, italic: true,
      color: GOLD, align: "left", margin: 0
    });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.92, y: 2.45, w: 1.6, h: 0.04, fill: { color: GOLD } });
    s.addText("企業研究", {
      x: 2.55, y: 1.35, w: 5, h: 0.8, fontFace: HF, fontSize: 30, bold: true, color: WHITE, align: "left", margin: 0, valign: "middle"
    });

    s.addText("Goldman Sachs 企業研究", {
      x: 0.85, y: 2.95, w: 11, h: 1.0, fontFace: HF, fontSize: 46, bold: true, color: WHITE, align: "left", margin: 0
    });
    s.addText("アセット・マネジメント部門 × 営業部門 を読み解く", {
      x: 0.88, y: 4.0, w: 11, h: 0.6, fontFace: BF, fontSize: 21, color: GOLDL, align: "left", margin: 0
    });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.9, y: 6.35, w: 0.5, h: 0.04, fill: { color: GOLD } });
    s.addText("就活企業研究  /  2025年版（FY2024決算ベース）", {
      x: 0.88, y: 6.5, w: 9, h: 0.4, fontFace: BF, fontSize: 13, color: "AEBAD0", align: "left", margin: 0
    });
    s.addNotes("表紙。ゴールドマン・サックスをアセマネ部門と営業部門の2軸で読み解く企業研究。FY2024決算ベース。");
  }

  // ============================================================ SLIDE 2 — Conclusion summary (light)
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    pageHeader(s, "EXECUTIVE SUMMARY", "まず結論 — Goldman Sachsの今");
    const cy = 1.95, ch = 4.6, cw = 3.85, gap = 0.28;
    const xs = [0.6, 0.6 + cw + gap, 0.6 + 2 * (cw + gap)];

    // Card 1 V字回復
    s.addShape(pres.shapes.RECTANGLE, { x: xs[0], y: cy, w: cw, h: ch, fill: { color: CARDBG }, line: { color: LINEC, width: 1 }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: xs[0], y: cy, w: cw, h: 0.62, fill: { color: NAVY } });
    s.addText("① V字回復", { x: xs[0] + 0.25, y: cy, w: cw - 0.4, h: 0.62, fontFace: HF, fontSize: 18, bold: true, color: WHITE, valign: "middle", margin: 0 });
    s.addText("12.7%", { x: xs[0] + 0.2, y: cy + 0.85, w: cw - 0.4, h: 1.05, fontFace: HF, fontSize: 60, bold: true, color: NAVY, align: "left", margin: 0 });
    s.addText("全社ROE（2024）", { x: xs[0] + 0.25, y: cy + 1.95, w: cw - 0.45, h: 0.3, fontFace: BF, fontSize: 12.5, color: SLATE, margin: 0 });
    s.addText([
      { text: "ROE 7.5%(2023) → 12.7%", options: { breakLine: true, bullet: true } },
      { text: "純利益 $14.3B", options: { breakLine: true, bullet: true } },
      { text: "EPS $40.54（+77%）", options: { bullet: true } }
    ], { x: xs[0] + 0.28, y: cy + 2.4, w: cw - 0.5, h: 2.0, fontFace: BF, fontSize: 13.5, color: INK, paraSpaceAfter: 7, margin: 0 });

    // Card 2 戦略の核心
    s.addShape(pres.shapes.RECTANGLE, { x: xs[1], y: cy, w: cw, h: ch, fill: { color: CARDBG }, line: { color: LINEC, width: 1 }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: xs[1], y: cy, w: cw, h: 0.62, fill: { color: GOLD } });
    s.addText("② 戦略の核心", { x: xs[1] + 0.25, y: cy, w: cw - 0.4, h: 0.62, fontFace: HF, fontSize: 18, bold: true, color: NAVY, valign: "middle", margin: 0 });
    s.addImage({ data: ic.swap, x: xs[1] + 0.25, y: cy + 0.95, w: 0.7, h: 0.7 });
    s.addText("安定収益へ", { x: xs[1] + 1.05, y: cy + 0.9, w: cw - 1.2, h: 0.8, fontFace: HF, fontSize: 26, bold: true, color: NAVY, valign: "middle", margin: 0 });
    s.addText("durable revenues", { x: xs[1] + 0.27, y: cy + 1.85, w: cw - 0.5, h: 0.3, fontFace: BF, italic: true, fontSize: 12.5, color: GOLD, margin: 0 });
    s.addText([
      { text: "ブレやすい 自己投資／仲介 から", options: { breakLine: true, bullet: true } },
      { text: "安定した 運用フィー／ファイナンシング へ", options: { breakLine: true, bullet: true } },
      { text: "全社を貫く一本の戦略", options: { bullet: true } }
    ], { x: xs[1] + 0.28, y: cy + 2.35, w: cw - 0.5, h: 2.0, fontFace: BF, fontSize: 13.5, color: INK, paraSpaceAfter: 7, margin: 0 });

    // Card 3 2部門
    s.addShape(pres.shapes.RECTANGLE, { x: xs[2], y: cy, w: cw, h: ch, fill: { color: CARDBG }, line: { color: LINEC, width: 1 }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: xs[2], y: cy, w: cw, h: 0.62, fill: { color: NAVY } });
    s.addText("③ 2部門の位置づけ", { x: xs[2] + 0.25, y: cy, w: cw - 0.4, h: 0.62, fontFace: HF, fontSize: 18, bold: true, color: WHITE, valign: "middle", margin: 0 });
    // mini sub-cards
    s.addShape(pres.shapes.RECTANGLE, { x: xs[2] + 0.25, y: cy + 0.9, w: cw - 0.5, h: 1.55, fill: { color: WHITE }, line: { color: GOLD, width: 1.3 } });
    s.addText("アセマネ部門", { x: xs[2] + 0.42, y: cy + 1.02, w: cw - 0.8, h: 0.35, fontFace: HF, fontSize: 16, bold: true, color: NAVY, margin: 0 });
    s.addText("運用フィー（手数料）の柱", { x: xs[2] + 0.42, y: cy + 1.45, w: cw - 0.8, h: 0.85, fontFace: BF, fontSize: 13, color: INK, margin: 0, valign: "top" });
    s.addShape(pres.shapes.RECTANGLE, { x: xs[2] + 0.25, y: cy + 2.6, w: cw - 0.5, h: 1.55, fill: { color: WHITE }, line: { color: NAVY, width: 1.3 } });
    s.addText("営業部門", { x: xs[2] + 0.42, y: cy + 2.72, w: cw - 0.8, h: 0.35, fontFace: HF, fontSize: 16, bold: true, color: NAVY, margin: 0 });
    s.addText("マーケットメイク＋ファイナンシングの柱", { x: xs[2] + 0.42, y: cy + 3.15, w: cw - 0.8, h: 0.9, fontFace: BF, fontSize: 13, color: INK, margin: 0, valign: "top" });

    pageNum(s, 2);
    s.addNotes("結論サマリー。V字回復・安定収益への戦略シフト・アセマネ/営業の2部門の位置づけを最初に提示。");
  }

  // ============================================================ SLIDE 3 — Company overview (light)
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    pageHeader(s, "COMPANY PROFILE", "会社の輪郭 — 155年の歴史と現体制");

    // Left timeline
    const tlx = 0.95, tly = 2.05;
    s.addText("沿革", { x: 0.6, y: 1.72, w: 4, h: 0.3, fontFace: HF, fontSize: 16, bold: true, color: NAVY, margin: 0 });
    s.addShape(pres.shapes.LINE, { x: tlx, y: tly + 0.1, w: 0, h: 3.7, line: { color: GOLD, width: 2 } });
    const events = [
      ["1869", "創業（ニューヨーク）"],
      ["1999", "NYSE上場"],
      ["2008", "銀行持株会社化"],
      ["2022", "3セグメント体制へ再編"]
    ];
    events.forEach((e, i) => {
      const y = tly + i * 0.95;
      s.addShape(pres.shapes.OVAL, { x: tlx - 0.11, y: y, w: 0.22, h: 0.22, fill: { color: GOLD }, line: { color: WHITE, width: 1.5 } });
      s.addText(e[0], { x: tlx + 0.3, y: y - 0.12, w: 1.3, h: 0.45, fontFace: HF, fontSize: 22, bold: true, color: NAVY, margin: 0, valign: "middle" });
      s.addText(e[1], { x: tlx + 1.65, y: y - 0.12, w: 3.4, h: 0.45, fontFace: BF, fontSize: 13.5, color: INK, margin: 0, valign: "middle" });
    });

    // Right leadership cards
    const rx = 7.0, rw = 5.7;
    s.addText("現経営体制", { x: rx, y: 1.72, w: 4, h: 0.3, fontFace: HF, fontSize: 16, bold: true, color: NAVY, margin: 0 });
    const leaders = [
      ["David Solomon", "会長 兼 CEO"],
      ["John Waldron", "社長 兼 COO"],
      ["Denis Coleman", "CFO"]
    ];
    leaders.forEach((l, i) => {
      const y = 2.05 + i * 1.12;
      s.addShape(pres.shapes.RECTANGLE, { x: rx, y, w: rw, h: 0.98, fill: { color: CARDBG }, line: { color: LINEC, width: 1 }, shadow: makeShadow() });
      s.addShape(pres.shapes.OVAL, { x: rx + 0.22, y: y + 0.22, w: 0.55, h: 0.55, fill: { color: NAVY } });
      s.addImage({ data: ic.ceo, x: rx + 0.3, y: y + 0.3, w: 0.38, h: 0.38 });
      // recolor: navy icon on navy circle is low contrast, use gold icon overlay instead
      s.addText(l[0], { x: rx + 1.0, y: y + 0.16, w: rw - 1.2, h: 0.4, fontFace: HF, fontSize: 19, bold: true, color: NAVY, margin: 0, valign: "middle" });
      s.addText(l[1], { x: rx + 1.0, y: y + 0.54, w: rw - 1.2, h: 0.34, fontFace: BF, fontSize: 13, color: GOLD, bold: true, margin: 0, valign: "middle" });
    });

    // bottom strip
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 6.45, w: 12.1, h: 0.62, fill: { color: NAVY } });
    s.addText([
      { text: "本社  ", options: { color: GOLDL, bold: true } }, { text: "ニューヨーク      ", options: { color: WHITE } },
      { text: "従業員  ", options: { color: GOLDL, bold: true } }, { text: "約 46,500人（2024年末）", options: { color: WHITE } }
    ], { x: 0.9, y: 6.45, w: 11.5, h: 0.62, fontFace: BF, fontSize: 15, valign: "middle", margin: 0 });

    pageNum(s, 3);
    s.addNotes("会社概観。1869年創業の155年の歴史と、Solomon・Waldron・Colemanの現経営体制。本社NY、従業員約46,500人。");
  }
  // fix leadership icon contrast: overlay gold icon
  // (handled by recoloring below in a simpler way — re-add gold ceo icon)

  // ============================================================ SLIDE 4 — 3 segments (light)
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    pageHeader(s, "BUSINESS SEGMENTS", "3つの事業セグメント");

    const cy = 2.05, ch = 4.2, cw = 3.85, gap = 0.28;
    const xs = [0.6, 0.6 + cw + gap, 0.6 + 2 * (cw + gap)];
    const segs = [
      { icon: ic.layer, t: "Global Banking\n& Markets", desc: "投資銀行 ＋ FICC ＋ Equities", rev: "$34.94B", tag: "営業部門はここ", hi: true },
      { icon: ic.coins, t: "Asset & Wealth\nManagement", desc: "運用（GSAM）＋ ウェルス（PWM）", rev: "$16.14B", tag: "アセマネ部門はここ", hi: true },
      { icon: ic.cogs, t: "Platform\nSolutions", desc: "カード提携 等", rev: "約 $1.76B", tag: "縮小・黒字化途上", hi: false }
    ];
    segs.forEach((sg, i) => {
      const x = xs[i];
      const accent = sg.hi ? GOLD : LINEC;
      s.addShape(pres.shapes.RECTANGLE, { x, y: cy, w: cw, h: ch, fill: { color: sg.hi ? WHITE : CARDBG }, line: { color: accent, width: sg.hi ? 2.2 : 1 }, shadow: makeShadow() });
      s.addShape(pres.shapes.RECTANGLE, { x, y: cy, w: cw, h: 0.12, fill: { color: sg.hi ? GOLD : SLATE } });
      s.addShape(pres.shapes.OVAL, { x: x + cw / 2 - 0.5, y: cy + 0.4, w: 1.0, h: 1.0, fill: { color: NAVY } });
      s.addImage({ data: i === 1 ? ic.coins : (i === 0 ? ic.layer : ic.cogs), x: x + cw / 2 - 0.28, y: cy + 0.62, w: 0.56, h: 0.56 });
      s.addText(sg.t, { x: x + 0.2, y: cy + 1.55, w: cw - 0.4, h: 0.85, fontFace: HF, fontSize: 18, bold: true, color: NAVY, align: "center", margin: 0, valign: "top" });
      s.addText(sg.desc, { x: x + 0.25, y: cy + 2.45, w: cw - 0.5, h: 0.55, fontFace: BF, fontSize: 12.5, color: SLATE, align: "center", margin: 0, valign: "top" });
      s.addText(sg.rev, { x: x + 0.2, y: cy + 3.0, w: cw - 0.4, h: 0.65, fontFace: HF, fontSize: 34, bold: true, color: sg.hi ? NAVY : SLATE, align: "center", margin: 0 });
      // tag pill
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + cw / 2 - 1.35, y: cy + 3.65, w: 2.7, h: 0.42, fill: { color: sg.hi ? GOLD : "E3E7EE" }, rectRadius: 0.21 });
      s.addText(sg.tag, { x: x + cw / 2 - 1.35, y: cy + 3.65, w: 2.7, h: 0.42, fontFace: BF, fontSize: 12, bold: true, color: sg.hi ? NAVY : SLATE, align: "center", valign: "middle", margin: 0 });
    });
    s.addText("純収益はFY2024（通期）。本件で深掘りする2部門をゴールドで強調。", { x: 0.6, y: 6.5, w: 12, h: 0.3, fontFace: BF, fontSize: 11.5, italic: true, color: SLATE, margin: 0 });
    pageNum(s, 4);
    s.addNotes("3つの事業セグメント。GBM（営業部門）とAWM（アセマネ部門）を強調。Platformは縮小中。");
  }

  // ============================================================ SLIDE 5 — V字回復 chart (light)
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    pageHeader(s, "FY2024 RESULTS", "全社業績：2024年はV字回復");

    // Comparison column chart 2023 vs 2024 (normalized? use two series)
    s.addChart(pres.charts.BAR, [
      { name: "2023", labels: ["純収益 ($B)", "純利益 ($B)", "EPS ($)"], values: [46.25, 8.52, 22.87] },
      { name: "2024", labels: ["純収益 ($B)", "純利益 ($B)", "EPS ($)"], values: [53.51, 14.28, 40.54] }
    ], {
      x: 0.6, y: 2.0, w: 7.4, h: 4.4, barDir: "col",
      chartColors: [SLATE, GOLD], barGapWidthPct: 60,
      chartArea: { fill: { color: WHITE } },
      catAxisLabelColor: INK, catAxisLabelFontSize: 12, catAxisLabelFontBold: true, catAxisLabelFontFace: BF,
      valAxisLabelColor: SLATE, valAxisHidden: false, valAxisLabelFontSize: 10,
      valGridLine: { color: "EAEDF2", size: 0.5 }, catGridLine: { style: "none" },
      showValue: true, dataLabelPosition: "outEnd", dataLabelColor: NAVY, dataLabelFontSize: 11, dataLabelFontBold: true, dataLabelFontFace: BF,
      showLegend: true, legendPos: "t", legendColor: INK, legendFontSize: 12, legendFontFace: BF,
      valAxisMaxVal: 60, valAxisMinVal: 0
    });

    // Right ratio stats
    const rx = 8.45, rw = 4.25;
    statCard(s, rx, 2.05, rw, 1.55, "7.5% → 12.7%", "全社ROE", "収益性が大幅改善", { accent: GOLD, bigSize: 30 });
    statCard(s, rx, 3.78, rw, 1.55, "74.6% → 63.1%", "効率比率（経費率）", "経費規律で改善", { accent: NAVY, bigSize: 30 });
    s.addShape(pres.shapes.RECTANGLE, { x: rx, y: 5.5, w: rw, h: 0.95, fill: { color: NAVY }, shadow: makeShadow() });
    s.addText("市況回復 ＋ 経費規律で、収益性が改善。", { x: rx + 0.25, y: 5.5, w: rw - 0.45, h: 0.95, fontFace: BF, fontSize: 14, bold: true, color: WHITE, valign: "middle", margin: 0 });

    pageNum(s, 5);
    s.addNotes("全社業績のV字回復。純収益・純利益・EPSが軒並み増加、ROE7.5→12.7%、効率比率も改善。");
  }

  // ============================================================ SLIDE 6 — AWM intro (light)
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    pageHeader(s, "DIVISION 1 — AWM", "【部門①】アセット・マネジメント部門（AWM）とは");

    // Left: role text
    const lx = 0.6, lw = 5.6;
    s.addShape(pres.shapes.RECTANGLE, { x: lx, y: 2.0, w: lw, h: 2.05, fill: { color: CARDBG }, line: { color: LINEC, width: 1 } });
    s.addShape(pres.shapes.RECTANGLE, { x: lx, y: 2.0, w: 0.09, h: 2.05, fill: { color: GOLD } });
    s.addText("役割", { x: lx + 0.28, y: 2.12, w: lw - 0.5, h: 0.35, fontFace: HF, fontSize: 16, bold: true, color: NAVY, margin: 0 });
    s.addText("機関投資家・富裕層の資産を運用し、フィー（手数料）を得る。", { x: lx + 0.28, y: 2.5, w: lw - 0.55, h: 0.7, fontFace: BF, fontSize: 14, color: INK, margin: 0, valign: "top" });
    s.addText([
      { text: "GSAM ＝ 運用", options: { breakLine: true, bullet: true } },
      { text: "PWM ＝ 超富裕層向けウェルス", options: { bullet: true } }
    ], { x: lx + 0.28, y: 3.2, w: lw - 0.55, h: 0.8, fontFace: BF, fontSize: 13.5, color: INK, paraSpaceAfter: 5, margin: 0 });

    // Big AUS stat
    s.addShape(pres.shapes.RECTANGLE, { x: lx, y: 4.25, w: lw, h: 2.15, fill: { color: NAVY }, shadow: makeShadow() });
    s.addText("運用資産（AUS）", { x: lx + 0.3, y: 4.4, w: lw - 0.5, h: 0.4, fontFace: BF, fontSize: 14, bold: true, color: GOLDL, margin: 0 });
    s.addText("$3.14兆", { x: lx + 0.25, y: 4.7, w: lw - 0.5, h: 1.1, fontFace: HF, fontSize: 64, bold: true, color: WHITE, margin: 0 });
    s.addText("2024年末・過去最高", { x: lx + 0.3, y: 5.85, w: lw - 0.5, h: 0.4, fontFace: BF, fontSize: 13, color: "AEBAD0", margin: 0 });

    // Right: AUS trend mini bar chart
    s.addText("AUS推移（兆ドル）", { x: 6.6, y: 1.85, w: 5, h: 0.35, fontFace: HF, fontSize: 15, bold: true, color: NAVY, margin: 0 });
    s.addChart(pres.charts.BAR, [{
      name: "AUS", labels: ["2022", "2023", "2024"], values: [2.55, 2.81, 3.14]
    }], {
      x: 6.5, y: 2.2, w: 6.2, h: 3.4, barDir: "col",
      chartColors: [GOLD], barGapWidthPct: 55,
      chartArea: { fill: { color: WHITE } },
      catAxisLabelColor: INK, catAxisLabelFontSize: 13, catAxisLabelFontBold: true, catAxisLabelFontFace: BF,
      valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
      showValue: true, dataLabelPosition: "outEnd", dataLabelColor: NAVY, dataLabelFontSize: 16, dataLabelFontBold: true, dataLabelFontFace: HF,
      showLegend: false, valAxisMaxVal: 3.6, valAxisMinVal: 0
    });
    s.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 5.85, w: 6.2, h: 0.62, fill: { color: CARDBG }, line: { color: GOLD, width: 1.3 } });
    s.addText("28四半期連続で長期フィーベースの純流入", { x: 6.7, y: 5.85, w: 6.0, h: 0.62, fontFace: BF, fontSize: 14, bold: true, color: NAVY, valign: "middle", margin: 0 });

    pageNum(s, 6);
    s.addNotes("AWM導入。運用フィーで稼ぐ部門。AUSは$3.14兆で過去最高、28四半期連続で純流入。");
  }

  // ============================================================ SLIDE 7 — AWM strategy (light) ★
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    pageHeader(s, "DIVISION 1 — STRATEGY", "AWMの核心：自己投資 → 運用フィーへ");

    // Before / After
    const by = 2.0, bh = 1.95, bw = 5.0;
    // before card
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: by, w: bw, h: bh, fill: { color: CARDBG }, line: { color: LINEC, width: 1 }, shadow: makeShadow() });
    s.addText("自己投資（プリンシパル投資）残高", { x: 0.8, y: by + 0.18, w: bw - 0.4, h: 0.4, fontFace: BF, fontSize: 13.5, bold: true, color: SLATE, margin: 0 });
    s.addText([
      { text: "$64B ", options: { fontSize: 44, color: SLATE, bold: true } },
      { text: " → ", options: { fontSize: 30, color: GOLD, bold: true } },
      { text: " $6B", options: { fontSize: 52, color: NAVY, bold: true } }
    ], { x: 0.8, y: by + 0.6, w: bw - 0.4, h: 0.95, fontFace: HF, align: "left", valign: "middle", margin: 0 });
    s.addText("9割超を圧縮 ＝ 収益のブレを縮小", { x: 0.8, y: by + 1.5, w: bw - 0.4, h: 0.35, fontFace: BF, fontSize: 13, italic: true, color: GOLD, bold: true, margin: 0 });

    // arrow between
    s.addImage({ data: ic.arrow, x: 5.78, y: by + 0.62, w: 0.7, h: 0.7 });

    // after card (fees)
    s.addShape(pres.shapes.RECTANGLE, { x: 6.75, y: by, w: 5.95, h: bh, fill: { color: NAVY }, shadow: makeShadow() });
    s.addText("代わりに運用報酬を拡大", { x: 6.95, y: by + 0.18, w: 5.5, h: 0.4, fontFace: BF, fontSize: 13.5, bold: true, color: GOLDL, margin: 0 });
    s.addText([
      { text: "Management & other fees ", options: { fontSize: 16, color: WHITE, bold: false } },
      { text: "$10B超", options: { fontSize: 46, color: WHITE, bold: true } }
    ], { x: 6.95, y: by + 0.55, w: 5.5, h: 1.0, fontFace: HF, valign: "middle", margin: 0 });
    s.addText("（2024年）安定的なフィー収益が収益の柱に", { x: 6.95, y: by + 1.5, w: 5.5, h: 0.35, fontFace: BF, fontSize: 12.5, color: "AEBAD0", margin: 0 });

    // result: margin chart
    s.addText("結果：税前マージンが激変", { x: 0.6, y: 4.2, w: 6, h: 0.35, fontFace: HF, fontSize: 16, bold: true, color: NAVY, margin: 0 });
    s.addChart(pres.charts.BAR, [{
      name: "税前マージン", labels: ["2023（約10%）", "2024（約28%）"], values: [10, 28]
    }], {
      x: 0.55, y: 4.55, w: 6.1, h: 2.45, barDir: "bar",
      chartColors: [GOLD], barGapWidthPct: 50,
      chartArea: { fill: { color: WHITE } },
      catAxisLabelColor: INK, catAxisLabelFontSize: 13, catAxisLabelFontBold: true, catAxisLabelFontFace: BF,
      valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
      showValue: true, dataLabelPosition: "outEnd", dataLabelColor: NAVY, dataLabelFontSize: 15, dataLabelFontBold: true, dataLabelFontFace: HF,
      showLegend: false, valAxisMaxVal: 34
    });

    // right result stats
    statCard(s, 7.0, 4.4, 5.7, 1.05, "約$1.4B → 約$4.5B", "税前利益（AWM）", null, { accent: GOLD, bigSize: 26 });
    s.addShape(pres.shapes.RECTANGLE, { x: 7.0, y: 5.6, w: 5.7, h: 1.4, fill: { color: CARDBG }, line: { color: GOLD, width: 1.5 } });
    s.addText("「規模」より「収益の質」", { x: 7.2, y: 5.72, w: 5.3, h: 0.45, fontFace: HF, fontSize: 20, bold: true, color: NAVY, margin: 0 });
    s.addText("中期目標 mid-20s% マージンを達成。", { x: 7.2, y: 6.25, w: 5.3, h: 0.6, fontFace: BF, fontSize: 14, color: INK, margin: 0, valign: "top" });

    pageNum(s, 7);
    s.addNotes("AWM最重要。自己投資を$64B→$6Bに圧縮し運用フィーを拡大。税前マージン約10%→約28%へ激変。");
  }

  // ============================================================ SLIDE 8 — AWM differentiation + competitors (light) ★
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    pageHeader(s, "DIVISION 1 — EDGE", "AWMの勝ち筋：規模ではなく高マージン領域へ");

    // Left two pillars
    const lx = 0.6, lw = 5.55;
    s.addShape(pres.shapes.RECTANGLE, { x: lx, y: 2.0, w: lw, h: 2.1, fill: { color: CARDBG }, line: { color: LINEC, width: 1 }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: lx, y: 2.0, w: 0.09, h: 2.1, fill: { color: GOLD } });
    s.addImage({ data: ic.gem, x: lx + 0.25, y: 2.18, w: 0.5, h: 0.5 });
    s.addText("① オルタナティブ／プライベート市場", { x: lx + 0.85, y: 2.18, w: lw - 1.0, h: 0.5, fontFace: HF, fontSize: 15, bold: true, color: NAVY, valign: "middle", margin: 0 });
    s.addText([
      { text: "オルタナAUS $328B", options: { breakLine: true, bullet: true } },
      { text: "資金調達目標 $225B を1年前倒し達成", options: { breakLine: true, bullet: true } },
      { text: "「世界トップ5のオルタナ運用」", options: { bullet: true } }
    ], { x: lx + 0.3, y: 2.78, w: lw - 0.55, h: 1.25, fontFace: BF, fontSize: 13, color: INK, paraSpaceAfter: 5, margin: 0 });

    s.addShape(pres.shapes.RECTANGLE, { x: lx, y: 4.25, w: lw, h: 2.15, fill: { color: CARDBG }, line: { color: LINEC, width: 1 }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: lx, y: 4.25, w: 0.09, h: 2.15, fill: { color: NAVY } });
    s.addImage({ data: ic.target, x: lx + 0.25, y: 4.43, w: 0.5, h: 0.5 });
    s.addText("② UHNW（超富裕層）特化", { x: lx + 0.85, y: 4.43, w: lw - 1.0, h: 0.5, fontFace: HF, fontSize: 15, bold: true, color: NAVY, valign: "middle", margin: 0 });
    s.addText([
      { text: "低マージンのマスアフルエント（PFM）を売却", options: { breakLine: true, bullet: true } },
      { text: "PWM ＋ Ayco に集中", options: { breakLine: true, bullet: true } },
      { text: "「規模で挑まず、高マージンで勝つ」", options: { bullet: true } }
    ], { x: lx + 0.3, y: 5.0, w: lw - 0.55, h: 1.3, fontFace: BF, fontSize: 13, color: INK, paraSpaceAfter: 5, margin: 0 });

    // Right: competitor AUM bar (in 兆ドル)
    s.addText("運用規模の比較（兆ドル）", { x: 6.55, y: 1.85, w: 6, h: 0.35, fontFace: HF, fontSize: 15, bold: true, color: NAVY, margin: 0 });
    s.addChart(pres.charts.BAR, [{
      name: "AUM",
      labels: ["BlackRock", "JPMorgan AM", "GS AWM", "Morgan Stanley IM"],
      values: [11.6, 3.3, 3.14, 1.7]
    }], {
      x: 6.45, y: 2.2, w: 6.25, h: 3.5, barDir: "bar",
      chartColors: [NAVY], barGapWidthPct: 45,
      chartArea: { fill: { color: WHITE } },
      catAxisLabelColor: INK, catAxisLabelFontSize: 12, catAxisLabelFontBold: true, catAxisLabelFontFace: BF,
      valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
      showValue: true, dataLabelPosition: "outEnd", dataLabelColor: NAVY, dataLabelFontSize: 13, dataLabelFontBold: true, dataLabelFontFace: HF,
      showLegend: false, valAxisMaxVal: 13
    });
    s.addShape(pres.shapes.RECTANGLE, { x: 6.45, y: 5.95, w: 6.25, h: 1.05, fill: { color: NAVY }, shadow: makeShadow() });
    s.addText([
      { text: "BlackRockは規模（パッシブ）の王者。", options: { breakLine: true, color: WHITE } },
      { text: "GSは規模で挑まず、高マージンで勝つ。", options: { color: GOLDL, bold: true } }
    ], { x: 6.65, y: 5.95, w: 5.95, h: 1.05, fontFace: BF, fontSize: 13.5, valign: "middle", margin: 0 });

    pageNum(s, 8);
    s.addNotes("AWM最重要。オルタナとUHNW特化が差別化の2本柱。規模ではBlackRockに劣るが高マージンで勝負。");
  }

  // ============================================================ SLIDE 9 — Sales & Trading intro (light)
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    pageHeader(s, "DIVISION 2 — S&T", "【部門②】営業部門 ＝ Sales & Trading（GBM）");

    // top positioning band
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 1.95, w: 12.1, h: 0.95, fill: { color: CARDBG }, line: { color: LINEC, width: 1 } });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 1.95, w: 0.09, h: 0.95, fill: { color: GOLD } });
    s.addText([
      { text: "位置づけ： ", options: { bold: true, color: NAVY } },
      { text: "Global Banking & Markets の中核。日本のGS証券では「証券部門」。", options: { color: INK } }
    ], { x: 0.9, y: 1.95, w: 11.6, h: 0.95, fontFace: BF, fontSize: 15, valign: "middle", margin: 0 });

    // two group cards
    const gy = 3.15, gh = 1.55, gw = 5.95;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: gy, w: gw, h: gh, fill: { color: WHITE }, line: { color: NAVY, width: 1.6 }, shadow: makeShadow() });
    s.addText("Equities（株式）グループ", { x: 0.85, y: gy + 0.18, w: gw - 0.5, h: 0.4, fontFace: HF, fontSize: 17, bold: true, color: NAVY, margin: 0 });
    s.addText("株式・派生のマーケットメイクと顧客フロー", { x: 0.85, y: gy + 0.62, w: gw - 0.5, h: 0.8, fontFace: BF, fontSize: 13, color: INK, margin: 0, valign: "top" });

    s.addShape(pres.shapes.RECTANGLE, { x: 6.75, y: gy, w: gw, h: gh, fill: { color: WHITE }, line: { color: GOLD, width: 1.6 }, shadow: makeShadow() });
    s.addText("FICC（債券・為替・コモディティ）グループ", { x: 7.0, y: gy + 0.18, w: gw - 0.5, h: 0.4, fontFace: HF, fontSize: 16, bold: true, color: NAVY, margin: 0 });
    s.addText("金利・クレジット・通貨・商品のトレーディング", { x: 7.0, y: gy + 0.62, w: gw - 0.5, h: 0.8, fontFace: BF, fontSize: 13, color: INK, margin: 0, valign: "top" });

    // job roles pills
    s.addText("職種", { x: 0.6, y: 4.85, w: 3, h: 0.3, fontFace: HF, fontSize: 14, bold: true, color: NAVY, margin: 0 });
    const roles = ["Sales（機関投資家カバレッジ）", "Trading（マーケットメイク）", "Strats（クオンツ）"];
    roles.forEach((r, i) => {
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6 + i * 4.05, y: 5.2, w: 3.8, h: 0.55, fill: { color: NAVY }, rectRadius: 0.1 });
      s.addText(r, { x: 0.6 + i * 4.05, y: 5.2, w: 3.8, h: 0.55, fontFace: BF, fontSize: 12.5, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
    });

    // FY2024 big stats
    statCard(s, 0.6, 6.05, 5.95, 1.05, "$13.2B（+9%）", "FICC（FY2024）", null, { accent: GOLD, bigSize: 28 });
    statCard(s, 6.75, 6.05, 5.95, 1.05, "$13.43B（+16%）", "Equities（FY2024・過去最高）", null, { accent: NAVY, bigSize: 28 });

    pageNum(s, 9);
    s.addNotes("営業部門の導入。GBMの中核でEquitiesとFICCの2グループ。職種はSales/Trading/Strats。FY2024は両者とも好調。");
  }

  // ============================================================ SLIDE 10 — two-tier structure (light) ★
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    pageHeader(s, "DIVISION 2 — STRUCTURE", "営業の収益は「2階建て」");

    // Building diagram: floor 2 (top) financing, floor 1 (bottom) market making
    const bx = 0.6, bw = 7.4;
    // Floor 2
    s.addShape(pres.shapes.RECTANGLE, { x: bx, y: 2.0, w: bw, h: 1.85, fill: { color: NAVY }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: bx, y: 2.0, w: 1.3, h: 1.85, fill: { color: GOLD } });
    s.addText("2階", { x: bx, y: 2.0, w: 1.3, h: 1.85, fontFace: HF, fontSize: 26, bold: true, color: NAVY, align: "center", valign: "middle", margin: 0 });
    s.addText("ファイナンシング", { x: bx + 1.5, y: 2.15, w: bw - 1.7, h: 0.45, fontFace: HF, fontSize: 19, bold: true, color: WHITE, margin: 0 });
    s.addText("プライム・ブローカレッジ／レポ／担保貸付など", { x: bx + 1.5, y: 2.62, w: bw - 1.7, h: 0.4, fontFace: BF, fontSize: 13, color: "CBD5E8", margin: 0 });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: bx + 1.5, y: 3.12, w: 2.6, h: 0.5, fill: { color: GOLDL }, rectRadius: 0.1 });
    s.addText("反復的・安定収益", { x: bx + 1.5, y: 3.12, w: 2.6, h: 0.5, fontFace: BF, fontSize: 13, bold: true, color: NAVY, align: "center", valign: "middle", margin: 0 });

    // Floor 1
    s.addShape(pres.shapes.RECTANGLE, { x: bx, y: 3.95, w: bw, h: 1.85, fill: { color: NAVY3 }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: bx, y: 3.95, w: 1.3, h: 1.85, fill: { color: "8A97AD" } });
    s.addText("1階", { x: bx, y: 3.95, w: 1.3, h: 1.85, fontFace: HF, fontSize: 26, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
    s.addText("マーケットメイク（仲介）", { x: bx + 1.5, y: 4.1, w: bw - 1.7, h: 0.45, fontFace: HF, fontSize: 19, bold: true, color: WHITE, margin: 0 });
    s.addText("両建ての値段を提示し流動性を供給、顧客フローを仲介", { x: bx + 1.5, y: 4.57, w: bw - 1.7, h: 0.4, fontFace: BF, fontSize: 13, color: "DDE3EF", margin: 0 });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: bx + 1.5, y: 5.07, w: 2.9, h: 0.5, fill: { color: "E3E7EE" }, rectRadius: 0.1 });
    s.addText("市況・ボラ次第で変動", { x: bx + 1.5, y: 5.07, w: 2.9, h: 0.5, fontFace: BF, fontSize: 13, bold: true, color: NAVY, align: "center", valign: "middle", margin: 0 });

    // Right: financing big stat + chart bar
    statCard(s, 8.3, 2.0, 4.4, 1.85, "$9.1B", "ファイナンシング収益（2024・過去最高）", "2019年比 CAGR 15%", { accent: GOLD, bigSize: 56 });

    s.addText("ファイナンシング収益の伸び", { x: 8.3, y: 4.05, w: 4.4, h: 0.3, fontFace: HF, fontSize: 13, bold: true, color: NAVY, margin: 0 });
    s.addChart(pres.charts.BAR, [{
      name: "Financing", labels: ["2019", "2024"], values: [4.5, 9.1]
    }], {
      x: 8.2, y: 4.35, w: 4.55, h: 1.45, barDir: "bar",
      chartColors: [GOLD], barGapWidthPct: 50,
      chartArea: { fill: { color: WHITE } },
      catAxisLabelColor: INK, catAxisLabelFontSize: 12, catAxisLabelFontBold: true, catAxisLabelFontFace: BF,
      valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
      showValue: true, dataLabelPosition: "outEnd", dataLabelColor: NAVY, dataLabelFontSize: 13, dataLabelFontBold: true, dataLabelFontFace: HF,
      showLegend: false, valAxisMaxVal: 10.5
    });
    s.addText("※2019年は概算（CAGR15%からの逆算イメージ）", { x: 8.3, y: 5.78, w: 4.4, h: 0.25, fontFace: BF, fontSize: 8.5, italic: true, color: SLATE, margin: 0 });

    // bottom message
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 6.2, w: 12.1, h: 0.85, fill: { color: CARDBG }, line: { color: GOLD, width: 1.5 } });
    s.addText([
      { text: "メッセージ： ", options: { bold: true, color: GOLD } },
      { text: "AWMの「運用フィー」と同じく、営業も“安定収益”を厚くしている ＝ 全社で一貫。", options: { color: NAVY, bold: true } }
    ], { x: 0.85, y: 6.2, w: 11.6, h: 0.85, fontFace: BF, fontSize: 14.5, valign: "middle", margin: 0 });

    pageNum(s, 10);
    s.addNotes("営業最重要。1階マーケットメイク（変動）と2階ファイナンシング（安定）の2階建て。安定収益$9.1Bが過去最高。");
  }

  // ============================================================ SLIDE 11 — industry position (light)
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    pageHeader(s, "MARKET POSITION", "業界での立ち位置：助言の絶対王者");

    // Big hero stat left
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 2.0, w: 5.7, h: 4.5, fill: { color: NAVY }, shadow: makeShadow() });
    s.addImage({ data: ic.trophy, x: 0.95, y: 2.35, w: 0.9, h: 0.9 });
    s.addText("21年連続", { x: 0.9, y: 3.35, w: 5.1, h: 1.2, fontFace: HF, fontSize: 70, bold: true, color: GOLDL, margin: 0 });
    s.addText("M&Aアドバイザリー 世界No.1", { x: 0.95, y: 4.55, w: 5.0, h: 0.5, fontFace: HF, fontSize: 20, bold: true, color: WHITE, margin: 0 });
    s.addText("助言ビジネスで圧倒的なトップポジションを維持。", { x: 0.95, y: 5.15, w: 5.0, h: 0.8, fontFace: BF, fontSize: 13.5, color: "AEBAD0", margin: 0, valign: "top" });

    // Right stacked stats
    const rx = 6.65, rw = 6.05;
    statCard(s, rx, 2.0, rw, 1.35, "約$1.48兆 / シェア約32%", "2024 グローバルM&A 取扱額（首位）", null, { accent: GOLD, bigSize: 27 });
    statCard(s, rx, 3.5, rw, 1.35, "No.1", "株式引受ボリューム（2023）", null, { accent: NAVY, bigSize: 40 });
    // recent waves card
    s.addShape(pres.shapes.RECTANGLE, { x: rx, y: 5.0, w: rw, h: 1.5, fill: { color: CARDBG }, line: { color: LINEC, width: 1 }, shadow: makeShadow() });
    s.addText("近年の波", { x: rx + 0.25, y: 5.12, w: rw - 0.5, h: 0.35, fontFace: HF, fontSize: 14, bold: true, color: NAVY, margin: 0 });
    s.addText([
      { text: "2022 好調（高ボラ）", options: { color: SLATE } },
      { text: "  →  ", options: { color: GOLD, bold: true } },
      { text: "2023 減速", options: { color: SLATE } },
      { text: "  →  ", options: { color: GOLD, bold: true } },
      { text: "2024 V字（Equities過去最高）", options: { color: NAVY, bold: true } }
    ], { x: rx + 0.25, y: 5.5, w: rw - 0.5, h: 0.9, fontFace: BF, fontSize: 15, valign: "middle", margin: 0 });

    pageNum(s, 11);
    s.addNotes("業界ポジション。M&A助言で21年連続世界No.1、2024年シェア約32%。近年は2022好調→2023減速→2024V字。");
  }

  // ============================================================ SLIDE 12 — backbone strategy + consumer exit (light)
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    pageHeader(s, "ONE STRATEGY", "1本の背骨：durable revenues と「規律ある撤退」", { size: 26 });

    // Left: common strategy diagram (変動 -> 安定)
    const lx = 0.6, lw = 6.0;
    s.addText("両部門に共通の戦略", { x: lx, y: 1.85, w: lw, h: 0.3, fontFace: HF, fontSize: 15, bold: true, color: NAVY, margin: 0 });
    // variable box
    s.addShape(pres.shapes.RECTANGLE, { x: lx, y: 2.25, w: 2.7, h: 1.6, fill: { color: "E3E7EE" }, line: { color: SLATE, width: 1 } });
    s.addText("変動", { x: lx, y: 2.35, w: 2.7, h: 0.4, fontFace: HF, fontSize: 16, bold: true, color: SLATE, align: "center", margin: 0 });
    s.addText([
      { text: "自己投資", options: { breakLine: true } },
      { text: "マーケットメイク", options: {} }
    ], { x: lx, y: 2.8, w: 2.7, h: 0.95, fontFace: BF, fontSize: 13, color: INK, align: "center", valign: "middle", margin: 0 });
    s.addImage({ data: ic.arrow, x: lx + 2.85, y: 2.85, w: 0.6, h: 0.6 });
    // stable box
    s.addShape(pres.shapes.RECTANGLE, { x: lx + 3.5, y: 2.25, w: 2.5, h: 1.6, fill: { color: NAVY } });
    s.addText("安定", { x: lx + 3.5, y: 2.35, w: 2.5, h: 0.4, fontFace: HF, fontSize: 16, bold: true, color: GOLDL, align: "center", margin: 0 });
    s.addText([
      { text: "運用フィー", options: { breakLine: true } },
      { text: "ファイナンシング", options: {} }
    ], { x: lx + 3.5, y: 2.8, w: 2.5, h: 0.95, fontFace: BF, fontSize: 13, color: WHITE, align: "center", valign: "middle", margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: lx, y: 4.1, w: lw, h: 0.85, fill: { color: CARDBG }, line: { color: GOLD, width: 1.3 } });
    s.addText("durable revenues（安定収益）を厚くする ＝ 全社一貫", { x: lx + 0.2, y: 4.1, w: lw - 0.4, h: 0.85, fontFace: BF, fontSize: 13.5, bold: true, color: NAVY, valign: "middle", margin: 0 });

    // Right: consumer exit
    const rx = 6.9, rw = 5.8;
    s.addText("消費者事業からの撤退", { x: rx, y: 1.85, w: rw, h: 0.3, fontFace: HF, fontSize: 15, bold: true, color: NAVY, margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: rx, y: 2.25, w: rw, h: 1.05, fill: { color: NAVY }, shadow: makeShadow() });
    s.addText([
      { text: "$6B超", options: { fontSize: 38, bold: true, color: WHITE } },
      { text: "  の消費者貸付損失（2020〜）", options: { fontSize: 14, color: "CBD5E8" } }
    ], { x: rx + 0.25, y: 2.25, w: rw - 0.4, h: 1.05, fontFace: HF, valign: "middle", margin: 0 });
    s.addText("Marcus / Apple Card / GreenSky", { x: rx + 0.27, y: 3.0, w: rw - 0.5, h: 0.28, fontFace: BF, fontSize: 11, color: GOLDL, margin: 0 });

    s.addShape(pres.shapes.RECTANGLE, { x: rx, y: 3.45, w: rw, h: 1.5, fill: { color: CARDBG }, line: { color: LINEC, width: 1 } });
    s.addText([
      { text: "GreenSky：$1.73Bで取得 → 約$500Mで売却", options: { breakLine: true, bullet: true } },
      { text: "Apple Card は JPMorgan へ移管", options: { bullet: true } }
    ], { x: rx + 0.25, y: 3.6, w: rw - 0.45, h: 1.2, fontFace: BF, fontSize: 13.5, color: INK, paraSpaceAfter: 8, margin: 0, valign: "top" });

    // bottom full message
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 5.35, w: 12.1, h: 1.5, fill: { color: NAVY }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 5.35, w: 0.12, h: 1.5, fill: { color: GOLD } });
    s.addText("メッセージ", { x: 0.9, y: 5.5, w: 4, h: 0.35, fontFace: BF, fontSize: 12, bold: true, color: GOLDL, charSpacing: 2, margin: 0 });
    s.addText("失敗を認め、得意領域（IB・Markets・オルタナ・UHNW）へ回帰。", { x: 0.9, y: 5.85, w: 11.6, h: 0.85, fontFace: HF, fontSize: 22, bold: true, color: WHITE, valign: "middle", margin: 0 });

    pageNum(s, 12);
    s.addNotes("全社を貫く戦略。変動→安定への転換が両部門共通の背骨。消費者事業は損失$6B超で撤退し得意領域へ回帰。");
  }

  // ============================================================ SLIDE 13 — risks (light)
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    pageHeader(s, "KEY RISKS", "リスク：強さの裏側");

    const risks = [
      { icon: ic.wave, t: "景気循環性", d: "IB・トレーディングは市況依存。2023の急減がそれを示す。" },
      { icon: ic.scale, t: "規制資本", d: "バーゼルⅢ最終化（緩和方向だが不確実性が残る）。" },
      { icon: ic.gavel, t: "訴訟・レピュテーション", d: "1MDB事件で約$2.9Bの制裁金（2020年）。" },
      { icon: ic.cogs, t: "戦略実行", d: "消費者撤退コスト、Platform黒字化の遅れ。" }
    ];
    const cw = 5.95, ch = 2.0, gx = 0.6, gapx = 0.28, gapy = 0.3, gy = 2.05;
    risks.forEach((r, i) => {
      const col = i % 2, row = Math.floor(i / 2);
      const x = gx + col * (cw + gapx), y = gy + row * (ch + gapy);
      s.addShape(pres.shapes.RECTANGLE, { x, y, w: cw, h: ch, fill: { color: CARDBG }, line: { color: LINEC, width: 1 }, shadow: makeShadow() });
      s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.09, h: ch, fill: { color: GOLD } });
      s.addShape(pres.shapes.OVAL, { x: x + 0.3, y: y + 0.32, w: 0.85, h: 0.85, fill: { color: NAVY } });
      s.addImage({ data: r.icon, x: x + 0.49, y: y + 0.51, w: 0.47, h: 0.47 });
      s.addText(r.t, { x: x + 1.35, y: y + 0.28, w: cw - 1.6, h: 0.5, fontFace: HF, fontSize: 19, bold: true, color: NAVY, valign: "middle", margin: 0 });
      s.addText(r.d, { x: x + 1.35, y: y + 0.85, w: cw - 1.6, h: 0.95, fontFace: BF, fontSize: 13.5, color: INK, valign: "top", margin: 0 });
    });
    pageNum(s, 13);
    s.addNotes("主要リスク4点。景気循環性、規制資本、1MDB等の訴訟、戦略実行（消費者撤退とPlatform黒字化遅れ）。");
  }

  // ============================================================ SLIDE 14 — Japan & recruiting (light)
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    pageHeader(s, "JAPAN & CAREERS", "日本拠点と就活の視点");

    // Left: Japan
    const lx = 0.6, lw = 5.75;
    s.addShape(pres.shapes.RECTANGLE, { x: lx, y: 1.95, w: lw, h: 4.95, fill: { color: CARDBG }, line: { color: LINEC, width: 1 }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: lx, y: 1.95, w: lw, h: 0.6, fill: { color: NAVY } });
    s.addImage({ data: ic.globe, x: lx + 0.2, y: 2.05, w: 0.4, h: 0.4 });
    s.addText("Goldman Sachs Japan", { x: lx + 0.7, y: 1.95, w: lw - 0.9, h: 0.6, fontFace: HF, fontSize: 17, bold: true, color: WHITE, valign: "middle", margin: 0 });
    s.addText([
      { text: "東京拠点 1974年〜、六本木ヒルズ", options: { breakLine: true, bullet: true } },
      { text: "GS証券 ＋ GSアセット・マネジメント", options: { breakLine: true, bullet: true } },
      { text: "部門：証券（営業）／アセマネ／IBD／", options: { breakLine: true, bullet: true } },
      { text: "投資調査／エンジニアリング", options: { indentLevel: 1 } }
    ], { x: lx + 0.3, y: 2.8, w: lw - 0.55, h: 3.9, fontFace: BF, fontSize: 14.5, color: INK, paraSpaceAfter: 11, margin: 0, valign: "top" });

    // Right: talent & selection
    const rx = 6.6, rw = 6.1;
    s.addShape(pres.shapes.RECTANGLE, { x: rx, y: 1.95, w: rw, h: 4.95, fill: { color: WHITE }, line: { color: GOLD, width: 1.6 }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: rx, y: 1.95, w: rw, h: 0.6, fill: { color: GOLD } });
    s.addImage({ data: ic.brief, x: rx + 0.2, y: 2.05, w: 0.4, h: 0.4 });
    s.addText("求める人材・選考", { x: rx + 0.7, y: 1.95, w: rw - 0.9, h: 0.6, fontFace: HF, fontSize: 17, bold: true, color: NAVY, valign: "middle", margin: 0 });
    s.addText([
      { text: "資質：高い知性・行動力・倫理観（integrity）・チームワーク／日英バイリンガル必須", options: { breakLine: true, bullet: true } },
      { text: "選考：ES → Webテスト → GD/面接 → 最終（部門別・併願可）", options: { breakLine: true, bullet: true } },
      { text: "キャリア：Analyst → Associate → VP → MD。Exit：HF/PE/事業会社財務", options: { breakLine: true, bullet: true } },
      { text: "文化：14のビジネス原則（第1条「顧客の利益を常に最優先」）", options: { bullet: true } }
    ], { x: rx + 0.3, y: 2.78, w: rw - 0.55, h: 4.0, fontFace: BF, fontSize: 14, color: INK, paraSpaceAfter: 13, margin: 0, valign: "top" });

    pageNum(s, 14);
    s.addNotes("日本拠点と就活。東京は1974年から。求める人材は知性・行動力・倫理観・バイリンガル。14のビジネス原則も重要。");
  }

  // ============================================================ SLIDE 15 — takeaways (dark)
  {
    const s = pres.addSlide();
    s.background = { color: NAVY };
    s.addText("CONCLUSION", { x: 0.6, y: 0.5, w: 11, h: 0.3, fontFace: BF, fontSize: 12.5, bold: true, color: GOLD, charSpacing: 2, margin: 0 });
    s.addText("まとめ：面接で効く5つの視点", { x: 0.6, y: 0.82, w: 12, h: 0.8, fontFace: HF, fontSize: 32, bold: true, color: WHITE, margin: 0 });

    const points = [
      ["1", "AWMと営業は同じ戦略の両輪", "変動 → 安定へ"],
      ["2", "AWMはマージン10%→28%", "“収益の質”が激変"],
      ["3", "規模より収益性", "BlackRockに規模で挑まない"],
      ["4", "規律ある撤退", "経営の自己規律"],
      ["5", "マクロ感応度", "ROE 7.5%→12.7% のV字"]
    ];
    const sy = 2.0, sh = 0.92, gap = 0.12, sw = 12.1;
    points.forEach((p, i) => {
      const y = sy + i * (sh + gap);
      s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y, w: sw, h: sh, fill: { color: NAVY2 }, line: { color: NAVY3, width: 1 } });
      s.addShape(pres.shapes.OVAL, { x: 0.85, y: y + (sh - 0.62) / 2, w: 0.62, h: 0.62, fill: { color: GOLD } });
      s.addText(p[0], { x: 0.85, y: y + (sh - 0.62) / 2, w: 0.62, h: 0.62, fontFace: HF, fontSize: 26, bold: true, color: NAVY, align: "center", valign: "middle", margin: 0 });
      s.addText(p[1], { x: 1.75, y, w: 6.6, h: sh, fontFace: HF, fontSize: 20, bold: true, color: WHITE, valign: "middle", margin: 0 });
      s.addShape(pres.shapes.RECTANGLE, { x: 8.4, y: y + 0.22, w: 0.03, h: sh - 0.44, fill: { color: GOLD } });
      s.addText(p[2], { x: 8.65, y, w: 3.9, h: sh, fontFace: BF, fontSize: 15, color: GOLDL, valign: "middle", margin: 0 });
    });
    s.addNotes("まとめ。面接で効く5視点。両輪戦略・マージン激変・規模より収益性・規律ある撤退・マクロ感応度。");
  }

  // ============================================================ SLIDE 16 — sources (dark)
  {
    const s = pres.addSlide();
    s.background = { color: NAVY };
    s.addText("APPENDIX", { x: 0.6, y: 0.5, w: 11, h: 0.3, fontFace: BF, fontSize: 12.5, bold: true, color: GOLD, charSpacing: 2, margin: 0 });
    s.addText("出典と注記", { x: 0.6, y: 0.82, w: 12, h: 0.8, fontFace: HF, fontSize: 32, bold: true, color: WHITE, margin: 0 });

    const blocks = [
      ["一次情報", "GS FY2024/FY2023 10-K・決算リリース・Investor Day(2020/2023)・FICC and Equities事業説明"],
      ["報道", "Reuters, CNBC, Bloomberg, Fortune, Banking Dive, wealthbriefing, privatebankerinternational, PwC, DOJ(1MDB)"],
      ["日本", "goldmansachs.com/japan, am.gs.com, gBizINFO"]
    ];
    let y = 2.0;
    blocks.forEach((b) => {
      s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y, w: 12.1, h: 1.05, fill: { color: NAVY2 }, line: { color: NAVY3, width: 1 } });
      s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y, w: 0.1, h: 1.05, fill: { color: GOLD } });
      s.addText(b[0], { x: 0.85, y: y + 0.15, w: 2.4, h: 0.4, fontFace: HF, fontSize: 17, bold: true, color: GOLDL, margin: 0 });
      s.addText(b[1], { x: 0.85, y: y + 0.52, w: 11.6, h: 0.5, fontFace: BF, fontSize: 13, color: "DDE3EF", margin: 0, valign: "top" });
      y += 1.2;
    });
    // note
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 5.65, w: 12.1, h: 1.25, fill: { color: "07142F" }, line: { color: GOLD, width: 1 } });
    s.addText("注記", { x: 0.85, y: 5.78, w: 3, h: 0.35, fontFace: HF, fontSize: 15, bold: true, color: GOLD, margin: 0 });
    s.addText("GBM/Platformの通期セグメント税前、ファイナンシング内訳、CET1詳細は10-Kセグメント表で要一次確認。数値はFY2024決算ベース。", { x: 0.85, y: 6.12, w: 11.6, h: 0.7, fontFace: BF, fontSize: 12.5, color: "AEBAD0", margin: 0, valign: "top" });

    s.addNotes("出典と注記。一次情報は10-K・決算リリース・Investor Day。一部は要一次確認。FY2024決算ベース。");
  }

  await pres.writeFile({ fileName: "/home/user/Koki/projects/goldman-sachs-research/Goldman-Sachs-就活企業研究.pptx" });
  console.log("done");
})();
