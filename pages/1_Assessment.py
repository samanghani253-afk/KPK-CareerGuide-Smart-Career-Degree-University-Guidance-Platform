import streamlit as st
from utils.translations import t
from utils.helpers import ensure_session_defaults
from utils.validation import validate_percentage, marks_to_percentage, validate_budget
from services.data_loader import load_universities
from services.recommendation_engine import generate_recommendations
from services.university_matcher import match_universities

st.set_page_config(page_title="Assessment — KPK CareerGuide", page_icon="📝", layout="wide")
ensure_session_defaults(st)
lang = st.session_state["language"]

st.title(f"📝 {t('nav_assessment', lang)}")
st.caption("This assessment is for educational career guidance only. It is not a psychological or medical diagnosis.")

if "step" not in st.session_state:
    st.session_state["step"] = 1

STEPS = ["Academic Info", "Financial Profile", "Location", "Interests", "Skills", "Personality", "Review"]
step = st.session_state["step"]
st.progress(step / len(STEPS), text=f"Step {step} of {len(STEPS)}: {STEPS[step-1]}")

INTEREST_CATEGORIES = {
    "Health & Medicine": ["Treating patients", "Biology", "Human anatomy", "Healthcare", "Laboratory work", "Public health"],
    "Technology": ["Programming", "Computers", "AI", "Software", "Cybersecurity", "Problem solving"],
    "Engineering": ["Machines", "Mathematics", "Construction", "Electronics", "Design", "Technical problem solving"],
    "Business": ["Entrepreneurship", "Marketing", "Finance", "Management", "Selling", "Leadership"],
    "Social Sciences": ["Psychology", "Sociology", "Education", "Human behaviour", "Community work"],
    "Arts & Communication": ["Writing", "Journalism", "Media", "Design", "Public speaking"],
    "Natural/Biosciences": ["Plants", "Animals", "Environment", "Research", "Biotechnology"],
    "Law & Public Service": ["Law", "Government", "Justice", "Public administration", "Leadership"],
}
INTEREST_OPTIONS = ["Strongly like", "Like", "Neutral", "Dislike", "Strongly dislike"]

SKILLS_LIST = [
    "Communication", "Mathematics", "Biology", "Chemistry", "Physics", "Computer skills",
    "Programming", "Problem solving", "Critical thinking", "Creativity", "Leadership",
    "Teamwork", "Public speaking", "Writing", "Research", "Practical/manual skills",
    "Organization", "Empathy", "Analytical thinking",
]

PERSONALITY_LABELS = [
    "Analytical", "Creative", "Social", "Helping-oriented", "Enterprising",
    "Practical", "Research-oriented", "Organized", "Leadership-oriented",
]

DISTRICTS = ["Peshawar", "Mardan", "Swabi", "Abbottabad", "Kohat", "Nowshera", "Charsadda", "Other KPK district"]


def next_step():
    st.session_state["step"] = min(len(STEPS), st.session_state["step"] + 1)


def prev_step():
    st.session_state["step"] = max(1, st.session_state["step"] - 1)


profile = st.session_state["profile"]

# ---------------- Step 1: Academic ----------------
if step == 1:
    with st.form("academic_form"):
        name = st.text_input("Student name (optional)", value=profile.get("name", ""))
        c1, c2 = st.columns(2)
        district = c1.selectbox("District/region", DISTRICTS, index=DISTRICTS.index(profile.get("district")) if profile.get("district") in DISTRICTS else 0)
        city = c2.text_input("Current city", value=profile.get("city", ""))

        fsc_group = st.selectbox("FSc group", ["Pre-Medical", "Pre-Engineering", "ICS", "General Science", "Other"],
                                  index=["Pre-Medical", "Pre-Engineering", "ICS", "General Science", "Other"].index(profile.get("fsc_group")) if profile.get("fsc_group") else 0)
        status = st.selectbox("Current status", ["FSc 1st year", "FSc 2nd year", "Recently completed FSc", "Already enrolled in university", "Other"])

        matric_pct = st.number_input("Matric percentage", min_value=0.0, max_value=100.0, value=float(profile.get("matric_percentage", 0)), step=0.1)

        st.markdown("**FSc marks** — enter percentage directly, or obtained/total marks (percentage auto-calculates)")
        entry_mode = st.radio("How would you like to enter FSc marks?", ["Percentage", "Obtained + Total marks"], horizontal=True)
        fsc_percentage = profile.get("fsc_percentage")
        expected_pct = profile.get("expected_fsc_percentage")
        if entry_mode == "Percentage":
            fsc_percentage = st.number_input("FSc percentage (leave 0 if result pending)", min_value=0.0, max_value=100.0, value=float(fsc_percentage or 0), step=0.1)
            expected_pct = st.number_input("Expected FSc percentage (if result pending)", min_value=0.0, max_value=100.0, value=float(expected_pct or 0), step=0.1)
        else:
            oc1, oc2 = st.columns(2)
            obtained = oc1.number_input("Obtained marks", min_value=0.0, value=0.0, step=1.0)
            total = oc2.number_input("Total marks", min_value=1.0, value=1100.0, step=1.0)
            calc_pct, err = marks_to_percentage(obtained, total)
            if calc_pct is not None:
                st.success(f"Calculated percentage: {calc_pct}%")
                fsc_percentage = calc_pct
            elif obtained or total != 1100.0:
                st.error(err)

        submitted = st.form_submit_button("Next →", type="primary")
        if submitted:
            ok, err = validate_percentage(matric_pct if matric_pct else 0)
            if not ok:
                st.error(err)
            else:
                profile.update({
                    "name": name, "district": district, "city": city or district,
                    "fsc_group": fsc_group, "status": status,
                    "matric_percentage": matric_pct,
                    "fsc_percentage": fsc_percentage or None,
                    "expected_fsc_percentage": expected_pct or None,
                })
                st.session_state["profile"] = profile
                next_step()
                st.rerun()

# ---------------- Step 2: Financial ----------------
elif step == 2:
    with st.form("financial_form"):
        budget_band = st.selectbox("Affordable education cost (annual)", [
            "Under PKR 50,000/year", "PKR 50,000\u2013100,000", "PKR 100,000\u2013200,000",
            "PKR 200,000\u2013400,000", "PKR 400,000+", "Not sure",
        ])
        c1, c2 = st.columns(2)
        hostel_ok = c1.radio("Can you afford hostel?", ["Yes", "No", "Maybe"], horizontal=True)
        daily_travel = c2.radio("Can you travel daily?", ["Yes", "No", "Maybe"], horizontal=True)
        scholarship_required = st.radio("Is a scholarship required?", ["Yes", "No", "Maybe"], horizontal=True)
        uni_type = st.selectbox("University type preference", [
            "Public university preferred", "Private university acceptable", "Both acceptable",
        ], index=2)

        submitted = st.form_submit_button("Next →", type="primary")
        if submitted:
            profile.update({
                "budget_band": budget_band, "hostel_afford": hostel_ok,
                "daily_travel": daily_travel, "scholarship_required": scholarship_required,
                "university_type_preference": uni_type,
            })
            st.session_state["profile"] = profile
            next_step()
            st.rerun()
    if st.button("← Back"):
        prev_step(); st.rerun()

# ---------------- Step 3: Location ----------------
elif step == 3:
    with st.form("location_form"):
        preferred_location = st.selectbox("Preferred study location", [
            "Peshawar", "Mardan", "Swabi", "Abbottabad", "Kohat", "Nowshera", "Charsadda",
            "Other KPK district", "Anywhere in KPK", "Anywhere in Pakistan",
        ])
        max_distance = st.slider("Maximum acceptable travel distance (km)", 0, 300, 50)
        c1, c2 = st.columns(2)
        hostel_required = c1.radio("Hostel required?", ["Yes", "No"], horizontal=True)
        close_to_home = c2.radio("Prefer university close to home?", ["Yes", "No"], horizontal=True)

        submitted = st.form_submit_button("Next →", type="primary")
        if submitted:
            profile.update({
                "preferred_location": preferred_location, "max_distance_km": max_distance,
                "hostel_required": hostel_required, "close_to_home": close_to_home,
            })
            st.session_state["profile"] = profile
            next_step()
            st.rerun()
    if st.button("← Back"):
        prev_step(); st.rerun()

# ---------------- Step 4: Interests ----------------
elif step == 4:
    st.write("Rate each activity based on how much you enjoy it.")
    interests = st.session_state["interests"]
    with st.form("interests_form"):
        for category, items in INTEREST_CATEGORIES.items():
            st.markdown(f"#### {category}")
            cat_ratings = interests.get(category, {})
            cols = st.columns(2)
            for i, item in enumerate(items):
                with cols[i % 2]:
                    current = cat_ratings.get(item, "Neutral")
                    rating = st.select_slider(item, options=INTEREST_OPTIONS,
                                               value=current if current in INTEREST_OPTIONS else "Neutral",
                                               key=f"interest_{category}_{item}")
                    cat_ratings[item] = rating
            interests[category] = cat_ratings
        submitted = st.form_submit_button("Next →", type="primary")
        if submitted:
            st.session_state["interests"] = interests
            next_step()
            st.rerun()
    if st.button("← Back"):
        prev_step(); st.rerun()

# ---------------- Step 5: Skills ----------------
elif step == 5:
    st.write("Rate your current skill level: 1 = Beginner, 5 = Excellent.")
    skills = st.session_state["skills"]
    with st.form("skills_form"):
        cols = st.columns(2)
        for i, skill in enumerate(SKILLS_LIST):
            with cols[i % 2]:
                skills[skill] = st.slider(skill, 1, 5, value=skills.get(skill, 3), key=f"skill_{skill}")
        submitted = st.form_submit_button("Next →", type="primary")
        if submitted:
            st.session_state["skills"] = skills
            next_step()
            st.rerun()
    if st.button("← Back"):
        prev_step(); st.rerun()

# ---------------- Step 6: Personality ----------------
elif step == 6:
    st.info("This assessment is for educational career guidance only. It is not a psychological or medical diagnosis.")
    personality = st.session_state["personality"]
    with st.form("personality_form"):
        st.write("Select the work-style labels that best describe how you like to work (choose as many as fit):")
        selected = st.multiselect("Work style", PERSONALITY_LABELS, default=personality.get("selected_labels", []))
        submitted = st.form_submit_button("See My Results →", type="primary")
        if submitted:
            personality["selected_labels"] = selected
            st.session_state["personality"] = personality
            next_step()
            st.rerun()
    if st.button("← Back"):
        prev_step(); st.rerun()

# ---------------- Step 7: Review / Generate ----------------
elif step == 7:
    st.subheader("Review your information")
    profile = st.session_state["profile"]
    c1, c2, c3 = st.columns(3)
    c1.metric("FSc Group", profile.get("fsc_group", "-"))
    c2.metric("FSc %", profile.get("fsc_percentage") or profile.get("expected_fsc_percentage") or "Not provided")
    c3.metric("Budget", profile.get("budget_band", "-"))

    required_ok, missing = True, []
    if not profile.get("fsc_group"):
        missing.append("FSc group")
    if not (profile.get("fsc_percentage") or profile.get("expected_fsc_percentage")):
        missing.append("FSc percentage / expected percentage")
    required_ok = len(missing) == 0

    if not required_ok:
        st.error(f"Please complete required fields before continuing: {', '.join(missing)}")
    else:
        if st.button("✨ Generate My Career Recommendations", type="primary", use_container_width=True):
            universities = load_universities()
            recs = generate_recommendations(
                profile, st.session_state["interests"], st.session_state["skills"],
                st.session_state["personality"], universities,
            )
            career_ids = [r["career"]["id"] for r in recs]
            uni_matches = match_universities(profile, career_ids, universities)

            st.session_state["recommendations"] = recs
            st.session_state["university_matches"] = uni_matches
            st.session_state["assessment_complete"] = True
            st.switch_page("pages/2_Dashboard.py")

    if st.button("← Back"):
        prev_step(); st.rerun()
