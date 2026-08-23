import streamlit as st
from utils.translations import t
from utils.helpers import ensure_session_defaults, today_str

st.set_page_config(page_title="Talk to a Career Counsellor — KPK CareerGuide", page_icon="🧑‍🏫", layout="wide")
ensure_session_defaults(st)
lang = st.session_state["language"]

st.title("🧑‍🏫 Talk to a Career Counsellor")

st.warning(
    "⚠️ Live counsellor matching and appointment booking are not yet connected in this MVP. "
    "This page collects your question/request so it can be reviewed manually, or routed to a "
    "future counsellor-matching backend once available."
)

with st.container(border=True):
    st.markdown("#### About Career Counselling")
    st.write(
        "Human mentorship complements this platform's automated recommendations — a counsellor can "
        "help you weigh trade-offs, talk through family/financial constraints, and interpret your "
        "results in more depth."
    )

st.subheader("Submit a Question / Counselling Request")
with st.form("counsellor_request_form"):
    name = st.text_input("Your name (optional)")
    contact = st.text_input("Contact (email or phone, optional)")
    question = st.text_area("Your question or what you'd like help with", height=150)
    submitted = st.form_submit_button("Submit Request", type="primary")
    if submitted:
        if not question.strip():
            st.error("Please enter your question before submitting.")
        else:
            # NOTE: MVP has no backend/storage — this is a placeholder confirmation only.
            # A future implementation should persist this to a database and route it to
            # a counsellor-matching/appointment-booking backend (see MASTER PROMPT section 22).
            st.success(
                f"Thanks{', ' + name if name else ''} — your request has been recorded for this session "
                f"({today_str()}). Note: this MVP does not yet have a live backend, so please also consider "
                f"discussing your question with a teacher, parent, or school counsellor in the meantime."
            )
