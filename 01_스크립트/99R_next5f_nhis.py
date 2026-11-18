#!/usr/bin/env python3
#  HTPS 고혈압 비지속 투약: 요양급여일수 240일 미만(179일 이하 + 180~239일) 진료실인원 / 4구간 합(TX_35003_A040·A069·A098·A127). 사전 고정: 주 = <240일, 민감도 = ≤179일·<360일.
#  DMPS 당뇨 비지속 투약: 같은 정의(TX_35003_A041·A070·A099·A128).
#  INPT 거주지 입원 이용: 관내 입원 + 관외 입원 입내원일수(TX_35003_A027·A056·A085·A114 + A030·A059·A088·A117), E = 시군구 성×5세 인구 × 전국 성×5세 입원 입내원일수 율(TX_35001_A047).
#  OUTI 입원 관외 유출: 관외 입원 입내원일수 / (관내+관외 입원 입내원일수), E = 분모 × 전국 연도 비율.
#  HTPS·DMPS·OUTI는 연령 분해가 원표에 없어 E = 분모 × 전국 연도 비율(간접, 연령 미보정 → 착수 때 80+ 비율 강제통제). 연도별 ΣE = Σcases.
#  키: ~/.kosis_key(내용 출력 금지). 산출: 02_패널/<TAG>_Estd3r.csv·_Estd.csv, 04_분석/<TAG>/panel_<TAG>.csv·config·graph
import os, json, time, shutil, sqlite3, unicodedata, importlib.util, urllib.request, urllib.parse
import numpy as np, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); PAN = os.path.join(ROOT, "02_패널"); AN = os.path.join(ROOT, "04_분석")
SRC = os.path.join(ROOT, "00_원천", "B_NHIS_진료"); NAT = os.path.join(ROOT, "00_원천", "NHIS_전국_질병분류_연령")
SIDO = {"서울", "인천", "경기", "강원", "대전", "세종", "충북", "충남", "부산", "대구", "울산", "경북", "경남", "광주", "전북", "전남", "제주"}
YRS = range(2011, 2025)

def load(files, c2map=None, items=("진료실인원수",), tag=""):
    fr = []
    for f in files:
        d = pd.read_csv(os.path.join(SRC, f"TX_35003_{f}.csv"), encoding="utf-8-sig", dtype=str); d = d[d.PRD_DE != "PRD_DE"]
        d["C1_NM"] = d.C1_NM.map(NFC).str.strip(); d["C1"] = d.C1.str.replace(r"^1110HJG", "11101HJG", regex=True)
        hd = d[d.C1.str.len() == 10].drop_duplicates("C1").set_index("C1").C1_NM
        d["_sido"] = d.C1.str[:10].map(hd).fillna(d.C1.map({"A01": "경기", "BB38": "충남"}))
        assert d._sido.notna().all() and set(hd) <= SIDO, (f, d[d._sido.isna()].C1.unique()[:5])
        sj = (d.C1.str.len() == 10) & (d.C1_NM == "세종"); d.loc[sj, "C1_NM"] = "세종시"
        d = d[((d.C1.str.len() != 10) | sj) & d.ITM_NM.isin(items)].copy()
        d["v"] = d.ITM_NM.map({"진료실인원수": "pt", "입내원일수": "vd"}) + ("_" + d.C2_NM.map(c2map) if c2map else "")
        assert d.v.notna().all(), d[d.v.isna()].C2_NM.unique()
        d["DT"] = pd.to_numeric(d.DT.str.replace(",", ""), errors="coerce"); fr.append(d[["PRD_DE", "_sido", "C1_NM", "v", "DT"]])
    L = pd.concat(fr); L = L[L.PRD_DE.astype(int).between(2011, 2024)]
    W = L.pivot_table(index=["PRD_DE", "_sido", "C1_NM"], columns="v", values="DT", aggfunc="sum").reset_index().rename(columns={"PRD_DE": "year", "_sido": "sido", "C1_NM": "sigungu"})
    tmpf = f"_tmp_next5f_{tag}.csv"; W.to_csv(os.path.join(PAN, tmpf), index=False, encoding="utf-8-sig")
    spec = importlib.util.spec_from_file_location("m50", os.path.join(HERE, "50_build_master_panel.py")); m50 = importlib.util.module_from_spec(spec); spec.loader.exec_module(m50)
    mk = pd.read_csv(os.path.join(PAN, "시군구_마스터키.csv"), dtype=str); mk = mk[mk.fbd_sido.notna()].drop_duplicates("key")
    log = dict(missing_files=[], level_filter={}, unmatched=[], special=[], overlap=[], sources={})
    src = dict(name=f"n5f{tag}", prefix="", files=[tmpf], sido="sido", sgg="sigungu", merge_counts=True, level=None, ratio=lambda c: False, label=tag)
    agg, meta = m50.load_source(src, set(mk.key), log); os.remove(os.path.join(PAN, tmpf))
    um = pd.concat(log["unmatched"]) if log["unmatched"] else pd.DataFrame()
    print(f"[n5f {tag}] 미결합:", um[["_sido", "_sgg", "years"]].values.tolist() if len(um) else "없음")
    agg = agg.merge(mk[["key", "fbd_region"]], on="key", how="left"); agg["fbd_region"] = agg.fbd_region.map(NFC); agg["year"] = agg.year.astype(int)
    return agg

# ---- 기준 인구(성×5세) 블록: 99R_next5b_build_E.py 앞부분(POP 생성까지) 그대로 실행 ----
s5 = open(os.path.join(HERE, "99R_next5b_build_E.py"), encoding="utf-8").read(); cut = s5.index("\n", s5.index("POP = pd.DataFrame(rows)"))
g = {"__file__": os.path.join(HERE, "99R_next5b_build_E.py"), "__name__": "x"}; exec(compile(s5[:cut], "5b_pop", "exec"), g)
POP, base, DB = g["POP"].copy(), g["base"], g["DB"]
A5 = [f"{5*i}-{5*i+4}" for i in range(17)] + ["85+"]; assert all(a in POP.columns for a in A5), POP.columns.tolist()

# ---- 전국 성×5세 입원 입내원일수(TX_35001_A047) ----
os.makedirs(NAT, exist_ok=True); fn = os.path.join(NAT, "TX_35001_A047_입원_2011_2024.csv")
if not os.path.exists(fn):
    KEY = open(os.path.expanduser("~/.kosis_key")).read().strip(); rows = []
    for y in YRS:
        q = dict(method="getList", apiKey=KEY, itmId="ALL", format="json", jsonVD="Y", prdSe="Y", startPrdDe=str(y), endPrdDe=str(y), orgId="350", tblId="TX_35001_A047", objL1="ALL", objL2="ALL")
        d = json.loads(urllib.request.urlopen("https://kosis.kr/openapi/Param/statisticsParameterData.do?" + urllib.parse.urlencode(q), timeout=300).read().decode())
        assert isinstance(d, list), d
        rows += [{k: r.get(k) for k in ("PRD_DE", "C1_NM", "C2_NM", "ITM_NM", "DT")} for r in d]; time.sleep(1)
    pd.DataFrame(rows).to_csv(fn, index=False, encoding="utf-8-sig")
N = pd.read_csv(fn, encoding="utf-8-sig", dtype=str); N = N[(N.ITM_NM == "입내원일수") & N.C2_NM.isin(["남자", "여자"])].copy()
N["DT"] = pd.to_numeric(N.DT.str.replace(",", "")); N["C1_NM"] = N.C1_NM.str.replace(" ", "")
amap = {"0세": "0-4", "1-4세": "0-4", "85세이상": "85+"}; amap.update({f"{5*i}-{5*i+4}세": f"{5*i}-{5*i+4}" for i in range(1, 17)})
N = N[N.C1_NM != "합계"]; N["a"] = N.C1_NM.map(amap); assert N.a.notna().all(), N[N.a.isna()].C1_NM.unique()
NR = N.groupby(["PRD_DE", "C2_NM", "a"]).DT.sum().reset_index(); NR["year"] = NR.PRD_DE.astype(int)
assert NR.groupby("year").size().eq(36).all() and set(NR.year) == set(YRS)

c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
bp = pd.read_sql("select * from disease_panel where tag='PERIO'", c).drop(columns=["tag"], errors="ignore"); bp["fbd_region"] = bp.fbd_region.map(NFC); bp = bp.sort_values(["fbd_region", "year"]).reset_index(drop=True)
_r = bp.fbd_region.map(bp[bp.year.isin([2020, 2024])].groupby("fbd_region").basic_livelihood_rate_raw.mean())
_bad = bp.year.isin([2021, 2022, 2023]) & ((bp.basic_livelihood_rate_raw < 0.2 * _r) | (bp.basic_livelihood_rate_raw > 5 * _r)); print("[n5f] 수급률 정정 칸", int(_bad.sum()))
bp.loc[_bad, "basic_livelihood_rate_raw"] = np.nan; bp["basic_livelihood_rate_raw"] = bp.groupby("fbd_region").basic_livelihood_rate_raw.transform(lambda s: s.interpolate(limit_area="inside"))
_s = bp.basic_livelihood_rate_raw; bp["basic_livelihood_rate"] = (_s - _s.mean()) / _s.std(ddof=0)
cfg = json.loads(c.execute("select content from model_settings where tag='PERIO' and kind='config'").fetchone()[0])
cfg["forced"] = ["care_institutions_per_100k", "urban_population_share", "older_adult_share", "sex_ratio", "fiscal_independence"]

def finish(T, P, note):
    P = P.copy(); P["E_std"] = P.E_std * P.year.map(P.groupby("year").cases.sum() / P.groupby("year").E_std.sum())
    P["E_crude"] = P.offset * P.year.map(P.groupby("year").cases.sum() / P.groupby("year").offset.sum()); P["offset"] = P.offset
    P[["year", "fbd_region", "offset", "cases", "E_std", "E_crude"]].to_csv(os.path.join(PAN, f"{T}_Estd3r.csv"), index=False, encoding="utf-8-sig")
    Q = bp.drop(columns=["cases", "E", "E_crude", "SIR", "offset"], errors="ignore").merge(P[["year", "fbd_region", "offset", "cases", "E_crude"]], on=["year", "fbd_region"], how="inner", validate="one_to_one").rename(columns={"E_crude": "E"})
    Q["cases"] = Q.cases.round().astype(np.int64); Q["SIR"] = Q.cases / Q.E
    # 분석 전 데이터 게이트: 키 유일·결측 0·음수 0·E>0·연도별 시군구 229·세종 전 연도·강제통제 결측 0
    assert not Q.duplicated(["year", "fbd_region"]).any() and Q[["cases", "E", "offset"]].notna().all().all() and (Q.cases >= 0).all() and (Q.E > 0).all()
    ny = Q.groupby("year").fbd_region.nunique(); sej = Q[Q.fbd_region == NFC("세종시세종시")].year.nunique()
    print(f"[n5f {T}] 연도별 시군구 {ny.min()}-{ny.max()}, 세종 {sej}년, 칸 {len(Q)}, 합계 {Q.cases.sum():,}, {note}")
    assert ny.min() >= 229 and sej == Q.year.nunique(), f"{T} 시군구·세종 누락"
    assert Q[[x for x in cfg["forced"] if x in Q.columns]].notna().all().all()
    D = os.path.join(AN, T); os.makedirs(os.path.join(D, "results"), exist_ok=True)
    Q.to_csv(os.path.join(D, f"panel_{T}.csv"), index=False, encoding="utf-8-sig"); P[["year", "fbd_region", "E_std"]].to_csv(os.path.join(PAN, f"{T}_Estd.csv"), index=False, encoding="utf-8-sig")
    json.dump(cfg, open(os.path.join(D, f"config_{T}.json"), "w"), ensure_ascii=False, indent=1)
    shutil.copy2(os.path.join(AN, "METS_std", "results", "nb_METS_std.graph"), os.path.join(D, "results", f"nb_{T}.graph"))

def keep229(agg, cols):
    P = base[["year", "fbd_region", "key"]].merge(agg[["year", "fbd_region"] + cols], on=["year", "fbd_region"], how="left", validate="one_to_one")
    miss = P[P[cols].isna().any(axis=1)]; print("  빠진 칸:", miss.groupby("fbd_region").year.apply(list).to_dict() if len(miss) else "없음")
    return P

BIN = {"179일 이하": "b179", "180~239일": "b239", "180-239일": "b239", "240~359일": "b359", "360일 이상": "b360",
       "239일 이하": "b239", "240~299일": "b359", "300~359일": "b359"}  # 당뇨 2011-12 구간(239일 이하·240~299·300~359): <240 경계는 같음, ≤179 민감도는 2013~만
for T, fs in [("HTPS", ["A040", "A069", "A098", "A127"]), ("DMPS", ["A041", "A070", "A099", "A128"])]:
    a = load(fs, BIN, tag=T); cols = ["pt_b179", "pt_b239", "pt_b359", "pt_b360"]
    a["pt_b179"] = a.pt_b179.fillna(0) if T == "DMPS" else a.pt_b179
    P = keep229(a, cols); P = P.dropna(subset=cols)
    den = P[cols].sum(1); P["cases"] = P.pt_b179 + P.pt_b239; P["offset"] = den; P["E_std"] = den.values  # 분모 × 전국 연도 비율(finish에서 재척도)
    nat = P.groupby("year").apply(lambda d: d.cases.sum() / d.offset.sum()).round(3).to_dict()
    sens = {k: round(float((P[v].sum(1) if isinstance(v, list) else P[v]).sum() / den.sum()), 3) for k, v in {"le179": "pt_b179", "lt360": ["pt_b179", "pt_b239", "pt_b359"]}.items()}
    finish(T, P[["year", "fbd_region", "cases", "offset", "E_std"]], f"전국 <240일 비율 {nat}, 민감도 전 기간 {sens}")
    P.to_csv(os.path.join(PAN, f"next5f_{T}_bins.csv"), index=False, encoding="utf-8-sig")

a_in = load(["A027", "A056", "A085", "A114"], None, items=("입내원일수",), tag="IN"); a_out = load(["A030", "A059", "A088", "A117"], None, items=("입내원일수",), tag="OUT")
I = keep229(a_in.rename(columns={"vd": "vd_in"}), ["vd_in"]).merge(a_out.rename(columns={"vd": "vd_out"})[["year", "fbd_region", "vd_out"]], on=["year", "fbd_region"], how="left", validate="one_to_one")
z = I.vd_in.isna() & I.vd_out.notna(); print("[n5f] 관내 입원 '-'·행 없음 = 관내 입원 기관 없음(관외 행은 있음) → 0으로 명시:", I.loc[z, ["fbd_region", "year"]].values.tolist())
I.loc[z, "vd_in"] = 0.0
I = I.dropna(subset=["vd_in", "vd_out"]); I["vd_tot"] = I.vd_in + I.vd_out
# INPT: 성×5세 간접표준화
E = np.zeros(len(I)); off = np.zeros(len(I))
for s in ["남자", "여자"]:
    X = I[["year", "key"]].merge(POP[POP.sex == s], on=["year", "key"], how="left", validate="one_to_one"); assert X[A5].notna().all().all()
    pop = X[A5].values; nr = NR[NR.C2_NM == s].pivot(index="year", columns="a", values="DT")[A5]
    npop = POP[POP.sex == s].merge(base[["year", "key"]], on=["year", "key"]).groupby("year")[A5].sum()
    E += (pop * (nr / npop).loc[I.year.values].values).sum(1); off += pop.sum(1)
I["E_std"] = E; I["offset"] = off; I["cases"] = I.vd_tot
finish("INPT", I[["year", "fbd_region", "cases", "offset", "E_std"]], "거주지 입원 입내원일수, 성×5세 간접표준화")
J = I[["year", "fbd_region"]].copy(); J["cases"] = I.vd_out; J["offset"] = I.vd_tot; J["E_std"] = I.vd_tot
finish("OUTI", J, f"관외 입원 비율 전국 {(I.groupby('year').vd_out.sum() / I.groupby('year').vd_tot.sum()).round(3).iloc[[0, -1]].tolist()}")
I.to_csv(os.path.join(PAN, "next5f_INPT_OUTI_counts.csv"), index=False, encoding="utf-8-sig")
