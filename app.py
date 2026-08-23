import base64
import os
import streamlit as st
from utils.translations import t, language_options
from utils.helpers import ensure_session_defaults

st.set_page_config(
    page_title="KPK CareerGuide",
    page_icon="🎓",
    layout="wide",
)

ensure_session_defaults(st)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")


@st.cache_data
def _b64_svg(filename: str):
    """Returns the base64-encoded file, or None if it's missing — so a
    missing/misconfigured asset degrades gracefully instead of crashing
    the whole app (e.g. if assets/ wasn't pushed to the deployed repo)."""
    path = os.path.join(ASSETS_DIR, filename)
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return None


paper_bg_b64 = _b64_svg("paper_bg.svg")
student_hero_b64 = _b64_svg("student_hero.svg")

if paper_bg_b64 is None or student_hero_b64 is None:
    st.warning(
        "🖼️ Background/illustration assets are missing from this deployment "
        "(expected at `assets/paper_bg.svg` and `assets/student_hero.svg` next to `app.py`). "
        "The app will still work — just without the decorative graphics. "
        "Make sure the `assets/` folder was pushed to your GitHub repo."
    )

# ---- Design tokens & background ----
# Palette: paper cream #F7F1E1, deep teal ink #12403D, warm ochre accent #C98A2E,
# sage #6E8F71, brick #96412A (echoed from the illustration's building).
_bg_css = (
    f'background-image: url("data:image/svg+xml;base64,{paper_bg_b64}");'
    if paper_bg_b64 else "background-color: #F7F1E1;"
)
st.markdown(
    f"""
    <style>
    .stApp {{
        {_bg_css}
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}
    .kpk-hero-card {{
        background: rgba(247, 241, 225, 0.72);
        border: 1px solid rgba(18, 64, 61, 0.12);
        border-radius: 18px;
        padding: 2.2rem 2.4rem;
        backdrop-filter: blur(2px);
    }}
    .kpk-hero-title {{
        font-family: Georgia, 'Times New Roman', serif;
        color: #12403D;
        font-size: 2.6rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        line-height: 1.15;
    }}
    .kpk-hero-tagline {{
        font-family: Georgia, 'Times New Roman', serif;
        color: #96412A;
        font-size: 1.3rem;
        font-style: italic;
        margin-bottom: 0.8rem;
    }}
    .kpk-hero-subtitle {{
        color: #2B2620;
        font-size: 1.05rem;
        max-width: 46ch;
    }}
    .kpk-hero-illustration img {{
        max-width: 100%;
        filter: drop-shadow(0 8px 18px rgba(18, 64, 61, 0.18));
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Language selector (top of app, applies globally via session_state) ----
top_l, top_r = st.columns([3, 1])
with top_r:
    st.session_state["language"] = st.selectbox(
        "🌐", language_options(),
        index=language_options().index(st.session_state["language"]),
        label_visibility="collapsed",
    )
lang = st.session_state["language"]

# ---- Hero section: folded-paper card with the student/university illustration ----
st.markdown('<div class="kpk-hero-card">', unsafe_allow_html=True)
hero_l, hero_r = st.columns([3, 2])
with hero_l:
    st.markdown(f'<div class="kpk-hero-title">🎓 {t("app_title", lang)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpk-hero-tagline">{t("tagline", lang)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpk-hero-subtitle">{t("subtitle", lang)}</div>', unsafe_allow_html=True)
with hero_r:
    if student_hero_b64:
        st.markdown(
            f'<div class="kpk-hero-illustration"><img src="data:image/svg+xml;base64,{student_hero_b64}" '
            f'alt="Illustration of a student looking up happily at a university building"/></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown("### 🎓🏫")  # simple emoji fallback if the illustration asset is missing
st.markdown("</div>", unsafe_allow_html=True)

st.write("")
st.divider()

col1, col2 = st.columns([2, 1])
with col1:
    if st.button(f"🚀 {t('start_assessment', lang)}", type="primary", use_container_width=True):
        st.switch_page("pages/1_Assessment.py")
    if st.button(f"🏫 {t('explore_universities', lang)}", use_container_width=True):
        st.switch_page("pages/4_Universities.py")

with col2:
    if st.button(f"⚖️ {t('compare_universities', lang)}", use_container_width=True):
        st.switch_page("pages/7_Compare.py")
    if st.button(f"✅ {t('check_eligibility', lang)}", use_container_width=True):
        st.switch_page("pages/6_Eligibility.py")
    if st.button(f"🧭 {t('explore_careers', lang)}", use_container_width=True):
        st.switch_page("pages/3_Careers.py")

st.divider()

with st.expander("About this platform / research basis"):
    st.markdown("""
This platform is built around findings from a student survey in Peshawar/KPK:
- **86%** of respondents were willing to use a system combining FSc group, marks, interests and skills.
- **~68%** had never taken a proper aptitude/personality/career test.
- **~82%** had experienced confusion about universities, degrees or entry tests.
- **~46%** reported wasting money on an entry test or application due to eligibility uncertainty.

Based on this, the platform follows a two-stage **Assess → Recommend** flow, uses verified-or-labeled
university/eligibility/cost data, and generates parent-shareable reports.
    """)

st.info(
    "⚠️ **University, fee, entry-test and affiliation data in this starter version is a demonstration "
    "dataset and is explicitly marked 'Needs Verification' where not confirmed.** Always verify final "
    "information on the university's official website before making decisions."
)

st.caption(t("disclaimer", lang))
st.caption("Illustration is an original graphic, not a photo of a real institution or person.")
