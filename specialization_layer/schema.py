"""Source-independent data model for the specialization layer.

A dictionary adapter turns any source into RetrievalUnits. Only `unit_id`,
`entry_id`, `source` and `headword` are required; every other semantic role is
optional and may be missing for some or all units.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Semantic roles an adapter may fill. Values are lists of strings.
# "translation" values are keyed by language: {"en": [...], "fr": [...]}.
TEXT_ROLES = ("definition", "alias", "abbreviation", "example", "domain", "note")


@dataclass
class RetrievalUnit:
    unit_id: str            # unique per retrievable unit (entry or sense)
    entry_id: str           # source entry the unit belongs to
    source: str             # dictionary identifier
    headword: str           # required
    sense_no: int | None = None
    roles: dict[str, list[str]] = field(default_factory=dict)
    translation: dict[str, list[str]] = field(default_factory=dict)

    def get(self, role: str) -> list[str]:
        return [v for v in self.roles.get(role, []) if v and v.strip()]

    def has(self, role: str) -> bool:
        if role == "translation":
            return any(v.strip() for vs in self.translation.values() for v in vs)
        return bool(self.get(role))

    def translations(self, lang: str) -> list[str]:
        return [v for v in self.translation.get(lang, []) if v and v.strip()]


@dataclass
class CapabilityProfile:
    source: str
    n_units: int
    coverage: dict[str, float]          # role -> fraction of units having it
    translation_langs: list[str]
    has_senses: bool

    def available(self, role: str) -> bool:
        return self.coverage.get(role, 0.0) > 0.0


def profile_of(source: str, units: list[RetrievalUnit]) -> CapabilityProfile:
    n = len(units)
    cov = {r: sum(u.has(r) for u in units) / n for r in TEXT_ROLES}
    cov["translation"] = sum(u.has("translation") for u in units) / n
    langs = sorted({l for u in units for l, vs in u.translation.items() if any(v.strip() for v in vs)})
    return CapabilityProfile(source, n, {k: round(v, 4) for k, v in cov.items()}, langs,
                             any(u.sense_no is not None for u in units))


def restrict_roles(units: list[RetrievalUnit], keep: set[str]) -> list[RetrievalUnit]:
    """Return copies exposing only the given roles ('translation' included by name).

    Used to simulate dictionaries with fewer fields; the headword is always kept.
    """
    out = []
    for u in units:
        out.append(RetrievalUnit(
            u.unit_id, u.entry_id, u.source, u.headword, u.sense_no,
            {r: list(v) for r, v in u.roles.items() if r in keep},
            {l: list(v) for l, v in u.translation.items()} if "translation" in keep else {}))
    return out
