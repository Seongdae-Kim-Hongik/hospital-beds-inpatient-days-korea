#   연구 질문 명시, 이중 익명(제목면 별도: 저자·소속·교신 연락처(전화 포함)·감사의 글·이해충돌·연구비·윤리·자료 진술), APA 참고문헌(저자-연도), 그림 별도 파일, 컬러 온라인 무료.
import os, re, json, subprocess
from jkms_engine import JKMS
import content_ms_inpt as C
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out"); os.makedirs(OUT, exist_ok=True)
N = C.N; REFS = json.load(open(os.path.join(HERE, "refs_inpt.json"), encoding="utf-8")); JFULL = json.load(open(os.path.join(HERE, "journal_full.json"), encoding="utf-8")); th = C.th
_zf = os.path.join(OUT, "zenodo_doi.txt"); ZENODO = open(_zf).read().strip() if os.path.exists(_zf) else "[ZENODO DOI]"
TITLE = C.TITLE; ORCID = "0000-0002-1525-0091"
ADDRESS = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
PHONE = "+82-2-320-1114"
FUNDING = "The author received no financial support for the research, authorship, and/or publication of this article."
COI = "The author declared no potential conflicts of interest with respect to the research, authorship, and/or publication of this article."
AI_HEAD = "Use of Artificial Intelligence"
AI_STATEMENT = "Claude (Anthropic) and ChatGPT (OpenAI) were used only for translation and English-language editing of the manuscript. The author reviewed and edited all text and takes full responsibility for the content."
def data_full(): return f"All source data are publicly available aggregate statistics cited in the Methods. The analysis code and the scripts that generate every number, table, and figure are openly available on Zenodo (https://doi.org/{ZENODO}) under the MIT License. The processed district-year data are available from the corresponding author on reasonable request."
IRB_ANON = "The institutional review board of the author's institution approved the study and waived informed consent because only published aggregate statistics were used (details on the title page)."
IRB_MS = "The institutional review board of the author's institution approved the study and waived informed consent because only published aggregate statistics were used (details withheld for anonymized review)."
IRB_FULL = "The Institutional Review Board of Hongik University approved the study on November 4, 2025 (7002340-202511-HR-012) and its continuing review on November 3, 2026 (7002340-202611-HR-040), and waived informed consent because only published aggregate statistics were used."

def cites(t): return re.sub(r"\s*\[(@[^\]]+)\]", lambda m: " {{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
SRC = [C.INTRO, C.NEW_CONTRIBUTION, C.CONCEPT, [p for x in C.METHODS for p in x[1:]], [p for x in C.RESULTS for p in x[1:]], C.DISCUSSION, C.CONCLUSION]
KEYS = sorted({k.strip().lstrip("@") for blk in SRC for p in blk for g in re.findall(r"\[(@[^\]]+)\]", p) for k in g.split(";")})
_miss = [k for k in KEYS if k not in REFS]; assert not _miss, _miss

KEEP = {"Korea", "Korean", "Medicare", "Medicaid", "Roemer's", "Japan", "Massachusetts", "OECD", "Bayesian", "Laplace", "Spatial+", "Besag", "STROBE", "Medical", "Aid", "National", "Health", "Insurance", "Service", "Community", "Survey", "Andersen's", "United", "States", "Gaussian", "Markov", "Moran", "I", "Wiley", "South", "RECORD", "R"}
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
SMALL = {"of", "and", "the", "in", "for", "on", "a", "an", "to"}
JFIX = {"Science (New York, N.Y.)": "Science", "Lancet (London, England)": "The Lancet", "PloS one": "PLOS ONE", "PLoS medicine": "PLOS Medicine", "BMC health services research": "BMC Health Services Research",
        "BMC public health": "BMC Public Health", "The journals of gerontology. Series A, Biological sciences and medical sciences": "The Journals of Gerontology: Series A",
        "Perspectives on psychological science : a journal of the Association for Psychological Science": "Perspectives on Psychological Science",
        "Health economics, policy, and law": "Health Economics, Policy and Law", "Social science & medicine (1982)": "Social Science & Medicine"}
def jname(k):
    j = JFULL[k]
    if j in JFIX: return JFIX[j]
    j = re.sub(r"\s*\([^)]*\)\s*$", "", j).split(" : ")[0]
    ws = j.split(" "); return " ".join(w if (w.isupper() or (i and w.lower() in SMALL)) else (w[:1].upper() + w[1:]) for i, w in enumerate(ws)).replace(" And ", " and ")
def person(a):   # "Kim JH" → ("Kim", "J. H.")
    p = a.split(" "); ini = p[-1]
    if len(p) >= 2 and ini.isupper() and ini.isalpha() and len(ini) <= 4: return " ".join(p[:-1]), " ".join(c + "." for c in ini)
    return a, ""
def surnames(k):
    au = REFS[k]["authors"]
    if isinstance(au, str): return [au]
    return [person(a)[0] for a in au]
def base_label(k):
    s = surnames(k); y = REFS[k]["year"]
    return (s[0] if len(s) == 1 else f"{s[0]} & {s[1]}" if len(s) == 2 else f"{s[0]} et al."), y
_lab = {}
for k in KEYS: _lab.setdefault(base_label(k), []).append(k)
SUFFIX = {}; LAB2 = {}
for (_a, _y), ks in _lab.items():
    if len(ks) > 1:
        if len({surnames(k)[0] for k in ks}) == 1 and len({tuple(surnames(k)) for k in ks}) == len(ks):   # 같은 첫 저자·다른 공저자 → 둘째 저자까지 밝힘(APA 8.18)
            for k in ks: s_ = surnames(k); LAB2[k] = f"{s_[0]}, {s_[1]}, et al." if len(s_) > 2 else f"{s_[0]} & {s_[1]}"
        else:
            for i, k in enumerate(sorted(ks, key=lambda x: REFS[x]["title"].lower())): SUFFIX[k] = "abcdefgh"[i]
def year(k): return f"{REFS[k]['year']}{SUFFIX.get(k, '')}"
def aylabel(k):
    a = LAB2.get(k) or base_label(k)[0]; return ((a.lower(), year(k)), f"{a}, {year(k)}")
def apa_authors(k):
    au = REFS[k]["authors"]
    if isinstance(au, str): return au
    ps = [f"{s}, {i}" if i else s for s, i in (person(a) for a in au)]
    if len(ps) == 1: return ps[0]
    if len(ps) <= 20: return ", ".join(ps[:-1]) + ", & " + ps[-1]
    return ", ".join(ps[:19]) + ", . . . " + ps[-1]
def aref(k):
    r = REFS[k]; A = apa_authors(k); A = A if A.endswith(".") else A + "."
    if r["type"] == "web": return f"{A} ({year(k)}). <i>{r['title']}</i>. {r['url']}"
    if r["type"] == "book": return f"{A} ({year(k)}). <i>{sent(r['title'])}</i>. {r['publisher'].replace('Paris: ', '')}." + (f" https://doi.org/{r['doi']}" if r.get("doi") else "")
    t = sent(r["title"].rstrip(".")); t = t + ("" if t.endswith(("?", "!")) else ".")
    s = f"{A} ({year(k)}). {t} <i>{jname(k)}</i>"
    if r.get("vol"): s += f", <i>{r['vol']}</i>" + (f"({r['issue']})" if r.get("issue") else "") + (f", {full_pages(r['pages']).replace('-', chr(8211))}" if r.get("pages") else "")
    return s + "." + (f" https://doi.org/{r['doi']}" if r.get("doi") else "")
def sortkey(k):
    au = REFS[k]["authors"]; s = [(au.lower(), "")] if isinstance(au, str) else [(person(a)[0].lower(), person(a)[1].lower()) for a in au]
    return (s, year(k))
def full_pages(p):   # PubMed 축약 쪽(120-8) → 전체(120-128), APA
    m = re.fullmatch(r"([A-Za-z]?)(\d+)-([A-Za-z]?)(\d+)", p or "")
    if not m: return p
    a, b = m.group(2), m.group(4)
    if len(b) < len(a): b = a[:len(a) - len(b)] + b
    return f"{m.group(1)}{a}-{m.group(3)}{b}"

class TX(JKMS):
    raw = False; table_bold = True
    def aylabel(self, k): return aylabel(k)
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw: text = re.sub(r"(^|[\s(])-(?=\d)", "\\1\u2212", text)
        return super()._emit(p, text, sz, bold, italic)

import build_tables_inpt as BT
table1, table2, FIGCAP, put_table = BT.table1, BT.table2, BT.FIGCAP, BT.put_table

def build(bw=0, aw=0):
    J = TX(cite="ay")
    dz = lambda t: t.replace(IRB_ANON, IRB_MS)
    J.para(f"<b>{TITLE}</b>")
    J.para(f"<b>Running title:</b> {C.RUNNING}", before=6)
    J.para("<b>Article type:</b> Empirical Research Article", before=6)
    J.para(f"<b>Word count:</b> {th(bw)} words (main text). <b>Abstract:</b> {aw} words. <b>Tables and figures:</b> 2 tables and 2 figures.", before=6)
    J.page_break(); J.head("Abstract", 1); J.para(C.ABSTRACT)
    J.para(f"<b>Keywords:</b> {C.KEYWORDS}", before=6)
    J.page_break(); J.counting = True
    J.head("Introduction", 1)
    for p in C.INTRO: J.para(cites(p), indent=True)
    J.head("New Contribution", 1)
    for p in C.NEW_CONTRIBUTION: J.para(cites(p), indent=True)
    J.head("Conceptual Framework", 1)
    for p in C.CONCEPT: J.para(cites(p), indent=True)
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
    J.head(AI_HEAD, 1); J.para(AI_STATEMENT)
    assert sorted(J.cites) == KEYS, (set(J.cites) ^ set(KEYS))
    J.page_break(); J.head("References", 1); J.raw = True; rl = []
    for k in sorted(KEYS, key=sortkey): s = aref(k); rl.append(re.sub(r"</?i>", "", s)); J.para(s)
    J.raw = False
    J.page_break(); put_table(J, table1()); J.page_break(); put_table(J, table2())
    J.page_break(); J.head("Figure Legends", 1)
    for k in sorted(FIGCAP): t, c = FIGCAP[k]; J.para(f"<b>Figure {k}.</b> {t}. {c}")
    return J, rl

def docx_bw(path):
    from docx import Document
    t = "\n".join(x.text for x in Document(path).paragraphs)
    return len(t[t.find("\nIntroduction\n"):t.find("\n" + AI_HEAD + "\n")].split())
def to_pdf(p): subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_inpt_ms", "--convert-to", "pdf", "--outdir", os.path.dirname(p), p], check=True, capture_output=True)

if __name__ == "__main__":
    p = os.path.join(OUT, "Manuscript.docx")
    aw = len(C.ABSTRACT.split()); assert aw <= 150, aw
    J, rl = build(); J.doc_title = "Manuscript"; J.save(p); bw = docx_bw(p)
    J, rl = build(bw, aw); J.doc_title = "Manuscript"; J.save(p); assert docx_bw(p) == bw, bw
    assert bw <= 6000, bw
    to_pdf(p)
    K = TX(cite="ay"); K.para(f"<b>{TITLE}</b>"); K.para(f"<b>Running title:</b> {C.RUNNING}", before=6)
    K.para("Seongdae Kim, PhD", before=12); K.para(ADDRESS)
    K.para(f"<b>Corresponding author:</b> Seongdae Kim, PhD, {ADDRESS}. Phone: {PHONE}. Email: kimsd@hongik.ac.kr. ORCID: {ORCID}.", before=6)
    for h, t in (("Acknowledgments", "None."), ("Declaration of conflicting interests", COI), ("Funding", FUNDING), ("Ethical approval and informed consent", IRB_FULL),
                 ("Data availability", data_full()), ("Author contribution", "Seongdae Kim is the sole author and was responsible for conception, data curation, analysis, interpretation, and writing."), (AI_HEAD, AI_STATEMENT)):
        K.para(f"<b>{h}:</b> {t}", before=6)
    K.para(f"<b>Word count:</b> main text {th(bw)}; abstract {aw}; 2 tables; 2 figures; {len(KEYS)} references.", before=6)
    K.doc_title = "Title page"; tpp = os.path.join(OUT, "Title_Page.docx"); K.save(tpp); to_pdf(tpp)
    open(os.path.join(OUT, "wordcount_ms.txt"), "w").write(f"body_words={bw}\nabstract_words={aw}\nrefs={len(KEYS)}\ntables=2\nfigures=2\ntitle_words={len(TITLE.split())}\n")
    open(os.path.join(OUT, "references.txt"), "w").write("\n".join(rl))
    print(f"body {bw} | abstract {aw} | refs {len(KEYS)} | title words {len(TITLE.split())}")
