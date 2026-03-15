"""
Document Intelligence App
=========================
Upload a PDF or image → extract text, entities, tables → download clean JSON.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Document Intelligence",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .entity-chip {
        display: inline-block;
        padding: 2px 10px;
        margin: 2px 4px;
        border-radius: 12px;
        font-size: 0.82em;
        font-weight: 600;
    }
    .stDownloadButton > button {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Entity label → colour mapping
# ---------------------------------------------------------------------------
LABEL_COLORS: dict[str, str] = {
    "PERSON":     "#d4edda",
    "ORG":        "#cce5ff",
    "GPE":        "#fff3cd",
    "LOC":        "#ffeeba",
    "DATE":       "#f8d7da",
    "MONEY":      "#d1ecf1",
    "PERCENT":    "#e2d9f3",
    "PRODUCT":    "#fde2e2",
    "LAW":        "#e8f4ea",
    "PATENT_NUM": "#ffe0b2",
    "IPC_CODE":   "#b2dfdb",
    "CLAIM_NUM":  "#f8bbd0",
    "INVENTOR":   "#dcedc8",
    "ASSIGNEE":   "#bbdefb",
}


def label_chip(text: str, label: str) -> str:
    color = LABEL_COLORS.get(label, "#eeeeee")
    return (
        f'<span class="entity-chip" style="background:{color}" '
        f'title="{label}">{text}</span>'
    )


# ---------------------------------------------------------------------------
# Cached pipeline
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def load_nlp():
    """Pre-warm the spaCy model so the first document is fast."""
    from extractor.ner import _get_nlp
    return _get_nlp()


@st.cache_data(show_spinner=False)
def run_pipeline(
    file_bytes: bytes,
    filename: str,
    ocr_languages: list[str],
    run_ner: bool,
    run_tables: bool,
) -> dict:
    from extractor.ocr import extract_text
    from extractor.ner import extract_entities
    from extractor.tables import extract_tables
    from extractor.schema import DocumentResult

    suffix = Path(filename).suffix.lower()
    doc_type = "pdf" if suffix == ".pdf" else "image"

    result = DocumentResult(filename=filename, doc_type=doc_type)

    # --- OCR / text extraction ---
    with st.spinner("Extracting text…"):
        result.pages = extract_text(file_bytes, filename, ocr_languages or ["en"])
        result.full_text = "\n\n".join(p.text for p in result.pages)
        result.metadata["pages"] = len(result.pages)
        result.metadata["ocr_languages"] = ocr_languages
        methods = {p.method for p in result.pages}
        result.metadata["extraction_method"] = (
            "native" if methods == {"native"}
            else "ocr" if methods == {"ocr"}
            else "mixed"
        )

    # --- NER ---
    if run_ner and result.full_text:
        with st.spinner("Running Named Entity Recognition…"):
            result.entities = extract_entities(result.full_text)
            result.metadata["entity_count"] = len(result.entities)

    # --- Tables ---
    if run_tables:
        with st.spinner("Extracting tables…"):
            result.tables = extract_tables(file_bytes, filename)
            result.metadata["table_count"] = len(result.tables)

    return result.to_dict()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Settings")

    st.subheader("OCR Languages")
    lang_options = {
        "English": "en",
        "French": "fr",
        "German": "de",
        "Italian": "it",
        "Spanish": "es",
        "Chinese (Simplified)": "ch_sim",
        "Japanese": "ja",
        "Arabic": "ar",
    }
    selected_langs = st.multiselect(
        "Languages to recognise",
        options=list(lang_options.keys()),
        default=["English"],
    )
    ocr_langs = [lang_options[l] for l in selected_langs] or ["en"]

    st.subheader("Pipeline Steps")
    run_ner = st.checkbox("Named Entity Recognition", value=True)
    run_tables = st.checkbox("Table Extraction", value=True)

    st.divider()
    st.caption(
        "**Stack:** EasyOCR · pdfplumber · spaCy · Streamlit\n\n"
        "Built for patent & legal document intelligence."
    )

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
st.title("📄 Document Intelligence")
st.caption("Extract structured data — entities, tables, and full text — from PDFs and scanned images.")

uploaded_file = st.file_uploader(
    "Upload a PDF or image",
    type=["pdf", "png", "jpg", "jpeg", "tiff", "tif", "bmp", "webp"],
    help="Supports born-digital PDFs (native extraction) and scanned documents / images (OCR).",
)

if uploaded_file is None:
    # Landing state
    st.info(
        "👆 Upload a document to get started.\n\n"
        "**Supported inputs:** PDF (native or scanned), PNG, JPG, TIFF\n\n"
        "**Outputs:** Full text · Named entities (persons, orgs, dates, patent numbers, IPC codes…) · Tables · Downloadable JSON"
    )
    st.stop()

# ---------------------------------------------------------------------------
# Run pipeline
# ---------------------------------------------------------------------------
file_bytes = uploaded_file.read()
start = time.perf_counter()

result_dict = run_pipeline(
    file_bytes=file_bytes,
    filename=uploaded_file.name,
    ocr_languages=ocr_langs,
    run_ner=run_ner,
    run_tables=run_tables,
)

elapsed = time.perf_counter() - start

# ---------------------------------------------------------------------------
# Summary bar
# ---------------------------------------------------------------------------
st.success(f"Processed **{uploaded_file.name}** in {elapsed:.1f}s")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Pages", result_dict["metadata"].get("pages", "—"))
col2.metric("Characters", f"{len(result_dict['full_text']):,}")
col3.metric("Entities", result_dict["metadata"].get("entity_count", 0))
col4.metric("Tables", result_dict["metadata"].get("table_count", 0))

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_text, tab_entities, tab_tables, tab_json = st.tabs(
    ["📝 Extracted Text", "🏷️ Entities", "📊 Tables", "🗂️ JSON Output"]
)

# --- Text tab ---
with tab_text:
    method_badge = result_dict["metadata"].get("extraction_method", "")
    st.caption(f"Extraction method: **{method_badge}**")

    pages = result_dict.get("pages", [])
    if len(pages) == 1:
        st.text_area("Full text", value=pages[0]["text"], height=500, label_visibility="collapsed")
    else:
        for page in pages:
            with st.expander(f"Page {page['page']}  ({page['method']})", expanded=page["page"] == 1):
                st.text(page["text"] or "*(no text extracted)*")

# --- Entities tab ---
with tab_entities:
    entities = result_dict.get("entities", [])
    if not entities:
        st.info("No entities found (enable NER in the sidebar or check the document content).")
    else:
        import pandas as pd
        from extractor.ner import group_entities
        from extractor.schema import Entity

        # Reconstruct Entity objects for grouping
        ent_objs = [
            Entity(
                text=e["text"],
                label=e["label"],
                start=e["start"],
                end=e["end"],
                description=e["description"],
            )
            for e in entities
        ]
        groups = group_entities(ent_objs)

        # Entity-type filter
        all_labels = sorted(groups.keys())
        selected_labels = st.multiselect(
            "Filter by entity type", options=all_labels, default=all_labels
        )

        # Chips view
        st.markdown("#### Entity highlights")
        for label in selected_labels:
            if label not in groups:
                continue
            chips_html = " ".join(label_chip(t, label) for t in groups[label])
            st.markdown(
                f"**{label}** — <small>{len(groups[label])} unique</small><br>{chips_html}",
                unsafe_allow_html=True,
            )

        # Table view
        st.markdown("#### All entities")
        df = pd.DataFrame(
            [
                {"Type": e["label"], "Text": e["text"], "Description": e["description"]}
                for e in entities
                if e["label"] in selected_labels
            ]
        )
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)

# --- Tables tab ---
with tab_tables:
    tables = result_dict.get("tables", [])
    if not tables:
        st.info("No tables detected. For images, install `img2table` for better table detection.")
    else:
        import pandas as pd

        for tbl in tables:
            st.markdown(f"**Table {tbl['index']}** — Page {tbl['page']}")
            try:
                df = pd.DataFrame(tbl["rows"], columns=tbl["headers"] if tbl["headers"] else None)
                st.dataframe(df, use_container_width=True, hide_index=True)
            except Exception:
                st.write(tbl)
            st.divider()

# --- JSON tab ---
with tab_json:
    json_str = json.dumps(result_dict, indent=2, ensure_ascii=False)
    st.code(json_str, language="json")
    st.download_button(
        label="⬇️ Download JSON",
        data=json_str,
        file_name=Path(uploaded_file.name).stem + "_extracted.json",
        mime="application/json",
    )
