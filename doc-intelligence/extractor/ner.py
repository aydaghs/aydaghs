"""
Named Entity Recognition pipeline.
- spaCy en_core_web_sm for standard entities (PERSON, ORG, DATE, …)
- regex-based matcher for patent-specific entities
"""
from __future__ import annotations

import re
import logging
from functools import lru_cache

from .schema import Entity, LABEL_DESCRIPTIONS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Patent-specific patterns
# ---------------------------------------------------------------------------

_PATENT_PATTERNS: list[tuple[str, str, re.Pattern]] = [
    # US7,654,321 B2 | US20190123456A1 | WO2020/123456
    (
        "PATENT_NUM",
        "Patent number",
        re.compile(
            r"\b(?:US|EP|WO|JP|CN|DE|GB|FR|KR|AU)\s*"
            r"[\d,]{6,12}(?:\s*[A-Z]\d?)?\b",
            re.IGNORECASE,
        ),
    ),
    # IPC / CPC codes: H04L 29/06, G06F17/00
    (
        "IPC_CODE",
        "IPC/CPC classification",
        re.compile(r"\b[A-H]\d{2}[A-Z]\s*\d+/\d+\b"),
    ),
    # "Claim 1", "independent claim 3"
    (
        "CLAIM_NUM",
        "Patent claim reference",
        re.compile(r"\b(?:independent\s+)?[Cc]laim\s+\d+\b"),
    ),
]


# ---------------------------------------------------------------------------
# spaCy model
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _get_nlp():
    import spacy

    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        logger.warning("en_core_web_sm not found, downloading…")
        from spacy.cli import download
        download("en_core_web_sm")
        return spacy.load("en_core_web_sm")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_entities(text: str) -> list[Entity]:
    """Run spaCy + regex patterns and return a deduplicated entity list."""
    entities: list[Entity] = []
    seen: set[tuple[str, str]] = set()

    def _add(ent: Entity):
        key = (ent.text.strip(), ent.label)
        if key not in seen:
            seen.add(key)
            entities.append(ent)

    # 1. spaCy NER
    nlp = _get_nlp()
    # Process in chunks to avoid hitting the default 1 000 000 char limit
    chunk_size = 500_000
    offset = 0
    for chunk_start in range(0, len(text), chunk_size):
        chunk = text[chunk_start : chunk_start + chunk_size]
        doc = nlp(chunk)
        for ent in doc.ents:
            if ent.label_ in LABEL_DESCRIPTIONS:
                _add(
                    Entity(
                        text=ent.text,
                        label=ent.label_,
                        start=chunk_start + ent.start_char,
                        end=chunk_start + ent.end_char,
                        description=LABEL_DESCRIPTIONS.get(ent.label_, ""),
                    )
                )
        offset += chunk_size

    # 2. Regex patent patterns
    for label, description, pattern in _PATENT_PATTERNS:
        for m in pattern.finditer(text):
            _add(
                Entity(
                    text=m.group(),
                    label=label,
                    start=m.start(),
                    end=m.end(),
                    description=description,
                )
            )

    entities.sort(key=lambda e: e.start)
    return entities


def group_entities(entities: list[Entity]) -> dict[str, list[str]]:
    """Group entity texts by label for easy display."""
    groups: dict[str, list[str]] = {}
    for ent in entities:
        groups.setdefault(ent.label, [])
        if ent.text not in groups[ent.label]:
            groups[ent.label].append(ent.text)
    return groups
