# Hospital beds and inpatient days of residents across South Korean districts, 2011-2024

Analysis code for the manuscript

> Kim S. *Do more hospital beds mean more days in hospital? Inpatient care of residents across Korean districts, 2011-2024.*

Archived version: Zenodo, https://doi.org/10.5281/zenodo.24332390 (v1.0.1).

This code is released under the MIT licence.

## Contents

This repository contains code only. The processed district-year data (analytic panel, expected counts, result tables and boundary file) are not included; they are available from the author on reasonable request. All source statistics are public (see Data sources).

| Path | What it is |
|---|---|
| `01_스크립트/` | Analysis scripts (below) |
| `04_분석/INPT/` | Covariate pool and model settings (`make_pool_sets_inpt.py`, `sets_INPT_*.json`, `config_INPT_std3.json`), descriptive inpatient table builder (`inpt_aux_build.py`), the full model chain (`run_std3_chain.sh`) and the district adjacency graph (`graph_593.graph`). Sensitivity versions: queen contiguity graph `s577`, without the share aged 80 or older `s2`, unstandardised expected counts `sc` |
| `04_분석/INPT/MS/build/` | Scripts that read the result tables and write every number, table and figure in the manuscript and appendix (`numbers_inpt.py`, `figs_inpt.py`, `content_inpt.py`, `content_ms_inpt.py`, `build_tables_inpt.py`, `build_ms_inpt.py`, `journal_full.json`, `esm_inpt.py`, `build_refs_inpt.py`) |

Folder and some column names are in Korean because the source tables are Korean; each script has a header comment describing its inputs and outputs.

## Data sources

All inputs are public, aggregated statistics. No individual-level data are included.

- Inpatient days of residents in hospitals inside and outside the district of residence (all diagnoses, National Health Insurance and Medical Aid): National Health Insurance Service regional health care utilisation statistics, KOSIS tables TX_35003 (A027, A056, A085, A114; A030, A059, A088, A117), 2011-2024.
- National inpatient days by sex and 5-year age group: KOSIS TX_35001 (A047), 2011-2024.
- Population by sex and 5-year age group: Ministry of the Interior and Safety, resident registration statistics.
- District covariates: Community Health Survey (walking, moderate-or-higher physical activity, chewing discomfort aged 65 or older, cardiopulmonary resuscitation awareness), public sports facility register, National Health Insurance Service (Medical Aid type 1), health-resource statistics (hospital beds, long-term care hospitals) and KOSIS local indicators (fixed adjustments and negative controls).

## Pipeline

Set `ST_DATA_ROOT` and `ST_GPT_DATASET` to the local copies of the public source files and the read-only district database, then run from the repository root.

| Step | Script | Output |
|---|---|---|
| 1 | `99R_next5f_nhis.py` (uses `99R_next5b_build_E.py`, `38_build_Estd_all.py`, `40_region_crosswalk.py`, `50_build_master_panel.py`) | District inpatient days (code-based linkage) and expected days by indirect standardisation in 2 sexes x 18 age groups |
| 2 | `99c_extra_canonical_pool_digx.py`, `99H_hcuv_build.py`, then `04_분석/INPT/make_pool_sets_inpt.py` | Covariate pool and model settings; comparison outcomes |
| 3 | `80_build_disease_panel_v.py INPT` (`ST_VER=std3`) | Analytic panel |
| 4 | `81_fit_inla.R INPT` (see `04_분석/INPT/run_std3_chain.sh`, which wraps R jobs in `rslot.sh`) | Principal model, 200-subset multiverse, period models, sensitivity versions |
| 5 | `85_window_maps.R`, `86_yearly_maps_ehsa.py`, `87_window_grid.py` | Maps and yearly smoothed ratios |
| 6 | `88g_sens_prep.py INPT std3 HCUVC,OUTV`, `88g_sens_suite.R` (`GROUP=1..6`), `88h_ppc_varpart.R`, `88k_struct_kh.R` (nb, struct, kh, review) with `kh_constraints.R`, `89g_sens_combine.py` | Alternative specifications, comparison outcomes, Knorr-Held models, decomposition |
| 7 | `04_분석/INPT/inpt_aux_build.py`, then `04_분석/INPT/MS/build/` | Descriptive table of inpatients, manuscript numbers, tables, figures and appendix |

The boundary file is found at `data/boundary/final.shp` by default; set `ST_SHP` to use another path.

## Software

R 4.6.0 with R-INLA 25.10.19, spdep and sf; Python 3.9 with pandas, geopandas, numpy, scipy, matplotlib and python-docx.

## Licence

MIT (see `LICENSE`).
