"""Input validation helpers. Every function returns (is_valid, error_message)
so callers can show a friendly message instead of crashing."""


def validate_percentage(value):
    if value is None:
        return False, "Please enter a value."
    try:
        v = float(value)
    except (TypeError, ValueError):
        return False, "Percentage must be a number."
    if v < 0 or v > 100:
        return False, "Percentage must be between 0 and 100."
    return True, ""


def validate_marks(obtained, total):
    try:
        o = float(obtained)
        t_ = float(total)
    except (TypeError, ValueError):
        return False, "Marks must be numbers."
    if t_ <= 0:
        return False, "Total marks must be greater than 0."
    if o < 0:
        return False, "Obtained marks cannot be negative."
    if o > t_:
        return False, "Obtained marks cannot exceed total marks."
    return True, ""


def marks_to_percentage(obtained, total):
    ok, err = validate_marks(obtained, total)
    if not ok:
        return None, err
    return round((float(obtained) / float(total)) * 100, 2), ""


def validate_budget(value):
    if value is None:
        return False, "Please enter a budget."
    try:
        v = float(value)
    except (TypeError, ValueError):
        return False, "Budget must be a number."
    if v < 0:
        return False, "Budget must be positive."
    return True, ""


def validate_required_fields(fields: dict):
    """fields: {label: value}. Returns (is_valid, list_of_missing_labels)."""
    missing = [label for label, value in fields.items() if value in (None, "", [])]
    return (len(missing) == 0), missing
