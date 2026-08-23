import streamlit as st
from datetime import datetime
from utils.translations import t
from utils.helpers import ensure_session_defaults

st.set_page_config(page_title="My Report — KPK CareerGuide", page_icon="📄", layout="wide")
ensure_session_defaults(st)
lang = st.session_state["language"]

st.title(f"📄 {t('nav_report', lang)}")

if not st.session_state.get("assessment_complete"):
    st.warning("Please complete the assessment first to generate your report.")
    if st.button("Go to Assessment"):
        st.switch_page("pages/1_Assessment.py")
    st.stop()

profile = st.session_state["profile"]
recs = st.session_state["recommendations"] or []
uni_matches = st.session_state["university_matches"] or []
interests = st.session_state["interests"]
skills = st.session_state["skills"]
personality = st.session_state["personality"]

st.subheader("My Career & University Guidance Report")
st.caption(f"Generated: {datetime.now().strftime('%Y-%m-%d')}")

with st.container(border=True):
    st.markdown("#### 1. Student Profile")
    st.write(f"Name: {profile.get('name') or 'Not provided'}")
    st.write(f"District/City: {profile.get('district','-')}, {profile.get('city','-')}")
    st.write(f"FSc Group: {profile.get('fsc_group','-')}")
    st.write(f"FSc %: {profile.get('fsc_percentage') or profile.get('expected_fsc_percentage') or 'Not provided'}")
    st.write(f"Budget: {profile.get('budget_band','-')}")
    st.write(f"Preferred Location: {profile.get('preferred_location','-')}")

with st.container(border=True):
    st.markdown("#### 6-7. Recommended Careers & Degrees")
    for i, rec in enumerate(recs, start=1):
        career = rec["career"]
        st.write(f"**#{i} {career['name']}** — Match Score: {rec['match_score']}/100")
        st.caption(f"Entry test: {career.get('entry_test')} | Duration: {career.get('degree_duration')}")

with st.container(border=True):
    st.markdown("#### 8. Recommended Universities")
    for m in uni_matches[:5]:
        uni = m["university"]
        st.write(f"**{uni['name']}** — Match: {m['match_score']}% — {uni.get('verification_status')}")

st.divider()
st.markdown("#### Skills to Develop")
if recs:
    top_career = recs[0]["career"]
    needed = [tag for tag in top_career.get("skill_tags", []) if skills.get(tag, 0) < 4]
    if needed:
        st.write("Based on your top career match, consider strengthening: " + ", ".join(needed))
    else:
        st.write("Your self-rated skills already align well with your top career match.")

st.divider()
st.markdown("#### Next Steps")
st.write("""
1. Verify entry-test requirements and current dates on official sources.
2. Confirm eligibility and merit trends directly with your top-matched universities.
3. Explore scholarship options if budget is a concern.
4. Begin entry-test preparation early.
5. Discuss this report with a parent, teacher, or counsellor.
""")

st.divider()
st.subheader("Download Reports")
col1, col2 = st.columns(2)

with col1:
    if st.button("📄 Generate Student PDF Report", use_container_width=True):
        try:
            from services.report_generator import generate_pdf_report
            pdf_bytes = generate_pdf_report(profile, recs, uni_matches, lang, parent_friendly=False)
            st.download_button(
                "⬇️ Download Student Report (PDF)", data=pdf_bytes,
                file_name="my_career_guidance_report.pdf", mime="application/pdf",
                use_container_width=True,
            )
        except ImportError:
            st.error("PDF generation requires the 'reportlab' package. Please install it (see requirements.txt) and restart the app.")
        except Exception as e:
            st.error(f"Could not generate the PDF report right now: {e}")

with col2:
    if st.button("👨‍👩‍👧 Generate Parent-Friendly Report", use_container_width=True):
        try:
            from services.report_generator import generate_pdf_report
            pdf_bytes = generate_pdf_report(profile, recs, uni_matches, lang, parent_friendly=True)
            st.download_button(
                "⬇️ Download Parent-Friendly Report (PDF)", data=pdf_bytes,
                file_name="parent_friendly_career_report.pdf", mime="application/pdf",
                use_container_width=True,
            )
        except ImportError:
            st.error("PDF generation requires the 'reportlab' package. Please install it (see requirements.txt) and restart the app.")
        except Exception as e:
            st.error(f"Could not generate the PDF report right now: {e}")

st.info(t("disclaimer", lang))
