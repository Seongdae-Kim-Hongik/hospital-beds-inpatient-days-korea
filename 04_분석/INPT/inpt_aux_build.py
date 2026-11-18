#!/usr/bin/env python3
#  99R_next5f_nhis.load()와 같은 결합(시도 머리행 + 시군구 이름 → 50.load_source → 마스터키 → fbd_region, 세종 머리행 살림). 공유 스크립트 수정 없음.
#  산출: 02_패널/INPT_aux.csv (pt_in, pt_out, vd_in, vd_out, cost_in, cost_out). 진료실인원은 관내·관외 모두 이용한 사람이 두 번 세어질 수 있음(합 = 상한).
import os, importlib.util, unicodedata, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); HERE = os.path.join(ROOT, "01_스크립트"); PAN = os.path.join(ROOT, "02_패널"); SRC = os.path.join(ROOT, "00_원천", "B_NHIS_진료")
SIDO = {"서울", "인천", "경기", "강원", "대전", "세종", "충북", "충남", "부산", "대구", "울산", "경북", "경남", "광주", "전북", "전남", "제주"}
spec = importlib.util.spec_from_file_location("m50", os.path.join(HERE, "50_build_master_panel.py")); m50 = importlib.util.module_from_spec(spec); spec.loader.exec_module(m50)
mk = pd.read_csv(os.path.join(PAN, "시군구_마스터키.csv"), dtype=str); mk = mk[mk.fbd_sido.notna()].drop_duplicates("key")
IT = {"진료실인원수": "pt", "입내원일수": "vd", "진료비": "cost"}
def load(files, tag):
    fr = []
    for f in files:
        d = pd.read_csv(os.path.join(SRC, f"TX_35003_{f}.csv"), encoding="utf-8-sig", dtype=str); d = d[d.PRD_DE != "PRD_DE"]
        d["C1_NM"] = d.C1_NM.map(NFC).str.strip(); d["C1"] = d.C1.str.replace(r"^1110HJG", "11101HJG", regex=True)
        hd = d[d.C1.str.len() == 10].drop_duplicates("C1").set_index("C1").C1_NM
        d["_sido"] = d.C1.str[:10].map(hd).fillna(d.C1.map({"A01": "경기", "BB38": "충남"})); assert d._sido.notna().all() and set(hd) <= SIDO
        sj = (d.C1.str.len() == 10) & (d.C1_NM == "세종"); d.loc[sj, "C1_NM"] = "세종시"
        d = d[((d.C1.str.len() != 10) | sj) & d.ITM_NM.isin(IT)].copy(); d["v"] = d.ITM_NM.map(IT) + "_" + tag
        d["DT"] = pd.to_numeric(d.DT.str.replace(",", ""), errors="coerce"); fr.append(d[["PRD_DE", "_sido", "C1_NM", "v", "DT"]])
    L = pd.concat(fr); L = L[L.PRD_DE.astype(int).between(2011, 2024)]
    W = L.pivot_table(index=["PRD_DE", "_sido", "C1_NM"], columns="v", values="DT", aggfunc="sum").reset_index().rename(columns={"PRD_DE": "year", "_sido": "sido", "C1_NM": "sigungu"})
    tmpf = f"_tmp_inpt_aux_{tag}.csv"; W.to_csv(os.path.join(PAN, tmpf), index=False, encoding="utf-8-sig")
    log = dict(missing_files=[], level_filter={}, unmatched=[], special=[], overlap=[], sources={})
    src = dict(name=f"ia{tag}", prefix="", files=[tmpf], sido="sido", sgg="sigungu", merge_counts=True, level=None, ratio=lambda c: False, label=tag)
    agg, meta = m50.load_source(src, set(mk.key), log); os.remove(os.path.join(PAN, tmpf))
    agg = agg.merge(mk[["key", "fbd_region"]], on="key", how="left"); agg["fbd_region"] = agg.fbd_region.map(NFC); agg["year"] = agg.year.astype(int)
    return agg[["year", "fbd_region"] + [c for c in agg.columns if c.endswith("_" + tag)]]
A = load(["A027", "A056", "A085", "A114"], "in").merge(load(["A030", "A059", "A088", "A117"], "out"), on=["year", "fbd_region"], how="outer")
B = pd.read_csv(os.path.join(PAN, "next5f_INPT_OUTI_counts.csv"))[["year", "fbd_region", "vd_in", "vd_out", "offset"]].rename(columns={"vd_in": "chk_in", "vd_out": "chk_out", "offset": "pop"})
X = B.merge(A, on=["year", "fbd_region"], how="left", validate="one_to_one")
z = X.vd_in.isna(); X.loc[z, ["pt_in", "vd_in", "cost_in"]] = 0.0
print("관내 0 명시", int(z.sum()), "| 입내원일수 대조 최대 차", float((X.vd_in - X.chk_in).abs().max()), float((X.vd_out - X.chk_out).abs().max()))
print("결측", X.isna().sum()[X.isna().sum() > 0].to_dict())
X.drop(columns=["chk_in", "chk_out"]).to_csv(os.path.join(PAN, "INPT_aux.csv"), index=False, encoding="utf-8-sig"); print(len(X), "행 저장")
