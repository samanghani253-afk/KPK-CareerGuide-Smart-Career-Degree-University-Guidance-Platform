"""Loads all JSON data files. Centralizing this means the app can later swap
JSON for a PostgreSQL/Supabase-backed implementation by changing only this
module (see MASTER PROMPT section 28: data/logic separation)."""
import json
import os
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


@st.cache_data
def load_careers():
    return _load_json("careers.json").get("careers", [])


@st.cache_data
def load_universities():
    return _load_json("universities.json").get("universities", [])


@st.cache_data
def load_colleges():
    return _load_json("colleges.json").get("colleges", [])


@st.cache_data
def load_entry_tests():
    return _load_json("entry_tests.json").get("entry_tests", [])


@st.cache_data
def load_scholarships():
    return _load_json("scholarships.json").get("scholarships", [])


def career_by_id(career_id):
    for c in load_careers():
        if c["id"] == career_id:
            return c
    return None


def university_by_id(uni_id):
    for u in load_universities():
        if u["id"] == uni_id:
            return u
    return None


def colleges_for_university(uni_id):
    return [c for c in load_colleges() if c.get("university_affiliation") == uni_id]


def entry_test_by_id(test_id):
    for t in load_entry_tests():
        if t["id"] == test_id:
            return t
    return None
