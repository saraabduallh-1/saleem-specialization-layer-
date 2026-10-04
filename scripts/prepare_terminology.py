import json
import re
from pathlib import Path

# -----------------------------
# Paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_FILE = PROJECT_ROOT / "data" / "raw" / "data_ai" / "siwar_data_ai_dictionary.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "data_ai" / "terminology_base.json"


# -----------------------------
# Helpers
# -----------------------------
def extract_english_translation(translations):
    """
    Extract English term from translations.
    """
    for item in translations or []:
        if item.get("language") == "eng":
            return item.get("lemma", "").strip()
    return ""


# Compact parenthesized Latin/alphanumeric form (no spaces) with at least two
# uppercase letters: SVM, TF-IDF, A2A, GenAI, IoT, ReLU, LoRA, MLOps, Seq2Seq.
# Excludes phrases with spaces ("or Data Cleaning") and plain words ("Bagging", "Tanh").
ABBREVIATION = r"(?=(?:[^A-Z()]*[A-Z]){2})[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9]"


def extract_abbreviations(english_term):
    """
    Extract abbreviations written inside parentheses.
    Examples:
    Support Vector Machine (SVM) -> ["SVM"]
    Generative Artificial Intelligence (GenAI) -> ["GenAI"]
    """
    if not english_term:
        return []

    matches = re.findall(r"\((" + ABBREVIATION + r")\)", english_term)

    # remove duplicates while preserving order
    seen = set()
    abbreviations = []

    for match in matches:
        if match not in seen:
            seen.add(match)
            abbreviations.append(match)

    return abbreviations


def clean_english_term(english_term):
    """
    Remove abbreviation from the English term.
    Example:
    Support Vector Machine (SVM)
    -> Support Vector Machine
    """
    if not english_term:
        return ""

    cleaned = re.sub(r"\s*\(" + ABBREVIATION + r"\)\s*$", "", english_term)
    return cleaned.strip()


ALIAS_INTRO = re.compile(
    r'و?يُ?طلق\s+علي(?:ه|ها)\s+[أا]يض(?:ًا|اً|ا)\s*'
)
# One quoted alias, optionally followed by more joined with "أو" / "،" / "، أو".
ALIAS_CHAIN = re.compile(r'"([^"]+)"((?:\s*(?:،\s*)?(?:أو\s*)?"[^"]+")*)')


def extract_aliases(definition):
    """
    Extract every alias stated explicitly in the definition, e.g.:
    ويُطلق عليه أيضًا "..."
    ويطلق عليها أيضا "..." أو "..."
    يُطلق عليه أيضًا "..."، أو "..."، أو "..."
    """
    if not definition:
        return []

    aliases = []

    for intro in ALIAS_INTRO.finditer(definition):
        chain = ALIAS_CHAIN.match(definition, intro.end())
        if chain:
            aliases.extend(re.findall(r'"([^"]+)"', chain.group(0)))

    # remove duplicates while preserving order
    return list(dict.fromkeys([a.strip() for a in aliases if a.strip()]))


def extract_canonical_term(definition):
    """
    Detect entries like:
    انظر "المصطلح"
    """
    if not definition:
        return None

    match = re.search(r'انظر\s+"([^"]+)"', definition)

    if match:
        return match.group(1).strip()

    return None


# -----------------------------
# Main
# -----------------------------
def main():
    print("Reading Siwar dictionary...")

    with open(RAW_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    entries = data.get("entries", [])

    # Arabic entries only
    arabic_entries = [
        entry for entry in entries
        if entry.get("language") == "ar"
    ]

    print(f"Arabic entries found: {len(arabic_entries)}")

    processed = []

    for entry in arabic_entries:
        english_raw = extract_english_translation(entry.get("translations", []))

        abbreviations = extract_abbreviations(english_raw)
        english_term = clean_english_term(english_raw)

        definition = entry.get("definition", "").strip()

        aliases = extract_aliases(definition)
        canonical_term = extract_canonical_term(definition)

        item = {
            "id": entry.get("id"),

            "source": "siwar",
            "source_dictionary": "data_ai",
            "domain": "data_ai",

            "term": entry.get("lemma", "").strip(),
            "lemma_type": entry.get("lemmaType"),
            "pos": entry.get("pos"),

            "definition": definition,

            "english_term": english_term,
            "abbreviations": abbreviations,

            "aliases": aliases,

            "canonical_term": canonical_term,
            "canonical_term_id": None,

            "variants": [],
            "positive_examples": [],
            "negative_examples": []
        }

        processed.append(item)

    # Create output folder if needed
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(processed)} entries to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
    