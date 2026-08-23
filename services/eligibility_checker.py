"""'Am I Eligible?' feature (MASTER PROMPT section 14).

Distinguishes minimum eligibility from merit/closing-merit and entry-test
requirements, and never guarantees admission.
"""

GREEN = "\U0001F7E2 Likely Eligible"
YELLOW = "\U0001F7E1 Eligibility Needs Verification"
RED = "\U0001F534 Does Not Meet Listed Minimum Requirement"

VERIFY_NOTE = ("Eligibility information can change. Verify the latest admission "
               "advertisement on the university's official website before applying.")


def check_eligibility(percentage: float, fsc_group: str, university: dict, career: dict):
    """Returns a dict with status, explanation, and the verify-note. Because
    most university records in the MVP dataset are marked 'Needs
    Verification', the checker defaults to YELLOW whenever it can't confirm
    a real minimum against the university's own data."""
    if percentage is None or career is None or university is None:
        return {
            "status": YELLOW,
            "reasons": ["Insufficient information to evaluate eligibility."],
            "verify_note": VERIFY_NOTE,
        }

    reasons = []
    uni_min = university.get("min_percentage")
    career_min = career.get("min_percentage")

    group_ok = fsc_group in career.get("fsc_groups", [])
    if not group_ok:
        reasons.append(
            f"Your FSc group ({fsc_group}) is not typically listed for {career.get('name')} "
            f"— confirm whether the university accepts your background."
        )

    # If the university itself has published a minimum, that takes priority.
    effective_min = uni_min if uni_min is not None else career_min

    if effective_min is None:
        reasons.append("This university has not published a verified minimum percentage in our dataset.")
        status = YELLOW
    elif percentage >= effective_min:
        reasons.append(f"Your percentage ({percentage}%) meets the general minimum we have on file ({effective_min}%).")
        status = GREEN if group_ok else YELLOW
    else:
        reasons.append(f"Your percentage ({percentage}%) is below the general minimum we have on file ({effective_min}%).")
        status = RED

    reasons.append(
        "Note: meeting the minimum eligibility is NOT the same as meeting the closing "
        "merit for a given year, and does not account for the entry-test score, which "
        "usually also affects final admission."
    )

    programme_offered = career.get("id") in university.get("programmes", [])
    if not programme_offered:
        reasons.append(f"Our dataset does not list {career.get('name')} as offered at {university.get('name')} — verify directly with the university.")
        if status == GREEN:
            status = YELLOW

    return {
        "status": status,
        "reasons": reasons,
        "verify_note": VERIFY_NOTE,
    }
