# -*- coding: utf-8 -*-
#  시리즈 규칙: 컬러, 패널 문자 대문자·모든 패널 같은 크기(28pt), 방위표 3배, 0-50-100 km 축척, 그림 안 설명문 없음, 한글 없음, 결합은 시군구 코드로만.
#  Fig 1 (A) 14년 SUR 지도 + Gi* 핫·콜드 윤곽 (B) 주민 1인당 입원일수 추이 (C) 핫·기타·콜드 시군구 중앙값 비교 · Fig 2 강건 4개 변수의 모형별 비
import os, json, unicodedata, numpy as np, pandas as pd, geopandas as gpd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch, Rectangle, Polygon
from matplotlib.lines import Line2D
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
from numbers_inpt import SHP
HERE = os.path.dirname(os.path.abspath(__file__)); FIG = os.path.join(HERE, "figs"); OUTF = os.path.join(os.path.dirname(HERE), "out", "Figures"); os.makedirs(FIG, exist_ok=True); os.makedirs(OUTF, exist_ok=True)
N = json.load(open(os.path.join(HERE, "numbers_inpt.json"))); GI = pd.read_csv(os.path.join(HERE, "gi_inpt.csv"), dtype={"sigungu_cd": str})
MM = 1 / 25.4; W = 166 * MM; LW = 0.3
plt.rcParams.update({"font.family": "Arial", "font.size": 8, "legend.fontsize": 7.5, "legend.title_fontsize": 8, "axes.linewidth": 1.0, "xtick.major.width": 1.0, "ytick.major.width": 1.0, "lines.linewidth": 1.0, "pdf.fonttype": 42})
G = gpd.read_file(SHP); G["cd"] = G.sigungu_cd.astype(str); G["sido"] = G.cd.str[:2]; SIDO = G.dissolve("sido"); XL = (G.total_bounds[0], G.total_bounds[2]); YL = (G.total_bounds[1], G.total_bounds[3])
def letter(ax, ch, dx=0.0, dy=1.03, fs=28): ax.text(dx, dy, ch.upper(), transform=ax.transAxes, fontsize=fs, fontweight="bold", va="bottom", ha="left", clip_on=False)
def mapax(ax):
    SIDO.boundary.plot(ax=ax, color="#404040", linewidth=1.0); ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_axis_off(); ax.set_aspect("equal")
    x0, x1 = XL; y0, y1 = YL; W_ = x1 - x0; H_ = y1 - y0; bx, by = x0 + 0.62 * W_, y0 + 0.04 * H_; hh = 0.012 * H_
    ax.add_patch(Rectangle((bx, by), 50000, hh, facecolor="black", edgecolor="black", linewidth=1.0)); ax.add_patch(Rectangle((bx + 50000, by), 50000, hh, facecolor="white", edgecolor="black", linewidth=1.0))
    for xx, lab in ((0, "0"), (50000, "50"), (100000, "100")): ax.text(bx + xx, by + hh + 0.008 * H_, lab, ha="center", va="bottom", fontsize=7)
    ax.text(bx + 108000, by + 0.5 * hh, "km", ha="left", va="center", fontsize=7)
    nx, ny = x0 + 0.90 * W_, y0 + 0.70 * H_
    ax.add_patch(Polygon([[nx - 0.036 * W_, ny], [nx + 0.036 * W_, ny], [nx, ny + 0.21 * H_]], closed=True, facecolor="black", edgecolor="none")); ax.text(nx, ny + 0.225 * H_, "N", ha="center", va="bottom", fontsize=24)
def save(fig, k, dpi):
    p = os.path.join(FIG, f"Fig{k}.png"); fig.savefig(p, dpi=dpi, facecolor="white"); plt.close(fig)
    im = Image.open(p).convert("RGB"); im.save(p, dpi=(dpi, dpi)); im.save(os.path.join(OUTF, f"Figure_{k}.tif"), dpi=(dpi, dpi), compression="tiff_lzw"); return im.size

# Fig 1
fig = plt.figure(figsize=(W, 5.0))
ax = fig.add_axes([0.0, 0.17, 0.52, 0.78]); gg = G.merge(GI[["sigungu_cd", "SUR", "cls"]], left_on="cd", right_on="sigungu_cd", how="left"); assert gg.SUR.notna().all() and len(gg) == 229
BR = [0, 0.7, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5, 9]; LB = ["<0.70", "0.70-0.79", "0.80-0.89", "0.90-0.99", "1.00-1.09", "1.10-1.24", "1.25-1.49", "≥1.50"]
PAL = ["#2166AC", "#4393C3", "#92C5DE", "#D1E5F0", "#FDDBC7", "#F4A582", "#D6604D", "#B2182B"]
gg.plot(ax=ax, column="SUR", cmap=ListedColormap(PAL), norm=BoundaryNorm(BR, len(PAL)), edgecolor="#a0a0a0", linewidth=LW); mapax(ax)
gg[gg.cls == "cold"].boundary.plot(ax=ax, color="#08306B", linewidth=1.0, linestyle=(0, (2.0, 1.2))); gg[gg.cls == "hot"].boundary.plot(ax=ax, color="black", linewidth=1.1); letter(ax, "A", dy=0.95)
h = [Patch(facecolor=c, edgecolor="#777777", linewidth=0.5, label=l) for c, l in zip(PAL, LB)] + [Patch(facecolor="none", edgecolor="black", linewidth=1.1, label="Hot spot"), Patch(facecolor="none", edgecolor="#08306B", linewidth=1.0, linestyle="--", label="Cold spot")]
ax.legend(handles=h, title="Standardized inpatient-day ratio, 2011-2024", loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=4, frameon=False, columnspacing=0.8, handlelength=1.3)
b = fig.add_axes([0.62, 0.62, 0.36, 0.30]); yrs = sorted(int(k) for k in N["pc"])
b.plot(yrs, [N["pc"][str(y)] for y in yrs], color="#B2182B", marker="o", ms=2.8, lw=1.2); b.set_ylim(0, 3.6); b.set_xticks([2011, 2014, 2017, 2020, 2024]); b.set_ylabel("Inpatient days per resident"); b.set_xlabel("Year")
b.spines[["top", "right"]].set_visible(False); letter(b, "B", dx=-0.30, dy=1.02)
c = fig.add_axes([0.62, 0.17, 0.36, 0.30]); K = [("dpp", "Days per\ninpatient"), ("beds", "Beds\nper 1,000"), ("ltc", "LTC\nhospitals"), ("aid", "Medical\nAid type 1")]
HC = N["hc"]; xs = np.arange(len(K)); cols = {"hot": "#B2182B", "other": "#BDBDBD", "cold": "#2166AC"}
for j, (cl, lab) in enumerate((("hot", "Hot spots"), ("other", "Other"), ("cold", "Cold spots"))):
    v = [HC[cl][k] / max(HC[c_][k] for c_ in HC) for k, _ in K]; c.bar(xs + (j - 1) * 0.26, v, 0.26, color=cols[cl], label=lab, edgecolor="none")
c.set_xticks(xs); c.set_xticklabels([l for _, l in K], fontsize=6.5); c.set_ylabel("Median, relative to highest group"); c.set_ylim(0, 1.15); c.spines[["top", "right"]].set_visible(False)
c.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.18), fontsize=6.8, handlelength=1.0, columnspacing=0.8); letter(c, "C", dx=-0.30, dy=1.10)
s1 = save(fig, 1, 600)

# Fig 2 — 강건 4개 변수의 모형별 비(1 SD당)
LAB = {"beds_per_1000": "Hospital beds\nper 1,000", "ltc_hospitals": "LTC hospitals per\n100,000 aged 65+", "medicaid1_share": "Medical Aid\ntype 1 share", "moderate_pa_rate": "Moderate-or-higher\nphysical activity"}
ORD = list(LAB)
MOD = [("Principal model", lambda v: N["main"][v], "#000000", "o"),
       ("Knorr-Held type II", lambda v: N["KH_typeII"][v], "#E08214", "P"),
       ("Knorr-Held type IV", lambda v: N["KH_typeIV"][v], "#B2182B", "D"),
       ("Covariates lagged 2 years", lambda v: N["E2_lag2"][v], "#6a3d9a", "X"),
       ("Between-district component", lambda v: N["bw"][v + "__between"], "#7f7f7f", "^"),
       ("Within-district component", lambda v: N["bw"][v + "__within"], "#67A9CF", "v"),
       ("Outpatient visit-days", lambda v: N["nco"]["OUTV|" + v], "#2166AC", "s")]
vals = [MOD[j][1](v) for v in ORD for j in range(len(MOD))]; lo_all = min(t[1] for t in vals); hi_all = max(t[2] for t in vals)
fig, ax = plt.subplots(figsize=(W, 4.2)); fig.subplots_adjust(left=0.22, right=0.98, top=0.98, bottom=0.27)
off = np.linspace(-0.34, 0.34, len(MOD))
for i, v in enumerate(ORD):
    for (lab, f, col, mk), o in zip(MOD, off):
        e, lo, hi = f(v); ax.plot([lo, hi], [i + o] * 2, color=col, lw=1.0); ax.plot(e, i + o, marker=mk, color=col, ms=3.6, mew=0, ls="none")
ax.axvline(1, color="#404040", lw=1.0, ls=":"); ax.set_yticks(range(len(ORD))); ax.set_yticklabels([LAB[v] for v in ORD]); ax.invert_yaxis()
xt = [0.96, 0.98, 1.00, 1.02, 1.04, 1.06, 1.08, 1.10]; assert xt[0] <= lo_all and hi_all <= xt[-1], (lo_all, hi_all)
ax.set_xlim(xt[0], xt[-1]); ax.set_xticks(xt); ax.set_xticklabels([f"{x:.2f}" for x in xt]); ax.minorticks_off()
ax.set_xlabel("Rate ratio per 1 standard deviation (95% credible interval)"); ax.spines[["top", "right"]].set_visible(False)
ax.legend(handles=[Line2D([0], [0], color=c_, marker=m, lw=1.0, ms=3.6, mew=0, label=l) for l, _, c_, m in MOD], loc="upper center", bbox_to_anchor=(0.36, -0.15), ncol=3, frameon=False)
s2 = save(fig, 2, 1000)
for k, s, d in ((1, s1, 600), (2, s2, 1000)): print(f"Fig{k}: {s[0]}x{s[1]} px = {s[0]/d*25.4:.0f} x {s[1]/d*25.4:.0f} mm @ {d} dpi")
