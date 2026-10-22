# Automatic Keyword and Keyphrase Extractor

> **A B.Tech 3rd-Year AIML Mini Project**  
> *Department of Artificial Intelligence and Machine Learning*

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://python.org)

[![Framework](https://img.shields.io/badge/Framework-Flask%203.x-green.svg)](https://flask.palletsprojects.com/)

[![NLP](https://img.shields.io/badge/NLP-NLTK%20%7C%20YAKE%20%7C%20Scikit--Learn-orange.svg)](https://nltk.org)

[![Tests](https://img.shields.io/badge/Tests-Passing%2026%2F26-brightgreen.svg)](#11-testing--verification)

## 1. Abstract

In the modern digital era, vast volumes of unstructured text are generated daily across academic repositories, digital journalism, and technical documentation. Identifying the main topics of documents manually is labor-intensive and difficult to scale.

**Automatic Keyword and Keyphrase Extractor** is a Natural Language Processing (NLP) web application designed to automatically extract and rank important keywords and multi-word keyphrases from text and uploaded PDF, DOCX, and TXT documents. The system supports three extraction methods: YAKE, TF-IDF, and RAKE. It provides an interactive dashboard, extraction statistics, Chart.js visualizations, and report exports in CSV, JSON, and TXT formats. The application is developed as a B.Tech 3rd-Year AIML mini project.

---

## 2. Problem Statement

Manual tagging and indexing of extensive documents is slow, error-prone, and inconsistent across different human annotators. Conventional keyword search methods rely on simple word counts or superficial frequency counters that capture common repetitive words rather than salient topical concepts.

The objective of this project is to develop an NLP system that extracts a ranked subset of $K$ keywords or keyphrases $\{k_1, k_2, \dots, k_K\}$ from an arbitrary document $D$ such that the selected phrases accurately encapsulate the topical semantics of $D$, while filtering out non-topical function words, boilerplate vocabulary, and noise.

---

## 3. Objectives

1. **Automated Phrase Extraction:** Automatically identify and extract meaningful single-word keywords and multi-word noun phrases.
2. **Multi-Format Document Ingestion:** Provide safe, in-memory parsing for PDF (via PyMuPDF), Microsoft Word (via python-docx), and plain text files.
3. **Multi-Algorithm Support:** Provide statistical (YAKE and RAKE) and vector-space (TF-IDF) keyword extraction methods.
4. **Interactive Dashboard:** Build a responsive, accessible user interface with live character/word counters and document domain selection.
5. **Data Visualization & Analytics:** Generate interactive horizontal relevance charts and term-frequency distributions using Chart.js.
6. **Multi-Format Export:** Enable 1-click downloading of analysis reports in CSV, JSON, and structured TXT formats.
7. **Educational Transparency:** Explicitly document score semantics, single-document TF-IDF behavior, and standard academic evaluation metrics ($P@K, R@K, F_1@K$).

---

## 4. Existing System vs. Proposed System

| Dimension | Existing System / Baseline | Proposed System (This Project) |
| :--- | :--- | :--- |
| **Methodology** | Simple word frequency counting or manual human tagging. | Unsupervised NLP algorithms (YAKE, TF-IDF, and RAKE) assessing word frequency, position, co-occurrence, and sentence dispersion. |
| **Phrase Extraction** | Mostly restricted to isolated single words; fails on multi-word entities. | Extracts both unigrams and linguistic noun phrases (e.g., *"natural language processing"*). |
| **Technical Terms** | Over-aggressive punctuation stripping corrupts hyphenated compounds and acronyms. | Safe tokenization preserving hyphenated terms (`state-of-the-art`) and acronyms (`BERT`, `NLP`, `API`). |
| **Document Formats** | Only supports plain text copy-pasting. | Directly ingests and validates `.pdf`, `.docx`, and `.txt` documents. |
| **Visualization** | Static, non-interactive tables or basic word clouds. | Interactive Chart.js charts, score progress bars, frequency distributions, and multi-format exports. |

---

## 5. System Architecture & NLP Pipeline

The pipeline follows a clean, modular six-stage progression:

```
+-----------------------------------------------------------------------------------+
|                            1. Document Ingestion                                  |
|   Pasted Text  |  PDF (PyMuPDF)  |  DOCX (python-docx)  |  Plain Text (UTF-8)    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                            2. NLP Preprocessing                                   |
|   • Whitespace & newline normalization                                            |
|   • Sentence segmentation (nltk.sent_tokenize)                                    |
|   • Word tokenization preserving hyphens & acronyms (BERT, NLP, API)              |
|   • Stopword filtering (NLTK base + Academic / News / Technical domain stops)     |
|   • WordNet POS-guided lemmatization                                              |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        3. Candidate Phrase Generation                             |
|   • POS-guided noun phrase chunking: (Adjective)* (Noun)+                         |
|   • N-gram generation (Unigrams, Bigrams, Trigrams)                               |
|   • Boundary stopword filtering & punctuation validation                          |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                            4. Algorithm Ranking                                   |
|   [YAKE] Statistical features: casing, position, frequency, dispersion            |
|   [TF-IDF] Sentence-level pseudo-corpus (Inverse Sentence Frequency)              |
|   [RAKE] Keyword and keyphrase scoring using word frequency and co-occurrence     |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                         5. Normalization & Scoring                                |
|   • YAKE score inversion: Relevance = 1 / (1 + raw_score) in (0, 1]              |
|   • Exact term frequency calculation in source text                               |
|   • Candidate classification (Keyword vs Keyphrase)                               |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                       6. Dashboard Presentation & Export                          |
|   • Summary cards (Words, Vocab, Sentences, Latency)                              |
|   • Chart.js horizontal score chart & frequency chart                             |
|   • Ranked interactive results table                                              |
|   • Export: CSV | JSON | Formatted TXT Report                                     |
+-----------------------------------------------------------------------------------+
```

---

## 6. Extraction Algorithms Explained

### Method 1: YAKE (Yet Another Keyword Extractor)
- **Type:** Unsupervised Statistical
- **Working Principle:** Evaluates individual term features within a single document without requiring external training corpora. Features include:
  1. *Casing Aspect:* Identifies acronyms and capitalized terms.
  2. *Word Positional Bias:* Gives preferential weight to terms appearing in opening sentences.
  3. *Word Frequency & Relatedness:* Compares occurrence frequency against lexical context.
  4. *Dispersion across Sentences:* Analyzes how uniformly terms disperse throughout the text.
- **Score Semantics:** In YAKE, a **lower raw score indicates higher importance** ($0$ is an ideal score). To provide intuitive comparison alongside other methods, our system computes a normalized relevance metric:
  $$\text{Relevance} = \frac{1}{1 + S_{\text{raw}}} \in (0, 1]$$

### Method 2: TF-IDF (Sentence-Level Pseudo-Corpus)
- **Type:** Vector Space Model / Term Frequency - Inverse Document Frequency
- **Working Principle:** Standard TF-IDF requires a large corpus of distinct documents to calculate Inverse Document Frequency ($\text{IDF}$). When processing a solitary document, calculating corpus IDF yields flat, uninformative weights.
- **Our Implementation:** The document's constituent sentences are treated as a *pseudo-corpus*. This allows calculating **Inverse Sentence Frequency (ISF)**:
  - Words occurring in almost every sentence are penalized as generic document filler.
  - Words concentrated in topical sentences receive elevated weights.
  - Scikit-learn's `TfidfVectorizer` evaluates unigrams, bigrams, and trigrams with domain stopword removal.
  - Candidate scores are combined using maximum sentence activation ($60\%$) and mean sentence activation ($40\%$), normalized to $[0, 1]$.

### Method 3: RAKE (Rapid Automatic Keyword Extraction)

- **Type:** Unsupervised Statistical Keyword Extraction
- **Working Principle:** RAKE identifies candidate keywords and keyphrases by splitting text using stopwords and punctuation. It calculates word-level scores using word frequency and degree, then combines these scores to rank candidate phrases.
- **Advantages:** It can extract meaningful multi-word phrases without requiring a trained model or external training corpus.
---

## 7. Project Folder Structure

```
automatic-keyword-extractor/
│
├── app.py                      # Flask web application & REST API endpoints
├── requirements.txt            # Python package dependencies
├── README.md                   # Complete academic project documentation & guide
├── .gitignore                  # Git ignore rules
│
├── templates/                  # Frontend HTML templates
│   ├── index.html              # Main interactive dashboard
│   └── about.html              # Academic methodology & viva guide
│
├── static/                     # Static frontend assets
│   ├── css/
│   │   └── style.css           # Modern navy/indigo styling & layout
│   └── js/
│       ├── app.js              # Application logic, API integration, validations
│       └── charts.js           # Chart.js visualization management
│
├── nlp/                        # Core Natural Language Processing modules
│   ├── __init__.py             # Extraction pipeline orchestration & metadata
│   ├── preprocessing.py        # Text cleaning, tokenization, POS chunking
│   ├── yake_extractor.py       # YAKE statistical extractor wrapper
│   ├── tfidf_extractor.py      # TF-IDF sentence-level pseudo-corpus extractor
│   └──rake_extractor.py      # RAKE keyword and keyphrase extractor
│
├── utils/                      # Document parsing and export helpers
│   ├── __init__.py             # Utils package exports
│   ├── document_reader.py      # PyMuPDF, python-docx, and TXT safe extraction
│   └── exporters.py            # CSV, JSON, and TXT report generators
│
└── tests/                      # Automated test suite (26 passing tests)
    ├── __init__.py             # Tests package
    ├── test_preprocessing.py   # Tokenization, cleaning, and candidate tests
    ├── test_extraction.py      # YAKE, TF-IDF, and filter tests
    ├── test_document_reader.py # PDF, DOCX, and TXT reader tests
    └── test_api_and_exports.py # Flask endpoints, error handling, export tests
```

---

## 8. Installation & Setup Guide (Windows PowerShell)

Follow these step-by-step instructions to run the application on a Windows laptop using Windows PowerShell:

### Step 1: Open Windows PowerShell
Navigate to the project directory:
```powershell
cd C:\Users\Asus\.gemini\antigravity\scratch\automatic-keyword-extractor
```

### Step 2: Create and Activate Virtual Environment
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
*(If PowerShell displays an Execution Policy restriction, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and re-run activate).*

### Step 3: Install Required Dependencies
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Step 4: Download Essential NLTK Corpora
```powershell
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('averaged_perceptron_tagger_eng')"
```

### Step 5: Run the Flask Application
```powershell
python app.py
```

### Step 6: Open the Dashboard in your Browser
Once started, open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 9. How to Use the Application

1. **Option 1 (Paste Text):**
   - Click on the *Option 1: Paste Text* tab.
   - Enter or paste your text. For a quick demo, click one of the preloaded sample buttons: **Academic**, **News**, or **Technical**.
   - Observe the live word and character counters update in real-time.
2. **Option 2 (Upload Document):**
   - Switch to the *Option 2: Upload Document* tab.
   - Drag and drop or browse to select a `.pdf`, `.docx`, or `.txt` file (Max 10 MB).
3. **Configure Extraction Parameters:**
   - **Keywords to Extract:** Choose 5, 10, 15, or 20.
   - **NLP Extraction Method:** Choose YAKE (Default), TF-IDF, or RAKE.
   - **Document Domain:** Choose Academic Paper, News Article, or Technical Documentation.
   - **Candidate Type:** Choose Both (Keywords & Phrases), Single Words Only, or Multi-word Phrases Only.
4. **Extract Keywords:**
   - Click the **Extract Keywords** button.
   - View the execution time and summary metrics cards.
   - Inspect the horizontal relevance score bar chart and the term frequency chart.
   - Review the sortable, ranked table with classification badges and relevance scores.
5. **Export Analysis:**
   - Click **CSV**, **JSON**, or **TXT Report** to download the analysis report.

---

## 10. API Endpoint Documentation
### 1. Health Check

- **Endpoint:** `GET /api/health`
- **Description:** Verifies that the Flask service is running and reports algorithm availability.
- **Response Example:**

```json
{
  "status": "healthy",
  "service": "Automatic Keyword and Keyphrase Extractor",
  "python_version": "3.14.6",
  "algorithms": {
    "yake": {
      "available": true,
      "type": "Statistical"
    },
    "tfidf": {
      "available": true,
      "type": "Vector Space / Sentence-level"
    },
    "rake": {
      "available": true,
      "type": "Statistical"
    }
  }
}
```
### 2. Keyword Extraction

- **Endpoint:** `POST /api/extract`
- **Content-Type:** `application/json` or `multipart/form-data`

- **Parameters:**
  - `text` (string, optional if file provided): Document text content.
  - `file` (binary, optional if text provided): Uploaded `.pdf`, `.docx`, or `.txt` file.
  - `method` (string): `"yake"` (default), `"tfidf"`, or `"rake"`.
  - `top_n` (integer): `5`, `10`, `15`, or `20` (default: `10`).
  - `doc_type` (string): `"academic"` (default), `"news"`, or `"technical"`.
  - `candidate_type` (string): `"both"` (default), `"single"`, or `"multi"`.

- **Response Structure:**

```json
{
  "success": true,
  "algorithm": "YAKE",
  "document_type": "Academic",
  "candidate_filter": "both",
  "total_keywords_extracted": 10,
  "statistics": {
    "total_characters": 820,
    "total_words": 104,
    "unique_words": 76,
    "total_sentences": 5,
    "processing_time_ms": 14.8,
    "estimated_reading_time_sec": 31
  },
  "keywords": [
    {
      "rank": 1,
      "text": "natural language processing",
      "score": 0.8842,
      "raw_score": 0.130965,
      "frequency": 3,
      "word_count": 3,
      "type": "keyphrase"
    }
  ]
}
```

### 3. Export Report
- **Endpoint:** `POST /api/export/<format>`
- **URL Parameters:** `format` $\in$ `{csv, json, txt}`
- **Payload:** Extraction results JSON object.
- **Response:** File attachment with proper `Content-Disposition` header.

---

## 11. Testing & Verification

The project includes an automated test suite using Python's `unittest` framework:

```powershell
python -m unittest discover tests -v
```
### Test Coverage Summary

- **`tests/test_preprocessing.py` (6 tests):** Whitespace normalization, sentence tokenization, hyphen preservation, document statistics, candidate validation, and candidate phrase generation.
- **`tests/test_extraction.py` (5 tests):** YAKE extraction, TF-IDF extraction, RAKE extraction, candidate type filtering (single vs. multi), and pipeline integration.
- **`tests/test_document_reader.py` (6 tests):** TXT parsing, in-memory DOCX parsing, in-memory PDF parsing via PyMuPDF, blank PDF detection, unsupported file type rejection, and empty file handling.
- **`tests/test_api_and_exports.py` (9 tests):** Health check endpoint, valid JSON extraction, empty text rejection, short input validation, CSV export generation, JSON export formatting, TXT report generation, and home/about template rendering.

**Total: 26 tests, 26 passing (100% pass rate).**

**Verification command:**
`python -m unittest discover tests -v`

## 12. Academic Evaluation & Viva Guide

### How is Keyword Extraction Evaluated in NLP Research?
In academic evaluations, automatic keyword extractors are evaluated against gold-standard human-annotated reference keywords (e.g., from datasets such as **Inspec**, **SemEval-2010**, or **DUC-2001**).

The standard performance metrics calculated at cutoff rank $K$ are:

#### 1. Precision@K ($P@K$)
The fraction of extracted top-$K$ candidates that match human-annotated gold-standard keywords:
$$P@K = \frac{|E_K \cap G|}{K}$$
*Where $E_K$ is the set of top-$K$ extracted keywords and $G$ is the gold-standard reference keyword set.*

#### 2. Recall@K ($R@K$)
The fraction of human-annotated gold-standard keywords discovered in the extracted top-$K$ candidates:
$$R@K = \frac{|E_K \cap G|}{|G|}$$

#### 3. F1-Score@K ($F_1@K$)
The harmonic mean of Precision@K and Recall@K:
$$F_1@K = \frac{2 \times P@K \times R@K}{P@K + R@K}$$

> **Important Viva Tip for Students:** Never claim an arbitrary "98% accuracy" for unsupervised keyword extraction in an exam. State that unsupervised extraction is evaluated on benchmark corpora using F1-score@K. Due to the high linguistic variation in how different human experts tag the same paper, state-of-the-art unsupervised extractors (including YAKE, TextRank, and TF-IDF) typically achieve F1-scores between **0.30 and 0.48** on standard benchmark datasets like SemEval-2010.

---

## 13. System Requirements

### Hardware Requirements
- **Processor:** Intel Core i3 / AMD Ryzen 3 or higher.
- **RAM:** Minimum 4 GB (8 GB recommended).
- **Disk Space:** ~500 MB for Python environment and NLP corpora.

### Software Requirements
- **Operating System:** Windows 10/11, Linux, or macOS.
- **Python Version:** Python 3.10 to Python 3.14.
- **Web Browser:** Google Chrome, Mozilla Firefox, or Microsoft Edge.

---

## 14. Advantages, Limitations & Future Scope

### Advantages
- **Lightweight & Fast:** Runs locally on a standard student laptop in milliseconds without requiring external APIs or paid keys.
- **Multi-Format Ingestion:** Directly parses PDF, DOCX, and TXT files without external conversion tools.
- **Linguistic Safeguards:** Preserves hyphenated technical terms and domain acronyms.
- **Transparent Score Interpretation:** Cleary separates raw algorithm metrics from normalized user-facing relevance scores.

### Limitations
- **Scanned Image PDFs:** PDFs containing only scanned page images cannot be read without an Optical Character Recognition (OCR) engine like Tesseract.
- **Single-Document IDF:** Because only one document is analyzed at a time, TF-IDF relies on sentence-level pseudo-corpus segmentation rather than an internet-scale corpus.

### Future Scope
- **Tesseract OCR Integration:** Add optical character recognition to extract text from scanned research papers and image-heavy PDFs.
- **Corpus Upload:** Allow uploading a ZIP file of 50+ papers to compute true cross-document TF-IDF matrices.
- **Knowledge Graph Visualization:** Render an interactive co-occurrence graph linking extracted keyphrases using D3.js or Vis.js.
- **Multi-Lingual Support:** Extend the stopwords and lemmatization pipeline to Hindi, Spanish, French, and German.

---

## 15. Conclusion

The **Automatic Keyword and Keyphrase Extractor** fulfills all the functional and academic criteria of a B.Tech 3rd-year Artificial Intelligence and Machine Learning mini project. By combining NLP preprocessing techniques, unsupervised statistical algorithms (YAKE and RAKE), vector-space methods (TF-IDF), Flask-based web development, and interactive visual analytics with Chart.js, the project provides a functional tool for technical document analysis.
