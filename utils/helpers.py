"""Small shared helpers used across pages."""
from datetime import datetime


def today_str():
    return datetime.now().strftime("%Y-%m-%d")


def safe_get(d: dict, key, default="Information not verified"):
    """Return d[key] if present and truthy, otherwise a safe placeholder.
    Prevents the app from ever displaying blank/None fields as if they were
    confirmed facts."""
    if not isinstance(d, dict):
        return default
    value = d.get(key)
    if value in (None, "", []):
        return default
    return value


def budget_band_to_range(band: str):
    """Map a budget category label to an (min, max) PKR/year tuple used for
    matching. max=None means unbounded."""
    mapping = {
        "Under PKR 50,000/year": (0, 50000),
        "PKR 50,000\u2013100,000": (50000, 100000),
        "PKR 100,000\u2013200,000": (100000, 200000),
        "PKR 200,000\u2013400,000": (200000, 400000),
        "PKR 400,000+": (400000, None),
        "Not sure": (0, None),
    }
    return mapping.get(band, (0, None))


def cost_band_to_estimate(band: str):
    """Rough midpoint estimate (PKR/year) for a career's typical_annual_cost_band
    string, used ONLY for relative budget-matching — never displayed as a
    guaranteed fee."""
    mapping = {
        "Under PKR 50,000/year": 40000,
        "PKR 50,000-100,000": 75000,
        "PKR 100,000-200,000": 150000,
        "PKR 100,000-250,000": 175000,
        "PKR 100,000-300,000": 200000,
        "PKR 150,000-300,000": 225000,
        "PKR 150,000-350,000": 250000,
        "PKR 200,000-400,000": 300000,
        "PKR 400,000+": 500000,
    }
    return mapping.get(band, 200000)


def ensure_session_defaults(st):
    """Initialize all session_state keys the app relies on, so pages can be
    visited in any order without KeyErrors."""
    defaults = {
        "language": "English",
        "profile": {},
        "interests": {},
        "skills": {},
        "personality": {},
        "assessment_complete": False,
        "recommendations": None,
        "university_matches": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
