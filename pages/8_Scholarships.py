import streamlit as st
from utils.translations import t
from utils.helpers import ensure_session_defaults
from services.data_loader import load_scholarships, load_universities

st.set_page_config(page_title="Scholarships — KPK CareerGuide", page_icon="🎓", layout="wide")
ensure_session_defaults(st)
lang = st.session_state["language"]

st.title(f"🎓 {t('nav_scholarships', lang)}")

scholarships = load_scholarships()
universities = load_universities()

search = st.text_input("🔎 Search scholarships")
filtered = scholarships
if search:
    s = search.lower()
    filtered = [sc for sc in filtered if s in sc["name"].lower() or s in sc.get("eligibility", "").lower()]

st.write(f"Showing {len(filtered)} scholarship(s)")

for sc in filtered:
    with st.container(border=True):
        st.markdown(f"### {sc['name']}")
        st.markdown(f"**Eligibility:** {sc.get('eligibility','Needs Verification')}")
        st.markdown(f"**Deadline:** {sc.get('deadline','Needs Verification')}")
        st.markdown(f"**Coverage:** {sc.get('coverage','Needs Verification')}")
        st.markdown(f"**How to apply:** {sc.get('application_method','Needs Verification')}")
        st.caption(f"Official source: {sc.get('official_source','Not specified')} | Verified: {sc.get('verification_date') or 'Not yet verified'}")

st.warning(
    "Scholarship deadlines and eligibility criteria change frequently and are never fabricated by "
    "this platform. Always confirm the current cycle's details directly through the official source "
    "listed above before applying."
)
