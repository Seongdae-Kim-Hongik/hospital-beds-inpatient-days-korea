import os, glob, json, re
import pandas as pd
from build_ms_inpt import TX, put_table, OUT, N, to_pdf, TITLE
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.abspath(os.path.join(HERE, "..", "..")); RS = os.path.join(B, "results_std3")
VARS = {"walking_rate": "ext__walking_rate", "moderate_pa_rate": "moderate_pa_rate", "public_sport_fac_per100k": "ext__public_sport_fac_per100k", "village_sport_fac_per100k": "ext__village_sport_fac_per100k",
        "basic_livelihood_rate": "basic_livelihood_rate", "medicaid1_share": "ext__medicaid1_share", "chewing_discomfort_65": "ext__chewing_discomfort_65", "beds_per_1000": "ext__beds_per_1000",
        "ltc_hospitals": "ltc_hospitals_per_100k_65", "urban_population_share": "urban_population_share", "physicians_per_1000": "physicians_per_1000", "sex_ratio": "sex_ratio",
        "fiscal_independence": "fiscal_independence", "pop80_share": "pop80_share"}
ROB = [("beds_per_1000", "Beds"), ("ltc_hospitals", "LTC hospitals"), ("medicaid1_share", "Medical Aid type 1"), ("moderate_pa_rate", "Moderate activity")]
f3 = lambda r: f"{r[0]:.3f} ({r[1]:.3f}-{r[2]:.3f})"
def row(d, c):
    x = d[d["cov"].astype(str) == c]
    return f3([float(x.IRR.iloc[0]), float(x.lo.iloc[0]), float(x.hi.iloc[0])]) if len(x) else "–"

T1 = [("Walking rate", "Physical activity", "Adults walking ≥30 min on ≥5 days a week, age-standardized, %", "Community Health Survey", "−"),
      ("Moderate-or-higher physical activity", "Physical activity", "Adults meeting moderate or vigorous activity criteria, age-standardized, %", "Community Health Survey", "−"),
      ("Public sports facilities", "Physical activity", "Public sports facilities per 100,000 residents", "National public sports facility register", "−"),
      ("Village sports facilities", "Physical activity", "Village (neighborhood) sports facilities per 100,000 residents", "National public sports facility register", "−"),
      ("Public assistance recipients", "Need", "Basic livelihood security recipients per 100 residents; 2021-2023 values in 10 cities below 20% or above 5 times the 2020/2024 mean set to missing and interpolated", "Ministry of Health and Welfare via KOSIS", "+"),
      ("Medical Aid type 1", "Need", "Medical Aid type 1 beneficiaries treated per 100 residents", "National Health Insurance Service", "+"),
      ("Chewing discomfort", "Need", "Adults aged 65+ reporting chewing discomfort, %", "Community Health Survey", "+"),
      ("Hospital beds", "Supply", "Hospital beds per 1,000 residents", "KOSIS e-local indicators", "+"),
      ("LTC hospitals", "Supply", "Long-term care hospitals per 100,000 residents aged 65+", "Health Insurance Review and Assessment Service via KOSIS", "+"),
      ("Urban population share", "Fixed adjustment", "Residents in urban zones, % of population", "Ministry of Land via KOSIS", "–"),
      ("Physicians", "Fixed adjustment", "Physicians working in medical institutions per 1,000 residents", "KOSIS e-local indicators", "–"),
      ("Sex ratio", "Fixed adjustment", "Men per 100 women", "Resident registration", "–"),
      ("Fiscal autonomy", "Fixed adjustment", "Fiscal autonomy ratio of the local government, %", "Ministry of the Interior and Safety via KOSIS", "–"),
      ("Aged 80 years or older", "Fixed adjustment", "Residents aged 80+, % of population", "Resident registration", "–"),
      ("CPR awareness", "Negative control", "Adults aware of cardiopulmonary resuscitation, %", "Community Health Survey", "none"),
      ("Road paving", "Negative control", "Paved share of roads, %", "KOSIS e-local indicators", "none"),
      ("Fires", "Negative control", "Fires per 10,000 residents", "National Fire Agency via KOSIS", "none")]
def t1():
    rows = [[a, b, c.replace("2021-2023", "2021\u20132023").replace("2020/2024", "2020 and 2024"), d.replace("e-local", "e\u2011local"), e] for a, b, c, d, e in T1]
    return ("Appendix Table 1. District Characteristics: Definitions, Sources, and Expected Direction", ["Characteristic", "Group", "Definition", "Source", "Expected"], rows,
            "Survey indicators were filled within districts for years without a survey by linear interpolation. All characteristics were standardized to 1 SD of district-years before modeling. KOSIS, Korean Statistical Information Service; LTC, long-term care.")
def t2():
    rows = [["Panel", "3,206 district-years = 229 districts × 14 years (2011-2024); unique keys; no missing outcome, expected count, or covariate"],
            ["Linkage", "District administrative codes; general districts within cities aggregated; Sejong retained from the province-level row"],
            ["Zero inpatient days inside district", "44 district-years in 5 districts without an inpatient facility (37 reported as 0; 7 blank cells set to 0); inpatient days outside the district present in all"],
            ["Population", "Sex and 5-year age group; 2023 Changwon corrected to 1,009,038"],
            ["Expected counts", "Indirect standardization, 2 sexes × 18 age groups; annual national rescaling (observed/expected = 1.0000 every year)"],
            ["National vs district totals", "National rate table summed to 0.82-0.85 of district totals (ratio 1.176-1.215); sensitivity with unstandardized expected days"],
            ["Standardized ratio", f"District-year range 0.49-3.24; 14-year district range {N['sur_min']:.2f}-{N['sur_max']:.2f}"],
            ["Comparison outcomes", "Total and outpatient visit-days of residents (sex- and age-standardized; outpatient 3,162 district-years with available data)"]]
    rows = [[a, re.sub(r"(\d)-(\d)", "\\1\u2013\\2", b)] for a, b in rows]
    return ("Appendix Table 2. Data Checks Before Modeling", ["Check", "Result"], rows, "")
def t3():
    rows = []
    for f in sorted(glob.glob(os.path.join(RS, "S41_part_*.csv"))):
        a = os.path.basename(f)[9:-4]
        if a.startswith(("H1_nco", "bw_")): continue
        d = pd.read_csv(f); note = str(d.note.iloc[0]) if "note" in d else a
        rows.append([note if not a.startswith(("F1", "F2")) else a.replace("F1_drop_sido_", "Without province ").replace("F2_drop_year_", "Without year ")] + [row(d, VARS[k]) for k, _ in ROB])
    for v, lab in (("s577", "Queen contiguity graph (577 pairs)"), ("s2", "Without the 80-and-over adjustment"), ("sc", "Unstandardized expected days")):
        d = pd.read_csv(os.path.join(B, f"results_{v}", "S3_main_IRR.csv")); rows.append([lab] + [row(d, VARS[k]) for k, _ in ROB])
    return ("Appendix Table 3. Alternative Specifications: Rate Ratios per 1 SD (95% CrI)", ["Specification"] + [l for _, l in ROB], rows,
            "Each row changes one element of the principal model. Province codes follow the Statistics Korea classification. LTC, long-term care.")
def t4():
    rows = []
    for lab, f in (("Principal model", "S3_main_IRR.csv"), ("Knorr-Held type I", "S9_typeI_IRR.csv"), ("Knorr-Held type II", "S43_part_KH_typeII.csv"), ("Knorr-Held type III", "S43_part_KH_typeIII.csv"),
                   ("Knorr-Held type IV", "S43_part_KH_typeIV.csv"), ("ICAR district effect", "S43_part_icar_besag.csv"), ("Independent district effect only", "S43_part_iid_only.csv"), ("No district effect", "S43_part_no_spatial.csv"),
                   ("k-nearest neighbors (k = 3)", "S43_part_knn3.csv"), ("k-nearest neighbors (k = 5)", "S43_part_knn5.csv"), ("Relaxed priors A", "S43_part_pc_relaxA.csv"), ("Relaxed priors B", "S43_part_pc_relaxB.csv")):
        d = pd.read_csv(os.path.join(RS, f)); w = d.WAIC.iloc[0] if "WAIC" in d else N["waic_main"]
        rows.append([lab, f"{float(w):,.1f}"] + [row(d, VARS[k]) for k, _ in ROB])
    rows.append(["Between-district component", "–"] + [f3(N["bw"][k + "__between"]) for k, _ in ROB])
    rows.append(["Within-district component", "–"] + [f3(N["bw"][k + "__within"]) for k, _ in ROB])
    return ("Appendix Table 4. Space-Time Interaction, District Effects, and Decomposition: Rate Ratios per 1 SD (95% CrI)", ["Model", "WAIC"] + [l for _, l in ROB], rows,
            "Types II and IV allow district-specific trends. The decomposition entered the district mean and the two-way-centered within-district deviation of each characteristic together. WAIC, widely applicable information criterion.")
def t5():
    W = pd.read_csv(os.path.join(RS, "S4_window_IRR.csv")); rows = []
    lab = {"walking_rate": "Walking rate", "moderate_pa_rate": "Moderate-or-higher physical activity", "public_sport_fac_per100k": "Public sports facilities", "village_sport_fac_per100k": "Village sports facilities",
           "basic_livelihood_rate": "Public assistance recipients", "medicaid1_share": "Medical Aid type 1", "chewing_discomfort_65": "Chewing discomfort", "beds_per_1000": "Hospital beds", "ltc_hospitals": "LTC hospitals",
           "urban_population_share": "Urban population share", "physicians_per_1000": "Physicians", "sex_ratio": "Sex ratio", "fiscal_independence": "Fiscal autonomy", "pop80_share": "Aged 80+"}
    for k, c in VARS.items(): rows.append([lab[k]] + [row(W[W.window == w], c) for w in ("W1_2011-15", "W2_2016-19", "W3_2020-24")])
    return ("Appendix Table 5. Principal Model by Calendar Period: Rate Ratios per 1 SD (95% CrI)", ["Characteristic", "2011-2015", "2016-2019", "2020-2024"], rows, "LTC, long-term care.")
def t6():
    R = [("Capital", "Capital"), ("Chungcheong", "Chungcheong"), ("Honam", "Honam"), ("Yeongnam", "Yeongnam"), ("Gangwon_Jeju", "Gangwon and Jeju")]
    rows = [[lab] + [f3(N["reg"][f"{VARS[k]}|{r}"]) for k, _ in ROB] for r, lab in R]
    rows.append(["\u0394WAIC vs common slope"] + [f"{N['reg_dwaic'][VARS[k]]:.1f}" for k, _ in ROB])
    return ("Appendix Table 6. Region-Specific Slopes: Rate Ratios per 1 SD (95% CrI)", ["Region"] + [l for _, l in ROB], rows,
            "One model per characteristic, with region-specific slopes for that characteristic and common slopes for the others. \u0394WAIC, WAIC of the region-specific model minus that of the common-slope model. LTC, long-term care.")
def t7():
    rows = [[l, f3(N["main"][k]), f3(N["nco"][f"HCUVC|{k}"]), f3(N["nco"][f"OUTV|{k}"]), f"{N['evalue'][k][0]:.2f} ({N['evalue'][k][1]:.2f})"] for k, l in ROB]
    for k, l in (("cpr_awareness_rate", "CPR awareness (negative control)"), ("road_pavement_rate", "Road paving (negative control)"), ("fires_per_10000", "Fires (negative control)")):
        rows.append([l, f3(N["nc"][k]), "–", "–", "–"])
    return ("Appendix Table 7. Comparison Outcomes, Negative-Control Exposures, and E-Values", ["Characteristic", "Inpatient days\n(principal)", "Total visit-days", "Outpatient visit-days", "E-value (limit)"], rows,
            "Comparison outcomes were refitted with the principal model; expected counts were standardized for sex and 10-year age group. E-value: minimum strength of association, on the risk ratio scale, that an unmeasured confounder would need with both exposure and outcome to explain away the point estimate (limit: the CrI bound nearer 1). CPR, cardiopulmonary resuscitation; LTC, long-term care.")

if __name__ == "__main__":
    J = TX(cite="bracket"); J.para(f"<b>Appendix</b>"); J.para(TITLE)
    for i, t in enumerate((t1(), t2(), t3(), t4(), t5(), t6(), t7())):
        J.page_break(); put_table(J, t, fs=8)
    J.doc_title = "Appendix"; p = os.path.join(OUT, "Appendix.docx"); J.save(p); to_pdf(p); print("appendix ok")
