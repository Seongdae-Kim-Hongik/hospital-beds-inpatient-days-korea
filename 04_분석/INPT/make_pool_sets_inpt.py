#!/usr/bin/env python3
import os, json, shutil
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); PAN = os.path.join(ROOT, "02_패널"); AN = os.path.join(ROOT, "04_분석")
POOL = "EXT_canonical_pool_INPT_261115.csv"
D = pd.read_csv(os.path.join(PAN, "EXT_canonical_pool_DIGX_261114.csv")); D = D[D.year.between(2011, 2024)]
H = pd.read_csv(os.path.join(PAN, "EXT_canonical_pool_HCUV_261113.csv"))[["year", "fbd_region", "beds_per_1000", "older_single_household_share", "cpr_awareness_rate", "road_pavement_rate", "clinics_per_100k"]]
I = pd.read_csv(os.path.join(PAN, "INPT_Estd3r.csv")).rename(columns={"cases": "inpt_days"})[["year", "fbd_region", "inpt_days"]]
P = D.drop(columns=["digx_deaths"]).merge(H, on=["year", "fbd_region"], how="left", validate="one_to_one").merge(I, on=["year", "fbd_region"], how="left", validate="one_to_one")
assert len(P) == 229 * 14 and P.notna().all().all(), P.isna().sum()[P.isna().sum() > 0]
# 수급률 양쪽 규칙 재확인(2021-23 값이 2020·2024 평균의 20% 미만 또는 5배 초과면 결측 후 보간)
r = P.fbd_region.map(P[P.year.isin([2020, 2024])].groupby("fbd_region").basic_livelihood_rate.mean())
bad = P.year.isin([2021, 2022, 2023]) & ((P.basic_livelihood_rate < 0.2 * r) | (P.basic_livelihood_rate > 5 * r)); print("수급률 규칙 위반 칸(이미 정정이면 0):", int(bad.sum()))
P.to_csv(os.path.join(PAN, POOL), index=False, encoding="utf-8-sig")
# 비교 결과 패널
for t2, src in [("HCUVC", "HCUV"), ("OUTV", "HCUVO")]:
    S = pd.read_csv(os.path.join(AN, src, f"panel_{src}_std3.csv"), usecols=["year", "fbd_region", "cases", "E"])
    os.makedirs(os.path.join(AN, t2), exist_ok=True); S[["year", "fbd_region", "cases"]].to_csv(os.path.join(AN, t2, f"panel_{t2}.csv"), index=False)
    S.rename(columns={"E": "E_std"})[["year", "fbd_region", "E_std"]].to_csv(os.path.join(PAN, f"{t2}_Estd.csv"), index=False)
    open(os.path.join(AN, t2, "README.md"), "w").write(f"# {t2}: 56호 INPT 비교 결과 전용 복사본(2026-11-15). 원본 = 04_분석/{src}/panel_{src}_std3.csv cases·E(43호, 성×10세 간접표준화). 분석 대상 아님.\n")
    print(t2, len(S), S.year.min(), S.year.max())

FORCED = ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"]
NEG = ["cpr_awareness_rate", "road_pavement_rate", "fires_per_10000"]
SENS = ["living_alone_elderly", "genhosp_per100k", "tertiary_educated_share", "clinics_per_100k"]
HYP = ["walking_rate", "moderate_pa_rate", "public_sport_fac_per100k", "village_sport_fac_per100k",
       "basic_livelihood_rate", "medicaid1_share", "chewing_discomfort_65", "beds_per_1000", "ltc_hospitals_per100k_65"]
X = lambda L: ["ext__" + v for v in L]
EXPECT = {
 "walking_rate": "- (걷기 실천율: 신체활동 → 만성질환·낙상·허약 감소, 노년 입원 위험 감소; 체육 경로 주 가설)",
 "moderate_pa_rate": "- (중강도 이상 신체활동 실천율: 입원·재입원 위험 감소 코호트 근거)",
 "public_sport_fac_per100k": "- (공공체육시설 인구 10만 명당: 지역 신체활동 기회 구조; 체육 경로 주 가설)",
 "village_sport_fac_per100k": "- (마을체육시설 인구 10만 명당: 농촌 생활권 신체활동 기회)",
 "basic_livelihood_rate": "+ (기초생활 수급률, 2021-23 양쪽 규칙 정정: 박탈·만성질환 부담 → 입원 필요 증가; 선별 단순 ρ 0.55)",
 "medicaid1_share": "+ (의료급여 1종 진료실인원 인구 대비: 본인부담 거의 없음·장애·정신질환 동반 → 장기 입원; 선별 단순 ρ 0.49)",
 "chewing_discomfort_65": "+ (65세 이상 저작 불편 호소율: 구강 기능 저하·영양 결핍·허약 → 노년 입원; 선별 단순 ρ 0.41)",
 "beds_per_1000": "+ (병상 인구 천 명당: 공급 유인 수요 — 병상이 많으면 입원이 늘고 재원이 길어진다(Roemer); 역인과 위험 → 시차 민감도)",
 "ltc_hospitals_per100k_65": "+ (요양병원 65세 이상 10만 명당: 사회적 입원·장기 재원 공급; 역인과 위험 → 시차 민감도)",
}
SETS = {"S1_narrative_full": X(HYP),
        "S2_core": X(["walking_rate", "public_sport_fac_per100k", "basic_livelihood_rate", "medicaid1_share", "beds_per_1000", "ltc_hospitals_per100k_65"]),
        "S3_physical_activity": X(["walking_rate", "moderate_pa_rate", "public_sport_fac_per100k", "village_sport_fac_per100k"]),
        "S4_need": X(["basic_livelihood_rate", "medicaid1_share", "chewing_discomfort_65"]),
        "S5_supply": X(["beds_per_1000", "ltc_hospitals_per100k_65"]),
        "S6_need_supply": X(["basic_livelihood_rate", "medicaid1_share", "chewing_discomfort_65", "beds_per_1000", "ltc_hospitals_per100k_65"])}
pov = [{"year": 2023, "fbd_region": "경상남도창원시", "population": 1009038, "source": "KOSIS DT_1YL20651E 2023 통합창원시 계(유방암 11/4 population_final_audit)"}]
allv = ["inpt_days"] + FORCED + NEG + SENS + HYP
base = {
 "tag": "INPT", "outcome_column": "ext__inpt_days",
 "outcome_label_en": "Inpatient days of residents (inpatient days in hospitals inside plus outside the district of residence; NHIS regional health care utilisation statistics, annual)",
 "disease_en": "Resident inpatient care use (inpatient days)", "disease_ko": "거주지 입원 이용(관내+관외 입원 입내원일수)",
 "forced": X(FORCED), "negative_controls": X(NEG),
 "offset_E_column": "E_std", "offset_E_file": "INPT_Estd3r.csv",
 "offset_E_label": "sex-and-age-standardised expected inpatient days, 2 sexes x 18 five-year bands to 85+ (national inpatient-day rates, NHIS TX_35001_A047), 2011-2024",
 "graph": "593-edge contact graph, ST_GRAPH=04_분석/INPT/graph_593.graph",
 "population_override": pov, "sensitivity_only_extra": X(SENS),
 "version": "std3 physical-activity pathway (resident inpatient days: physical activity and sport facilities, need (deprivation, Medical Aid, oral function), supply-induced demand (beds, long-term care hospitals)), 2011-2024",
 "sets": SETS, "transform": {c: "none" for c in X(FORCED + NEG + SENS + HYP)},
 "expected_direction": {X([k])[0]: v for k, v in EXPECT.items()},
 "rules": {"likelihood": "forced-only 모형 WAIC 낮은 쪽(Poisson/NB)", "set_choice": "WAIC 최소, 4 이내면 변수 적은 세트", "credible": "95% CrI 1 제외", "vif_drop": 10,
           "multiverse_specs": 200, "main_model_note": "주모형 = S1_narrative_full(가설 9 + 강제통제 5). 세트를 다시 바꾸지 않음. VIF>10 유지·보고. 공급 변수(병상·요양병원)는 역인과 위험 → 88g 시차(lag1·lag2) 민감도로 판정.",
           "years": [2011, 2024], "windows": {"W1_2011-15": [2011, 2015], "W2_2016-19": [2016, 2019], "W3_2020-24": [2020, 2024]}, "covid_post_from": 2020},
 "note": "Outcome: inpatient days of residents (NHIS), 229 districts, 2011-2024; expected counts standardised for sex and 5-year age group.",
 "extra_columns": {"ext__" + v: [POOL, v] for v in allv},
}
def dump(suf, **kw):
    d = json.loads(json.dumps(base)); d.update(kw)
    json.dump(d, open(os.path.join(HERE, f"sets_INPT_{suf}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
dump("std3")
dump("s577", sens_note="민감도: 그래프만 queen 577")
dump("s2", sens_note="민감도: 80세 이상 비율 강제통제 없음", forced=X(FORCED[:4]))
dump("sc", sens_note="민감도: 비표준화(조) E(인구 × 전국 연도 입원 율)", offset_E_column="E_crude", offset_E_label="crude E (population x national annual inpatient-day rate)")
shutil.copy2(os.path.join(AN, "NIHD", "graph_593.graph"), os.path.join(HERE, "graph_593.graph"))
print("pool·sets 4종·graph_593 저장")
