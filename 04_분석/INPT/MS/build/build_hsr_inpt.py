#  HSR 규정(MS/00_저널가이드/hsr_ag.txt + 저자 지침 요건표): 본문 ≤4,500단어(제목면·초록·키워드·callout·참고문헌·표·범례 제외), 초록 ≤300(Objective; Study Setting and Design;
#   Data Sources and Analytic Sample; Principal Findings; Conclusions), 키워드 ≤7, callout box 2제목×최대 3개(각 ≤30단어), 표+그림 ≤5, 더블스페이스·쪽번호,
#   이중 익명(원고 한 파일 = 익명 제목면 → 초록·키워드 → callout → 본문 → 참고문헌 → 편집 가능한 표(쪽마다) → 그림 범례), 그림은 별도 파일, AMA 번호 인용(등장순).
import os, re, json, subprocess
from docx.shared import Pt
from jkms_engine import JKMS
import content_hsr_inpt as C
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out"); os.makedirs(OUT, exist_ok=True)
N = C.N; REFS = json.load(open(os.path.join(HERE, "refs_inpt.json"), encoding="utf-8")); th = C.th; tc = C.tc
_zf = os.path.join(OUT, "zenodo_doi.txt"); ZENODO = open(_zf).read().strip() if os.path.exists(_zf) else "[ZENODO DOI]"
TITLE = C.TITLE; ORCID = "0000-0002-1525-0091"
ADDRESS = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
FUNDING = "No funding to report."
COI = "The author declares no conflicts of interest."
AI_HEAD = "Use of Artificial Intelligence"
AI_STATEMENT = "Claude (Anthropic) and ChatGPT (OpenAI) were used only for translation and English-language editing of the manuscript. The author reviewed and edited all text and takes full responsibility for the content."
DATA_ANON = "All source data are publicly available aggregate statistics cited in the Methods. The analysis code is openly available in a public repository under the MIT License (link withheld for anonymized review). The processed district-year data are available from the author on reasonable request."
def data_full(): return f"All source data are publicly available aggregate statistics cited in the Methods. The analysis code and the scripts that generate every number, table, and figure are openly available on Zenodo (https://doi.org/{ZENODO}) under the MIT License. The processed district-year data are available from the author on reasonable request."
IRB_ANON = "The institutional review board of the author's institution approved the study and waived informed consent because only published aggregate statistics were used (details on the title page)."
IRB_HSR = "The institutional review board of the author's institution approved the study and waived informed consent because only published aggregate statistics were used (details withheld for anonymized review)."
IRB_FULL = "The Institutional Review Board of Hongik University approved the study on November 4, 2025 (7002340-202511-HR-012) and its continuing review on November 3, 2026 (7002340-202611-HR-040), and waived informed consent because only published aggregate statistics were used."

def cites(t): return re.sub(r"\s*\[(@[^\]]+)\]", lambda m: "{{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
def all_keys():
    import content_inpt
    src = open(content_inpt.__file__, encoding="utf-8").read(); src = re.sub(r"(?m)^\s*#.*$", "", src)
    return sorted({k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", src) for k in g.split(";")})
KEYS = all_keys(); _miss = [k for k in KEYS if k not in REFS]; assert not _miss, _miss
KEEP = {"Korea", "Korean", "Medicare", "Medicaid", "Roemer's", "Japan", "Massachusetts", "OECD", "Bayesian", "Laplace", "Spatial+", "Besag", "STROBE", "Medical", "Aid", "National", "Health", "Insurance", "Service", "Community", "Survey", "Andersen's", "United", "States", "Gaussian", "Markov", "Moran", "I", "Wiley", "South", "RECORD"}
def sent(t):
    w = t.split(" "); caps = sum(1 for x in w[1:] if x[:1].isupper())
    if len(w) < 4 or caps < 0.5 * (len(w) - 1): return t
    out = [w[0]]
    for x in w[1:]:
        core = x.strip("(),:;.?[]\"'")
        keep = core in KEEP or core.isupper() or any(c.isdigit() for c in core) or out[-1].endswith((":", "?"))
        out.append(x if keep else x[:1].lower() + x[1:])
    t2 = " ".join(out)
    for a_, b_ in (("medical Aid", "Medical Aid"), ("Medical care", "medical care"), ("Health care", "health care"), ("Medical service", "medical service"), ("National health insurance", "national health insurance")): t2 = t2.replace(a_, b_)
    return t2
def aref(k):   # AMA 11판: Chen LM, Ryan AM, Shih T, et al. Title. Health Serv Res. 2018;53(2):632-648. doi:10.1111/...
    r = REFS[k]
    if r["type"] == "web": return f"{r['authors']}. {r['title']}. Published {r['year']}. Accessed {r['accessed']}. {r['url']}"
    if r["type"] == "book": return f"{r['authors'][0]}. <i>{r['title']}</i>. {r['publisher'].replace('Paris: ', '')}; {r['year']}." + (f" doi:{r['doi']}" if r.get("doi") else "")
    au = r["authors"]; a = ", ".join(au) if len(au) <= 6 else ", ".join(au[:3]) + ", et al"
    t = sent(r["title"].rstrip(".")); t = t + ("" if t.endswith(("?", "!")) else ".")
    s = f"{a}. {t} <i>{r['journal']}</i>. {r['year']}"
    if r.get("vol"): s += f";{r['vol']}" + (f"({r['issue']})" if r.get("issue") else "") + (f":{r['pages']}" if r.get("pages") else "")
    return s + "." + (f" doi:{r['doi']}" if r.get("doi") else "")

class TX(JKMS):
    raw = False; table_bold = True
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw: text = re.sub(r"(^|[\s(])-(?=\d)", "\\1\u2212", text)
        return super()._emit(p, text, sz, bold, italic)

import build_tables_inpt as BT
table1, table2, FIGCAP, put_table = BT.table1, BT.table2, BT.FIGCAP, BT.put_table

def build(bw=0, aw=0, deanon=False):
    J = TX(cite="sup")
    dz = (lambda t: t.replace(IRB_ANON, IRB_FULL)) if deanon else (lambda t: t.replace(IRB_ANON, IRB_HSR))
    J.para(f"<b>{TITLE}</b>")
    J.para(f"<b>Running title:</b> {C.RUNNING}", before=6)
    J.para("<b>Article type:</b> Research Article", before=6)
    J.para(f"<b>Word count:</b> {th(bw)} words (main text). <b>Abstract:</b> {aw} words. <b>Tables and figures:</b> 2 tables and 2 figures. <b>References:</b> {len(KEYS)}.", before=6)
    J.para(f"<b>Acknowledgments:</b> {FUNDING}", before=6)
    J.page_break(); J.head("Abstract", 1)
    for h, t in C.ABSTRACT: J.para(f"<b>{h}.</b> {t}")
    J.para(f"<b>Keywords:</b> {C.KEYWORDS}", before=6)
    J.page_break(); J.head("What Is Known on This Topic and What This Study Found", 1)
    for h, bs in C.CALLOUT:
        J.para(f"<b>{h}</b>", before=6)
        for b in bs: J.para("\u2022 " + b)
    J.page_break(); J.counting = True
    J.head("Introduction", 1)
    for p in C.INTRO: J.para(cites(p), indent=True)
    J.head("Methods", 1)
    for x in C.METHODS:
        J.head(x[0], 2)
        for p in x[1:]: J.para(cites(dz(p)), indent=True)
    J.head("Results", 1)
    for x in C.RESULTS:
        J.head(x[0], 2)
        for p in x[1:]: J.para(cites(p), indent=True)
    J.head("Discussion", 1)
    for p in C.DISCUSSION:
        if p.startswith("### "): J.head(p[4:].strip(), 2); continue
        J.para(cites(p), indent=True)
    J.head("Conclusions", 2)
    for p in C.CONCLUSION: J.para(cites(p), indent=True)
    J.counting = False
    for h, t in (("Data Availability Statement", data_full() if deanon else DATA_ANON), (AI_HEAD, AI_STATEMENT)):
        J.head(h, 1); J.para(t)
    assert sorted(J.cites) == KEYS, (set(J.cites) ^ set(KEYS))
    J.page_break(); J.head("References", 1); J.raw = True; rl = []
    for n, k in enumerate(J.cites, 1): s = f"{n}. {aref(k)}"; rl.append(re.sub(r"</?i>", "", s)); J.para(s)
    J.raw = False
    J.page_break(); put_table(J, table1()); J.page_break(); put_table(J, table2())
    J.page_break(); J.head("Figure Legends", 1)
    for k in sorted(FIGCAP): t, c = FIGCAP[k]; J.para(f"<b>Figure {k}.</b> {t}. {c}")
    return J, rl

def docx_bw(path):
    from docx import Document
    t = "\n".join(x.text for x in Document(path).paragraphs)
    return len(t[t.find("\nIntroduction\n"):t.find("\nData Availability Statement\n")].split())
def to_pdf(p): subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_inpt_hsr", "--convert-to", "pdf", "--outdir", os.path.dirname(p), p], check=True, capture_output=True)

if __name__ == "__main__":
    p = os.path.join(OUT, "Manuscript.docx")
    aw = sum(len(t.split()) for _, t in C.ABSTRACT) + sum(len(h.split()) for h, _ in C.ABSTRACT); assert aw <= 300, aw
    J, rl = build(); J.doc_title = "Manuscript"; J.save(p); bw = docx_bw(p)
    J, rl = build(bw, aw); J.doc_title = "Manuscript"; J.save(p); assert docx_bw(p) == bw, bw
    assert bw <= 4500, bw
    to_pdf(p)
    # 제목면(심사자에게 가지 않음): 저자·학위·소속·이메일·주소, 교신, 감사의 글(연구비), 이해충돌, 윤리, 자료, AI
    K = TX(cite="sup"); K.para(f"<b>{TITLE}</b>"); K.para(f"<b>Running title:</b> {C.RUNNING}", before=6)
    K.para("Seongdae Kim, PhD", before=12); K.para(ADDRESS)
    K.para(f"<b>Corresponding author:</b> Seongdae Kim, PhD, {ADDRESS}. Email: kimsd@hongik.ac.kr. ORCID: {ORCID}.", before=6)
    for h, t in (("Acknowledgments", FUNDING), ("Conflict of interest", COI), ("Author contribution", "Seongdae Kim is the sole author and was responsible for conception, data curation, analysis, interpretation, and writing."),
                 ("Ethics", IRB_FULL), ("Data availability", data_full()), (AI_HEAD, AI_STATEMENT)):
        K.para(f"<b>{h}:</b> {t}", before=6)
    K.para(f"<b>Word count:</b> main text {th(bw)}; abstract {aw}; 2 tables; 2 figures; {len(KEYS)} references.", before=6)
    K.doc_title = "Title page"; tpp = os.path.join(OUT, "Title_Page.docx"); K.save(tpp); to_pdf(tpp)
    open(os.path.join(OUT, "wordcount_hsr.txt"), "w").write(f"body_words={bw}\nabstract_words={aw}\nrefs={len(KEYS)}\ntables=2\nfigures=2\ntitle_words={len(TITLE.split())}\n")
    open(os.path.join(OUT, "references.txt"), "w").write("\n".join(rl))
    print(f"body {bw} | abstract {aw} | refs {len(KEYS)} | title words {len(TITLE.split())}")
