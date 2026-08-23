import streamlit as st
import pandas as pd
from utils.translations import t
from utils.helpers import ensure_session_defaults
from services.data_loader import load_universities, load_careers

st.set_page_config(page_title="Compare — KPK CareerGuide", page_icon="⚖️", layout="wide")
ensure_session_defaults(st)
lang = st.session_state["language"]

st.title(f"⚖️ {t('nav_compare', lang)}")

universities = load_universities()
careers = {c["id"]: c["name"] for c in load_careers()}
uni_names = [u["name"] for u in universities]

st.session_state.setdefault("compare_list", [])
preselected_names = [u["name"] for u in universities if u["id"] in st.session_state["compare_list"]]

selected_names = st.multiselect(
    "Select universities to compare (2-4 recommended)", uni_names,
    default=preselected_names, max_selections=4,
)

selected = [u for u in universities if u["name"] in selected_names]

if not selected:
    st.info("Select at least two universities above to compare them side by side.")
else:
    cols = st.columns(len(selected))
    for col, uni in zip(cols, selected):
        with col:
            st.markdown(f"#### {uni['name']}")
            st.caption(f"{uni['type']} • {uni['district']}")
            prog_names = [careers.get(cid, cid) for cid in uni.get("programmes", [])]
            st.markdown(f"**Programmes:** {', '.join(prog_names)}")
            st.markdown(f"**Entry test:** {uni.get('entry_test','Needs Verification')}")
            st.markdown(f"**Min %:** {uni.get('min_percentage') or 'Needs Verification'}")
            st.markdown(f"**Hostel:** {uni.get('hostel','Needs Verification')}")
            st.markdown(f"**Verification:** {uni.get('verification_status')}")

    st.divider()
    st.subheader("💰 Cost Comparison")
    rows = []
    for uni in selected:
        for cid in uni.get("programmes", []):
            fee = uni.get("approx_fee_pkr_per_year")
            rows.append({
                "University": uni["name"],
                "Programme": careers.get(cid, cid),
                "Published Tuition (PKR/yr)": fee if fee else "Not verified",
                "Hostel": uni.get("hostel", "Needs Verification"),
                "Scholarship": uni.get("scholarships", "Needs Verification"),
                "Estimated Annual Cost": fee if fee else "Not verified",
                "Last Verified": uni.get("last_verified") or "Not yet verified",
            })
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(
            "'Not verified' means this platform's dataset does not yet contain a confirmed figure from "
            "the university's official source — do not treat blank/unverified cells as PKR 0."
        )
    else:
        st.write("No programme/cost data available for the selected universities yet.")
