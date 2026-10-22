"""
YAKE (Yet Another Keyword Extractor) Wrapper Module.

Unsupervised statistical keyword extraction based on text features
such as word casing, position, word frequency, relatedness to context,
and dispersion across sentences.
In YAKE, a LOWER raw score indicates a MORE SIGNIFICANT keyword/phrase.
"""

import re
import time
from typing import List, Dict, Any
import yake
from .preprocessing import TextPreprocessor

class YakeExtractor:
    """
    Extracts keywords and keyphrases using the statistical YAKE algorithm.
    """

    def __init__(self, doc_type: str = "academic"):
        self.doc_type = doc_type
        self.preprocessor = TextPreprocessor(doc_type=doc_type)

    def extract(
        self,
        text: str,
        top_n: int = 10,
        candidate_type: str = "both"
    ) -> List[Dict[str, Any]]:
        """
        Extracts ranked keywords/keyphrases from text.
        
        Args:
            text: Input document string.
            top_n: Desired number of keywords to return.
            candidate_type: 'single' (unigrams), 'multi' (2+ words), or 'both'.
            
        Returns:
            List of dictionaries containing:
                - text: keyword/keyphrase string
                - raw_score: original YAKE score (lower is more significant)
                - normalized_score: 0-1 relevance scale (higher is more significant)
                - frequency: count of occurrences in the text
                - word_count: number of words in the phrase
                - type: 'keyword' or 'keyphrase'
        """
        if not text or not text.strip():
            return []

        # Determine n-gram length constraint based on candidate_type
        if candidate_type == "single":
            max_ngram_size = 1
        else:
            max_ngram_size = 3

        # Configure YAKE extractor
        # dedupLim: deduplication threshold (0.9 avoids very close duplicates)
        # windowsSize: co-occurrence window size
        kw_extractor = yake.KeywordExtractor(
            lan="en",
            n=max_ngram_size,
            dedupLim=0.85,
            dedupFunc="seqm",
            windowsSize=1,
            top=max(top_n * 3, 30),  # Extract surplus to allow post-filtering
            features=None
        )

        raw_results = kw_extractor.extract_keywords(text)
        if not raw_results:
            return []

        clean_lower_text = " " + text.lower() + " "
        processed_results = []
        seen_texts = set()

        for phrase, raw_score in raw_results:
            phrase_str = phrase.strip()
            phrase_lower = phrase_str.lower()

            # Linguistic candidate check (filters pure numbers, invalid symbols)
            if not self.preprocessor.is_valid_candidate(phrase_str):
                continue

            words = phrase_str.split()
            word_count = len(words)

            # Filter by candidate_type
            if candidate_type == "single" and word_count > 1:
                continue
            if candidate_type == "multi" and word_count == 1:
                continue

            if phrase_lower in seen_texts:
                continue
            seen_texts.add(phrase_lower)

            # Calculate actual occurrence frequency in original text
            # Use regex word boundary matching for accurate frequency counting
            escaped_phrase = re.escape(phrase_lower)
            try:
                frequency = len(re.findall(r"\b" + escaped_phrase + r"\b", clean_lower_text))
            except Exception:
                frequency = clean_lower_text.count(phrase_lower)

            if frequency == 0:
                frequency = 1  # Fallback if boundary matching differed slightly

            # Normalized Score:
            # YAKE raw score is >= 0, where 0 is the most important candidate.
            # We map this to a normalized relevance score [0, 1] where 1.0 is most relevant:
            # relevance = 1 / (1 + raw_score)
            normalized_score = round(1.0 / (1.0 + float(raw_score)), 4)

            processed_results.append({
                "text": phrase_str,
                "raw_score": round(float(raw_score), 6),
                "score": normalized_score,  # UI friendly relevance score
                "frequency": frequency,
                "word_count": word_count,
                "type": "keyword" if word_count == 1 else "keyphrase"
            })

            if len(processed_results) >= top_n:
                break

        return processed_results
