"""Centralized translation helper. All UI copy should be pulled through t()
rather than hardcoded, so new languages/labels only need to be added in
data/translations.json."""
import json
import os

_TRANSLATIONS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "translations.json")

_LANG_CODE_MAP = {
    "English": "en",
    "اردو": "ur",
    "پښتو": "ps",
}


def load_translations() -> dict:
    with open(_TRANSLATIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


_TRANSLATIONS = load_translations()


def t(key: str, lang_label: str = "English") -> str:
    """Return the translated string for `key` in the language identified by
    `lang_label` (one of 'English', 'اردو', 'پښتو'). Falls back to English,
    then to the raw key, so a missing translation never crashes the app."""
    lang_code = _LANG_CODE_MAP.get(lang_label, "en")
    entry = _TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang_code) or entry.get("en") or key


def language_options():
    return list(_LANG_CODE_MAP.keys())
