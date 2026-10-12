from __future__ import annotations

import html
import subprocess
from pathlib import Path

import streamlit as st

from specialization_layer.runtime import SpecializationRuntime

ROOT = Path(__file__).resolve().parent


def git_version() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            text=True,
        ).strip()
    except Exception:
        return "local"


@st.cache_resource(show_spinner=False)
def load_layer(version: str) -> SpecializationRuntime:
    # Git version participates in the cache key. After git pull + rerun, the
    # updated runtime/data are loaded into a fresh layer instance.
    return SpecializationRuntime()


st.set_page_config(
    page_title="طبقة سليم",
    page_icon="س",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      html, body, [class*="css"] { direction: rtl; }
      .block-container { max-width: 860px; padding-top: 3rem; }
      h1 { text-align: center; }
      .stTextArea textarea {
        direction: rtl !important;
        text-align: right !important;
        min-height: 220px !important;
        font-size: 1.08rem !important;
        line-height: 1.9 !important;
      }
      .result-card {
        direction: rtl;
        text-align: right;
        border: 1px solid rgba(128,128,128,.22);
        border-radius: 14px;
        padding: 22px 24px;
        margin-top: 20px;
      }
      .result-label {
        font-size: .9rem;
        opacity: .62;
        margin-bottom: 10px;
      }
      .result-text {
        font-size: 1.12rem;
        line-height: 2;
        white-space: pre-wrap;
      }
      .terms-line {
        direction: rtl;
        text-align: right;
        font-size: .88rem;
        opacity: .68;
        margin-top: 12px;
      }
      .muted {
        opacity: .5;
        text-align: center;
        font-size: .76rem;
        margin-top: 2rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("طبقة سليم")

text = st.text_area(
    "النص",
    placeholder="اكتب النص الذي تبي تخصصه وتحسنه...",
    label_visibility="collapsed",
)

run = st.button("خصّص النص", type="primary", use_container_width=True)

if run:
    if not text.strip():
        st.warning("اكتب نصًا أولًا.")
    else:
        version = git_version()
        with st.spinner("جاري تخصيص النص..."):
            layer = load_layer(version)
            result = layer.analyze(text)

        output = html.escape(result.get("output") or text)
        st.markdown(
            f"""
            <div class="result-card">
              <div class="result-label">النص بعد التخصيص</div>
              <div class="result-text">{output}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        terms = [x["term"] for x in result.get("terms", []) if x.get("term")]
        if terms:
            st.markdown(
                '<div class="terms-line">المصطلحات التي اعتمدتها الطبقة: '
                + "، ".join(html.escape(x) for x in terms)
                + "</div>",
                unsafe_allow_html=True,
            )

st.markdown(
    f'<div class="muted">نسخة النظام: {git_version()}</div>',
    unsafe_allow_html=True,
)
