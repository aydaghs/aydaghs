from dataclasses import dataclass, field, asdict
from typing import Any
import json


@dataclass
class Entity:
    text: str
    label: str
    start: int
    end: int
    description: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Table:
    page: int
    index: int
    headers: list[str]
    rows: list[list[Any]]
    caption: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PageText:
    page: int
    text: str
    method: str  # "native" | "ocr"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DocumentResult:
    filename: str
    doc_type: str  # "pdf" | "image"
    pages: list[PageText] = field(default_factory=list)
    full_text: str = ""
    entities: list[Entity] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "filename": self.filename,
            "doc_type": self.doc_type,
            "metadata": self.metadata,
            "full_text": self.full_text,
            "pages": [p.to_dict() for p in self.pages],
            "entities": [e.to_dict() for e in self.entities],
            "tables": [t.to_dict() for t in self.tables],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


# spaCy label descriptions for the UI
LABEL_DESCRIPTIONS: dict[str, str] = {
    "PERSON": "Person name",
    "ORG": "Organization / Company",
    "GPE": "Country / City / Region",
    "LOC": "Non-GPE location",
    "DATE": "Date or time period",
    "MONEY": "Monetary value",
    "PERCENT": "Percentage",
    "PRODUCT": "Product name",
    "LAW": "Law or regulation",
    "PATENT_NUM": "Patent number",
    "IPC_CODE": "IPC classification code",
    "CLAIM_NUM": "Patent claim number",
    "INVENTOR": "Inventor name",
    "ASSIGNEE": "Patent assignee",
}
