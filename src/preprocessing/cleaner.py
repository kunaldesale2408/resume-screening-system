"""
Text cleaning and normalisation.

Two outputs are produced from the same raw text:

* ``normalize``     - light clean-up that keeps the text readable. Used for
                      skill matching and entity extraction, where case and
                      punctuation still carry meaning (e.g. "C++", "B.Tech").
* ``lemmatize``     - aggressive clean-up for TF-IDF: lower-cased lemmas with
                      stop words, punctuation, numbers and contact details
                      removed, so "developed", "developing" and "develops"
                      all count as the same term "develop".
"""

import re
import unicodedata
from typing import List

from spacy.tokens import Doc

from src.nlp import get_nlp

_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_URL = re.compile(r"(https?://\S+|www\.\S+|\b\w+\.(?:com|in|io|org|net)/\S*)", re.I)
_PHONE_CANDIDATE = re.compile(r"\+?\(?\d[\d\s().-]{8,}\d")
_BULLETS = re.compile(r"[•●▪◦‣⁃]")
_SPACES = re.compile(r"[ \t ]+")
_BLANK_LINES = re.compile(r"\n\s*\n+")

# Words that appear in almost every resume and job post. Keeping them would
# make every resume look a bit similar to every job, so TF-IDF ignores them.
DOMAIN_STOPWORDS = {
    "experience", "experienced", "year", "skill", "education", "summary", "profile",
    "responsibility", "requirement", "require", "qualification", "role", "position",
    "candidate", "job", "work", "company", "ideal", "strong", "good", "excellent",
    "knowledge", "ability", "etc", "include", "including", "use", "using", "new",
}

# spaCy's lemmatizer is trained on general English; fix tech words it mangles.
_LEMMA_FIXES = {"datum": "data", "pandas": "pandas", "kera": "keras"}


def _drop_phone(match: "re.Match") -> str:
    """
    Remove a phone-number-like match, but keep date ranges such as
    "2018 - 2021" (8 digits), which experience extraction needs.
    """
    digits = sum(ch.isdigit() for ch in match.group())
    return " " if 10 <= digits <= 15 else match.group()


def normalize(text: str) -> str:
    """
    Make extracted text consistent without losing meaning.

    - Unicode NFKC (turns ligatures like "ﬁ" into "fi", full-width chars into ASCII)
    - Removes e-mail addresses, URLs and phone numbers (noise for matching,
      and personal data we don't need)
    - Converts bullet symbols to dashes and collapses repeated whitespace
    """
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("�", "-")  # PDF fonts often turn dashes into this
    text = _EMAIL.sub(" ", text)
    text = _URL.sub(" ", text)
    text = _PHONE_CANDIDATE.sub(_drop_phone, text)
    text = _BULLETS.sub("-", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _SPACES.sub(" ", text)
    text = _BLANK_LINES.sub("\n\n", text)
    return text.strip()


def lemmatize(text: str) -> List[str]:
    """
    Turn text into a list of lower-case lemmas for TF-IDF.

    Keeps alphabetic tokens of length >= 2 that are not stop words.
    Falls back to lower-cased tokens when no trained spaCy model is installed.
    """
    return lemmatize_doc(get_nlp()(text))


def lemmatize_doc(doc: "Doc") -> List[str]:
    """Same as ``lemmatize`` but for an already-processed spaCy Doc."""
    lemmas = []
    for token in doc:
        if token.is_stop or token.is_punct or token.like_num or token.is_space:
            continue
        lemma = (token.lemma_ or token.text).lower().strip()
        lemma = _LEMMA_FIXES.get(lemma, lemma)
        if len(lemma) < 2 or not any(ch.isalpha() for ch in lemma) or lemma in DOMAIN_STOPWORDS:
            continue
        lemmas.append(lemma)
    return lemmas
