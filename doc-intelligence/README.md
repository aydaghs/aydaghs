# Document Intelligence App

Extract structured data from PDFs and scanned images — entities, tables, relationships — and export clean JSON.

Built to demonstrate end-to-end document understanding, with a direct application to patent analysis (extracting inventors, assignees, IPC codes, claims, and prior art from patent PDFs).

---

## Features

| Capability | Detail |
|---|---|
| **Multi-format input** | Born-digital PDF, scanned PDF, PNG, JPG, TIFF |
| **Hybrid OCR** | Native text extraction for digital PDFs; EasyOCR fallback for scanned pages |
| **Named Entity Recognition** | spaCy `en_core_web_sm` + custom regex patterns for patent-specific entities |
| **Patent entity types** | Patent numbers (US/EP/WO/JP/CN…), IPC/CPC codes, claim references |
| **Standard NER types** | PERSON, ORG, GPE, DATE, MONEY, LAW, PRODUCT |
| **Table extraction** | pdfplumber for native PDF tables; optional `img2table` for image tables |
| **Structured JSON output** | Full-text per page, all entities with positions, all tables as row/column arrays |
| **Multi-language OCR** | English, French, German, Italian, Spanish, Chinese, Japanese, Arabic |

---

## Architecture

```
doc-intelligence/
├── app.py                  # Streamlit frontend
├── extractor/
│   ├── __init__.py
│   ├── ocr.py              # Text extraction (pdfplumber + EasyOCR)
│   ├── ner.py              # Named Entity Recognition (spaCy + regex)
│   ├── tables.py           # Table extraction (pdfplumber + img2table)
│   └── schema.py           # Dataclasses: DocumentResult, Entity, Table
└── requirements.txt
```

### Pipeline

```
Input file (PDF / image)
        │
        ▼
  ┌─────────────┐      born-digital PDF    ┌───────────────┐
  │  File type? │ ─────────────────────── ▶│  pdfplumber   │
  └─────────────┘                          │  native text  │
        │                                  └───────────────┘
        │ scanned PDF / image                      │
        ▼                                          │
  ┌───────────┐    rasterise (pdf2image)   ┌───────────────┐
  │  EasyOCR  │ ◀─────────────────────────│   PIL Image   │
  └───────────┘                           └───────────────┘
        │
        ▼
  Full text per page
        │
        ├──▶ spaCy NER + regex ──▶ Entity list
        │
        ├──▶ pdfplumber / img2table ──▶ Table list
        │
        └──▶ DocumentResult ──▶ JSON
```

---

## Quick Start

```bash
# 1. Create and activate a virtual environment
python -m venv .venv && source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download spaCy language model
python -m spacy download en_core_web_sm

# 4. (Linux) Install poppler for PDF rasterisation
#    Ubuntu/Debian: sudo apt-get install poppler-utils
#    macOS:         brew install poppler

# 5. Launch the app
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## Output Schema

```json
{
  "filename": "patent_US7654321.pdf",
  "doc_type": "pdf",
  "metadata": {
    "pages": 12,
    "extraction_method": "native",
    "entity_count": 47,
    "table_count": 3,
    "ocr_languages": ["en"]
  },
  "full_text": "...",
  "pages": [
    { "page": 1, "text": "...", "method": "native" }
  ],
  "entities": [
    {
      "text": "US7,654,321",
      "label": "PATENT_NUM",
      "start": 142,
      "end": 153,
      "description": "Patent number"
    },
    {
      "text": "H04L 29/06",
      "label": "IPC_CODE",
      "start": 201,
      "end": 211,
      "description": "IPC/CPC classification"
    }
  ],
  "tables": [
    {
      "page": 4,
      "index": 1,
      "headers": ["Claim", "Feature", "Prior Art"],
      "rows": [["1", "Wireless protocol", "US6,123,456"]]
    }
  ]
}
```

---

## Tech Stack

`EasyOCR` · `pdfplumber` · `pdf2image` · `spaCy` · `Streamlit` · `Pandas` · `Pillow`

---

## Relevance to Patent Research

This project maps directly onto the challenges of automated patent analysis:

- **Bibliographic extraction** — patent numbers, filing dates, inventors, assignees
- **Classification codes** — IPC/CPC section, class, subclass, group
- **Claim parsing** — identifying independent and dependent claims
- **Prior art detection** — extracting cited patent numbers from reference lists
- **Table data** — performance metrics, comparison tables in technical sections

The JSON output feeds directly into a database or downstream ML pipeline for similarity search, claim mapping, or landscape analysis.
