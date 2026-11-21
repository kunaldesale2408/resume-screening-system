"""Tests for skill and entity extraction."""

from datetime import date

from src.feature_engineering import build_resume_profile, group_label
from src.feature_engineering.entities import (
    required_education,
    required_years,
    resume_education,
    split_sections,
    years_from_date_ranges,
)
from src.feature_engineering.skills import extract_skills, job_skill_requirements


# ------------------------------------------------------------------ skills

def test_aliases_map_to_canonical_names():
    skills = extract_skills("Built models with sklearn, ML pipelines and torch")
    assert {"scikit-learn", "Machine Learning", "PyTorch"} <= skills


def test_matching_is_token_based():
    # "ML" must not be found inside "HTML"
    assert "Machine Learning" not in extract_skills("Wrote HTML pages")


def test_ambiguous_words_are_case_sensitive():
    assert "Go" not in extract_skills("Ready to go the extra mile")
    assert "Excel" not in extract_skills("I excel at teamwork")
    assert {"Go", "Excel"} <= extract_skills("Skills: Go, Excel")


def test_any_of_sentences_become_one_group():
    required, _ = job_skill_requirements("Familiarity with FastAPI, Flask, or Django for building APIs.")
    assert frozenset({"FastAPI", "Flask", "Django"}) in required


def test_and_sentences_require_each_skill():
    required, _ = job_skill_requirements("Strong Python and SQL.")
    assert frozenset({"Python"}) in required
    assert frozenset({"SQL"}) in required


def test_nice_to_have_skills_are_preferred():
    text = "Requirements\n- Python\nNice to have:\n- Docker\nKnowledge of AWS is a plus."
    required, preferred = job_skill_requirements(text)
    assert [group_label(g) for g in required] == ["Python"]
    assert {group_label(g) for g in preferred} == {"Docker", "AWS"}


def test_soft_skills_are_not_requirements():
    required, preferred = job_skill_requirements("Excellent communication and teamwork skills.")
    assert required == [] and preferred == []


# ------------------------------------------------------- experience, education

def test_date_ranges_with_months_are_inclusive():
    assert years_from_date_ranges("Intern, April 2026 – September 2026") == 0.5


def test_overlapping_jobs_are_not_double_counted():
    text = "Job A (Jan 2020 - Dec 2021)\nJob B (Jan 2021 - Dec 2021)"
    assert years_from_date_ranges(text) == 2.0


def test_present_uses_today():
    assert years_from_date_ranges("Engineer (Jan 2024 - Present)", today=date(2026, 1, 1)) == 2.0


def test_required_years_takes_the_lowest_number():
    assert required_years("Work experience: 0-1 year") == 0
    assert required_years("Python (3+ years). 5+ years preferred.") == 3


def test_education_levels():
    assert resume_education("B.Tech in Artificial Intelligence") == 2
    assert resume_education("M.Tech, B.E.") == 3
    assert required_education("Bachelor's or Master's degree") == 2
    assert required_education("A degree in computer science") == 2
    assert required_education("No formal requirements") == 0


def test_sections_split_on_headers():
    sections = split_sections("Jane Doe\nEXPERIENCE\nAnalyst\nEducation:\nB.Sc")
    assert sections["experience"] == "Analyst"
    assert sections["education"] == "B.Sc"


def test_resume_profile(sample_resume):
    profile = build_resume_profile(sample_resume, name="john.pdf")
    assert profile.candidate_name == "John Doe"
    assert profile.years_experience == 5
    assert profile.education == "Bachelor's"
    assert {"Python", "FastAPI", "spaCy", "Docker"} <= profile.skills
