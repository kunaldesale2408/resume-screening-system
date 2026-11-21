"""
Shared spaCy pipeline.

Loading a spaCy model takes about a second, so it is loaded once per process
and reused by every module (extraction, skills, entities, scoring).
"""

import logging
from functools import lru_cache

import spacy
from spacy.language import Language

from src.config import settings

log = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_nlp() -> Language:
    """
    Return the spaCy pipeline named in settings (en_core_web_sm by default).

    The dependency parser is disabled because nothing here needs syntax trees,
    which makes processing roughly twice as fast. If the model is not
    installed, a blank English pipeline is used so the system still runs
    (without lemmas or named entities) and a warning is logged.
    """
    try:
        return spacy.load(settings.SPACY_MODEL, disable=["parser"])
    except OSError:
        log.warning(
            "spaCy model '%s' not found; falling back to a blank English "
            "pipeline. Install it with: python -m spacy download %s",
            settings.SPACY_MODEL,
            settings.SPACY_MODEL,
        )
        return spacy.blank("en")


def has_statistical_model() -> bool:
    """True when a trained pipeline (with lemmatizer and NER) is loaded."""
    nlp = get_nlp()
    return "ner" in nlp.pipe_names
