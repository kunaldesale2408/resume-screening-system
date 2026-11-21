"""
Structured information extraction from resumes and job descriptions.

Rule-based extraction (regular expressions) is used for things with a
predictable written form: years of experience, date ranges and degrees.
spaCy's statistical NER is used for things that don't have one: people's
names and organisations.
"""

import re
from datetime import date
from typing import Dict, List, Optional, Tuple

from spacy.tokens import Doc

# ---------------------------------------------------------------- sections

_SECTION_HEADERS = {
    "summary": ["summary", "professional summary", "profile", "objective", "about me", "career objective"],
    "experience": ["experience", "work experience", "professional experience", "employment",
                   "employment history", "work history", "internship", "internships", "internship experience"],
    "education": ["education", "academic background", "academics", "qualifications", "educational qualifications"],
    "skills": ["skills", "technical skills", "core skills", "key skills", "skills & tools", "technologies"],
    "projects": ["projects", "personal projects", "academic projects", "key projects"],
    "certifications": ["certifications", "certificates", "licenses & certifications",
                       "awards & certifications", "courses", "certifications & awards"],
    "achievements": ["achievements", "awards", "honors", "competitive data science"],
}
_HEADER_LOOKUP = {name: section for section, names in _SECTION_HEADERS.items() for name in names}


def split_sections(text: str) -> Dict[str, str]:
    """
    Split a resume into sections by recognising header lines such as
    "EXPERIENCE" or "Technical Skills:". Text before the first header goes
    into "header" (usually name and contact details).
    """
    sections: Dict[str, List[str]] = {"header": []}
    current = "header"
    for line in text.splitlines():
        key = re.sub(r"[^a-z& ]", "", line.strip().lower()).strip()
        if key in _HEADER_LOOKUP and len(key.split()) <= 4:
            current = _HEADER_LOOKUP[key]
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


# ------------------------------------------------------ years of experience

_YEARS = re.compile(
    r"(\d{1,2}(?:\.\d)?)(?:\s*(?:-|–|to)\s*(\d{1,2}))?\s*\+?\s*(?:years?|yrs?)\b",
    re.I,
)
_MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}
_DATE = r"(?:(?P<{p}m>jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?,?\s*)?(?P<{p}y>(?:19|20)\d{{2}})"
_RANGE = re.compile(
    _DATE.format(p="s")
    + r"\s*(?:-|–|—|to|until)\s*(?:"
    + _DATE.format(p="e")
    + r"|(?P<present>present|current|now|till date|ongoing|today))",
    re.I,
)


def stated_years(text: str) -> List[Tuple[float, Optional[float]]]:
    """
    Find phrases like "5+ years", "3 yrs" or "0-1 year".
    Returns (low, high) pairs; high is None when no range was given.
    """
    out = []
    for match in _YEARS.finditer(text):
        low = float(match.group(1))
        high = float(match.group(2)) if match.group(2) else None
        if low <= 50:
            out.append((low, high))
    return out


def years_from_date_ranges(text: str, today: Optional[date] = None) -> float:
    """
    Add up job durations from date ranges such as "Jan 2020 - Mar 2022"
    or "2021 - Present". Overlapping jobs are merged so they aren't
    counted twice.
    """
    today = today or date.today()
    spans = []
    for m in _RANGE.finditer(text):
        start = int(m.group("sy")) * 12 + _MONTHS.get((m.group("sm") or "jan")[:3].lower(), 1) - 1
        if m.group("present"):
            end = today.year * 12 + today.month - 1
        else:
            end = int(m.group("ey")) * 12 + _MONTHS.get((m.group("em") or "jan")[:3].lower(), 1) - 1
            if m.group("em"):
                end += 1  # "Apr 2026 - Sep 2026" includes September
        if end > start:
            spans.append((start, end))

    total, last_end = 0, None
    for start, end in sorted(spans):
        if last_end is not None and start < last_end:
            start = last_end  # skip the overlapping part
        if end > start:
            total += end - start
            last_end = end if last_end is None else max(last_end, end)
    return round(total / 12, 1)


def resume_years(text: str, sections: Dict[str, str]) -> Optional[float]:
    """
    Years of experience for a resume: the largest figure the candidate
    states (e.g. "5+ years"), or else the total of the date ranges in the
    experience section. Education dates are ignored.
    """
    stated = [low for low, _ in stated_years(sections.get("summary", "") + "\n" + sections.get("header", ""))]
    if stated:
        return max(stated)
    experience_text = sections.get("experience", "")
    if experience_text:
        years = years_from_date_ranges(experience_text)
        return years if years > 0 else 0.0
    return None


def required_years(jd_text: str) -> Optional[float]:
    """Minimum years a job description asks for (the smallest number stated)."""
    found = stated_years(jd_text)
    return min(low for low, _ in found) if found else None


# --------------------------------------------------------------- education

EDUCATION_LEVELS = {0: None, 1: "Diploma", 2: "Bachelor's", 3: "Master's", 4: "PhD"}

_EDU_PATTERNS = [
    (4, r"\bph\.?\s?d\b|\bdoctorate\b|\bdoctor of philosophy\b"),
    (3, r"\bmaster'?s?\b|\bm\.?\s?tech\b|\bm\.\s?e\.|\bm\.?\s?sc\b|\bm\.s\.|\bms\s+(?:in|degree)\b"
        r"|\bmca\b|\bmba\b|\bpost[\s-]?graduat"),
    (2, r"\bbachelor'?s?\b|\bb\.?\s?tech\b|\bb\.\s?e\.|\bb\.?\s?sc\b|\bb\.s\.|\bbs\b|\bbca\b|\bbba\b"
        r"|\bb\.?\s?com\b|\bundergraduate degree\b"),
    (1, r"\bdiploma\b"),
]


def education_levels(text: str) -> List[int]:
    """All degree levels mentioned in the text (1 = diploma ... 4 = PhD)."""
    return [level for level, pattern in _EDU_PATTERNS if re.search(pattern, text, re.I)]


def resume_education(text: str) -> int:
    """Highest degree level on a resume, 0 if none found."""
    levels = education_levels(text)
    return max(levels) if levels else 0


def required_education(jd_text: str) -> int:
    """
    Lowest degree level a job accepts ("Bachelor's or Master's" -> Bachelor's).
    A bare mention of "degree" counts as Bachelor's. 0 means no requirement.
    """
    levels = education_levels(jd_text)
    if levels:
        return min(levels)
    return 2 if re.search(r"\bdegree\b", jd_text, re.I) else 0


# ------------------------------------------------------------ certifications

def certifications(text: str, sections: Dict[str, str]) -> List[str]:
    """Lines that describe a certification (from that section, or containing 'certif')."""
    lines = [l for l in sections.get("certifications", "").splitlines() if l.strip()]
    lines += [l for l in text.splitlines() if re.search(r"certif", l, re.I)]
    seen, out = set(), []
    for line in lines:
        clean = line.strip(" -•\t")[:100]
        if clean and clean.lower() not in seen and clean.lower() not in _HEADER_LOOKUP:
            seen.add(clean.lower())
            out.append(clean)
    return out


def requires_certification(jd_text: str) -> bool:
    return bool(re.search(r"certif", jd_text, re.I))


# ------------------------------------------------------- named entities (NER)

def candidate_name(doc: Doc, text: str) -> Optional[str]:
    """
    Guess the candidate's name: the first PERSON entity near the top of the
    resume, or else a short first line made only of words (e.g. "JOHN DOE").
    """
    def plausible(name: str) -> bool:
        return not _NOT_A_NAME.search(name)

    for ent in doc.ents:
        if ent.start_char > 300:
            break
        # NER can run across a line break ("JOHN DOE\nEmail"); a name never does.
        name = ent.text.strip().split("\n")[0].strip()
        if ent.label_ == "PERSON" and 1 < len(name.split()) <= 4 and plausible(name):
            return name.title()
    for line in text.splitlines()[:3]:
        words = line.strip(" #*").split()
        if 2 <= len(words) <= 4 and all(w.replace(".", "").isalpha() for w in words) and plausible(line):
            return " ".join(words).title()
    return None


_NOT_A_NAME = re.compile(r"\b(resume|curriculum|vitae|cv|profile|summary)\b", re.I)


def organizations(doc: Doc, limit: int = 8) -> List[str]:
    """Organisations (companies, universities) recognised by spaCy NER."""
    seen, out = set(), []
    for ent in doc.ents:
        name = ent.text.strip()
        if ent.label_ == "ORG" and 2 < len(name) < 60 and name.lower() not in seen:
            seen.add(name.lower())
            out.append(name)
    return out[:limit]
