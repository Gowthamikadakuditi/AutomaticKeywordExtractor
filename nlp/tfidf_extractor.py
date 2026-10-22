"""
TF-IDF (Term Frequency - Inverse Document Frequency) Extractor Module.

Uses scikit-learn's TfidfVectorizer. In single-document mode, the document's
sentences are utilized as a pseudo-corpus to compute Inverse Sentence Frequency (ISF),
identifying terms that are topically distinctive rather than ubiquitous document filler.
Includes candid explanations of single-document vs corpus-trained TF-IDF.
"""

import re
from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from .preprocessing import TextPreprocessor

class TfidfExtractor:
    """
    Ranks candidate keywords and keyphrases using TF-IDF statistics.
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
        Extracts keywords/keyphrases using TF-IDF weighting across sentences.
        
        Args:
            text: Input document string.
            top_n: Number of keywords to return.
            candidate_type: 'single', 'multi', or 'both'.
            
        Returns:
            Ranked list of extracted candidate dictionaries.
        """
        if not text or not text.strip():
            return []

        # 1. Break text into sentences to create document pseudo-corpus
        sentences = self.preprocessor.tokenize_sentences(text)
        if not sentences:
            sentences = [text]

        # 2. Determine n-gram range based on candidate_type
        if candidate_type == "single":
            ngram_range = (1, 1)
        elif candidate_type == "multi":
            ngram_range = (2, 3)
        else:
            ngram_range = (1, 3)

        # 3. Stopwords list
        stop_words = list(self.preprocessor.all_stopwords)

        # 4. Configure TfidfVectorizer
        # token_pattern matches words and hyphenated words
        vectorizer = TfidfVectorizer(
            ngram_range=ngram_range,
            stop_words=stop_words,
            token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9_-]+\b",
            lowercase=True,
            sublinear_tf=True,
            smooth_idf=True
        )

        try:
            tfidf_matrix = vectorizer.fit_transform(sentences)
            feature_names = vectorizer.get_feature_names_out()
        except ValueError:
            # Occurs if vocabulary is completely empty after stopword removal
            return []

        # 5. Aggregate TF-IDF scores across sentences
        # Using max score across sentences highlights topical bursts,
        # combined with sum to capture overall document importance.
        dense_matrix = tfidf_matrix.toarray()
        # Mean non-zero score or column sum
        mean_scores = np.mean(dense_matrix, axis=0)
        max_scores = np.max(dense_matrix, axis=0)
        # Combined score balance
        combined_scores = 0.6 * max_scores + 0.4 * mean_scores

        clean_lower_text = " " + text.lower() + " "
        candidates = []

        for idx, term in enumerate(feature_names):
            term_str = term.strip()
            
            # Linguistic candidate validation
            if not self.preprocessor.is_valid_candidate(term_str):
                continue

            words = term_str.split()
            word_count = len(words)

            if candidate_type == "single" and word_count > 1:
                continue
            if candidate_type == "multi" and word_count == 1:
                continue

            raw_tfidf = float(combined_scores[idx])
            if raw_tfidf <= 0.0:
                continue

            # Frequency count in original text
            escaped_term = re.escape(term_str.lower())
            try:
                frequency = len(re.findall(r"\b" + escaped_term + r"\b", clean_lower_text))
            except Exception:
                frequency = clean_lower_text.count(term_str.lower())

            if frequency == 0:
                frequency = 1

            candidates.append({
                "text": term_str,
                "raw_score": round(raw_tfidf, 6),
                "score": round(raw_tfidf, 4),  # Directly usable as 0-1 relevance
                "frequency": frequency,
                "word_count": word_count,
                "type": "keyword" if word_count == 1 else "keyphrase"
            })

        # Sort candidates descending by score, then by frequency
        candidates.sort(key=lambda x: (x["score"], x["frequency"]), reverse=True)

        # Normalize score to max 1.0 if not empty
        if candidates and candidates[0]["score"] > 0:
            max_s = candidates[0]["score"]
            for cand in candidates:
                cand["score"] = round(cand["score"] / max_s, 4)

        return candidates[:top_n]
