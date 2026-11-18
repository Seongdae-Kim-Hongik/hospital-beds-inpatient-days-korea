import re
from docx.shared import Pt
import content_inpt as C
N = C.N; th = C.th; tc = C.tc
COVLAB = [("Physical activity", [("walking_rate", "Walking rate, %"), ("moderate_pa_rate", "Moderate-or-higher physical activity, %"), ("public_sport_fac_per100k", "Public sports facilities per 100,000"), ("village_sport_fac_per100k", "Village sports facilities per 100,000")]),
          ("Need", [("basic_livelihood_rate", "Public assistance recipients, %"), ("medicaid1_share", "Medical Aid type 1 beneficiaries treated, %"), ("chewing_discomfort_65", "Chewing discomfort, aged 65+, %")]),
          ("Supply", [("beds_per_1000", "Hospital beds per 1,000"), ("ltc_hospitals", "LTC hospitals per 100,000 aged 65+")]),
          ("Fixed adjustments", [("urban_population_share", "Urban population share, %"), ("physicians_per_1000", "Physicians per 1,000"), ("sex_ratio", "Sex ratio, men per 100 women"), ("fiscal_independence", "Fiscal autonomy, %"), ("pop80_share", "Aged 80 years or older, %")])]
def table1():
    T = C.T1; cols = ["2011-2015", "2016-2019", "2020-2024", "2011-2024"]
    rows = [["__H__", "Inpatient days"], ["  District-years, n"] + [th(T[c]["n"]) for c in cols], ["  Inpatient days, million"] + [th(T[c]["days"] / 1e6) for c in cols],
            ["  Days per resident per year"] + [f"{T[c]['pc']:.2f}" for c in cols], ["  Share outside district of residence, %"] + [f"{100*T[c]['out']:.1f}" for c in cols],
            ["  Days per inpatient<sup>a</sup>"] + [f"{T[c]['dpp']:.1f}" for c in cols], ["  District ratio, median<sup>b</sup>"] + [f"{T[c]['sur_med']:.2f}" for c in cols],
            ["  District ratio, 10th-90th percentile<sup>b</sup>"] + [f"{T[c]['sur_p10']:.2f}-{T[c]['sur_p90']:.2f}" for c in cols]]
    for g, vs in COVLAB:
        rows.append(["__H__", f"{g}, mean (SD)"])
        for v, lab in vs:
            mx = max(abs(T[c]["cov"][v][0]) for c in cols); dp = 0 if mx >= 100 else (2 if mx < 5 else 1)
            rows.append([f"  {lab}"] + [f"{T[c]['cov'][v][0]:,.{dp}f} ({T[c]['cov'][v][1]:,.{dp}f})" for c in cols])
    foot = ("<sup>a</sup>Inpatient days divided by the summed numbers of patients treated in hospitals inside and outside the district; patients treated in both are counted twice. "
            "<sup>b</sup>Observed over expected inpatient days (indirect standardization for sex and 5-year age group), summed over the period. Means and SDs are over district-years. LTC, long-term care.")
    return ("Table 1. Inpatient Days of Residents and District Characteristics by Period, Korea, 2011-2024", ["Characteristic"] + cols, rows, foot)
def table2():
    rows = []
    for g, vs in COVLAB:
        rows.append(["__H__", g])
        for v, lab in vs:
            lab = re.sub(r", %$|, men per 100 women$", "", lab)
            m = N["main"][v]; mv = N["mv"].get(v); k2 = N["KH_typeII"].get(v); lg = N["E2_lag2"].get(v); op = N["nco"].get("OUTV|" + v)
            f = lambda x: f"{x[0]:.3f} ({x[1]:.3f}-{x[2]:.3f})" if x else "\u2013"
            rows.append([f"  {lab}", f(m), f"{100*mv[0]:.0f}" if mv else "\u2013", f(k2), f(lg), f(op)])
    foot = ("Rate ratios per 1 SD with 95% credible intervals (CrIs). Principal model: negative binomial with a Besag-York-Molli\u00e9 2 district effect and random-walk and independent year effects, "
            f"9 characteristics and 5 fixed adjustments ({th(N['n_rows'])} district-years). \u2013, forced into every model (no subset share). "
            "<sup>a</sup>Share of the 200 covariate-subset models containing the characteristic in which the CrI excluded 1. "
            "<sup>b</sup>Principal model plus a Knorr-Held type II space-time interaction (district-specific trends). "
            "<sup>c</sup>Hypothesized characteristics lagged by 2 years (2013-2024). "
            "<sup>d</sup>Principal model refitted with outpatient visit-days of residents, standardized for sex and age. LTC, long-term care.")
    return ("Table 2. District Characteristics and Inpatient Days of Residents, Korea, 2011-2024",
            ["Characteristic", "Principal model\nRR (95% CrI)", "Subsets\ncredible, %<sup>a</sup>", "District trends\nRR (95% CrI)<sup>b</sup>", "2-year lag\nRR (95% CrI)<sup>c</sup>", "Outpatient days\nRR (95% CrI)<sup>d</sup>"], rows, foot)

FIGCAP = {
 1: ("Standardized inpatient days of residents across Korean districts, 2011-2024",
     "(A) Ratio of observed to expected inpatient days (indirect standardization for sex and 5-year age group) summed over 2011-2024; solid outlines, Getis-Ord Gi* hot spots, and dashed outlines, cold spots (P < .05). (B) National inpatient days per resident by year. (C) Median days per inpatient, hospital beds per 1,000 residents, long-term care (LTC) hospitals per 100,000 residents aged 65 years or older, and Medical Aid type 1 beneficiaries treated per 100 residents in hot spots, other districts, and cold spots, each relative to the highest group. Map lines delineate study areas and do not necessarily depict accepted national boundaries."),
 2: ("Rate ratios of inpatient days per 1 SD of 4 district characteristics across model specifications",
     "Points and lines show rate ratios and 95% credible intervals from the principal model; models with Knorr-Held type II and type IV space-time interactions; a model with covariates lagged by 2 years; the between-district and within-district components of a decomposition model; and the principal model refitted with outpatient visit-days of residents. LTC, long-term care."),
}
def foot_row(J, text, sz=8, ls=12):
    from docx.enum.text import WD_LINE_SPACING
    t = J.doc.tables[-1]; r = t.add_row(); m = r.cells[0].merge(r.cells[-1]); m.text = ""; p = m.paragraphs[0]
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(ls); p.paragraph_format.space_before = Pt(4)
    c = J.counting; J.counting = False; J._emit(p, text, sz); J.counting = c
def put_table(J, t, fs=9):
    c = J.counting; J.counting = False; J.table_fit(t[0], t[1], t[2], "", fs_max=fs, title_bold=False); foot_row(J, t[3]); J.counting = c
