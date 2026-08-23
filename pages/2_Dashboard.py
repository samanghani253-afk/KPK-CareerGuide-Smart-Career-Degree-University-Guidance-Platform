import streamlit as st
from utils.translations import t
from utils.helpers import ensure_session_defaults

st.set_page_config(page_title="Dashboard — KPK CareerGuide", page_icon="📊", layout="wide")
ensure_session_defaults(st)
lang = st.session_state["language"]

st.title(f"📊 {t('dashboard', lang)}")

if not st.session_state.get("assessment_complete"):
    st.warning("Please complete the assessment first to see your dashboard.")
    if st.button("Go to Assessment"):
        st.switch_page("pages/1_Assessment.py")
    st.stop()

profile = st.session_state["profile"]
recs = st.session_state["recommendations"] or []
uni_matches = st.session_state["university_matches"] or []

# ---- Summary cards ----
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Academic Score", f"{profile.get('fsc_percentage') or profile.get('expected_fsc_percentage') or '-'}%")
c2.metric("Top Career Match", f"{recs[0]['match_score']}%" if recs else "-")
c3.metric("Top University Match", f"{uni_matches[0]['match_score']}%" if uni_matches else "-")
budget_display = profile.get("budget_band", "-")
c4.metric("Budget", budget_display if len(budget_display) < 14 else "Set")
c5.metric("Eligibility", "See below")
c6.metric("Assessment", "Complete ✅")

st.divider()

st.subheader(f"🏆 {t('top_careers', lang)}")
for i, rec in enumerate(recs, start=1):
    career = rec["career"]
    with st.expander(f"#{i} {career['name']} — Match Score: {rec['match_score']}%", expanded=(i == 1)):
        colA, colB = st.columns([2, 1])
        with colA:
            st.markdown(f"**Why this score?**")
            for k, v in rec["breakdown"].items():
                st.write(f"- {k}: {v}/{rec['max_breakdown'][k]}")
            st.markdown(f"**Career paths:** {', '.join(career.get('career_paths', []))}")
            st.markdown(f"**Advantages:** {', '.join(career.get('advantages', []))}")
            st.markdown(f"**Challenges:** {', '.join(career.get('challenges', []))}")
        with colB:
            st.markdown(f"**Entry test:** {career.get('entry_test','Needs Verification')}")
            st.markdown(f"**Duration:** {career.get('degree_duration','Needs Verification')}")
            st.markdown(f"**Est. annual cost band:** {career.get('typical_annual_cost_band','Needs Verification')}")
            st.caption(career.get("notes", ""))

st.divider()
st.subheader("🏫 Your Top Universities")
for m in uni_matches[:5]:
    uni = m["university"]
    with st.expander(f"{uni['name']} — Match: {m['match_score']}%"):
        for kind, text in m["flags"]:
            icon = "✓" if kind == "check" else "⚠"
            st.write(f"{icon} {text}")
        st.caption(f"Verification status: {uni.get('verification_status', 'Needs verification')}")

st.divider()
st.subheader(f"➡️ {t('next_steps', lang)}")
next_steps = [
    "Verify the entry-test requirements and dates for your top career choices on official sources.",
    "Confirm current eligibility criteria and merit trends directly with your top-matched universities.",
    "Check scholarship options if budget is a concern (see the Scholarships page).",
    "Start preparing for the relevant entry test (e.g. MDCAT, ECAT) well in advance.",
    "Download your full report to share with parents or a counsellor.",
]
for s in next_steps:
    st.write(f"- {s}")

col1, col2 = st.columns(2)
with col1:
    if st.button("📄 Go to Full Report", use_container_width=True):
        st.switch_page("pages/9_Report.py")
with col2:
    if st.button("✅ Check Eligibility in Detail", use_container_width=True):
        st.switch_page("pages/6_Eligibility.py")
