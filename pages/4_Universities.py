import streamlit as st
from utils.translations import t
from utils.helpers import ensure_session_defaults
from services.data_loader import load_universities, load_careers, colleges_for_university

st.set_page_config(page_title="Universities — KPK CareerGuide", page_icon="🏫", layout="wide")
ensure_session_defaults(st)
lang = st.session_state["language"]

st.title(f"🏫 {t('nav_universities', lang)}")

universities = load_universities()
careers = {c["id"]: c["name"] for c in load_careers()}

with st.sidebar:
    st.header("Filters")
    districts = sorted({u["district"] for u in universities})
    district_filter = st.multiselect("District", districts)
    type_filter = st.multiselect("Public/Private", sorted({u["type"] for u in universities}))
    programme_filter = st.multiselect("Programme", list(careers.values()))
    search = st.text_input("Search university or programme")
    sort_by = st.selectbox("Sort by", ["Name (A-Z)", "Public first"])

filtered = universities
if district_filter:
    filtered = [u for u in filtered if u["district"] in district_filter]
if type_filter:
    filtered = [u for u in filtered if u["type"] in type_filter]
if programme_filter:
    ids = [cid for cid, name in careers.items() if name in programme_filter]
    filtered = [u for u in filtered if any(cid in u.get("programmes", []) for cid in ids)]
if search:
    s = search.lower()
    filtered = [u for u in filtered if s in u["name"].lower() or any(s in careers.get(cid, "").lower() for cid in u.get("programmes", []))]

if sort_by == "Name (A-Z)":
    filtered = sorted(filtered, key=lambda u: u["name"])
elif sort_by == "Public first":
    filtered = sorted(filtered, key=lambda u: (u["type"] != "Public", u["name"]))

st.write(f"Showing {len(filtered)} institution(s)")

for uni in filtered:
    with st.container(border=True):
        st.markdown(f"### {uni['name']}")
        badge = "🟢 " + uni["verification_status"] if uni["verification_status"] == "Verified" else "🟡 " + uni["verification_status"]
        st.caption(f"{uni['type']} • {uni['district']} • {badge}")
        c1, c2 = st.columns([2, 1])
        with c1:
            prog_names = [careers.get(cid, cid) for cid in uni.get("programmes", [])]
            st.markdown(f"**Programmes:** {', '.join(prog_names) if prog_names else 'Not listed'}")
            st.markdown(f"**Faculties:** {', '.join(uni.get('faculties', []))}")
            st.markdown(f"**Entry test:** {uni.get('entry_test', 'Needs Verification')}")
        with c2:
            st.markdown(f"**Website:** {uni.get('website', 'Needs Verification')}")
            st.markdown(f"**Last verified:** {uni.get('last_verified') or 'Not yet verified'}")
            n_colleges = len(colleges_for_university(uni["id"]))
            if n_colleges:
                st.markdown(f"**Affiliated colleges on file:** {n_colleges}")

        bcol1, bcol2, bcol3 = st.columns(3)
        if bcol1.button("Check My Eligibility", key=f"elig_{uni['id']}"):
            st.session_state["eligibility_preselect_uni"] = uni["id"]
            st.switch_page("pages/6_Eligibility.py")
        if bcol2.button("Compare", key=f"cmp_{uni['id']}"):
            st.session_state.setdefault("compare_list", [])
            if uni["id"] not in st.session_state["compare_list"]:
                st.session_state["compare_list"].append(uni["id"])
            st.switch_page("pages/7_Compare.py")
        if uni.get("website") and uni["website"] != "Needs Verification":
            bcol3.link_button("Visit Website", uni["website"])

        with st.expander("Affiliated Colleges"):
            affiliated = colleges_for_university(uni["id"])
            if not affiliated:
                st.write("No affiliated colleges on file yet for this university.")
            for col in affiliated:
                st.markdown(f"**{col['name']}** — {col.get('city','-')} — Status: {col.get('verification_status')}")

        st.caption(f"Source: {uni.get('data_source', 'Not specified')}")
