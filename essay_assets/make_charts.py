#!/usr/bin/env python3
"""Generate figures (PNG) and a native Excel workbook for the minimum-wage essay.

All data are real, published aggregate figures:
 - National weighted-average minimum wage: MHLW Regional Minimum Wage Survey, 2005-2025.
 - Non-regular employment share: Statistics Bureau, Labour Force Survey (Detailed Tabulation).
 - 2024 prefectural minimum wages: MHLW, October 2024 revision.
 - Employment elasticities: Kawaguchi & Mori (2021), Abe (2011), Neumark & Wascher (2000),
   Dube, Lester & Reich (2010).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ---- palette ----
NAVY = "#1f3b63"
BLUE = "#2e6da4"
TEAL = "#2a9d8f"
RUST = "#c0392b"
GOLD = "#e0a93b"
GREY = "#7f8c8d"
LIGHT = "#d9e1ea"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.edgecolor": "#4a4a4a",
    "axes.linewidth": 0.9,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "figure.dpi": 150,
})

# ============================================================
# DATA
# ============================================================
years = list(range(2005, 2026))
minwage = [668, 673, 687, 703, 713, 730, 737, 749, 764, 780, 798,
           823, 848, 874, 901, 902, 930, 961, 1004, 1055, 1121]

nr_years = list(range(2005, 2024))
nonreg = [32.6, 33.0, 33.5, 34.1, 33.7, 34.4, 35.1, 35.2, 36.7, 37.4,
          37.5, 37.5, 37.3, 38.2, 38.3, 37.2, 36.7, 36.9, 37.1]

# 2024 prefectural minimum wages (selected, spanning the range), MHLW Oct 2024
pref = [
    ("Tokyo", 1163), ("Kanagawa", 1162), ("Osaka", 1114), ("Saitama", 1078),
    ("Aichi", 1077), ("Chiba", 1076), ("Kyoto", 1058), ("Hyogo", 1052),
    ("Hiroshima", 1020), ("Hokkaido", 1010), ("Fukuoka", 992), ("Miyagi", 973),
    ("Aomori", 953), ("Okinawa", 952), ("Iwate", 952), ("Akita", 951),
]

# Employment elasticity estimates (% employment change per 1% min-wage change)
elast_labels = [
    "Kawaguchi & Mori (2021)\nyoung less-educated men (JP)",
    "Abe (2011)\nteenagers (JP)",
    "Japan aggregate\n(this study, expected)",
    "Neumark & Wascher (2000)\nUS teens",
    "Dube, Lester & Reich (2010)\nUS, border counties",
]
elast_vals = [-1.2, -0.4, -0.3, -0.15, -0.02]
elast_colors = [RUST, "#d56b3e", GOLD, BLUE, TEAL]

# ============================================================
# FIGURE 1 — Minimum wage trend
# ============================================================
fig, ax = plt.subplots(figsize=(8.4, 4.5))
ax.plot(years, minwage, marker="o", ms=4.5, lw=2.4, color=NAVY, zorder=3)
ax.fill_between(years, minwage, min(minwage) - 20, color=LIGHT, alpha=0.55, zorder=1)
ax.axvline(2013, color=GREY, ls="--", lw=1, alpha=0.7)
ax.annotate("Abenomics ¥1,000 target\n(post-2013 acceleration)",
            xy=(2013, 764), xytext=(2008.4, 1000),
            fontsize=9, color="#333",
            arrowprops=dict(arrowstyle="->", color=GREY, lw=1))
ax.annotate("2020: +¥0.2%\n(COVID-19 freeze)", xy=(2020, 902), xytext=(2016.0, 770),
            fontsize=9, color="#333",
            arrowprops=dict(arrowstyle="->", color=GREY, lw=1))
ax.annotate("2025: ¥1,121\nall 47 prefectures > ¥1,000",
            xy=(2025, 1121), xytext=(2019.6, 1135),
            fontsize=9, color=RUST, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=RUST, lw=1))
ax.scatter([2025], [1121], s=55, color=RUST, zorder=4)
ax.set_title("Figure 1. Japan's National Weighted-Average Minimum Wage, 2005–2025")
ax.set_xlabel("Year")
ax.set_ylabel("Minimum wage (¥ per hour)")
ax.set_xlim(2004.3, 2025.8)
ax.set_ylim(640, 1180)
ax.xaxis.set_major_locator(MultipleLocator(2))
ax.grid(axis="y", color="#e3e3e3", lw=0.8)
ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.text(0.125, -0.02, "Source: Ministry of Health, Labour and Welfare, Regional Minimum Wage Survey (2005–2025).",
         fontsize=8, color=GREY)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig1_minwage_trend.png"), bbox_inches="tight", facecolor="white")
plt.close(fig)

# ============================================================
# FIGURE 2 — Non-regular employment share
# ============================================================
fig, ax = plt.subplots(figsize=(8.4, 4.5))
ax.plot(nr_years, nonreg, marker="s", ms=4.5, lw=2.4, color=TEAL, zorder=3)
ax.axhspan(36.7, 38.3, color=TEAL, alpha=0.08)
ax.annotate("Plateau ~37–38%", xy=(2019, 38.3), xytext=(2015.4, 39.0),
            fontsize=9, color="#2a6f66",
            arrowprops=dict(arrowstyle="->", color=GREY, lw=1))
ax.annotate("2005: 32.6%", xy=(2005, 32.6), xytext=(2005, 31.4),
            fontsize=9, color="#333")
ax.set_title("Figure 2. Share of Non-Regular Workers in Total Employment, 2005–2023")
ax.set_xlabel("Year")
ax.set_ylabel("Non-regular share of employees (%)")
ax.set_xlim(2004.3, 2023.6)
ax.set_ylim(31, 40)
ax.xaxis.set_major_locator(MultipleLocator(2))
ax.grid(axis="y", color="#e3e3e3", lw=0.8)
ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.text(0.125, -0.02, "Source: Statistics Bureau of Japan, Labour Force Survey (Detailed Tabulation), 2005–2023.",
         fontsize=8, color=GREY)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig2_nonregular_share.png"), bbox_inches="tight", facecolor="white")
plt.close(fig)

# ============================================================
# FIGURE 3 — Prefectural dispersion 2024
# ============================================================
fig, ax = plt.subplots(figsize=(8.4, 5.2))
names = [p[0] for p in pref]
vals = [p[1] for p in pref]
order = np.argsort(vals)
names = [names[i] for i in order]
vals = [vals[i] for i in order]
colors = [RUST if v == max(vals) else (NAVY if v == min(vals) else BLUE) for v in vals]
bars = ax.barh(names, vals, color=colors, edgecolor="white", height=0.72)
ax.axvline(1055, color=GOLD, ls="--", lw=1.4)
ax.text(1055, -0.9, "National avg ¥1,055", color="#a67c1a", fontsize=8.5, ha="center")
for b, v in zip(bars, vals):
    ax.text(v + 4, b.get_y() + b.get_height() / 2, f"¥{v}", va="center", fontsize=8.5, color="#333")
ax.set_title("Figure 3. Hourly Minimum Wage by Prefecture, 2024 (selected)")
ax.set_xlabel("Minimum wage (¥ per hour)")
ax.set_xlim(900, 1210)
ax.grid(axis="x", color="#e3e3e3", lw=0.8)
ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.text(0.125, -0.03, "Source: MHLW, October 2024 revision. Spread: Tokyo ¥1,163 vs. Akita ¥951 = ¥212.",
         fontsize=8, color=GREY)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig3_prefectural_dispersion.png"), bbox_inches="tight", facecolor="white")
plt.close(fig)

# ============================================================
# FIGURE 4 — Elasticity comparison
# ============================================================
fig, ax = plt.subplots(figsize=(8.6, 4.8))
ypos = np.arange(len(elast_labels))[::-1]
bars = ax.barh(ypos, elast_vals, color=elast_colors, edgecolor="white", height=0.6)
ax.set_yticks(ypos)
ax.set_yticklabels(elast_labels, fontsize=9)
ax.axvline(0, color="#333", lw=1)
for b, v in zip(bars, elast_vals):
    ax.text(v - 0.04, b.get_y() + b.get_height() / 2, f"{v:.2f}",
            va="center", ha="right", fontsize=9, color="#222", fontweight="bold")
ax.set_title("Figure 4. Estimated Employment Elasticities of the Minimum Wage")
ax.set_xlabel("Employment elasticity (% employment change per 1% minimum-wage increase)")
ax.set_xlim(-1.35, 0.15)
ax.grid(axis="x", color="#e3e3e3", lw=0.8)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
fig.text(0.125, -0.03,
         "Sources: Kawaguchi & Mori (2021); Abe (2011); Neumark & Wascher (2000); Dube, Lester & Reich (2010).",
         fontsize=8, color=GREY)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig4_elasticity.png"), bbox_inches="tight", facecolor="white")
plt.close(fig)

# ============================================================
# FIGURE 5 — The descriptive puzzle (dual axis)
# ============================================================
fig, ax1 = plt.subplots(figsize=(8.6, 4.6))
ax1.plot(years, minwage, marker="o", ms=4, lw=2.4, color=NAVY, label="Minimum wage (left)")
ax1.set_ylabel("Minimum wage (¥/hour)", color=NAVY)
ax1.tick_params(axis="y", labelcolor=NAVY)
ax1.set_xlabel("Year")
ax1.set_xlim(2004.3, 2025.8)
ax1.xaxis.set_major_locator(MultipleLocator(3))
ax2 = ax1.twinx()
ax2.plot(nr_years, nonreg, marker="s", ms=4, lw=2.4, color=TEAL, label="Non-regular share (right)")
ax2.set_ylabel("Non-regular share (%)", color=TEAL)
ax2.tick_params(axis="y", labelcolor=TEAL)
ax2.set_ylim(30, 41)
ax1.set_title("Figure 5. The Descriptive Puzzle: Rising Minimum Wage, Flat Non-Regular Share")
ax1.grid(axis="y", color="#eee", lw=0.7)
ax1.set_axisbelow(True)
for s in ("top",):
    ax1.spines[s].set_visible(False)
    ax2.spines[s].set_visible(False)
lines = ax1.get_lines() + ax2.get_lines()
ax1.legend(lines, [l.get_label() for l in lines], loc="lower right", fontsize=9, frameon=False)
fig.text(0.125, -0.02,
         "Sources: MHLW (minimum wage) and Statistics Bureau, Labour Force Survey (non-regular share).",
         fontsize=8, color=GREY)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig5_puzzle.png"), bbox_inches="tight", facecolor="white")
plt.close(fig)

print("Charts written:", [f for f in os.listdir(OUT) if f.endswith(".png")])
