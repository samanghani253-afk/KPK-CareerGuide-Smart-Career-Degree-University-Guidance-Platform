import streamlit as st
from utils.translations import t
from utils.helpers import ensure_session_defaults
from services.data_loader import load_colleges, load_universities, university_by_id

st.set_page_config(page_title="Colleges — KPK CareerGuide", page_icon="🏛️", layout="wide")
ensure_session_defaults(st)
lang = st.session_state["language"]

st.title(f"🏛️ {t('nav_colleges', lang)}")
st.caption("University → Affiliated Colleges → Programmes → Eligibility → Admission Information")

universities = load_universities()
colleges = load_colleges()

uni_options = ["All"] + [u["name"] for u in universities]
selected_uni_name = st.selectbox("Filter by affiliating university", uni_options)

filtered = colleges
if selected_uni_name != "All":
    uni_id = next((u["id"] for u in universities if u["name"] == selected_uni_name), None)
    filtered = [c for c in filtered if c.get("university_affiliation") == uni_id]

if not filtered:
    st.info(
        "No affiliated-college records match this filter yet. This is a starter dataset — "
        "affiliated colleges should be added from each university's official published list "
        "(see MASTER PROMPT section 12)."
    )

for college in filtered:
    parent = university_by_id(college.get("university_affiliation"))
    with st.container(border=True):
        st.markdown(f"### {college['name']}")
        st.caption(f"Affiliated with: {parent['name'] if parent else 'Unknown'} • {college.get('verification_status')}")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**City/District:** {college.get('city','-')}, {college.get('district','-')}")
            st.markdown(f"**Type:** {college.get('type','Needs Verification')}")
            st.markdown(f"**Programmes:** {', '.join(college.get('programmes', []))}")
        with c2:
            st.markdown(f"**Eligibility:** {college.get('eligibility','Needs Verification')}")
            st.markdown(f"**Entry requirements:** {college.get('entry_requirements','Needs Verification')}")
            st.markdown(f"**Fee status:** {college.get('fee_status','Needs Verification')}")
        st.caption(f"Source: {college.get('data_source','Not specified')} | Last verified: {college.get('last_verified') or 'Not yet verified'}")
