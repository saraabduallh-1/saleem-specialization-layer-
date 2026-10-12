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
    return SpecializationRuntime()


st.set_page_config(
    page_title="خصّص",
    page_icon="خ",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      html, body, [class*="css"] { direction: rtl; }
      .stApp { background: #f8fafc; color: #1f2937; }
      .block-container { max-width: 900px; padding-top: 3rem; }
      h1 { text-align: center; }
      .stTextArea textarea {
        direction: rtl !important;
        text-align: right !important;
        min-height: 220px !important;
        font-size: 1.08rem !important;
        line-height: 1.9 !important;
        background: #ffffff !important;
        color: #1f2937 !important;
      }
      .result-card, .meta-card {
        direction: rtl;
        text-align: right;
        background: #ffffff;
        border: 1px solid rgba(31,41,55,.12);
        border-radius: 14px;
        padding: 20px 22px;
        margin-top: 18px;
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
      .meta-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0,1fr));
        gap: 12px 18px;
      }
      .meta-item {
        border-bottom: 1px solid rgba(128,128,128,.12);
        padding-bottom: 9px;
      }
      .meta-key {
        font-size: .78rem;
        opacity: .55;
        margin-bottom: 3px;
      }
      .meta-value {
        font-size: 1rem;
        font-weight: 600;
      }
      .terms {
        font-size: 1rem;
        line-height: 2;
      }
      .muted {
        opacity: .5;
        text-align: center;
        font-size: .76rem;
        margin-top: 2rem;
      }
      @media (max-width: 650px) {
        .meta-grid { grid-template-columns: 1fr; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("خصّص")

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
        with st.spinner("جاري تحليل النص وتخصيصه..."):
            layer = load_layer(version)
            result = layer.analyze(text)

        profile = result.get("writing_profile") or {}
        domain = html.escape(result.get("domain") or "غير محدد")
        writing_type = html.escape(profile.get("writing_type") or "غير محدد")
        register = html.escape(profile.get("register") or "غير محدد")
        purpose = html.escape(profile.get("purpose") or "غير محدد")
        style_note = html.escape(profile.get("style_note") or "—")

        st.markdown(
            f"""
            <div class="meta-card">
              <div class="result-label">تحليل النص</div>
              <div class="meta-grid">
                <div class="meta-item">
                  <div class="meta-key">المجال التخصصي</div>
                  <div class="meta-value">{domain}</div>
                </div>
                <div class="meta-item">
                  <div class="meta-key">نوع الكتابة</div>
                  <div class="meta-value">{writing_type}</div>
                </div>
                <div class="meta-item">
                  <div class="meta-key">الأسلوب اللغوي</div>
                  <div class="meta-value">{register}</div>
                </div>
                <div class="meta-item">
                  <div class="meta-key">الغرض من النص</div>
                  <div class="meta-value">{purpose}</div>
                </div>
              </div>
              <div style="margin-top:14px">
                <div class="meta-key">طريقة الحفاظ على الأسلوب</div>
                <div>{style_note}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        terms = [x["term"] for x in result.get("terms", []) if x.get("term")]
        terms_html = (
            "، ".join(html.escape(x) for x in terms)
            if terms
            else "لم تعتمد الطبقة مصطلحًا من المعجم في هذا النص."
        )

        st.markdown(
            f"""
            <div class="meta-card">
              <div class="result-label">المصطلحات التي اعتمدتها الطبقة</div>
              <div class="terms">{terms_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        output = html.escape(result.get("output") or text)
        st.markdown(
            f"""
            <div class="result-card">
              <div class="result-label">النص بعد التخصيص والتحسين</div>
              <div class="result-text">{output}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    f'<div class="muted">نسخة النظام: {git_version()}</div>',
    unsafe_allow_html=True,
)
