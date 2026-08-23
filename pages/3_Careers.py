import streamlit as st
from utils.translations import t
from utils.helpers import ensure_session_defaults
from services.career_matcher import all_careers, alternative_careers

st.set_page_config(page_title="Careers — KPK CareerGuide", page_icon="🧭", layout="wide")
ensure_session_defaults(st)
lang = st.session_state["language"]

st.title(f"🧭 {t('nav_careers', lang)}")
st.caption("Browse careers independent of the full assessment. Run the Assessment for a personalized ranked match.")

careers = all_careers()
groups = sorted({g for c in careers for g in c.get("fsc_groups", [])})
selected_group = st.selectbox("Filter by FSc group", ["All"] + groups)

filtered = careers if selected_group == "All" else [c for c in careers if selected_group in c.get("fsc_groups", [])]

search = st.text_input("🔎 Search careers", "")
if search:
    filtered = [c for c in filtered if search.lower() in c["name"].lower()]

st.write(f"Showing {len(filtered)} career(s)")

for career in filtered:
    with st.expander(f"{career['name']}"):
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(f"**FSc groups:** {', '.join(career.get('fsc_groups', []))}")
            st.markdown(f"**Career paths:** {', '.join(career.get('career_paths', []))}")
            st.markdown(f"**Advantages:** {', '.join(career.get('advantages', []))}")
            st.markdown(f"**Challenges:** {', '.join(career.get('challenges', []))}")
            alts = alternative_careers(career["id"])
            if alts:
                st.markdown(f"**Alternative careers to consider:** {', '.join(a['name'] for a in alts)}")
        with c2:
            st.markdown(f"**Min. FSc %:** {career.get('min_percentage','-')}")
            st.markdown(f"**Entry test:** {career.get('entry_test','Needs Verification')}")
            st.markdown(f"**Duration:** {career.get('degree_duration','Needs Verification')}")
            st.markdown(f"**Est. cost band:** {career.get('typical_annual_cost_band','Needs Verification')}")
        st.caption(career.get("notes", ""))
