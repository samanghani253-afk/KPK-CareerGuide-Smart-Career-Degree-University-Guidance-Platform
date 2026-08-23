"""Career recommendation engine.

Combines FSc group, academic percentage, interests, skills, personality,
budget and location into a transparent, weighted match score per career
(see MASTER PROMPT sections 9-10). Weights are configurable below so they
can be tuned without touching the scoring logic.
"""
from services.data_loader import load_careers
from utils.helpers import budget_band_to_range, cost_band_to_estimate

# ---- Configurable weights (must sum to 100) ----
WEIGHTS = {
    "academic": 25,
    "interest": 20,
    "skill": 20,
    "personality": 10,
    "financial": 10,
    "location": 10,
    "availability": 5,
}

INTEREST_RATING_SCORE = {
    "Strongly like": 1.0,
    "Like": 0.7,
    "Neutral": 0.4,
    "Dislike": 0.1,
    "Strongly dislike": 0.0,
}


def _academic_score(profile: dict, career: dict) -> float:
    """0-1. Rewards meeting/exceeding the career's stated minimum percentage
    and having a matching FSc group."""
    fsc_group = profile.get("fsc_group")
    percentage = profile.get("fsc_percentage") or profile.get("expected_fsc_percentage") or 0
    min_pct = career.get("min_percentage") or 0

    group_match = 1.0 if fsc_group in career.get("fsc_groups", []) else 0.2
    if min_pct <= 0:
        pct_component = 0.7
    elif percentage >= min_pct:
        # scale: meeting minimum = 0.7, +bonus up to 1.0 for exceeding by 20pts
        pct_component = min(1.0, 0.7 + (percentage - min_pct) / 100.0)
    else:
        # below minimum: scaled penalty, floors at 0
        gap = min_pct - percentage
        pct_component = max(0.0, 0.5 - gap / 40.0)
    return round(0.5 * group_match + 0.5 * pct_component, 3)


def _interest_score(interests: dict, career: dict) -> float:
    """0-1. Compares the student's rated interest categories against the
    career's weighted interest_categories."""
    cat_weights = career.get("interest_categories", {})
    if not cat_weights:
        return 0.5
    total_weight = sum(cat_weights.values()) or 1
    score = 0.0
    for category, weight in cat_weights.items():
        cat_ratings = interests.get(category, {})
        if cat_ratings:
            vals = [INTEREST_RATING_SCORE.get(r, 0.4) for r in cat_ratings.values()]
            avg = sum(vals) / len(vals)
        else:
            avg = 0.4  # neutral default if unanswered
        score += (weight / total_weight) * avg
    return round(score, 3)


def _skill_score(skills: dict, career: dict) -> float:
    """0-1. Averages the student's self-rated (1-5) skills tagged as
    relevant to this career."""
    tags = career.get("skill_tags", [])
    if not tags:
        return 0.5
    ratings = []
    for tag in tags:
        val = skills.get(tag)
        if val:
            ratings.append(val / 5.0)
    if not ratings:
        return 0.4
    return round(sum(ratings) / len(ratings), 3)


def _personality_score(personality: dict, career: dict) -> float:
    """0-1. Checks overlap between the student's selected personality/work
    style labels and the career's tags."""
    tags = set(career.get("personality_tags", []))
    selected = set(personality.get("selected_labels", []))
    if not tags:
        return 0.5
    if not selected:
        return 0.4
    overlap = len(tags & selected)
    return round(min(1.0, overlap / max(1, len(tags))), 3)


def _financial_score(profile: dict, career: dict) -> float:
    """0-1. Compares the student's budget band against the career's typical
    cost band (rough estimate only, never a guaranteed fee)."""
    band = profile.get("budget_band")
    if not band or band == "Not sure":
        return 0.6
    b_min, b_max = budget_band_to_range(band)
    est_cost = cost_band_to_estimate(career.get("typical_annual_cost_band", ""))
    if b_max is None:
        return 1.0 if est_cost >= (b_min or 0) else 0.7
    if b_min <= est_cost <= b_max:
        return 1.0
    if est_cost < b_min:
        return 0.8
    # over budget: scaled penalty
    overshoot = (est_cost - b_max) / max(b_max, 1)
    return max(0.1, 0.8 - overshoot)


def _location_score(profile: dict, career: dict, universities: list) -> float:
    """0-1. Rough proxy: does at least one university offering this career
    exist in the student's preferred location? Peshawar-focused dataset for
    the MVP, per MASTER PROMPT scope."""
    preferred = profile.get("preferred_location", "Anywhere in KPK")
    matches = [u for u in universities if career["id"] in u.get("programmes", [])]
    if not matches:
        return 0.3
    if preferred in ("Anywhere in KPK", "Anywhere in Pakistan"):
        return 0.9
    local_matches = [u for u in matches if u.get("district") == preferred or u.get("city") == preferred]
    return 0.95 if local_matches else 0.5


def _availability_score(career: dict, universities: list) -> float:
    """0-1. How many verified/starter universities in the dataset currently
    offer this career's programme — a rough demand/availability proxy."""
    count = len([u for u in universities if career["id"] in u.get("programmes", [])])
    if count == 0:
        return 0.2
    if count == 1:
        return 0.6
    return 1.0


def generate_recommendations(profile: dict, interests: dict, skills: dict,
                              personality: dict, universities: list, top_n: int = 5):
    """Returns a ranked list of dicts, each containing the career record plus
    a full transparent score breakdown (see MASTER PROMPT section 10)."""
    careers = load_careers()
    results = []
    for career in careers:
        academic = _academic_score(profile, career)
        interest = _interest_score(interests, career)
        skill = _skill_score(skills, career)
        personality_s = _personality_score(personality, career)
        financial = _financial_score(profile, career)
        location = _location_score(profile, career, universities)
        availability = _availability_score(career, universities)

        breakdown = {
            "Academic Match": round(academic * WEIGHTS["academic"], 1),
            "Interest Match": round(interest * WEIGHTS["interest"], 1),
            "Skill Match": round(skill * WEIGHTS["skill"], 1),
            "Personality Match": round(personality_s * WEIGHTS["personality"], 1),
            "Budget Match": round(financial * WEIGHTS["financial"], 1),
            "Location Match": round(location * WEIGHTS["location"], 1),
            "Career Availability": round(availability * WEIGHTS["availability"], 1),
        }
        total = round(sum(breakdown.values()), 1)
        max_possible = {k: v for k, v in WEIGHTS.items()}

        results.append({
            "career": career,
            "match_score": total,  # out of 100
            "breakdown": breakdown,
            "max_breakdown": {
                "Academic Match": WEIGHTS["academic"],
                "Interest Match": WEIGHTS["interest"],
                "Skill Match": WEIGHTS["skill"],
                "Personality Match": WEIGHTS["personality"],
                "Budget Match": WEIGHTS["financial"],
                "Location Match": WEIGHTS["location"],
                "Career Availability": WEIGHTS["availability"],
            },
        })

    results.sort(key=lambda r: r["match_score"], reverse=True)
    return results[:top_n]
