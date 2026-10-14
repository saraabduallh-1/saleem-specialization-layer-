"""Conservative checks for manual Arabic rewrite experiments, not semantic validation."""
from __future__ import annotations
import re
from dataclasses import dataclass, field

DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed\u0640]")
EGYPTIAN = (r"(?<!\w)إيه(?!\w)",r"(?<!\w)ازاي(?!\w)",r"(?<!\w)إزاي(?!\w)",
            r"(?<!\w)عايز(?:ة|ين)?(?!\w)",r"(?<!\w)مش(?!\w)",
            r"(?<!\w)بيحفظ(?!\w)",r"(?<!\w)بيعمل(?!\w)")

def norm(s: str) -> str:
    s = DIAC.sub("", s).casefold()
    return " ".join(re.sub(r"[إأآٱ]", "ا", s).replace("ى", "ي").split())

def contains_term(text: str, term: str) -> bool:
    term, text = norm(term), norm(text)
    if not term:
        return False
    return re.search(r"(?<!\w)" + re.escape(term).replace(r"\ ", r"\s+") + r"(?!\w)", text) is not None

@dataclass
class RewriteCheck:
    warnings: list[str] = field(default_factory=list)
    checks: dict[str, bool] = field(default_factory=dict)
    @property
    def passed(self) -> bool:
        return not self.warnings

def check_rewrite(source: str, output: str, *, style: str | None = None,
                  terms: list[str] | None = None, preserve_newlines: bool = False) -> RewriteCheck:
    """Terms must be approved upstream; cannot establish meaning or dialect fidelity."""
    r = RewriteCheck()
    r.checks["nonempty"] = bool(output.strip())
    if not r.checks["nonempty"]:
        r.warnings.append("empty_output")
    missing = [t for t in (terms or []) if t.strip() and not contains_term(output, t)]
    r.checks["canonical_terms_present"] = not missing
    if missing:
        r.warnings.append("missing_canonical_terms: " + ", ".join(missing))
    if style == "saudi_colloquial":
        markers = [p for p in EGYPTIAN if re.search(p, output, re.I) and not re.search(p, source, re.I)]
        r.checks["no_obvious_egyptian_drift"] = not markers
        if markers:
            r.warnings.append("possible_egyptian_dialect_drift")
    if preserve_newlines and "\n" in source:
        r.checks["newlines_preserved"] = "\n" in output
        if not r.checks["newlines_preserved"]:
            r.warnings.append("newlines_lost")
    return r
