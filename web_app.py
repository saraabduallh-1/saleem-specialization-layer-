from __future__ import annotations

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
    # The git version is part of the cache key. After git pull, the next rerun
    # builds a fresh runtime from the updated code/data.
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
      .block-container { max-width: 820px; padding-top: 3rem; }
      h1 { text-align: center; }
      .stTextArea textarea {
        direction: rtl !important;
        text-align: right !important;
        min-height: 180px !important;
        font-size: 1.05rem !important;
        line-height: 1.9 !important;
      }
      .result-card {
        direction: rtl;
        text-align: right;
        border: 1px solid rgba(128,128,128,.22);
        border-radius: 14px;
        padding: 22px 24px;
        margin-top: 20px;
        font-size: 1.1rem;
      }
      .result-term {
        font-size: 1.55rem;
        font-weight: 700;
        margin-top: 8px;
      }
      .muted {
        opacity: .58;
        text-align: center;
        font-size: .78rem;
        margin-top: 2rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("طبقة سليم")

text = st.text_area(
    "النص",
    placeholder="اكتب النص هنا...",
    label_visibility="collapsed",
)

run = st.button("حلّل النص", type="primary", use_container_width=True)

if run:
    if not text.strip():
        st.warning("اكتب نصًا أولًا.")
    else:
        version = git_version()
        with st.spinner("جاري التحليل..."):
            layer = load_layer(version)
            result = layer.analyze(text)

        if result["status"] == "SPECIALIZED":
            st.markdown(
                f"""
                <div class="result-card">
                  <div>المصطلح التخصصي الأنسب</div>
                  <div class="result-term">{result["term"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="result-card">
                  <div>النتيجة</div>
                  <div class="result-term">لا يوجد مصطلح تخصصي مؤكد</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown(
    f'<div class="muted">نسخة النظام: {git_version()}</div>',
    unsafe_allow_html=True,
)
