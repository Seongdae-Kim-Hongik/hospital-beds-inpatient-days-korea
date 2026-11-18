import os, json, unicodedata, numpy as np, pandas as pd
from scipy.stats import spearmanr, norm
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.abspath(os.path.join(HERE, "..", "..")); AN = os.path.dirname(B); ROOT = os.path.dirname(AN); PAN = os.path.join(ROOT, "02_패널")
RS = lambda v="std3": os.path.join(B, f"results_{v}"); NFC = lambda s: unicodedata.normalize("NFC", str(s))
SHP = os.environ.get("ST_SHP", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "data", "boundary", "final.shp"))
VARS = {"walking_rate": "ext__walking_rate", "moderate_pa_rate": "moderate_pa_rate", "public_sport_fac_per100k": "ext__public_sport_fac_per100k", "village_sport_fac_per100k": "ext__village_sport_fac_per100k",
        "basic_livelihood_rate": "basic_livelihood_rate", "medicaid1_share": "ext__medicaid1_share", "chewing_discomfort_65": "ext__chewing_discomfort_65", "beds_per_1000": "ext__beds_per_1000",
        "ltc_hospitals": "ltc_hospitals_per_100k_65", "urban_population_share": "urban_population_share", "physicians_per_1000": "physicians_per_1000", "sex_ratio": "sex_ratio",
        "fiscal_independence": "fiscal_independence", "pop80_share": "pop80_share"}
HYP = list(VARS)[:9]; ROB = ["beds_per_1000", "ltc_hospitals", "medicaid1_share", "moderate_pa_rate"]
def tab(f, v="std3"):
    d = pd.read_csv(os.path.join(RS(v), f)); d["cov"] = d["cov"].astype(str); return d
def get(d, c, item=None):
    r = d[d["cov"] == c]
    if item is not None and "item" in d: r = r[r.item == item]
    r = r.iloc[0]; return [round(float(r.IRR), 3), round(float(r.lo), 3), round(float(r.hi), 3)]
N = {}
P = pd.read_csv(os.path.join(B, "panel_INPT_std3.csv")); P["fbd_region"] = P.fbd_region.map(NFC)
X = pd.read_csv(os.path.join(PAN, "INPT_aux.csv")); X["fbd_region"] = X.fbd_region.map(NFC)
P = P.merge(X, on=["year", "fbd_region"], how="left", validate="one_to_one"); assert P.pt_in.notna().all()
N["n_rows"] = len(P); N["n_districts"] = P.fbd_region.nunique(); N["days_total_bn"] = round(P.cases.sum() / 1e9, 2)
g = P.groupby("year"); pc = g.cases.sum() / g.population.sum(); N["pc"] = {int(k): round(v, 2) for k, v in pc.items()}
N["outside_share"] = {int(k): round(v, 3) for k, v in (g.vd_out.sum() / g.cases.sum()).items()}
N["days_per_pt"] = {int(k): round(v, 1) for k, v in (g.cases.sum() / (g.pt_in.sum() + g.pt_out.sum())).items()}
N["zero_in_cells"] = int((P.vd_in == 0).sum())
L = P.groupby("fbd_region").apply(lambda d: d.cases.sum() / d.E.sum(), include_groups=False)
N["sur_min"], N["sur_max"] = round(L.min(), 2), round(L.max(), 2); N["sur_p10"], N["sur_p90"] = round(L.quantile(.1), 2), round(L.quantile(.9), 2); N["p90p10"] = round(L.quantile(.9) / L.quantile(.1), 2)
N["sur_top"] = [[r, round(v, 2)] for r, v in L.sort_values(ascending=False).head(6).items()]; N["sur_bottom"] = [[r, round(v, 2)] for r, v in L.sort_values().head(6).items()]
crude = P.cases / (P.population * P.year.map(g.cases.sum() / g.population.sum()))
N["rho80_crude"] = round(spearmanr(crude, P.pop80_share_raw).correlation, 2); N["rho80_std"] = round(spearmanr(P.cases / P.E, P.pop80_share_raw).correlation, 2)
# 창별 기술(Table 1)
WIN = {"2011-2015": (2011, 2015), "2016-2019": (2016, 2019), "2020-2024": (2020, 2024), "2011-2024": (2011, 2024)}
COV1 = ["walking_rate", "moderate_pa_rate", "public_sport_fac_per100k", "village_sport_fac_per100k", "basic_livelihood_rate", "medicaid1_share", "chewing_discomfort_65", "beds_per_1000", "ltc_hospitals",
        "urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"]
raw = {k: (VARS[k] + "_raw") for k in COV1}; assert all(c in P for c in raw.values()), [c for c in raw.values() if c not in P]
T1 = {}
for w, (a, b) in WIN.items():
    s = P[P.year.between(a, b)]; sw = s.groupby("fbd_region").apply(lambda d: d.cases.sum() / d.E.sum(), include_groups=False)
    T1[w] = dict(n=len(s), days=float(s.cases.sum()), pc=float(s.cases.sum() / s.population.sum()), out=float(s.vd_out.sum() / s.cases.sum()),
                 dpp=float(s.cases.sum() / (s.pt_in.sum() + s.pt_out.sum())), sur_med=float(sw.median()), sur_p10=float(sw.quantile(.1)), sur_p90=float(sw.quantile(.9)),
                 cov={k: [float(s[raw[k]].mean()), float(s[raw[k]].std())] for k in COV1})
N["T1"] = T1
# 연도별 Moran·Kendall
mo = pd.read_csv(os.path.join(RS(), "S6_moran_year.csv")); N["moran_min"], N["moran_max"] = round(mo.moran_I.min(), 2), round(mo.moran_I.max(), 2)
N["kendall_w"] = round(float(pd.read_csv(os.path.join(RS(), "S12_persistence.csv")).iloc[0].kendall_W), 2)
Y = P.pivot_table(index="fbd_region", columns="year", values="SIR"); N["rho_2011_2024"] = round(spearmanr(Y[2011], Y[2024]).correlation, 2)
# Gi*(593 그래프, 자기 포함) — 14년 log SUR
import geopandas as gpd
G = open(os.path.join(B, "graph_593.graph")).read().split("\n"); nreg = int(G[0]); nb = {}
for line in G[1:]:
    t = line.split()
    if len(t) >= 2: nb[int(t[0])] = [int(x) for x in t[2:]]
area = pd.DataFrame({"fbd_region": gpd.read_file(SHP)["region"].values}); area["fbd_region"] = area.fbd_region.map(NFC); assert len(area) == nreg
id2r = dict(zip(range(1, nreg + 1), area.fbd_region))
x = np.log(L.reindex([id2r[i] for i in range(1, nreg + 1)]).values); assert not np.isnan(x).any(); xb, sd = x.mean(), x.std(); gi = []
for i in range(1, nreg + 1):
    w = np.zeros(nreg); w[i - 1] = 1; w[[j - 1 for j in nb.get(i, [])]] = 1; W = w.sum()
    gi.append(((w * x).sum() - xb * W) / (sd * np.sqrt((nreg * (w ** 2).sum() - W ** 2) / (nreg - 1))))
GI = pd.DataFrame({"fbd_region": [id2r[i] for i in range(1, nreg + 1)], "SUR": np.exp(x), "z": gi}); GI["p"] = 2 * norm.sf(GI.z.abs())
GI["cls"] = np.where((GI.p < 0.05) & (GI.z > 0), "hot", np.where((GI.p < 0.05) & (GI.z < 0), "cold", "other"))
S6 = pd.read_csv(os.path.join(RS(), "S6_spatial_RR.csv")); S6["fbd_region"] = S6.fbd_region.map(NFC); GI = GI.merge(S6[["fbd_region", "sigungu_cd"]], on="fbd_region", validate="one_to_one")
GI.to_csv(os.path.join(HERE, "gi_inpt.csv"), index=False, encoding="utf-8-sig")
SIDO = {"서울": "Seoul", "부산": "Busan", "대구": "Daegu", "인천": "Incheon", "광주": "Gwangju", "대전": "Daejeon", "울산": "Ulsan", "세종": "Sejong", "경기": "Gyeonggi", "강원": "Gangwon", "충청북": "Chungbuk", "충청남": "Chungnam", "전라북": "Jeonbuk", "전라남": "Jeonnam", "경상북": "Gyeongbuk", "경상남": "Gyeongnam", "제주": "Jeju"}
GI["sido"] = GI.fbd_region.map(lambda r: next(v for k, v in SIDO.items() if r.startswith(k)))
for c in ("hot", "cold"):
    s = GI[GI.cls == c]; N[f"gi_{c}"] = len(s); N[f"gi_{c}_sido"] = s.sido.value_counts().to_dict(); N[f"gi_{c}_sur_med"] = round(s.SUR.median(), 2)
    N[f"gi_{c}_gun"] = int(s.fbd_region.str.endswith("군").sum()); N[f"gi_{c}_gu"] = int(s.fbd_region.str.endswith("구").sum()); N[f"gi_{c}_si"] = len(s) - N[f"gi_{c}_gun"] - N[f"gi_{c}_gu"]
# hot/cold 기술 비교: 관외 입원 비중·1인당(진료실인원 합) 재원일수·병상·요양병원(14년 평균)
D = P.groupby("fbd_region").agg(out=("vd_out", "sum"), days=("cases", "sum"), pt=("pt_in", "sum"), pto=("pt_out", "sum"), beds=(raw["beds_per_1000"], "mean"), ltc=(raw["ltc_hospitals"], "mean"), aid=(raw["medicaid1_share"], "mean"))
D["out"] = D.out / D.days; D["dpp"] = D.days / (D.pt + D.pto); D = D.join(GI.set_index("fbd_region").cls)
N["hc"] = {c: {k: round(float(D[D.cls == c][k].median()), 3) for k in ("out", "dpp", "beds", "ltc", "aid")} for c in ("hot", "other", "cold")}
# 모형
M = tab("S3_main_IRR.csv"); N["main"] = {k: get(M, VARS[k]) for k in VARS}
F = pd.read_csv(os.path.join(RS(), "S3_main_fit.csv")).iloc[0]; N["waic_main"] = float(F.WAIC); N["phi"] = float(F.phi); N["n_hot_bym"] = int(F.n_hotspot); N["n_cold_bym"] = int(F.n_coldspot)
N["resid_moran"] = float(F.resid_moran_I); N["obs_moran"] = float(F.obs_moran_I)
LK = pd.read_csv(os.path.join(RS(), "S1_likelihood.csv")); N["waic_forced"] = float(LK[LK.family == "nbinomial"].WAIC.iloc[0]); N["waic_forced_pois"] = float(LK[LK.family == "poisson"].WAIC.iloc[0])
hy = pd.read_csv(os.path.join(RS(), "S3_main_hyper.csv")); N["phi_ci"] = [round(hy.iloc[2, 1], 2), round(hy.iloc[2, 2], 2), round(hy.iloc[2, 3], 2)]
NC = tab("S3_negcontrol.csv"); N["nc"] = {c.replace("ext__", ""): get(NC, c) for c in NC["cov"]}
MV = pd.read_csv(os.path.join(RS(), "S7_multiverse_summary.csv")); MV["cov"] = MV["cov"].astype(str)
N["mv"] = {k: [round(float(MV[MV["cov"] == VARS[k]].cred_frac.iloc[0]), 3), round(float(MV[MV["cov"] == VARS[k]].sign_agree.iloc[0]), 3), int(MV[MV["cov"] == VARS[k]].n_specs.iloc[0])] for k in HYP}
for t in ("KH_typeI", "KH_typeII", "KH_typeIII", "KH_typeIV"):
    f = "S9_typeI_IRR.csv" if t == "KH_typeI" else f"S43_part_{t}.csv"
    d = tab(f); N[t] = {k: get(d, VARS[k]) for k in VARS}; N[t + "_waic"] = float(d.WAIC.iloc[0])
d = pd.read_csv(os.path.join(RS(), "S50_resid_moran_by_spec.csv")).set_index("spec"); N["waic_typeI"] = float(d.loc["typeI_interaction", "WAIC"])
N["rm_spec"] = {s: round(float(d.loc[s, "resid_moran_I"]), 2) for s in d.index}
for a in ("E1_lag1", "E2_lag2", "D1_spatial_plus", "C4_sido_year_iid", "C1_poisson_lognormal"):
    d = tab(f"S41_part_{a}.csv"); N[a] = {k: get(d, VARS[k]) for k in VARS if (d["cov"] == VARS[k]).any()}
for a in ("no_spatial", "iid_only"):
    d = tab(f"S43_part_{a}.csv"); N[a] = {k: get(d, VARS[k]) for k in VARS if (d["cov"] == VARS[k]).any()}
BW = tab("S41_part_bw_twoway.csv"); N["bw"] = {f"{k}__{s}": get(BW, f"{VARS[k]}__{s}") for k in ROB for s in ("between", "within")}
N["nco"] = {}
for a in ("HCUVC", "OUTV"):
    d = tab(f"S41_part_H1_nco_{a}.csv"); N["nco"].update({f"{a}|{k}": get(d, VARS[k]) for k in VARS})
W = tab("S4_window_IRR.csv"); N["win"] = {f"{k}|{w}": get(W[W.window == w], VARS[k]) for k in VARS for w in W.window.unique()}
RET = pd.read_csv(os.path.join(RS(), "S41_retention_by_cov.csv")); N["ret"] = {k: [int(RET[RET["cov"] == VARS[k]].kept.iloc[0]), int(RET[RET["cov"] == VARS[k]].n_specs.iloc[0])] for k in ROB}
EV = pd.read_csv(os.path.join(RS(), "S41_evalues.csv")); N["evalue"] = {k: [float(EV[EV["cov"] == VARS[k]].E_point.iloc[0]), float(EV[EV["cov"] == VARS[k]].E_limit.iloc[0])] for k in ROB}
VP = pd.read_csv(os.path.join(RS(), "S42_variance_partition.csv")).set_index("component"); N["vp_spatial"] = round(100 * VP.loc["spatial_structured", "share_of_linear_predictor_var"]); N["vp_hyp"] = round(100 * VP.loc["fixed_hypothesis", "share_of_linear_predictor_var"])
PPC = pd.read_csv(os.path.join(RS(), "S42_ppc.csv")).iloc[0]; N["ppc95"] = round(100 * PPC.coverage95, 1)
OOS = pd.read_csv(os.path.join(RS(), "S41_oos2024.csv")).iloc[0]; N["oos_cov"] = round(100 * OOS.coverage95, 1); N["oos_mape"] = round(OOS.median_abs_pct_error, 1)
RG = pd.read_csv(os.path.join(RS(), "S50_region_slopes.csv")); N["reg"] = {f"{r.covariate}|{r.region}": [r.IRR, r.lo, r.hi] for r in RG.itertuples()}; N["reg_dwaic"] = {r.covariate: r.dWAIC_vs_common for r in RG.drop_duplicates("covariate").itertuples()}
for v in ("s577", "s2", "sc"):
    d = tab("S3_main_IRR.csv", v); N[v] = {k: get(d, VARS[k]) for k in VARS if (d["cov"] == VARS[k]).any()}
N["n_hyp"] = 9; N["chance_n"] = round(9 * 0.05, 2); N["mv_n"] = 200
json.dump(N, open(os.path.join(HERE, "numbers_inpt.json"), "w"), ensure_ascii=False, indent=1, default=float)
if __name__ == "__main__": print({k: N[k] for k in ("days_total_bn", "sur_p10", "sur_p90", "gi_hot", "gi_cold", "gi_hot_sido", "gi_cold_sido", "hc", "rho80_crude", "rho80_std", "kendall_w", "rho_2011_2024", "rm_spec", "days_per_pt")})
