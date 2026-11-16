<h1 align="center">Ayda Ghasemazar</h1>

<p align="center">
  MSc Data Science & Engineering · Politecnico di Torino<br>
  <sub>AI agents, automation and machine learning that people use in their daily work</sub>
</p>

<p align="center">
  <a href="https://www.linkedin.com/in/ayda-ghasemazar">
    <img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white"/>
  </a>
  <a href="mailto:ghasemazar.ayda@gmail.com">
    <img src="https://img.shields.io/badge/Email-EA4335?style=flat-square&logo=gmail&logoColor=white"/>
  </a>
  <img src="https://img.shields.io/badge/Turin,%20Italy-555555?style=flat-square&logo=googlemaps&logoColor=white"/>
</p>

---

## About

I'm a Data Science & Engineering master's student at Politecnico di Torino with a B.Sc. in Computer Science. I like finding the repetitive part of a process and building a working tool for it: an agent, a pipeline or a small interface, with checks so people can trust what it produces.

Recent work: AI Engineer Intern at BoostEd AI (Jul–Nov 2026), Research Assistant at DIGEP, Politecnico di Torino (Mar–Jul 2026).

---

## AI agents and automation

### Daily job-search agent on a cloud server · [job-scout](https://github.com/aydaghs/job-scout)
**Problem:** checking several job boards every day by hand, and seeing the same adverts again and again.
**Tools:** Python, Gemini API, SQLite, Telegram Bot API, Linux (systemd timers), Oracle Cloud.
**How it works:** every day it fetches postings from job boards, removes duplicates, asks an LLM to score each posting against a YAML profile of my skills and gaps, and sends the good matches to a Telegram bot.
**My part:** built on an open-source project; I deployed and run three scouts (jobs, internships, thesis) on a free cloud VM with daily timers, wrote and tuned the profiles, and fixed repeated alerts for listings that have no company name (the board gives them a new link every day).

### Multi-agent compliance analysis · NTT Data × BEST Torino Hackathon, Top 10 Finalist
**Problem:** a compliance analysis that was done by hand.
**Tools:** Python, LLM APIs, multi-agent design.
**How it works:** four agents split the analysis between them and pass their results on to produce the final report. Built in under 48 hours; I led the architecture and presented the working prototype.

### LLM Planner agent with a validation layer · BoostEd AI internship
**Problem:** AI-generated learning chapters needed quizzes, flashcards and exercises in the right places, and model output could not be used without checks.
**Tools:** LLMs, TypeScript, Zod, React, Docker.
**How it works:** a Planner agent decides where each interactive element goes; every model output is validated against a schema before use, and a human-in-the-loop React screen lets experts approve or correct results. *(Company code, not public.)*

### Screen-recording tutorials to interactive web pages · BoostEd AI internship
**Problem:** turning video tutorials into step-by-step interactive pages by hand is slow.
**Tools:** Python, OpenCV, NumPy, Tesseract OCR, Gemini, Playwright.
**How it works:** frame-change detection and pointer tracking find each step, OCR reads the screen, Gemini generates the page, and Playwright tests check the result automatically. *(Company code, not public.)*

### Document Intelligence app · [document-intelligence-app](https://github.com/aydaghs/document-intelligence-app)
**Problem:** getting structured data out of PDFs and scanned documents.
**Tools:** Python, Streamlit, Tesseract and EasyOCR, spaCy, OpenCV, SQLite.
**How it works:** OCR with a native-text fallback, table extraction, named-entity and relationship extraction, then export to clean JSON or a SQLite database, from a simple web interface.

---

## Machine learning projects

| Project | What it does | Tools |
|---|---|---|
| [Prompt compression for summarization](https://github.com/aydaghs/nlp-prompt-compression) *(team)* | 100+ experiments: up to 79% fewer input tokens while tracking ROUGE and BERTScore | Python, Mistral-7B, Transformers |
| [6D object pose estimation](https://github.com/aydaghs/6d-pose-estimation) *(team)* | Detection plus 3D pose from RGB-D images; my RGB-D model cut pose error by 16% | PyTorch, YOLOv8, ResNet-18, OpenCV |
| [Apartment rent price prediction](https://github.com/aydaghs/Apartment-Rent-Price-Prediction) *(team)* | Regression on 100K+ rental listings, explained with SHAP | Python, LightGBM, Scikit-learn |
| [PageRank from scratch](https://github.com/aydaghs/pagerank-from-scratch) | Sparse power iteration on a 6,012-page web graph, validated against published results | Python, NumPy |
| [Discrete event simulation](https://github.com/aydaghs/discrete-event-simulation) | Queueing, epidemic and random-graph simulations with confidence intervals | Python, SciPy, NetworkX |

---

## Skills

**Agents and LLMs:** LLM APIs (Gemini), prompting, multi-agent systems, RAG, LangChain, output validation (Zod)
**Building tools:** Python, TypeScript, React, REST APIs and JSON, Docker, Git, Playwright, Linux
**Data and ML:** Pandas, NumPy, SQL, PyTorch, Scikit-learn, OpenCV, OCR
**Languages:** English (IELTS 7.0), Persian and Azerbaijani (native), Italian (A2)
