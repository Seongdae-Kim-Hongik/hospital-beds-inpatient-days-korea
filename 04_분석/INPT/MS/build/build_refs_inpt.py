import json, os, time, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__)); AN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
H = json.load(open(os.path.join(AN, "HCUV/MS/build/refs_hcuv.json"))); A = json.load(open(os.path.join(AN, "HTND/MS_AJPM/build/refs_htnd.json")))
PM = {"kwon2009thirty": 19004861, "cho2023effects": 36189771, "hyun2014does": 25528468, "kim2018implementation": 30015058, "kim2026longterm": 42497224,
      "wennberg1973small": 4750608, "wennberg2002geography": 12703563, "corallo2014systematic": 24054709, "roemer1961bed": 14493273, "ginsburg1983bed": 10310279,
      "fisher2000associations": 10654835, "delamater2013more": 23418432, "shwartz2011bringing": 22002646, "kim2019hospitalizations": 31029134, "kim2019spatial": 31253046,
      "andersen1995revisiting": 7738325, "kong2020factors": 32689960, "kim2026comparison": 41975406, "han2026medical": 42879845, "lee2020effect": 33109176,
      "sari2009physical": 18792089, "tsuji2003impact": 14559755, "min2016excess": 26797622, "langsetmo2019association": 29771295, "inskip1983methods": 6672943,
      "riebler2016intuitive": 27566770, "knorrheld2000bayesian": 10960871, "steegen2016increasing": 27694465, "dupont2022spatial": 35258102, "vonelm2007strengthening": 18064739,
      "morgenstern1995ecologic": 7639884, "chung2010determinants": 19783062, "okumura2019geographical": 30249947, "finkelstein2016sources": 28111482, "barrenetxea2021emergency": 34732180,
      "fisher2003implicationsa": 12585825, "benchimol2015reporting": 26440803}
ABBR = {"bell2015explaining": "Political Sci Res Methods", "besag1991bayesian": "Ann Inst Stat Math", "gelman2014understanding": "Stat Comput", "moran1950notes": "Biometrika",
        "ord1995local": "Geogr Anal", "rue2009approximate": "J R Stat Soc Series B Stat Methodol", "simpson2017penalising": "Stat Sci"}
R = {}
ids = ",".join(str(v) for v in PM.values())
d = json.loads(urllib.request.urlopen("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urllib.parse.urlencode(dict(db="pubmed", id=ids, retmode="json")), timeout=60).read())["result"]
for k, p in PM.items():
    x = d[str(p)]; doi = next((a["value"] for a in x.get("articleids", []) if a["idtype"] == "doi"), "")
    au = [a["name"] for a in x.get("authors", []) if a.get("authtype") == "Author"]
    R[k] = dict(type="journal", authors=au, title=x["title"].rstrip("."), journal=x["source"], year=int(x["pubdate"][:4]), vol=x.get("volume", ""), issue=x.get("issue", ""),
                pages=x.get("pages", ""), doi=doi, pmid=str(p), verified="PubMed esummary 2026-11-15")
for k, j in ABBR.items():
    r = dict(H[k]); r["journal"] = j; r["verified"] = "43호 refs_hcuv 검증본(DOI) + LTWA 약어"; R[k] = r
R["oecd2023health"] = dict(type="book", authors=["OECD"], title="Health at a Glance 2023: OECD Indicators", journal="", publisher="Paris: OECD Publishing", year=2023, doi="10.1787/7a7afb35-en", verified="DOI 확인")
R["web:nhis2026regional"] = dict(type="web", authors="National Health Insurance Service", title="Regional health care utilization statistics: inpatient care of residents within and outside the district of residence, and national inpatient days by sex and 5-year age group (TX_35003, TX_35001), 2011-2024. Korean Statistical Information Service", url="https://kosis.kr", year=2026, accessed="November 15, 2026")
R["web:mois2026population"] = dict(A["web:mois2026population"], accessed="November 15, 2026")
R["web:rcore2026"] = dict(A["web:rcore2026"], accessed="November 15, 2026")
R["wennberg1973small"]["authors"] = ["Wennberg J", "Gittelsohn A"]; R["roemer1961bed"]["authors"] = ["Roemer MI"]; R["kim2026comparison"]["pages"] = "565"; R["min2016excess"]["pages"] = "136"; R["kong2020factors"]["title"] = R["kong2020factors"]["title"].replace("Korea welfare panel study", "Korea Welfare Panel Study"); R["delamater2013more"]["title"] = R["delamater2013more"]["title"].replace("? a spatial", "? A spatial")
R["min2016excess"]["title"] = "Excess medical care costs associated with physical inactivity among Korean adults: retrospective cohort study"
R["langsetmo2019association"]["title"] = "The association between objectively measured physical activity and subsequent health care utilization in older men"
R["kong2020factors"]["title"] = R["kong2020factors"]["title"].replace("medical aid", "Medical Aid")
A = json.load(open(os.path.join(AN, "HTND/MS_AJPM/build/refs_htnd.json"))); R["kang2015korea"] = A["kang2015korea"]
json.dump(R, open(os.path.join(HERE, "refs_inpt.json"), "w"), ensure_ascii=False, indent=1)
for k, r in R.items(): print(k, "|", r.get("journal"), r.get("year"), r.get("vol"), r.get("pages"), r.get("doi"), "|", (r["authors"][:2] if isinstance(r["authors"], list) else r["authors"]))
print(len(R))
