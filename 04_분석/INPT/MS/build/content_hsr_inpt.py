#  HSR 규정에 맞춰 제목(새 제목)·구조 초록 5항목·callout box·키워드만 바꾼다. 수치는 numbers_inpt.json에서만.
from content_inpt import *          # noqa: F401,F403  (N, th, ci, tc, pct, T1, HC, PC, INTRO, METHODS, RESULTS, DISCUSSION, CONCLUSION)
import content_inpt as _C

TITLE = "Do more hospital beds mean more days in hospital? Inpatient care of residents across Korean districts, 2011-2024"
assert ":" not in TITLE and "229" not in TITLE and "standardi" not in TITLE.lower() and TITLE != _C.TITLE
KEYWORDS = "hospital bed capacity; length of stay; long-term care hospitals; small-area variation; supply-sensitive care; Bayesian spatio-temporal models; Republic of Korea"
RUNNING = "Hospital beds and inpatient days in Korea"

ABSTRACT = [
("Objective", "To examine whether hospital bed and long-term care hospital supply, need indicators, and physical activity are associated with the days residents of Korean districts spend in hospital, after accounting for age and sex."),
("Study Setting and Design", f"An ecological panel study of all residents of {N['n_districts']} districts of the Republic of Korea, a single-payer system with fee-for-service payment, from 2011 to 2024. The outcome was inpatient days of residents in hospitals inside and outside the district; exposures were 9 district characteristics."),
("Data Sources and Analytic Sample", f"Secondary National Health Insurance statistics ({th(N['n_rows'])} district-years; {N['days_total_bn']:.2f} billion inpatient days) were linked to resident registration, health resource, and Community Health Survey data. Expected days were indirectly standardized for sex and 5-year age group. Bayesian spatio-temporal negative binomial models were followed by 200 covariate subsets, space-time interaction models, lags, and between- and within-district decomposition."),
("Principal Findings", f"Inpatient days per resident rose from {PC['2011']:.2f} in 2011 to {PC['2024']:.2f} in 2024. The district ratio of observed to expected days ranged from {N['sur_p10']:.2f} to {N['sur_p90']:.2f} (10th-90th percentile), with a stable ranking (Kendall W {N['kendall_w']:.2f}). Per 1 SD, inpatient days were higher with more hospital beds (rate ratio {tc('beds_per_1000', 'main')}), long-term care hospitals ({tc('ltc_hospitals', 'main')}), and Medical Aid beneficiaries ({tc('medicaid1_share', 'main')}); these associations persisted with district-specific trends and lags. Bed density was not positively associated with outpatient visit-days."),
("Conclusions", "Districts with more hospital beds and long-term care hospitals had more inpatient days per resident, consistent with supply-sensitive inpatient care, although reverse causation cannot be excluded."),
]
CALLOUT = [
("What is known on this topic", [
  "Hospital use varies widely between small areas with similar populations, and part of this variation follows the supply of hospital beds.",
  "Korea has the most hospital beds per person in the OECD, and long-term care hospitals have become a major setting of long stays for older adults.",
]),
("What this study found", [
  "Across 14 years, standardized inpatient days per resident differed about 2-fold between Korean districts, with a stable excess in the southwest and southeast.",
  "Districts with more hospital beds and long-term care hospitals had more inpatient days, and these associations persisted with district-specific trends and lagged supply.",
  "Bed density was not associated with more outpatient visits, a contrast expected if inpatient care is supply-sensitive.",
]),
]
for _h, _bs in CALLOUT:
    assert len(_bs) <= 3 and all(len(b.split()) <= 30 for b in _bs), (_h, [len(b.split()) for b in _bs])
