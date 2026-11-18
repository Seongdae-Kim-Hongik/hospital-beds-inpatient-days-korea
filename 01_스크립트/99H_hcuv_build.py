#!/usr/bin/env python3
#  분자 = 02_패널/hcuv_counts_fix_261113.csv(KOSIS TX_35003 연령별 진료현황, 남·여 × 10세 9구간 입내원일수 합; 99R_next5c_hcu_counts.py)
#  E_std  = Σ_성 Σ_연령(9) 시군구 인구 × 같은 해 전국 성·연령 율, 연도별 ΣE = Σ관측 (간접 표준화, 주 offset)
#  E_age  = 성 미구분 연령(9)만 표준화 (민감도 sage)
#  인구 = 99R_next5b_build_E.py 인구 블록(창원 2023 = 1,009,038 정정 포함)
#  공변량 풀 = 기준 SQLite disease_panel(tag PERIO) *_raw 열, 기초생활수급률은 2021-23 양쪽 규칙(<20% 또는 >5배 → 결측 → 지역 내 선형 보간)
#  산출: 02_패널/HCUV_Estd2.csv, 02_패널/EXT_canonical_pool_HCUV_261113.csv
import os, sqlite3, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); PAN = os.path.join(ROOT, "02_패널")
src = open(os.path.join(HERE, "99R_next5b_build_E.py"), encoding="utf-8").read(); cut = src.index("\n", src.index("POP = pd.DataFrame(rows)"))
g = {"__file__": os.path.join(HERE, "99R_next5b_build_E.py"), "__name__": "x"}; exec(compile(src[:cut], "5b_pop", "exec"), g)
POP, NFC, base, DB = g["POP"].copy(), g["NFC"], g["base"], g["DB"]
A10 = ["a0", "a10", "a20", "a30", "a40", "a50", "a60", "a70", "a80"]
for i, a in enumerate(A10[:-1]): lo = 10 * i; POP[a] = POP[f"{lo}-{lo+4}"] + POP[f"{lo+5}-{lo+9}"]
POP["a80"] = POP["80-84"] + POP["85+"]
H = pd.read_csv(os.path.join(PAN, "hcuv_counts_fix_261113.csv"), encoding="utf-8-sig"); H["fbd_region"] = H.fbd_region.map(NFC)
P = base.merge(H, on=["year", "fbd_region"], how="inner", validate="one_to_one").reset_index(drop=True)
X = {s: P[["year", "key"]].merge(POP[POP.sex == s], on=["year", "key"], how="left", validate="one_to_one") for s in ["남자", "여자"]}
for s in X: assert X[s][A10].notna().all().all()
yrs = P.year.values; E = np.zeros(len(P)); P["cases"] = 0.0; numT = np.zeros((len(P), 9)); popT = np.zeros((len(P), 9))
for sx, s in [("m", "남자"), ("f", "여자")]:
    num = P[[f"vd_{sx}_{a}" for a in A10]].values.astype(float); pop = X[s][A10].values.astype(float)
    rate = pd.DataFrame(num, columns=A10).groupby(yrs).sum() / pd.DataFrame(pop, columns=A10).groupby(yrs).sum()
    E += (pop * rate.loc[yrs].values).sum(1); P["cases"] += num.sum(1); numT += num; popT += pop
rateT = pd.DataFrame(numT, columns=A10).groupby(yrs).sum() / pd.DataFrame(popT, columns=A10).groupby(yrs).sum()
Ea = (popT * rateT.loc[yrs].values).sum(1)
tot = P.groupby("year").cases.transform("sum").values
P["E_std"] = E * tot / pd.Series(E).groupby(yrs).transform("sum").values
P["E_age"] = Ea * tot / pd.Series(Ea).groupby(yrs).transform("sum").values
P["population_E"] = popT.sum(1)
if "population" in P.columns: print(f"[99H] 인구(성×9구간 합) / 마스터 인구 비 중앙 {np.median(P.population_E / P.population):.4f}, 최소 {np.min(P.population_E / P.population):.4f}, 최대 {np.max(P.population_E / P.population):.4f}")
P["pop80_share_raw"] = (X["남자"].a80.values + X["여자"].a80.values) / P.population_E * 100
P["cases"] = P.cases.round().astype(np.int64)
P["visits_per_capita"] = P.cases / P.population_E
print("[99H] 행", len(P), "시군구", P.fbd_region.nunique(), "연도별:", P.groupby("year").fbd_region.nunique().to_dict())
print("[99H] 연도별 1인당 입내원일수:", (P.groupby("year").cases.sum() / P.groupby("year").population_E.sum()).round(2).to_dict())
sir = P.cases / P.E_std; lv = sir.groupby(P.fbd_region).mean()
print(f"[99H] SIR(E_std) 14년 평균 P10 {lv.quantile(.1):.3f} P90 {lv.quantile(.9):.3f} P90/P10 {lv.quantile(.9)/lv.quantile(.1):.3f}; E_std/E_age 비 중앙 {np.median(P.E_std/P.E_age):.4f}")
from scipy.stats import spearmanr
print(f"[99H] SIR–80+ Spearman crude {spearmanr(P.cases/(P.population_E*tot/P.groupby('year').population_E.transform('sum')), P.pop80_share_raw).correlation:.3f}, std {spearmanr(sir, P.pop80_share_raw).correlation:.3f}")
P[["year", "fbd_region", "cases", "population_E", "E_std", "E_age", "pop80_share_raw", "visits_per_capita"]].to_csv(os.path.join(PAN, "HCUV_Estd2.csv"), index=False, encoding="utf-8-sig")
# ── 공변량 풀(기준 SQLite) ──
c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
COLS = ["basic_livelihood_rate_raw", "medical_aid1_patients_per_100k_raw", "older_single_household_share_raw", "good_self_rated_health_rate_raw",
        "screening_suspected_diabetes_share_raw", "screening_suspected_hypertension_share_raw", "current_smoking_rate_raw", "clinics_per_100k_raw", "beds_per_1000_raw",
        "ltc_hospitals_per_100k_65_raw", "general_hospitals_per_100k_raw", "walking_practice_rate_raw", "moderate_pa_rate_raw", "public_sports_facilities_per_100k_raw",
        "outside_care_share_raw", "public_health_centre_use_rate_raw", "tertiary_educated_share_raw", "cpr_awareness_rate_raw", "road_pavement_rate_raw", "fires_per_10000_raw"]
# 열마다 비결측이 가장 많은 태그에서 가져옴(태그 간 같은 칸 값 일치 확인). 수급률은 PERIO(창원 부풀림 포함 원값 → 양쪽 규칙 정정)
ALL = pd.read_sql("select tag, year, fbd_region, " + ", ".join(COLS) + " from disease_panel", c); ALL["fbd_region"] = ALL.fbd_region.map(NFC)
bp = ALL[ALL.tag == "PERIO"][["year", "fbd_region"]].copy()
for k in COLS:
    if k == "basic_livelihood_rate_raw": t = "PERIO"
    else: t = ALL.groupby("tag")[k].apply(lambda s: s.notna().sum()).idxmax()
    v = ALL[ALL.tag == t][["year", "fbd_region", k]]; bp = bp.merge(v, on=["year", "fbd_region"], how="left", validate="one_to_one")
    W = ALL[ALL[k].notna()].pivot_table(index=["year", "fbd_region"], columns="tag", values=k); dif = (W.max(1) - W.min(1)).abs()
    print(f"[99H] {k}: 태그 {t}, 비결측 {int(v[k].notna().sum())}, 태그 간 최대 차 {dif.max():.4g} (차>1e-6 칸 {int((dif > 1e-6).sum())})")
bp = bp.sort_values(["fbd_region", "year"]).reset_index(drop=True)
_r = bp.fbd_region.map(bp[bp.year.isin([2020, 2024])].groupby("fbd_region").basic_livelihood_rate_raw.mean())
_bad = bp.year.isin([2021, 2022, 2023]) & ((bp.basic_livelihood_rate_raw < 0.2 * _r) | (bp.basic_livelihood_rate_raw > 5 * _r))
print("[99H] 수급률 정정 칸", int(_bad.sum()), sorted(bp.loc[_bad, "fbd_region"].unique()))
bp.loc[_bad, "basic_livelihood_rate_raw"] = np.nan
bp["basic_livelihood_rate_raw"] = bp.groupby("fbd_region").basic_livelihood_rate_raw.transform(lambda s: s.interpolate(limit_area="inside"))
cw = bp[(bp.fbd_region.str.contains("창원")) & bp.year.between(2020, 2024)][["year", "fbd_region", "basic_livelihood_rate_raw"]]; print("[99H] 창원 수급률 2020-24:", cw.basic_livelihood_rate_raw.round(2).tolist())
O = bp.rename(columns={k: k[:-4] for k in COLS}); O = O[O.year.between(2011, 2024)]
print("[99H] 풀 결측 칸:", {k: int(v) for k, v in O.isna().sum().items() if v})
O.to_csv(os.path.join(PAN, "EXT_canonical_pool_HCUV_261113.csv"), index=False, encoding="utf-8-sig")
