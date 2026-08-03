"""Build competitor-due-diligence PDF report from a structured config JSON.

Usage:
    python build_pdf.py --config config.json --output report.pdf

The config JSON drives both the chart data and the HTML template. See
`examples/shining-lighting.json` for a complete example schema.

Dependencies (install once):
    pip install matplotlib xhtml2pdf

This script auto-detects a CJK font (SimHei on Windows, PingFang on macOS,
Noto Sans CJK on Linux). The PDF engine (xhtml2pdf) does NOT support modern
CSS — keep the HTML template conservative (table-based layout, solid colors,
no flexbox / grid / gradients / pseudo-elements).
"""
import argparse
import base64
import io
import json
import os
import platform
import sys
from pathlib import Path

# Matplotlib must be set to non-interactive backend before importing pyplot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ---------------------------------------------------------------------
# CJK font auto-detection
# ---------------------------------------------------------------------
def configure_cjk_font():
    """Find a CJK font on the system and register it for matplotlib + reportlab.

    Returns the font family name (e.g., 'SimHei') or None if nothing found.
    """
    candidates_by_os = {
        "Windows": [
            ("SimHei", r"C:\Windows\Fonts\simhei.ttf"),
            ("Microsoft YaHei", r"C:\Windows\Fonts\msyh.ttc"),
            ("SimSun", r"C:\Windows\Fonts\simsun.ttc"),
        ],
        "Darwin": [
            ("PingFang SC", "/System/Library/Fonts/PingFang.ttc"),
            ("Heiti SC", "/System/Library/Fonts/STHeiti Medium.ttc"),
        ],
        "Linux": [
            ("Noto Sans CJK SC", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
            ("WenQuanYi Zen Hei", "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"),
            ("Source Han Sans", "/usr/share/fonts/opentype/source-han-sans/SourceHanSansSC-Regular.otf"),
        ],
    }
    system = platform.system()
    fallbacks = candidates_by_os.get(system, []) + candidates_by_os["Linux"]

    for family, path in fallbacks:
        if Path(path).exists():
            # Configure matplotlib
            plt.rcParams["font.sans-serif"] = [family, "DejaVu Sans"]
            plt.rcParams["axes.unicode_minus"] = False
            # Register with reportlab (used by xhtml2pdf)
            try:
                from reportlab.pdfbase import pdfmetrics
                from reportlab.pdfbase.ttfonts import TTFont
                pdfmetrics.registerFont(TTFont(family, path))
                return family
            except Exception as exc:
                print(f"[warn] reportlab font registration failed for {family}: {exc}")
                return family
    print("[warn] no CJK font found; Chinese may render as boxes")
    return None


# ---------------------------------------------------------------------
# Brand palette (industrial / horticulture vibe — green + amber + teal)
# ---------------------------------------------------------------------
PALETTE = {
    "accent":  "#0a8f5a",   # primary green
    "accent2": "#d97706",   # amber
    "accent3": "#0c8a8a",   # teal
    "ink":     "#1a1a1a",
    "ink2":    "#424245",
    "mute":    "#9ca3af",
    "hairline":"#e5e7eb",
    "rule":    "#d1d5db",
    "light":   "#f9fafb",
}


def style_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(PALETTE["hairline"])
    ax.spines["bottom"].set_color(PALETTE["hairline"])
    ax.tick_params(colors=PALETTE["ink2"], labelsize=8)
    ax.yaxis.grid(True, color=PALETTE["hairline"], linewidth=0.5, alpha=0.7)
    ax.set_axisbelow(True)


def fig_to_png_b64(fig, dpi=180):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=dpi, facecolor="white")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


# ---------------------------------------------------------------------
# Chart generators — each takes the config and returns a base64 PNG string.
# Each function is defensive: if the data is missing or empty, returns None.
# ---------------------------------------------------------------------
def chart_efficiency(cfg):
    """Chart 1 — product μmol/J horizontal bar (self vs competitors)."""
    bench = cfg.get("products", {}).get("efficiency_benchmark", [])
    if not bench:
        return None
    fig, ax = plt.subplots(figsize=(8, 3.6), dpi=150)
    items = [f"{b['name']}\n({b.get('power', '')})" for b in bench]
    effs = [b["eff"] for b in bench]
    colors = [PALETTE["accent"] if b.get("is_self") else PALETTE["accent3"] for b in bench]
    bars = ax.barh(items, effs, color=colors, height=0.7)
    for bar, v in zip(bars, effs):
        ax.text(v + 0.04, bar.get_y() + bar.get_height() / 2,
                f"{v} μmol/J", va="center", fontsize=8, color=PALETTE["ink2"])
    ax.set_xlim(0, max(effs) + 0.6)
    ax.set_xlabel(cfg.get("charts", {}).get("efficiency_xlabel", "光合光子效率 (μmol/J)"),
                  fontsize=9, color=PALETTE["ink2"])
    ax.set_title(cfg.get("charts", {}).get("efficiency_title",
            "产品效率对标"), fontsize=10.5, color=PALETTE["ink"],
                 loc="left", weight="bold", pad=12)
    style_axes(ax)
    ax.invert_yaxis()
    plt.tight_layout()
    return fig_to_png_b64(fig)


def chart_power_range(cfg):
    """Chart 2 — power range coverage (5 product lines)."""
    pr = cfg.get("products", {}).get("power_range", {})
    if not pr.get("series"):
        return None
    fig, ax = plt.subplots(figsize=(8, 3.4), dpi=150)
    for i, (s, lo, hi) in enumerate(zip(pr["series"], pr["low"], pr["high"])):
        ax.barh(i, hi - lo, left=lo, height=0.55,
                color=PALETTE["accent"], edgecolor=PALETTE["accent"], alpha=0.85)
        ax.text(lo - 15, i, f"{lo}", va="center", ha="right",
                fontsize=8, color=PALETTE["ink2"])
        ax.text(hi + 25, i, f"{hi} W", va="center", ha="left",
                fontsize=8, color=PALETTE["ink"], weight="bold")
    ax.set_yticks(range(len(pr["series"])))
    ax.set_yticklabels(pr["series"], fontsize=9)
    ax.set_xlim(0, max(pr["high"]) * 1.15)
    ax.set_xlabel("功率 (W)", fontsize=9, color=PALETTE["ink2"])
    ax.set_title(cfg.get("charts", {}).get("power_title",
            "产品线功率覆盖"), fontsize=10.5, color=PALETTE["ink"],
                 loc="left", weight="bold", pad=12)
    style_axes(ax)
    ax.invert_yaxis()
    plt.tight_layout()
    return fig_to_png_b64(fig)


def chart_confidence_radar(cfg):
    """Chart 3 — 12-dimension confidence radar."""
    dims_cfg = cfg.get("confidence", {}).get("dims", [])
    if len(dims_cfg) < 3:
        return None
    fig, ax = plt.subplots(figsize=(7, 6.5), dpi=150, subplot_kw=dict(polar=True))
    dims = [d["name"] for d in dims_cfg]
    scores = [d["score"] for d in dims_cfg]
    angles = np.linspace(0, 2 * np.pi, len(dims), endpoint=False).tolist()
    scores_plot = scores + [scores[0]]
    angles += angles[:1]
    ax.fill(angles, scores_plot, color=PALETTE["accent"], alpha=0.30)
    ax.plot(angles, scores_plot, color=PALETTE["accent"], linewidth=2)
    ax.scatter(angles, scores_plot, color=PALETTE["accent"], s=24, zorder=5)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dims, fontsize=8.5, color=PALETTE["ink2"])
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"],
                       fontsize=7, color=PALETTE["mute"])
    ax.set_ylim(0, 100)
    ax.set_title(cfg.get("confidence", {}).get("chart_title",
            "数据置信度雷达"), fontsize=10.5, color=PALETTE["ink"],
                 loc="left", weight="bold", pad=18)
    ax.grid(color=PALETTE["hairline"], linewidth=0.5)
    plt.tight_layout()
    return fig_to_png_b64(fig)


def chart_digital_presence(cfg):
    """Chart 4 — digital channels horizontal bar."""
    channels = cfg.get("digital", {}).get("channels", [])
    if not channels:
        return None
    fig, ax = plt.subplots(figsize=(7, 4.0), dpi=150)
    names = [c["name"] for c in channels]
    scores = [c["score"] for c in channels]
    colors = []
    for v in scores:
        if v >= 30:
            colors.append(PALETTE["accent"])
        elif v >= 5:
            colors.append(PALETTE["accent2"])
        else:
            colors.append(PALETTE["mute"])
    bars = ax.barh(names, scores, color=colors, height=0.7)
    for bar, v, ch in zip(bars, scores, channels):
        lbl = ch.get("label", f"{v}%")
        ax.text(v + 1.5, bar.get_y() + bar.get_height() / 2,
                lbl, va="center", fontsize=8, color=PALETTE["ink2"])
    ax.set_xlim(0, 100)
    ax.set_xlabel(cfg.get("digital", {}).get("xlabel",
            "数字化存在度 (%)"), fontsize=9, color=PALETTE["ink2"])
    ax.set_title(cfg.get("digital", {}).get("chart_title",
            "数字化布局"), fontsize=10.5, color=PALETTE["ink"],
                 loc="left", weight="bold", pad=12)
    style_axes(ax)
    ax.invert_yaxis()
    plt.tight_layout()
    return fig_to_png_b64(fig)


def chart_threat_donut(cfg):
    """Chart 5 — threat level donut chart."""
    dist = cfg.get("threats", {}).get("level_distribution", [])
    if not dist:
        return None
    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
    labels = [d["label"] for d in dist]
    sizes = [d["pct"] for d in dist]
    color_map = {"低": PALETTE["accent"], "中": PALETTE["accent2"],
                 "高": PALETTE["mute"]}
    colors = []
    for d in dist:
        for k, c in color_map.items():
            if k in d["label"]:
                colors.append(c)
                break
        else:
            colors.append(PALETTE["accent2"])
    explode = [0.05] * len(dist)
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct="%1.0f%%",
        startangle=90, explode=explode, pctdistance=0.7,
        textprops={"fontsize": 9.5, "color": PALETTE["ink"]}
    )
    for t in autotexts:
        t.set_color("white")
        t.set_weight("bold")
    ax.set_title(cfg.get("threats", {}).get("chart_title",
            "威胁等级分布"), fontsize=10.5, color=PALETTE["ink"],
                 loc="left", weight="bold", pad=12)
    centre_circle = plt.Circle((0, 0), 0.50, fc="white")
    fig.gca().add_artist(centre_circle)
    overall = cfg.get("threats", {}).get("overall_label", "")
    if overall:
        ax.text(0, 0, overall, ha="center", va="center",
                fontsize=22, color=PALETTE["ink"], weight="bold")
    ax.text(0, -0.18, cfg.get("threats", {}).get("overall_sub", "综合"),
            ha="center", va="center", fontsize=9, color=PALETTE["ink2"])
    plt.tight_layout()
    return fig_to_png_b64(fig)


def chart_swot(cfg):
    """Chart 6 — SWOT 4-quadrant visual."""
    swot = cfg.get("swot", {})
    quads = [
        ("S", "优势 Strengths", swot.get("S", []), "#dcfce7"),
        ("W", "劣势 Weaknesses", swot.get("W", []), "#fee2e2"),
        ("O", "机会 Opportunities", swot.get("O", []), "#dbeafe"),
        ("T", "威胁 Threats", swot.get("T", []), "#fef3c7"),
    ]
    if not any(q[2] for q in quads):
        return None
    fig, ax = plt.subplots(figsize=(7.5, 5.0), dpi=150)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    positions = [(0, 5, 5, 5), (5, 5, 5, 5), (0, 0, 5, 5), (5, 0, 5, 5)]
    for (key, title, items, bg), (x, y, w, h) in zip(quads, positions):
        if not items:
            continue
        rect = mpatches.FancyBboxPatch(
            (x + 0.15, y + 0.15), w - 0.3, h - 0.3,
            boxstyle="round,pad=0.02",
            linewidth=1.2, edgecolor=PALETTE["hairline"], facecolor=bg
        )
        ax.add_patch(rect)
        ax.text(x + 0.4, y + h - 0.6, title, fontsize=11,
                color=PALETTE["ink"], weight="bold")
        for i, item in enumerate(items):
            font_size = 8 if len(item) < 30 else 7
            ax.text(x + 0.4, y + h - 1.3 - i * 0.7, f"· {item}",
                    fontsize=font_size, color=PALETTE["ink2"], va="top",
                    wrap=True)
    ax.set_title(cfg.get("swot", {}).get("chart_title", "SWOT 分析"),
                 fontsize=10.5, color=PALETTE["ink"],
                 loc="left", weight="bold", pad=12)
    fig.subplots_adjust(top=0.92, bottom=0.02, left=0.02, right=0.98)
    return fig_to_png_b64(fig)


def chart_recs_scatter(cfg):
    """Chart 7 — recommendations impact × effort scatter."""
    items = cfg.get("recs", {}).get("scatter", [])
    if not items:
        return None
    fig, ax = plt.subplots(figsize=(7.5, 5.0), dpi=150)
    color_map = {"高": PALETTE["accent"], "中": PALETTE["accent"],
                 "低": PALETTE["mute"], "待评估": PALETTE["accent2"]}
    for it in items:
        impact = it.get("impact", 3)
        effort = it.get("effort", 3)
        c = color_map.get(it.get("level", "中"), PALETTE["accent"])
        ax.scatter(effort, impact, s=380, color=c, alpha=0.85,
                   edgecolors=PALETTE["ink"], linewidth=1.2, zorder=5)
        offset_y = 0.22 if it.get("id") != "R3" else -0.32
        ax.text(effort, impact + offset_y, f"{it.get('id', '')} {it.get('title', '')}",
                ha="center", fontsize=8.5, color=PALETTE["ink"], weight="bold")
    ax.axhline(y=3.5, color=PALETTE["mute"], linestyle="--", linewidth=0.6, alpha=0.6)
    ax.axvline(x=2.5, color=PALETTE["mute"], linestyle="--", linewidth=0.6, alpha=0.6)
    ax.text(0.6, 5.3, "高 ROI 优先做", fontsize=8, color="#15803d",
            weight="bold", style="italic")
    ax.text(3.4, 5.3, "重投入需评估", fontsize=8, color="#b45309",
            weight="bold", style="italic")
    ax.text(0.6, 0.7, "战略备选", fontsize=8, color=PALETTE["mute"], style="italic")
    ax.text(3.4, 0.7, "低优先级", fontsize=8, color=PALETTE["mute"], style="italic")
    ax.set_xlim(0, 5.5)
    ax.set_ylim(0, 6)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xticklabels(["极低", "低", "中", "高", "极高"])
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["极低", "低", "中", "高", "极高"])
    ax.set_xlabel("实施难度 (Effort) →", fontsize=9, color=PALETTE["ink2"])
    ax.set_ylabel("战略影响 (Impact) →", fontsize=9, color=PALETTE["ink2"])
    ax.set_title(cfg.get("recs", {}).get("chart_title", "建议优先级矩阵"),
                 fontsize=10.5, color=PALETTE["ink"],
                 loc="left", weight="bold", pad=12)
    style_axes(ax)
    plt.tight_layout()
    return fig_to_png_b64(fig)


# ---------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
<meta charset="UTF-8">
<title>{{ company.name_zh }} 竞品背调报告</title>
<style>
  @page {
    size: A4 portrait;
    margin: 16mm 14mm 18mm 14mm;
  }
  html, body, div, p, span, h1, h2, h3, h4, h5, h6, table, td, th, tr, ul, ol, li, a, b, strong, i, em, small, code, pre, hr, section, article, header, footer, main, aside, blockquote, figure, figcaption, img {
    font-family: "{{ font_family }}", "STSong-Light", "Helvetica", sans-serif !important;
  }
  body { margin: 0; padding: 0; color: #1a1a1a; background: #fff; font-size: 9.5pt; line-height: 1.55; }

  /* Cover */
  table.cover-table { width: 100%; border-collapse: collapse; margin: 0; page-break-after: always; }
  table.cover-table td.cover-cell { background-color: #064e3b; color: #fff; padding: 30mm 22mm 20mm; width: 100%; }
  .cover-tag { display: inline-block; padding: 4px 12px; border: 1px solid rgba(255,255,255,0.5); color: #fff; font-size: 8.5pt; letter-spacing: 2px; }
  .cover h1 { color: #fff; font-size: 26pt; font-weight: 800; margin: 14px 0 6px; line-height: 1.15; letter-spacing: -1px; }
  .cover-cn { color: #fff; font-size: 12pt; font-weight: 500; opacity: 0.9; margin: 4px 0 6px; line-height: 1.3; }
  .cover .subtitle { color: #fff; font-size: 9.5pt; opacity: 0.85; line-height: 1.5; margin: 10px 0 12px; }
  .cover-divider { border: 0; border-top: 2px solid #10b981; width: 50px; margin: 0 0 12px; }
  .cover-foot { color: #fff; font-size: 8pt; opacity: 0.7; margin-top: 8mm; }
  .cover-foot .label { font-size: 8pt; letter-spacing: 1px; opacity: 0.7; }

  /* Section header */
  h2.section { font-size: 19pt; font-weight: 800; margin: 0 0 4px; color: #1a1a1a; letter-spacing: -0.5px; }
  .section-num { font-size: 9pt; font-weight: 700; color: #0a8f5a; letter-spacing: 3px; margin-bottom: 6px; }
  .section-line { border: 0; border-top: 3px solid #0a8f5a; width: 50px; margin: 10px 0 18px; }
  h3 { font-size: 12pt; font-weight: 700; margin: 18px 0 8px; color: #1a1a1a; letter-spacing: -0.3px; }
  h3 .num { color: #9ca3af; font-weight: 500; margin-right: 6px; }
  p { margin: 6px 0; }
  .lead { font-size: 10pt; color: #424245; line-height: 1.75; border-left: 3px solid #0a8f5a; background: #f3faf6; padding: 10px 14px; margin: 12px 0 16px; }
  .page-break { page-break-after: always; }
  .avoid-break { page-break-inside: avoid; }

  /* KPI cards (table-based) */
  table.kpis { width: 100%; border-collapse: separate; border-spacing: 6px; margin: 12px 0 4px; }
  table.kpis td { width: 25%; padding: 6px 8px; border: 1px solid #d1d5db; background: #f5f5f7; vertical-align: top; }
  table.kpis td.k-blue   { background: #e3f0ff; border-color: #b8d4ff; }
  table.kpis td.k-green  { background: #e8f7ee; border-color: #b3e0c2; }
  table.kpis td.k-orange { background: #fff0e0; border-color: #ffc89b; }
  table.kpis td.k-amber  { background: #fef3c7; border-color: #fcd34d; }
  table.kpis td.k-red    { background: #fee2e2; border-color: #fca5a5; }
  table.kpis td.k-teal   { background: #dff1f1; border-color: #9dd5d5; }
  table.kpis td.k-purple { background: #f0e8ff; border-color: #c9b3ff; }
  table.kpis .label { font-size: 7.5pt; color: #6b7280; letter-spacing: 0.5px; font-weight: 600; }
  table.kpis .value { font-size: 16pt; font-weight: 800; color: #1a1a1a; line-height: 1.05; margin-top: 2px; }
  table.kpis .unit  { font-size: 10pt; color: #6b7280; margin-left: 2px; font-weight: 500; }
  table.kpis .desc  { font-size: 7.5pt; color: #6b7280; margin-top: 3px; }

  /* Stats banner (used after lead paragraph in section 1) */
  .cover-stats { background: #f0fdf4; border: 1px solid #86efac; padding: 10px 14px; margin: 12px 0 18px; text-align: center; }
  .cover-stats table { width: 100%; border-collapse: collapse; }
  .cover-stats td { width: 25%; padding: 4px 8px; }
  .cover-stats .num { font-size: 18pt; font-weight: 800; color: #064e3b; line-height: 1; }
  .cover-stats .lbl { font-size: 7.5pt; color: #047857; margin-top: 2px; letter-spacing: 0.5px; }

  /* Chart card */
  .chart-card { background: #fff; border: 1px solid #e5e7eb; padding: 12px 14px; margin: 12px 0; }
  .chart-title { font-size: 10.5pt; font-weight: 700; color: #1a1a1a; margin: 0 0 4px; padding-left: 10px; border-left: 4px solid #0a8f5a; }
  .chart-sub  { font-size: 8.5pt; color: #6b7280; margin: 0 0 10px; padding-left: 10px; }
  .chart-img { text-align: center; }

  /* Data table */
  table.data { width: 100%; border-collapse: collapse; font-size: 8.5pt; margin: 8px 0; background: #fff; border: 1px solid #e5e7eb; }
  table.data thead th { background: #f5f5f7; padding: 7px 10px; text-align: left; font-weight: 700; color: #1a1a1a; border-bottom: 1px solid #d1d5db; font-size: 8pt; letter-spacing: 0.3px; }
  table.data tbody td { padding: 6px 10px; border-bottom: 1px solid #f0f0f0; color: #424245; }
  table.data tbody tr:last-child td { border-bottom: 0; }
  table.data tbody tr:nth-child(even) { background: #fbfbfd; }
  table.data tbody td.bold { font-weight: 700; color: #1a1a1a; }
  .pill { display: inline-block; padding: 1px 8px; border-radius: 10px; font-size: 7.5pt; font-weight: 600; }
  .pill-bad  { background: #fee2e2; color: #b91c1c; }
  .pill-warn { background: #fef3c7; color: #b45309; }
  .pill-ok   { background: #d1fae5; color: #047857; }
  .pill-good { background: #dbeafe; color: #1d4ed8; }
  .pill-best { background: #f3e8ff; color: #6b21a8; }

  /* Recommendation cards */
  table.rec-grid { width: 100%; border-collapse: separate; border-spacing: 8px; margin: 12px 0; }
  table.rec-grid td { width: 33.33%; padding: 12px 14px; vertical-align: top; border: 1px solid; }
  table.rec-grid td.r1 { background: #f0fdf4; border-color: #86efac; }
  table.rec-grid td.r2 { background: #f0f9ff; border-color: #93c5fd; }
  table.rec-grid td.r3 { background: #fdf4ff; border-color: #d8b4fe; }
  .rec-level { display: inline-block; padding: 2px 9px; color: #fff; font-size: 7.5pt; font-weight: 700; letter-spacing: 0.5px; }
  .rec-level.l1 { background: #16a34a; }
  .rec-level.l2 { background: #2563eb; }
  .rec-level.l3 { background: #9333ea; }
  .rec-title { font-size: 10pt; font-weight: 700; color: #1a1a1a; margin: 6px 0 4px; }
  .rec-desc  { font-size: 8.5pt; color: #424245; line-height: 1.55; }
  .rec-effort { font-size: 7.5pt; color: #6b7280; margin-top: 5px; font-style: italic; }

  /* Insight callout (yellow) */
  .insight { background: #fffbeb; border-left: 4px solid #d97706; padding: 10px 14px; margin: 12px 0; }
  .insight h4 { margin: 0 0 4px; font-size: 10pt; color: #92400e; }
  .insight p  { font-size: 8.5pt; color: #78350f; margin: 0; line-height: 1.6; }

  /* Bullets */
  ul, ol { margin: 6px 0 6px 18px; padding: 0; }
  li { margin: 3px 0; font-size: 9pt; line-height: 1.55; color: #0a8f5a; font-weight: 700; }
  li span { color: #1a1a1a; font-weight: 400; }

  /* Two-column layout */
  table.two-col { width: 100%; border-collapse: separate; border-spacing: 12px; margin: 10px 0; }
  table.two-col td { width: 50%; vertical-align: top; }

  /* Footer meta */
  .footer-meta { background: #f5f5f7; border: 1px solid #e5e7eb; padding: 10px 14px; margin-top: 18px; font-size: 8pt; color: #6b7280; }
  .footer-meta h4 { margin: 0 0 4px; font-size: 9pt; color: #1a1a1a; }
  .footer-meta ul { margin: 4px 0 0 16px; }
  .footer-meta li { font-size: 7.5pt; color: #6b7280; font-weight: 400; }
</style>
</head>
<body>

<!-- ============================== COVER ============================== -->
<table class="cover-table" cellpadding="0" cellspacing="0">
  <tr><td class="cover-cell">
    <div class="cover-tag">COMPETITOR DUE DILIGENCE · 12-DIMENSION</div>
    <h1>{{ company.name_en }}</h1>
    <div class="cover-cn">{{ company.name_zh }} · 竞品背调报告</div>
    <hr class="cover-divider">
    <p class="subtitle">{{ company.tagline }}</p>
    <div class="cover-foot">
      <span class="label">REPORT DATE · {{ report.date }} · {{ report.version }} · Mavis / MiniMax Code</span>
    </div>
  </td></tr>
</table>

<!-- ============================ SECTION 1 ============================ -->
<section>
  <div class="section-num">01 / EXECUTIVE SUMMARY</div>
  <h2 class="section">执行摘要</h2>
  <hr class="section-line">

  <p class="lead">{{ lead_text }}</p>

  <div class="cover-stats avoid-break">
    <table>
      <tr>
        {% for s in stats_banner %}
        <td><div class="num">{{ s.num }}</div><div class="lbl">{{ s.lbl }}</div></td>
        {% endfor %}
      </tr>
    </table>
  </div>

  <table class="kpis">
    <tr>
      {% for k in kpis %}
      <td class="k-{{ k.color | default('green') }}">
        <div class="label">{{ k.label }}</div>
        <div class="value">{{ k.value }}<span class="unit">{{ k.unit | default('') }}</span></div>
        <div class="desc">{{ k.desc }}</div>
      </td>
      {% endfor %}
    </tr>
  </table>

  <div class="insight">
    <h4>核心判断</h4>
    <p>{{ insight_text }}</p>
  </div>
</section>

<div class="page-break"></div>

<!-- ============================ SECTION 2 ============================ -->
<section>
  <div class="section-num">02 / COMPANY BASICS</div>
  <h2 class="section">基础信息</h2>
  <hr class="section-line">

  <table class="data avoid-break">
    <thead><tr><th style="width:30%;">字段</th><th>内容</th></tr></thead>
    <tbody>
      {% for r in basics_rows %}
      <tr><td class="bold">{{ r.label }}</td><td>{{ r.value | safe }}</td></tr>
      {% endfor %}
    </tbody>
  </table>

  <div class="insight">
    <h4>读这家公司的姿势</h4>
    <p>{{ basics_insight }}</p>
  </div>
</section>

<div class="page-break"></div>

<!-- ============================ SECTION 3 ============================ -->
<section>
  <div class="section-num">03 / PRODUCT MATRIX</div>
  <h2 class="section">产品矩阵</h2>
  <hr class="section-line">

  <p class="lead">{{ products.lead_text }}</p>

  <table class="data avoid-break">
    <thead>
      <tr>
        <th>系列</th><th>功率段 (W)</th><th>效率 (μmol/J)</th>
        <th>定位</th><th>对标</th>
      </tr>
    </thead>
    <tbody>
      {% for p in products.lines %}
      <tr>
        <td class="bold">{{ p.name }}</td>
        <td>{{ p.power_lo }} - {{ p.power_hi }}</td>
        <td>{{ p.eff }}</td>
        <td>{{ p.position }}</td>
        <td>{{ p.compete_with }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  {% if charts.efficiency %}
  <h3><span class="num">3.1</span>{{ products.section3_1_title | default('效率对标') }}</h3>
  <div class="chart-card avoid-break">
    <p class="chart-title">{{ products.chart_eff_title | default('产品效率对标') }}</p>
    <p class="chart-sub">{{ products.chart_eff_sub | default('数据来源：官网 + 公开技术规格') }}</p>
    <div class="chart-img">{{ charts.efficiency | safe }}</div>
  </div>
  {% endif %}

  {% if charts.power_range %}
  <h3><span class="num">3.2</span>{{ products.section3_2_title | default('功率覆盖') }}</h3>
  <div class="chart-card avoid-break">
    <p class="chart-title">{{ products.chart_power_title | default('产品线功率覆盖') }}</p>
    <p class="chart-sub">{{ products.chart_power_sub | default('') }}</p>
    <div class="chart-img">{{ charts.power_range | safe }}</div>
  </div>
  {% endif %}
</section>

<div class="page-break"></div>

<!-- ============================ SECTION 4 ============================ -->
<section>
  <div class="section-num">04 / THREAT ASSESSMENT</div>
  <h2 class="section">威胁评估</h2>
  <hr class="section-line">

  <p class="lead">{{ threats.lead_text }}</p>

  <table class="two-col">
    <tr>
      <td>
        {% if charts.threat_donut %}
        <div class="chart-card avoid-break">
          <p class="chart-title">{{ threats.chart_title | default('威胁等级分布') }}</p>
          <div class="chart-img">{{ charts.threat_donut | safe }}</div>
        </div>
        {% endif %}
      </td>
      <td>
        <h3><span class="num">4.1</span>威胁维度拆解</h3>
        <table class="data">
          <thead><tr><th>维度</th><th>威胁</th><th>说明</th></tr></thead>
          <tbody>
            {% for r in threats.dimensions %}
            <tr>
              <td class="bold">{{ r.name }}</td>
              <td><span class="pill pill-{{ r.level_class | default('ok') }}">{{ r.level }}</span></td>
              <td>{{ r.note }}</td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </td>
    </tr>
  </table>

  <div class="insight">
    <h4>关键结论</h4>
    <p>{{ threats.conclusion }}</p>
  </div>
</section>

<div class="page-break"></div>

<!-- ============================ SECTION 5 ============================ -->
<section>
  <div class="section-num">05 / DATA CONFIDENCE</div>
  <h2 class="section">数据置信度</h2>
  <hr class="section-line">

  <p class="lead">{{ confidence.lead_text }}</p>

  {% if charts.confidence_radar %}
  <div class="chart-card avoid-break">
    <p class="chart-title">{{ confidence.chart_title | default('12 维度数据置信度雷达') }}</p>
    <p class="chart-sub">0-100 分制，100 = 完全可验证 / 0 = 公开数据为零</p>
    <div class="chart-img">{{ charts.confidence_radar | safe }}</div>
  </div>
  {% endif %}

  <h3><span class="num">5.1</span>分维度评分</h3>
  <table class="data avoid-break">
    <thead><tr><th>维度</th><th>得分</th><th>等级</th><th>核心缺口</th></tr></thead>
    <tbody>
      {% for r in confidence.dims %}
      <tr>
        <td class="bold">{{ r.name }}</td>
        <td>{{ r.score }}</td>
        <td><span class="pill pill-{{ r.level_class | default('warn') }}">{{ r.level }}</span></td>
        <td>{{ r.gap }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</section>

<div class="page-break"></div>

<!-- ============================ SECTION 6 ============================ -->
<section>
  <div class="section-num">06 / SWOT</div>
  <h2 class="section">SWOT 分析</h2>
  <hr class="section-line">

  <p class="lead">{{ swot.lead_text }}</p>

  {% if charts.swot %}
  <div class="chart-card avoid-break">
    <p class="chart-title">SWOT 四象限</p>
    <div class="chart-img">{{ charts.swot | safe }}</div>
  </div>
  {% endif %}

  {% if swot.insights %}
  <h3><span class="num">6.1</span>关键解读</h3>
  <ul>
    {% for it in swot.insights %}
    <li><span><b>{{ it.label }}：</b>{{ it.text }}</span></li>
    {% endfor %}
  </ul>
  {% endif %}
</section>

<div class="page-break"></div>

<!-- ============================ SECTION 7 ============================ -->
<section>
  <div class="section-num">07 / DIGITAL PRESENCE</div>
  <h2 class="section">数字化布局</h2>
  <hr class="section-line">

  <p class="lead">{{ digital.lead_text }}</p>

  {% if charts.digital %}
  <div class="chart-card avoid-break">
    <p class="chart-title">{{ digital.chart_title | default('数字化存在度对比') }}</p>
    <p class="chart-sub">{{ digital.chart_sub | default('基于公开搜索与平台查询') }}</p>
    <div class="chart-img">{{ charts.digital | safe }}</div>
  </div>
  {% endif %}

  {% if digital.channels_table %}
  <h3><span class="num">7.1</span>渠道分项</h3>
  <table class="data avoid-break">
    <thead><tr><th>渠道</th><th>状态</th><th>备注</th></tr></thead>
    <tbody>
      {% for r in digital.channels_table %}
      <tr>
        <td class="bold">{{ r.name }}</td>
        <td><span class="pill pill-{{ r.status_class | default('ok') }}">{{ r.status }}</span></td>
        <td>{{ r.note }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% endif %}
</section>

<div class="page-break"></div>

<!-- ============================ SECTION 8 ============================ -->
<section>
  <div class="section-num">08 / STRATEGIC RECOMMENDATIONS</div>
  <h2 class="section">战略建议</h2>
  <hr class="section-line">

  <p class="lead">{{ recs.lead_text }}</p>

  {% if charts.recs_scatter %}
  <div class="chart-card avoid-break">
    <p class="chart-title">{{ recs.chart_title | default('建议优先级矩阵') }}</p>
    <div class="chart-img">{{ charts.recs_scatter | safe }}</div>
  </div>
  {% endif %}

  {% if recs.top3 %}
  <h3><span class="num">8.1</span>Top 3 建议（高 ROI）</h3>
  <table class="rec-grid">
    <tr>
      {% for r in recs.top3 %}
      <td class="r{{ loop.index }}">
        <span class="rec-level l{{ loop.index }}">{{ r.id }} · {{ r.level }}</span>
        <div class="rec-title">{{ r.title }}</div>
        <div class="rec-desc">{{ r.desc }}</div>
        <div class="rec-effort">实施难度：{{ r.effort }}</div>
      </td>
      {% endfor %}
    </tr>
  </table>
  {% endif %}

  {% if recs.backup %}
  <h3><span class="num">8.2</span>{{ recs.backup_title | default('R4 - R5 建议（备选）') }}</h3>
  <table class="data avoid-break">
    <thead><tr><th>编号</th><th>建议</th><th>动作</th><th>ROI</th></tr></thead>
    <tbody>
      {% for r in recs.backup %}
      <tr>
        <td class="bold">{{ r.id }}</td>
        <td>{{ r.title }}</td>
        <td>{{ r.action }}</td>
        <td><span class="pill pill-{{ r.roi_class | default('warn') }}">{{ r.roi }}</span></td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% endif %}
</section>

<div class="page-break"></div>

<!-- ============================ SECTION 9 ============================ -->
<section>
  <div class="section-num">09 / DATA GAPS &amp; NEXT STEPS</div>
  <h2 class="section">数据缺口与下一步</h2>
  <hr class="section-line">

  <p class="lead">{{ gaps.lead_text }}</p>

  <h3><span class="num">9.1</span>免费数据源已穷尽</h3>
  <table class="data avoid-break">
    <thead><tr><th>数据源</th><th>结果</th></tr></thead>
    <tbody>
      {% for r in gaps.free_sources %}
      <tr><td>{{ r.name }}</td><td>{{ r.result }}</td></tr>
      {% endfor %}
    </tbody>
  </table>

  <h3><span class="num">9.2</span>建议追加的付费数据源</h3>
  <table class="data avoid-break">
    <thead><tr><th>数据源</th><th>用途</th><th>预估成本</th><th>优先级</th></tr></thead>
    <tbody>
      {% for r in gaps.paid_sources %}
      <tr>
        <td class="bold">{{ r.name }}</td>
        <td>{{ r.use }}</td>
        <td>{{ r.cost }}</td>
        <td><span class="pill pill-{{ r.priority_class | default('good') }}">{{ r.priority }}</span></td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <div class="footer-meta">
    <h4>报告交付说明</h4>
    <ul>
      <li>{{ footer_note }}</li>
    </ul>
  </div>
</section>

</body>
</html>
"""


# ---------------------------------------------------------------------
# Templating — uses Jinja2 for proper nested-context support
# ---------------------------------------------------------------------
def render_template(text, ctx):
    """Render the HTML template with the given context dict.

    Adds a custom filter `default_or_blank` so optional fields render
    cleanly when missing (empty string instead of "None").
    """
    from jinja2 import Environment, BaseLoader

    env = Environment(loader=BaseLoader(), autoescape=False)
    env.filters["default_or_blank"] = lambda v, d="": v if v else d
    tmpl = env.from_string(text)
    return tmpl.render(**ctx)


# ---------------------------------------------------------------------
# Build pipeline
# ---------------------------------------------------------------------
def build(config_path: Path, output_path: Path, font_family: str):
    cfg = json.loads(config_path.read_text(encoding="utf-8"))

    # 1. Generate all charts
    charts = {
        "efficiency": chart_efficiency(cfg),
        "power_range": chart_power_range(cfg),
        "confidence_radar": chart_confidence_radar(cfg),
        "digital": chart_digital_presence(cfg),
        "threat_donut": chart_threat_donut(cfg),
        "swot": chart_swot(cfg),
        "recs_scatter": chart_recs_scatter(cfg),
    }
    # Embed charts as <img> tags
    for k, b64 in charts.items():
        if b64:
            charts[k] = f'<img src="data:image/png;base64,{b64}" width="500" />'
        else:
            charts[k] = ""

    # 2. Defaults
    if "lang" not in cfg:
        cfg["lang"] = "zh-CN"
    if "font_family" not in cfg:
        cfg["font_family"] = font_family or "Helvetica"
    if "report" not in cfg:
        cfg["report"] = {"date": "1970-01-01", "version": "v1.0"}
    if "footer_note" not in cfg:
        cfg["footer_note"] = (
            "本报告由 Mavis / MiniMax Code / competitor-due-diligence skill 自动生成。"
        )

    ctx = dict(cfg)
    ctx["charts"] = charts

    # 3. Render HTML
    html = render_template(HTML_TEMPLATE, ctx)

    # 4. Write HTML alongside PDF for inspection
    html_path = output_path.with_suffix(".html")
    html_path.write_text(html, encoding="utf-8")
    print(f"[ok] wrote HTML: {html_path} ({len(html):,} chars)")

    # 5. Render PDF
    from xhtml2pdf import pisa
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as dst:
        result = pisa.CreatePDF(src=html, dest=dst, encoding="utf-8")
    if result.err:
        print(f"[warn] PDF render reported {result.err} non-fatal errors")
    size_kb = output_path.stat().st_size / 1024
    print(f"[ok] wrote PDF: {output_path} ({size_kb:.0f} KB)")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--config", required=True, help="path to config JSON")
    ap.add_argument("--output", required=True, help="path to output PDF")
    args = ap.parse_args()

    font_family = configure_cjk_font()
    if font_family:
        print(f"[ok] CJK font: {font_family}")

    build(Path(args.config), Path(args.output), font_family)


if __name__ == "__main__":
    main()
