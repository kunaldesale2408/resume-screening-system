"""
Skill extraction with a curated taxonomy and spaCy's PhraseMatcher.

Why a taxonomy instead of plain TF-IDF? TF-IDF only matches identical words,
so "sklearn" and "scikit-learn", or "ML" and "machine learning", look
unrelated. Mapping every alias to one canonical name fixes that, and gives
the recruiter a readable list of matched and missing skills.
"""

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, FrozenSet, List, Set, Tuple

from spacy.matcher import PhraseMatcher

from src.nlp import get_nlp

SKILLS_PATH = Path(__file__).resolve().parents[2] / "config" / "skills.json"


@lru_cache(maxsize=1)
def _load_file() -> dict:
    with open(SKILLS_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def load_taxonomy() -> Dict[str, Dict[str, List[str]]]:
    """Load the skill taxonomy: {category: {canonical_name: [aliases]}}."""
    return {k: v for k, v in _load_file().items() if not k.startswith("_")}


def case_sensitive_forms() -> Dict[str, List[str]]:
    """Skills whose short form is also an ordinary word: {canonical: [exact forms]}."""
    return _load_file().get("_case_sensitive", {})


@lru_cache(maxsize=1)
def skill_categories() -> Dict[str, str]:
    """Map each canonical skill to its category."""
    return {
        skill: category
        for category, skills in load_taxonomy().items()
        for skill in skills
    }


@lru_cache(maxsize=1)
def _matchers() -> Tuple[PhraseMatcher, PhraseMatcher]:
    """
    Build two matchers:
    - LOWER: case-insensitive, for normal skill names and aliases
    - ORTH:  exact case, for words like "Go" or "Excel" that are also English
    """
    nlp = get_nlp()
    case_sensitive = case_sensitive_forms()
    lower = PhraseMatcher(nlp.vocab, attr="LOWER")
    exact = PhraseMatcher(nlp.vocab, attr="ORTH")

    for skills in load_taxonomy().values():
        for canonical, aliases in skills.items():
            phrases = set(aliases)
            if canonical not in case_sensitive:
                phrases.add(canonical)
            if phrases:
                lower.add(canonical, [nlp.make_doc(p) for p in phrases])

    for canonical, forms in case_sensitive.items():
        exact.add(canonical, [nlp.make_doc(f) for f in forms])
    return lower, exact


def extract_skills(text: str) -> Set[str]:
    """
    Return the set of canonical skill names mentioned in ``text``.

    Example: "Built models with sklearn and ML pipelines"
             -> {"scikit-learn", "Machine Learning"}
    """
    nlp = get_nlp()
    doc = nlp.make_doc(text)  # tokenizer only: fast, and enough for matching
    found = set()
    for matcher in _matchers():
        found.update(nlp.vocab.strings[match_id] for match_id, _, _ in matcher(doc))
    return found


# A sentence listing alternatives or examples: any one of its skills is enough.
_ANY_OF = re.compile(r"\b(or|such as|e\.g|like|for example)\b|/", re.I)
# A sentence or section describing nice-to-have skills.
_PREFERRED = re.compile(
    r"\b(a plus|plus|advantage|advantageous|preferred|nice to have|good to have|bonus|desirable)\b", re.I
)
_REQUIRED_HEADER = re.compile(r"\b(requirements?|required|responsibilit|must|qualifications|skills)\b", re.I)
_SENTENCES = re.compile(r"(?<=[.;])\s+|\n")

SkillGroup = FrozenSet[str]


def job_skill_requirements(text: str) -> Tuple[List[SkillGroup], List[SkillGroup]]:
    """
    Read a job description sentence by sentence and return
    (required_groups, preferred_groups).

    Each group is a set of skills where any one satisfies the requirement:
      "Familiarity with FastAPI, Flask, or Django"  -> {FastAPI, Flask, Django}
      "Strong proficiency in Python"                -> {Python}
    Sentences or sections that say "a plus", "preferred", "nice to have"
    etc. go into the preferred list. Soft skills are left out, because a
    resume can't really show them.
    """
    soft = {s for s, cat in skill_categories().items() if cat == "soft_skills"}
    required, preferred = [], []
    section_preferred = False

    for sentence in _SENTENCES.split(text):
        sentence = sentence.strip()
        if not sentence:
            continue
        words = sentence.strip("#*: ").split()
        is_header = len(words) <= 6 and (sentence.startswith("#") or sentence.endswith(":") or sentence.isupper())
        if is_header:
            if _PREFERRED.search(sentence):
                section_preferred = True
            elif _REQUIRED_HEADER.search(sentence):
                section_preferred = False

        skills = extract_skills(sentence) - soft
        if not skills:
            continue
        groups = [frozenset(skills)] if (len(skills) > 1 and _ANY_OF.search(sentence)) else [
            frozenset([s]) for s in skills
        ]
        target = preferred if (section_preferred or _PREFERRED.search(sentence)) else required
        target.extend(groups)

    required = _dedupe(required)
    # A skill that is required on its own doesn't also need a preferred entry.
    required_singles = {next(iter(g)) for g in required if len(g) == 1}
    preferred = [g for g in _dedupe(preferred) if not (g & required_singles) and g not in required]
    return required, preferred


def _dedupe(groups: List[SkillGroup]) -> List[SkillGroup]:
    seen, out = set(), []
    for g in groups:
        if g not in seen:
            seen.add(g)
            out.append(g)
    return out


def group_label(group: SkillGroup) -> str:
    """"Django / FastAPI / Flask" for display."""
    return " / ".join(sorted(group, key=str.lower))


def skill_token(skill: str) -> str:
    """
    Turn a canonical skill into one TF-IDF token, e.g. "scikit-learn" ->
    "skill_scikit_learn", so aliases count as the same term.
    """
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in skill.lower())
    return "skill_" + "_".join(part for part in cleaned.split("_") if part)
