#  본문 절·수치는 content_inpt.py를 쓰되, 저널 규정(초록 150단어, Introduction 뒤 New Contribution·Conceptual Framework 절, 연구 질문 명시)과
#  교차검토 합의 수정(KH type I 표현, 의료급여 측정 단서, 화재 음성대조, 공공체육시설 창별 반대 방향, 수급률·의사 밀도 해석, 신체활동 인용 범위, 필요 측정 한계)을 반영한다.
#  수치는 numbers_inpt.json에서만. [@key] = 인용.
import content_inpt as _C
from content_inpt import N, th, ci, tc, pct, T1, HC, PC   # noqa: F401

TITLE = "Do more hospital beds mean more days in hospital? Inpatient care of residents across Korean districts, 2011-2024"
assert ":" not in TITLE and "229" not in TITLE and "standardi" not in TITLE.lower() and TITLE != _C.TITLE
KEYWORDS = "hospital bed capacity; inpatient days; long-term care hospitals; small-area variation; supply-sensitive care; Republic of Korea"
RUNNING = "Hospital beds and inpatient days in Korea"

ABSTRACT = (f"Korea has the most hospital beds per person in the OECD. Using national insurance statistics for {N['n_districts']} districts (2011-2024; {th(N['n_rows'])} district-years), "
            "this ecological study related inpatient days of residents, standardized for sex and age, to hospital bed and long-term care hospital supply, need indicators, and physical activity "
            "in Bayesian spatio-temporal models. "
            f"Standardized inpatient days differed about 2-fold between the 10th and 90th percentile districts, and district rankings were stable (Kendall W {N['kendall_w']:.2f}). "
            f"Per 1 SD, inpatient days were higher with more hospital beds (rate ratio {N['main']['beds_per_1000'][0]:.3f}) and long-term care hospitals ({N['main']['ltc_hospitals'][0]:.3f}); "
            "both associations persisted with district-specific trends and lagged supply, and bed density was not positively associated with outpatient visits. "
            "A negative-control exposure showed an association of similar size, so unmeasured confounding and reverse causation remain possible. "
            "Planning of hospital and long-term care hospital capacity should consider supply alongside need.")

def _sub(s, a, b):
    assert a in s, a[:60]
    return s.replace(a, b)

INTRO = list(_C.INTRO)
INTRO[1] = _sub(INTRO[1], "Physically active people are admitted to hospital less often, and districts with more active populations might therefore use fewer inpatient days",
                "Physically active people use less health care, including hospital care, and districts with more active populations might therefore use fewer inpatient days")
INTRO[2] = ("No study has mapped inpatient days of residents across all Korean districts over a long period, or asked whether such a map follows bed and long-term care hospital supply, need, or physical activity once age and sex are taken into account. "
            "These questions matter to health services researchers and to policymakers who plan hospital and long-term care capacity for aging populations. "
            "This study used 14 years of national insurance statistics to answer 3 research questions. First, how much do inpatient days of residents vary across Korean districts after standardization for sex and age, and how stable is the pattern? "
            "Second, are hospital bed and long-term care hospital supply, need indicators, and physical activity associated with standardized inpatient days? "
            "Third, do these associations persist in models that allow district-specific trends, use lagged covariates, and separate differences between districts from changes within districts?")

NEW_CONTRIBUTION = [
"Previous small-area studies of bed supply mostly examined admissions in single regions or cross-sections, and Korean studies examined admissions for ambulatory care-sensitive conditions [@delamater2013more; @kim2019hospitalizations; @kim2019spatial]. "
"This study adds 4 things. It covers all inpatient days of every resident of a country with the highest bed density in the OECD for 14 years, including days in long-term care hospitals, a sector that is large in Korea and growing in other aging health systems [@oecd2023health; @kim2026longterm]. "
"It separates acute bed supply from long-term care hospital supply in the same model. It tests whether supply associations persist with district-specific trends, lags, and a between- and within-district decomposition, rather than relying on a cross-sectional contrast. "
"Finally, it uses outpatient visit-days of the same residents as a comparison outcome, which supply-sensitive inpatient care predicts should not follow bed supply [@fisher2003implicationsa; @wennberg2002geography].",
]
CONCEPT = [
"The analysis follows Andersen's behavioral model of health services use, in which use depends on predisposing characteristics, enabling resources, and need [@andersen1995revisiting], combined with the supply-sensitive care hypothesis [@roemer1961bed; @wennberg2002geography; @fisher2003implicationsa]. "
"Predisposing characteristics (age and sex) were handled by indirect standardization, and the urban population share, physician density, sex ratio, fiscal autonomy, and the share aged 80 years or older were adjusted for in every model. "
"Need was represented by public assistance, Medical Aid type 1 use, and chewing discomfort among older adults; health behavior by physical activity and sports facilities; and the health care system by hospital bed and long-term care hospital supply. "
"Under the supply-sensitive hypothesis, more beds and long-term care hospitals are associated with more inpatient days after need is accounted for, and this association is specific to inpatient care rather than to outpatient visits. "
"Under the alternative that supply follows demand, supply would track earlier use and need, which lags and the within-district decomposition address only partly.",
]

METHODS = [list(x) for x in _C.METHODS]
METHODS[2][1] = _sub(METHODS[2][1], f"; intervals were not adjusted for multiplicity, so about {N['chance_n']:.1f} of 9 intervals could exclude 1 by chance.", "; intervals were not adjusted for multiplicity.")
METHODS[2][2] = _sub(METHODS[2][2], "supply-sensitive inpatient care predicts associations of bed supply with inpatient days but not with outpatient visits.",
                     "supply-sensitive inpatient care predicts associations of bed supply with inpatient days but not with outpatient visits, although substitution between settings and case mix could also produce this contrast.")
METHODS = [tuple(x) for x in METHODS]

RESULTS = [list(x) for x in _C.RESULTS]
RESULTS[2][1] = _sub(RESULTS[2][1], f"All 4 associations persisted with a type I interaction, which fitted best (WAIC {th(N['KH_typeI_waic'],1)}).",
                     f"All 4 associations persisted with a type I interaction, an unstructured district-year term that had the lowest WAIC ({th(N['KH_typeI_waic'],1)}); among the types that allow district-specific trends, type II fitted best (WAIC {th(N['KH_typeII_waic'],1)}).")
RESULTS = [tuple(x) for x in RESULTS]

DISCUSSION = list(_C.DISCUSSION)
DISCUSSION[0] = _sub(DISCUSSION[0], "Hot spots had longer stays per patient and more beds and long-term care hospitals.",
                     "Hot spots had more days per inpatient, by a descriptive measure that counts some patients twice, and more beds and long-term care hospitals.")
DISCUSSION[0] = _sub(DISCUSSION[0], "Medical Aid enrollment was associated with both inpatient and outpatient use.",
                     "The Medical Aid type 1 measure, a count of beneficiaries who used care, was associated with both inpatient and outpatient use.")
DISCUSSION[4] = _sub(DISCUSSION[4], "Medical Aid enrollment was associated with both inpatient and outpatient use,",
                     "The Medical Aid measure counts beneficiaries who used care rather than enrollees; it was associated with both inpatient and outpatient use,")
DISCUSSION[2] = _sub(DISCUSSION[2], "Physician density, a fixed adjustment, was associated with fewer inpatient days, which may reflect better access to outpatient care where physicians are concentrated.",
                     f"Physician density, a fixed adjustment, was associated with fewer inpatient days in the principal model but not with district-specific trends ({tc('physicians_per_1000', 'KH_typeII')}), so it is not interpreted.")
DISCUSSION[2] = _sub(DISCUSSION[2], "Because about 60% of inpatient days", "Because about three-fifths of inpatient days")
DISCUSSION[4] = _sub(DISCUSSION[4], "The public assistance rate and chewing discomfort, other markers of need, were not associated once supply was in the model.",
                     f"The public assistance rate was not credibly associated in the principal model but was with district-specific trends ({tc('basic_livelihood_rate', 'KH_typeII')}), and chewing discomfort was not associated; these are indirect markers of need.")
DISCUSSION[4] = _sub(DISCUSSION[4], "Individual studies show that active people use fewer hospital days",
                     "Individual studies show that active people use less health care")
DISCUSSION[4] = DISCUSSION[4] + (" Public sports facilities were positively associated with inpatient days in 2016-2019 and 2020-2024 (Appendix Table 5), opposite to the hypothesized direction, "
                                 "but not in the principal model or the subset analysis; this pattern is not interpreted.")
DISCUSSION[6] = _sub(DISCUSSION[6], "Fifth, the fire negative control was associated with inpatient days with a rate ratio similar to that of long-term care hospitals,",
                     "Fifth, the fire negative control, which may also relate to injury admissions, was associated with inpatient days with a rate ratio similar to that of long-term care hospitals,")
DISCUSSION[6] = _sub(DISCUSSION[6], "Sixth, small rate ratios", "Sixth, no direct measure of morbidity, disability, or psychiatric illness was available, so need was represented only indirectly. Seventh, small rate ratios")

CONCLUSION = [_sub(_C.CONCLUSION[0], "an association that persists across specifications and is not seen for outpatient visits.",
                   "an association that persists across specifications and is not seen for outpatient visits, although its size is modest and a negative-control exposure showed a similar association.")]

assert len(ABSTRACT.split()) <= 150, len(ABSTRACT.split())
