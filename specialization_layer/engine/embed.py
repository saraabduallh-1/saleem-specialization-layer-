"""Dense encoder with an on-disk cache (E5 conventions: 'query: ' / 'passage: ')."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

MODEL_NAME = "intfloat/multilingual-e5-large"
CACHE = Path(__file__).resolve().parents[2] / ".cache/embeddings"
_model = None


def _get_model():
    global _model
    if _model is None:
        import torch
        from sentence_transformers import SentenceTransformer
        dev = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
        _model = SentenceTransformer(MODEL_NAME, device=dev)
    return _model


def encode(texts: list[str]) -> np.ndarray:
    if not texts:
        return np.zeros((0, 1024), dtype=np.float32)
    h = hashlib.sha256(("\x1e".join(texts) + MODEL_NAME).encode()).hexdigest()[:20]
    path = CACHE / f"{h}.npy"
    if path.exists():
        return np.load(path)
    vecs = _get_model().encode(texts, batch_size=32, convert_to_numpy=True,
                               normalize_embeddings=True, show_progress_bar=len(texts) > 64)
    CACHE.mkdir(parents=True, exist_ok=True)
    np.save(path, vecs)
    return vecs
