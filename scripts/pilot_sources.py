"""Shared helpers for the 50-term terminology pilot: fetch + cache sources, extract text,
parse ASJP article pages, search ASJP.

Requires: curl on PATH, PyMuPDF (`pip install pymupdf`).
Cached downloads go to <repo>/.cache/pilot_sources/ (git-ignored).
"""
import hashlib
import html
import re
import subprocess
import tempfile
from pathlib import Path

import fitz  # PyMuPDF

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE = PROJECT_ROOT / ".cache" / "pilot_sources"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"

DIAC = re.compile(r"[ً-ْـ]")


def norm(s):
    """Strip Arabic diacritics and tatweel."""
    return DIAC.sub("", s)


# -----------------------------
# Fetching and text extraction
# -----------------------------
def fix_ligatures(t):
    """Arabic PDFs exported from InDesign often map the lam-alef ligature glyph to
    "ال" instead of "لا". Only the unambiguous word-initial patterns are repaired;
    quotes taken from PDFs are additionally checked against rendered page images."""
    t = re.sub(r"(?<![ء-ي])اال", "الا", t)
    t = re.sub(r"(?<![ء-ي])األ", "الأ", t)
    t = re.sub(r"(?<![ء-ي])اإل", "الإ", t)
    t = re.sub(r"(?<![ء-ي])اآل", "الآ", t)
    return t


def _paths(url):
    key = hashlib.md5(url.encode()).hexdigest()[:16]
    return CACHE / f"{key}.raw", CACHE / f"{key}.txt"


def raw_path(url):
    """Download (once) and return the local path of the raw response."""
    raw, _ = _paths(url)
    if not raw.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        subprocess.run(["curl", "-sL", "--max-time", "60", "-A", UA, "-o", str(raw), url], check=True)
    return raw


def get(url):
    """Return extracted text of a URL (HTML stripped, or PDF text with [[PAGE n]] markers)."""
    raw, txt = _paths(url)
    if not txt.exists():
        data = raw_path(url).read_bytes()
        if data[:4] == b"%PDF":
            doc = fitz.open(str(raw))
            text = "".join(f"\n[[PAGE {i + 1}]]\n" + fix_ligatures(p.get_text()) for i, p in enumerate(doc))
        else:
            s = data.decode("utf-8", "replace")
            s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
            s = re.sub(r"(?s)<[^>]+>", " ", s)
            text = html.unescape(s)
            text = re.sub(r"[ \t\r\f\v]+", " ", text)
            text = re.sub(r"\n\s*\n+", "\n", text)
        txt.write_text(text)
    return txt.read_text()


def pdf_page_text(url, page):
    """Raw text layer of one (1-based) PDF page."""
    return fitz.open(str(raw_path(url)))[page - 1].get_text()


def url_status(url):
    return subprocess.run(["curl", "-sL", "-A", UA, "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "60", url],
                          capture_output=True, text=True).stdout


# -----------------------------
# ASJP (Algerian Scientific Journal Platform)
# -----------------------------
def asjp_article_url(aid):
    return f"https://asjp.cerist.dz/en/article/{aid}"


def asjp_abstract(page_text):
    """Arabic abstract paragraph(s) from an ASJP article page."""
    m = re.search(r"\n\s*الملخص\s*\n(.*?)\n\s*(?:الكلمات المفتاحية|Keywords|Mots-clés)", page_text, re.S)
    if not m:
        return None
    lines = [l.strip() for l in m.group(1).split("\n")
             if len(re.findall(r"[ء-ي]", l)) > len(l) * 0.4]
    return " ".join(lines)


def asjp_bibtex(aid):
    """Citation fields from ASJP's official BibTeX export."""
    b = subprocess.run(["curl", "-s", "-A", UA, f"https://asjp.cerist.dz/exportCitation/bibtex/{aid}"],
                       capture_output=True, text=True).stdout
    return dict(re.findall(r"(\w+)=\{(.*?)\}", b))


def asjp_search(query):
    """Run the ASJP site search. Wrap the query in double quotes for an exact phrase.
    Returns [(article_id, title)]. Run queries sequentially: parallel sessions get throttled."""
    with tempfile.TemporaryDirectory() as tmp:
        jar = str(Path(tmp) / "cj")
        home = subprocess.run(["curl", "-s", "-c", jar, "-b", jar, "-A", "Mozilla/5.0", "https://asjp.cerist.dz/en"],
                              capture_output=True, text=True).stdout
        tok = re.search(r'name="_token" value="([^"]*)"', home)
        res = subprocess.run(["curl", "-s", "-c", jar, "-b", jar, "-L", "-A", "Mozilla/5.0", "-X", "POST",
                              "--data-urlencode", f"_token={tok.group(1) if tok else ''}",
                              "--data-urlencode", f"rechercheG={query}",
                              "https://asjp.cerist.dz/en/rechercheGeneral"],
                             capture_output=True, text=True).stdout
    out, seen = [], set()
    for m in re.finditer(r'href="https://asjp.cerist.dz/en/article/(\d+)"[^>]*>(.*?)</a>', res, re.S):
        aid = m.group(1)
        title = re.sub(r"\s+", " ", html.unescape(re.sub("<[^>]+>", "", m.group(2)))).strip()
        if aid not in seen and title:
            seen.add(aid)
            out.append((aid, title))
    return out


# -----------------------------
# Matching helpers
# -----------------------------
def term_regex(term):
    """Clitic- and article-tolerant regex for an Arabic (multi-word) term."""
    parts = []
    for w in norm(term).split():
        w = re.escape(re.sub(r"^ال", "", w)).replace("ة", "[ةت]")
        parts.append(r"(?:[وفبلك]?(?:ال|لل)?)" + w + r"[ء-ي]{0,3}")
    return re.compile(r"(?<![ء-ي])" + r"\s+".join(parts) + r"(?![ء-ي]{4})")


def snippet_regex(snippet):
    """Regex for a literal snippet with diacritics optional (source texts vary in mark order)."""
    return re.compile("[ً-ْـ]*".join(re.escape(c) for c in norm(snippet)))


def fuzzy(s):
    """Normalisation for comparing transcriptions with corrupted PDF text layers
    (drops diacritics, alef/lam forms, digits, spaces and punctuation)."""
    s = norm(s)
    return re.sub(r"[اأإآلٱ\s\"«»“”.,،؛:()\-ـ0-9٠-٩]", "", s)
