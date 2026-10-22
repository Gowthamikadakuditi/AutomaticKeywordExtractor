
"""
NLP Keyword and Keyphrase Extraction Pipeline.

Exposes a unified interface for YAKE, TF-IDF, and RAKE extractors.
"""

import time
from typing import Dict, Any

from .preprocessing import TextPreprocessor
from .yake_extractor import YakeExtractor
from .tfidf_extractor import TfidfExtractor
from .rake_extractor import RakeExtractor


ALGORITHM_DESCRIPTIONS = {
    "yake": {
        "name": "YAKE (Yet Another Keyword Extractor)",
        "type": "Unsupervised Statistical",
        "description": (
            "Analyzes term frequency, casing, word position, and context. "
            "Lower raw YAKE scores indicate more significant keywords."
        ),
        "score_label": "YAKE Relevance Score"
    },
    "tfidf": {
        "name": "TF-IDF (Term Frequency - Inverse Document Frequency)",
        "type": "Statistical / Vector Space",
        "description": (
            "Uses term frequency and inverse sentence frequency to identify "
            "important terms in a document."
        ),
        "score_label": "TF-IDF Importance Score"
    },
    "rake": {
        "name": "RAKE (Rapid Automatic Keyword Extraction)",
        "type": "Unsupervised Statistical",
        "description": (
            "Extracts keywords and keyphrases using word frequency "
            "and word co-occurrence statistics."
        ),
        "score_label": "RAKE Importance Score"
    }
}


def extract_keywords_pipeline(
    text: str,
    method: str = "yake",
    top_n: int = 10,
    doc_type: str = "academic",
    candidate_type: str = "both"
) -> Dict[str, Any]:

    start_time = time.perf_counter()

    method_key = method.lower().strip()

    if method_key not in ["yake", "tfidf", "rake"]:
        method_key = "yake"

    doc_type_clean = doc_type.lower().strip()

    if doc_type_clean not in ["academic", "news", "technical"]:
        doc_type_clean = "academic"

    preprocessor = TextPreprocessor(doc_type=doc_type_clean)
    stats = preprocessor.compute_statistics(text)

    if method_key == "yake":
        extractor = YakeExtractor(doc_type=doc_type_clean)

    elif method_key == "tfidf":
        extractor = TfidfExtractor(doc_type=doc_type_clean)

    else:
        extractor = RakeExtractor(doc_type=doc_type_clean)

    keywords = extractor.extract(
        text,
        top_n=top_n,
        candidate_type=candidate_type
    )

    for rank, item in enumerate(keywords, start=1):
        item["rank"] = rank

    elapsed_ms = round(
        (time.perf_counter() - start_time) * 1000, 2
    )
    stats["processing_time_ms"] = elapsed_ms

    return {
        "success": True,
        "algorithm": (
            method_key.upper()
            if method_key != "tfidf"
            else "TF-IDF"
        ),
        "algorithm_info": ALGORITHM_DESCRIPTIONS[method_key],
        "document_type": doc_type_clean.capitalize(),
        "candidate_filter": candidate_type,
        "statistics": stats,
        "keywords": keywords,
        "total_keywords_extracted": len(keywords)
    }
