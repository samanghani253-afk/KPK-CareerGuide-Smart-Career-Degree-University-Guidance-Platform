# KPK CareerGuide — Smart Career, Degree & University Guidance Platform

An evidence-based career, degree and university guidance platform for FSc students in
**Peshawar and Khyber Pakhtunkhwa (KPK), Pakistan** — built on survey findings that most
students had never taken a proper career assessment and had experienced real confusion (and
wasted money) around university, eligibility and entry-test decisions.

The app runs a two-stage **Assess → Recommend** flow: a multi-step student assessment feeds a
transparent, weighted recommendation engine covering careers, universities, affiliated
colleges, eligibility, entry tests, cost, and scholarships — plus downloadable student and
parent-friendly PDF reports.

## ⚠️ Important: this ships with a STARTER dataset

Per the project's data-integrity requirement, **no university, fee, merit, entry-test-date or
affiliation fact has been fabricated.** Where a real, verifiable detail wasn't available during
development, the field is explicitly marked `"Needs Verification"` rather than invented. A few
records are marked `[PLACEHOLDER]` to demonstrate the data structure only — replace them with
real, verified institutions before using this for real decisions. See
[Updating the data](#updating-the-data) below.

---

## Project Structure

```text
kpk-careerguide/
├── app.py                     # Home page + language selector
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
│
├── data/
│   ├── universities.json
│   ├── colleges.json
│   ├── careers.json
│   ├── entry_tests.json
│   ├── scholarships.json
│   └── translations.json
│
├── pages/
│   ├── 1_Assessment.py        # Multi-step student assessment
│   ├── 2_Dashboard.py         # Results dashboard after assessment
│   ├── 3_Careers.py           # Career explorer (no assessment needed)
│   ├── 4_Universities.py      # University explorer with filters
│   ├── 5_Colleges.py          # Affiliated colleges browser
│   ├── 6_Eligibility.py       # "Am I Eligible?" checker
│   ├── 7_Compare.py           # University + cost comparison
│   ├── 8_Scholarships.py      # Scholarship finder
│   ├── 9_Report.py            # Student & parent PDF report generator
│   └── 10_Counsellor.py       # Counsellor request form (MVP, no live backend yet)
│
├── services/
│   ├── data_loader.py         # Central JSON data access layer
│   ├── recommendation_engine.py
│   ├── eligibility_checker.py
│   ├── university_matcher.py
│   ├── career_matcher.py
│   └── report_generator.py
│
└── utils/
    ├── translations.py        # English / اردو / پښتو dictionary lookup
    ├── validation.py
    └── helpers.py
```

Data is fully separated from application logic (`data/*.json` + `services/data_loader.py`),
so the project can later migrate from JSON to PostgreSQL/Supabase by changing only
`data_loader.py`.

---

## Running Locally

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app works fully without any API key — no AI API is required for the MVP. If you later add
an AI-assisted explanation feature, copy `.env.example` to `.env` and fill in
`OPENAI_API_KEY` (never commit `.env`).

---

## Deploying to Streamlit Community Cloud

1. Create a new GitHub repository and push this project to it.
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) and sign in with GitHub.
3. Click **New app**.
4. Select your repository and branch.
5. Set the main file path to `app.py`.
6. Click **Deploy**.
7. If you use any secrets (e.g. a future AI API key), add them under **App settings → Secrets**
   rather than committing them to the repo.

The app requires no local-only paths and runs with `streamlit run app.py`.

---

## Updating the Data

All factual data lives in `data/*.json`. Each record includes `data_source`,
`last_verified`, and `verification_status` fields — **do not remove these when editing.**

### To add or correct a university (`data/universities.json`)
1. Confirm the fact on the university's **official website** or an official admission
   advertisement.
2. Fill in the field with the confirmed value.
3. Set `"verification_status": "Verified"` and `"last_verified"` to today's date (`YYYY-MM-DD`).
4. Set `"data_source"` to the specific URL or document you used.
5. If you cannot verify a field, leave it as `"Needs Verification"` — never guess.

### To add an affiliated college (`data/colleges.json`)
Only add a college if the affiliating university's **own official published list** confirms
the relationship. Set `"university_affiliation"` to the matching university `id` from
`universities.json`.

### To add a new career (`data/careers.json`)
Add a new object following the existing schema. `interest_categories`, `skill_tags`, and
`personality_tags` drive the recommendation engine's scoring — keep them consistent with the
categories used in the assessment (see `pages/1_Assessment.py`).

### To add a future university/district
The app is architected so any Pakistani region can be added later — just add new records with
the appropriate `district`/`city` values; no code changes are required for new
locations to appear in filters.

---

## Recommendation Scoring Model

Weights (configurable in `services/recommendation_engine.py`, `WEIGHTS` dict):

| Factor | Weight |
|---|---|
| Academic compatibility | 25% |
| Interest compatibility | 20% |
| Skill compatibility | 20% |
| Personality/work-style compatibility | 10% |
| Financial compatibility | 10% |
| Location compatibility | 10% |
| Career demand/availability | 5% |

Every recommendation shown to the student includes the full breakdown ("Why this score?") —
the engine never returns a bare verdict without an explanation.

---

## Testing Instructions

Run the app and manually walk through the four profiles from the project's test plan to confirm
recommendations differ meaningfully by profile:

- **Student A** — Pre-Medical, 90%, strong biology, strong helping skills, Peshawar, low budget
  → should rank medical/health careers highest, flag budget tension with MBBS-tier costs.
- **Student B** — Pre-Medical, 72%, interested in computers, strong analytical skills, moderate
  budget → should surface both medical and tech-adjacent alternatives (e.g. MLT, Biotechnology)
  rather than only MBBS.
- **Student C** — ICS, 85%, strong programming, strong maths, interested in AI → should rank
  Computer Science / Data Science / Cybersecurity highest.
- **Student D** — Pre-Engineering, 78%, interested in engineering, low budget, wants public
  university → should rank Engineering/Computer Science highest and favor public universities
  in the Best Universities list.

Also verify:
- Entering marks (obtained/total) instead of percentage auto-calculates correctly and rejects
  obtained > total.
- Entering a percentage outside 0–100 shows a validation error instead of crashing.
- Visiting any `pages/*.py` file directly (without completing the assessment first) shows a
  friendly prompt to complete the assessment rather than an error.
- The Eligibility Checker always shows the "verify on official sources" note and never states a
  guarantee of admission.
- PDF report generation works, and shows a friendly error (not a crash) if `reportlab` is
  missing.
- Switching the language selector updates the home page and navigation labels.

---

## Disclaimer

This platform provides educational career guidance based on the information you provide.
Recommendations are not guarantees of admission, employment or future income. University
eligibility, merit, fees, deadlines and entry-test requirements can change. Always verify final
admission information through the university's official sources.
