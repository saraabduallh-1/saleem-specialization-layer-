"""Optional second-stage rerankers. Both see a unit rendered from whatever roles it has.

CrossEncoderReranker  local multilingual cross-encoder (no API calls)
LLMListwiseReranker   one LLM call ranks the candidate list (LLM injected by caller)
"""

from __future__ import annotations

import json
import re

from ..schema import RetrievalUnit


def render_unit(u: RetrievalUnit, max_def_words: int = 40) -> str:
    """Schema-independent textual view: headword, optional translation, optional definition."""
    parts = [u.headword]
    tr = [v for vs in u.translation.values() for v in vs if v.strip()]
    if tr:
        parts[0] += f" ({tr[0]})"
    d = u.get("definition")
    if d:
        parts.append(" ".join(d[0].split()[:max_def_words]))
    elif u.get("example"):
        parts.append(" ".join(u.get("example")[0].split()[:max_def_words]))
    return ": ".join(parts)


class CrossEncoderReranker:
    def __init__(self, model_name: str, device: str | None = None, max_length: int = 256):
        from sentence_transformers import CrossEncoder
        import torch
        if device is None:
            device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.model = CrossEncoder(model_name, device=device, max_length=max_length)
        self.model_name = model_name

    def rerank(self, query: str, units: list[RetrievalUnit]) -> tuple[list[int], list[float]]:
        scores = self.model.predict([(query, render_unit(u)) for u in units], batch_size=32,
                                    show_progress_bar=False)
        order = sorted(range(len(units)), key=lambda i: -float(scores[i]))
        return order, [float(scores[i]) for i in order]


LISTWISE_SYSTEM = (
    "أنت تعيد ترتيب مدخلات معجم متخصص بحسب مطابقتها للمفهوم الذي يصفه النص. "
    "رتّب المرشحين من الأكثر مطابقة إلى الأقل، معتمدًا على تطابق المعنى مع التعريف لا على تشابه الألفاظ. "
    "أعد JSON فقط بالشكل: {\"ranking\": [\"C3\", \"C1\", ...]} يتضمن أفضل عشرة مرشحين على الأكثر."
)


class LLMListwiseReranker:
    def __init__(self, llm, top_out: int = 10):
        self.llm, self.top_out = llm, top_out

    def messages(self, query: str, units: list[RetrievalUnit]) -> list[dict]:
        lines = [f"C{i + 1}: {render_unit(u, 25)}" for i, u in enumerate(units)]
        return [{"role": "system", "content": LISTWISE_SYSTEM},
                {"role": "user", "content": "النص:\n" + query + "\n\nالمرشحون:\n" + "\n".join(lines)}]

    @staticmethod
    def parse(raw: str, n: int) -> list[int]:
        try:
            s = raw.strip().replace("```json", "").replace("```", "")
            ids = json.loads(re.search(r"\{.*\}", s, flags=re.S).group(0)).get("ranking", [])
        except Exception:
            ids = re.findall(r"C(\d+)", raw)
        out = []
        for x in ids:
            m = re.match(r"C?(\d+)", str(x).strip())
            if m and 1 <= int(m.group(1)) <= n and int(m.group(1)) - 1 not in out:
                out.append(int(m.group(1)) - 1)
        return out

    def rerank(self, query: str, units: list[RetrievalUnit]) -> tuple[list[int], str]:
        raw = self.llm(self.messages(query, units))
        top = self.parse(raw, len(units))[: self.top_out]
        rest = [i for i in range(len(units)) if i not in top]   # keep first-stage order after
        return top + rest, raw
