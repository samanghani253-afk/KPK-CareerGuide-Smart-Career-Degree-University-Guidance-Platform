import streamlit as st
from utils.translations import t
from utils.helpers import ensure_session_defaults
from utils.validation import validate_percentage
from services.data_loader import load_universities, load_careers, university_by_id, career_by_id
from services.eligibility_checker import check_eligibility

st.set_page_config(page_title="Eligibility Checker — KPK CareerGuide", page_icon="✅", layout="wide")
ensure_session_defaults(st)
lang = st.session_state["language"]

st.title(f"✅ {t('nav_eligibility', lang)}")
st.write("Answer a few questions to see whether you're likely to meet the listed minimum requirements.")

universities = load_universities()
careers = load_careers()

profile = st.session_state.get("profile", {})

with st.form("eligibility_form"):
    percentage = st.number_input(
        "Your FSc percentage (or expected)", min_value=0.0, max_value=100.0,
        value=float(profile.get("fsc_percentage") or profile.get("expected_fsc_percentage") or 0),
    )
    fsc_group = st.selectbox(
        "Your FSc group", ["Pre-Medical", "Pre-Engineering", "ICS", "General Science", "Other"],
        index=["Pre-Medical", "Pre-Engineering", "ICS", "General Science", "Other"].index(profile.get("fsc_group")) if profile.get("fsc_group") else 0,
    )
    uni_names = [u["name"] for u in universities]
    default_uni_idx = 0
    preselect = st.session_state.get("eligibility_preselect_uni")
    if preselect:
        for i, u in enumerate(universities):
            if u["id"] == preselect:
                default_uni_idx = i
                break
    uni_choice = st.selectbox("Desired university", uni_names, index=default_uni_idx)
    career_names = [c["name"] for c in careers]
    career_choice = st.selectbox("Desired programme/career", career_names)

    submitted = st.form_submit_button("Check Eligibility", type="primary")

if submitted:
    ok, err = validate_percentage(percentage)
    if not ok:
        st.error(err)
    else:
        uni = next(u for u in universities if u["name"] == uni_choice)
        career = next(c for c in careers if c["name"] == career_choice)
        result = check_eligibility(percentage, fsc_group, uni, career)

        st.subheader(result["status"])
        for reason in result["reasons"]:
            st.write(f"- {reason}")
        st.warning(result["verify_note"])

        st.divider()
        st.caption(
            "This checker distinguishes minimum eligibility from merit/closing merit, entry-test "
            "requirements, and the final admission decision — these are NOT the same thing. Meeting "
            "the minimum does not guarantee admission."
        )
