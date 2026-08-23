"""Helpers for browsing careers independent of the full assessment flow
(MASTER PROMPT section 19 — alternative careers / explorer)."""
from services.data_loader import load_careers, career_by_id


def careers_for_fsc_group(fsc_group: str):
    return [c for c in load_careers() if fsc_group in c.get("fsc_groups", []) or fsc_group == "Other"]


def alternative_careers(career_id: str):
    career = career_by_id(career_id)
    if not career:
        return []
    return [career_by_id(cid) for cid in career.get("alternative_careers", []) if career_by_id(cid)]


def all_careers():
    return load_careers()
