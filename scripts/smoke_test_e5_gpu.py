"""GPU smoke test for intfloat/multilingual-e5-base.

Loads the model on CUDA, encodes a few Arabic sentences, and prints the
device, embedding shape, and timing. Exits with an error if CUDA is not used.
This is a setup check only; it does not touch the project data.
"""
import sys
import time

import torch
from sentence_transformers import SentenceTransformer

MODEL_NAME = "intfloat/multilingual-e5-base"

# E5 expects a "query: " / "passage: " prefix on every input.
SENTENCES = [
    "query: ما هو التعلم الآلي؟",
    "query: كيف تعمل الشبكات العصبية الاصطناعية؟",
    "passage: التعلم العميق فرع من التعلم الآلي يعتمد على شبكات عصبية متعددة الطبقات.",
    "passage: تنظيف البيانات خطوة أساسية قبل تدريب أي نموذج.",
]


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def main():
    if not torch.cuda.is_available():
        fail("CUDA is not available to PyTorch. Check the .venv uses the CUDA build of torch.")

    print(f"torch {torch.__version__} | CUDA {torch.version.cuda} | GPU: {torch.cuda.get_device_name(0)}")

    start = time.perf_counter()
    model = SentenceTransformer(MODEL_NAME, device="cuda")
    load_seconds = time.perf_counter() - start

    model_device = next(model.parameters()).device
    if model_device.type != "cuda":
        fail(f"Model loaded on {model_device}, expected cuda.")

    # Warm-up so the timed run excludes CUDA kernel initialisation.
    model.encode(SENTENCES[:1], convert_to_tensor=True)
    torch.cuda.synchronize()

    start = time.perf_counter()
    embeddings = model.encode(SENTENCES, convert_to_tensor=True, normalize_embeddings=True)
    torch.cuda.synchronize()
    encode_seconds = time.perf_counter() - start

    if embeddings.device.type != "cuda":
        fail(f"Embeddings computed on {embeddings.device}, expected cuda.")

    print(f"Model:           {MODEL_NAME}")
    print(f"Model device:    {model_device}")
    print(f"Embedding shape: {tuple(embeddings.shape)}")
    print(f"Load time:       {load_seconds:.2f} s")
    print(f"Encode time:     {encode_seconds * 1000:.1f} ms for {len(SENTENCES)} sentences")
    print(f"Query/passage cosine similarity:\n{(embeddings[:2] @ embeddings[2:].T).cpu().numpy().round(3)}")
    print("PASS: E5 ran on CUDA.")


if __name__ == "__main__":
    main()
