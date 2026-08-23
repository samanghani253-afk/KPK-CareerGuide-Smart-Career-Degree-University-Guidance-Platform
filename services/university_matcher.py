"""University match scoring (MASTER PROMPT section 13)."""
from utils.helpers import budget_band_to_range


def match_universities(profile: dict, career_ids: list, universities: list, top_n: int = 10):
    """Score each university against the student's profile and the list of
    recommended career ids. Returns a ranked list of dicts with score +
    human-readable check/warning flags."""
    preferred_location = profile.get("preferred_location", "Anywhere in KPK")
    uni_type_pref = profile.get("university_type_preference", "Both acceptable")
    budget_band = profile.get("budget_band")
    b_min, b_max = budget_band_to_range(budget_band) if budget_band else (0, None)
    percentage = profile.get("fsc_percentage") or profile.get("expected_fsc_percentage") or 0

    results = []
    for uni in universities:
        offered = [cid for cid in career_ids if cid in uni.get("programmes", [])]
        if not offered:
            continue

        score = 0.0
        flags = []

        # Programme availability (40%)
        prog_component = min(1.0, len(offered) / max(1, len(career_ids)))
        score += 0.4 * prog_component
        flags.append(("check", f"Offers {len(offered)} of your top {len(career_ids)} recommended programme(s)"))

        # Eligibility likelihood (20%) — based on published min_percentage if available
        uni_min = uni.get("min_percentage")
        if uni_min is None:
            score += 0.5 * 0.20
            flags.append(("warn", "Eligibility needs verification (no verified minimum on file)"))
        elif percentage >= uni_min:
            score += 1.0 * 0.20
            flags.append(("check", "Academic eligibility likely (meets listed minimum)"))
        else:
            flags.append(("warn", "Percentage below listed minimum — eligibility uncertain"))

        # Location (20%)
        if preferred_location in ("Anywhere in KPK", "Anywhere in Pakistan"):
            score += 0.8 * 0.20
            flags.append(("check", "Fits your open location preference"))
        elif uni.get("district") == preferred_location or uni.get("city") == preferred_location:
            score += 1.0 * 0.20
            flags.append(("check", "Fits your preferred location"))
        else:
            score += 0.3 * 0.20
            flags.append(("warn", "Located outside your preferred district"))

        # Budget (10%) — only estimable if the university has published fee data
        approx_fee = uni.get("approx_fee_pkr_per_year")
        if approx_fee is None:
            score += 0.5 * 0.10
            flags.append(("warn", "Fee information not verified — cannot confirm budget fit"))
        else:
            if b_max is None or (b_min <= approx_fee <= b_max):
                score += 1.0 * 0.10
                flags.append(("check", "Fits your budget"))
            elif approx_fee > (b_max or approx_fee):
                score += 0.2 * 0.10
                flags.append(("warn", "Higher estimated cost than your budget"))

        # University type preference (10%)
        if uni_type_pref == "Both acceptable":
            score += 1.0 * 0.10
        elif uni_type_pref == "Public university preferred" and uni.get("type") == "Public":
            score += 1.0 * 0.10
            flags.append(("check", "Matches your public-university preference"))
        elif uni_type_pref == "Private university acceptable" and uni.get("type") == "Private":
            score += 1.0 * 0.10
        else:
            score += 0.4 * 0.10

        results.append({
            "university": uni,
            "match_score": round(score * 100, 1),
            "flags": flags,
            "offered_career_ids": offered,
        })

    results.sort(key=lambda r: r["match_score"], reverse=True)
    return results[:top_n]
