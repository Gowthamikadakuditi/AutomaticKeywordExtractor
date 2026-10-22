
"""
RAKE (Rapid Automatic Keyword Extraction) Wrapper Module.

Extracts keywords and keyphrases using word frequency
and word co-occurrence statistics.
"""

import re
import string
from typing import List, Dict, Any

from rake_nltk import Rake, Metric
from .preprocessing import TextPreprocessor

class  RakeExtractor:
    """Extracts keywords and keyphrases using the RAKE algorithm."""

    def __init__(self, doc_type: str = "academic"):
        self.doc_type = doc_type
        self.preprocessor = TextPreprocessor(doc_type=doc_type)

        # Built-in stopwords avoid requiring NLTK corpus downloads.
        self.stopwords = set("""
            a an the and or but if while with to from in on at by for
            of is are was were be been being am do does did have has had
            this that these those it its as into about over after before
            between through during above below up down out off not no nor
            so too very can could will would should may might must
            we they them their he she his her you your i me my our ours
            what which who whom when where why how all any both each few
            more most other some such only own same than then once
        """.split())

    def extract(
        self,
        text: str,
        top_n: int = 10,
        candidate_type: str = "both"
    ) -> List[Dict[str, Any]]:

        if not text or not text.strip():
            return []

        # Split text into sentences and preserve punctuation boundaries.
        sentence_tokenizer = lambda s: re.split(
            r"(?<=[.!?])\s+|\n+", s.strip()
        )

        word_tokenizer = lambda s: re.findall(
            r"[A-Za-z0-9]+(?:'[A-Za-z]+)?|[^\w\s]", s
        )

        extractor = Rake(
            stopwords=self.stopwords,
            punctuations=set(string.punctuation),
            ranking_metric=Metric.DEGREE_TO_FREQUENCY_RATIO,
            sentence_tokenizer=sentence_tokenizer,
            word_tokenizer=word_tokenizer
        )

        extractor.extract_keywords_from_text(text)
        raw_results = extractor.get_ranked_phrases_with_scores()

        clean_text = text.lower()
        results = []
        seen = set()

        # RAKE returns higher scores for more highly ranked phrases.
        max_score = max(
            (float(score) for score, _ in raw_results),
            default=0.0
        )

        for raw_score, phrase in raw_results:
            phrase = phrase.strip()
            phrase_lower = phrase.lower()
            words = phrase.split()
            word_count = len(words)

            if not phrase or phrase_lower in seen:
                continue

            if candidate_type == "single" and word_count != 1:
                continue
            if candidate_type == "multi" and word_count < 2:
                continue
            if candidate_type not in ("single", "multi", "both"):
                candidate_type = "both"

            if not self.preprocessor.is_valid_candidate(phrase):
                continue

            seen.add(phrase_lower)

            frequency = len(re.findall(
                r"\b" + re.escape(phrase_lower) + r"\b",
                clean_text
            ))
            frequency = max(frequency, 1)

            normalized_score = (
                round(float(raw_score) / max_score, 4)
                if max_score > 0 else 0.0
            )

            results.append({
                "text": phrase,
                "raw_score": round(float(raw_score), 6),
                "score": normalized_score,
                "frequency": frequency,
                "word_count": word_count,
                "type": "keyword" if word_count == 1 else "keyphrase"
            })

            if len(results) >= top_n:
                break

        return results
