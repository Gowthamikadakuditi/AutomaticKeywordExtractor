"""
NLP Preprocessing Pipeline for Keyword and Keyphrase Extraction.

Provides text cleaning, normalization, tokenization, lemmatization,
stopword removal, technical term preservation, and candidate phrase generation.
Designed for B.Tech AIML academic mini-project standards.
"""

import re
import string
from typing import List, Dict, Set, Tuple, Optional
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize

# Domain-specific stopword dictionaries to refine extraction for specialized text
DOMAIN_STOPWORDS = {
    "academic": {
        "et", "al", "abstract", "introduction", "conclusion", "results", "discussion",
        "method", "methods", "figure", "table", "paper", "study", "research",
        "author", "authors", "propose", "proposed", "presents", "presented", "shown",
        "shows", "using", "used", "based", "approach", "experimental", "experiments",
        "analysis", "section", "ieee", "acm", "proceedings", "conference", "journal",
        "fig", "ref", "references", "respectively", "demonstrates", "furthermore"
    },
    "news": {
        "said", "reporting", "source", "sources", "according", "yesterday", "today",
        "tomorrow", "spokesman", "spokesperson", "statement", "press", "media", "told",
        "reports", "reported", "officials", "official", "monday", "tuesday", "wednesday",
        "thursday", "friday", "saturday", "sunday", "reuters", "associated", "ap",
        "evening", "morning", "agency", "agencies", "declined", "comment"
    },
    "technical": {
        "file", "code", "run", "running", "example", "examples", "user", "guide",
        "version", "support", "supported", "install", "installation", "click", "output",
        "input", "step", "steps", "documentation", "default", "command", "line",
        "system", "systems", "following", "given", "see", "below", "above"
    }
}

# Recognized acronyms and technical notations to preserve case and formatting
KNOWN_ACRONYMS = {
    "NLP", "BERT", "AI", "ML", "DL", "CNN", "RNN", "LSTM", "LLM", "API",
    "JSON", "XML", "HTTP", "HTTPS", "HTML", "CSS", "SQL", "GPU", "CPU",
    "TPU", "IoT", "RFID", "DNA", "RNA", "SVM", "KNN", "GAN", "VAE", "PCA",
    "TF-IDF", "YAKE", "REST", "SDK", "OS", "RAM", "ROM", "SSD", "CUDA"
}

class TextPreprocessor:
    """
    Handles end-to-end NLP text preprocessing while safeguarding technical terminology,
    hyphenated compounds, and domain-specific stopwords.
    """

    def __init__(self, doc_type: str = "academic"):
        self.doc_type = doc_type.lower()
        self.lemmatizer = WordNetLemmatizer()
        
        # Load standard English stopwords safely
        try:
            self.base_stopwords: Set[str] = set(stopwords.words("english"))
        except Exception:
            # Fallback stopword set if nltk download has not yet occurred
            self.base_stopwords = {
                "a", "an", "the", "and", "or", "but", "if", "because", "as", "what",
                "which", "this", "that", "these", "those", "then", "just", "so", "than",
                "such", "both", "through", "about", "for", "is", "of", "while", "during",
                "to", "from", "in", "out", "on", "off", "again", "further", "then", "once",
                "here", "there", "when", "where", "why", "how", "all", "any", "both", "each",
                "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only",
                "own", "same", "so", "than", "too", "very", "can", "will", "just", "don",
                "should", "now", "it", "its", "by", "with", "at", "be", "was", "were"
            }
            
        # Combine standard stopwords with domain-specific additions
        domain_stops = DOMAIN_STOPWORDS.get(self.doc_type, set())
        self.all_stopwords = self.base_stopwords.union(domain_stops)

    def normalize_whitespace(self, text: str) -> str:
        """
        Cleans tabs, non-breaking spaces, carriage returns, and multiple spaces.
        Preserves paragraph breaks while turning single line breaks into spaces.
        """
        if not text:
            return ""
        text = text.replace("\u00a0", " ").replace("\r\n", "\n").replace("\r", "\n")
        paragraphs = re.split(r"\n\s*\n+", text)
        cleaned_paragraphs = []
        for p in paragraphs:
            clean_p = re.sub(r"\s+", " ", p).strip()
            if clean_p:
                cleaned_paragraphs.append(clean_p)
        return "\n\n".join(cleaned_paragraphs)

    def tokenize_sentences(self, text: str) -> List[str]:
        """
        Tokenizes text into coherent sentences using NLTK sent_tokenize.
        """
        normalized = self.normalize_whitespace(text)
        if not normalized:
            return []
        try:
            return sent_tokenize(normalized)
        except Exception:
            # Fallback regex sentence splitter
            return [s.strip() for s in re.split(r"(?<=[.!?])\s+", normalized) if s.strip()]

    def tokenize_words(self, text: str) -> List[str]:
        """
        Tokenizes words while retaining hyphenated terms (e.g., 'state-of-the-art')
        and technical tokens.
        """
        if not text:
            return []
        try:
            return word_tokenize(text)
        except Exception:
            return re.findall(r"\b[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\b", text)

    def compute_statistics(self, text: str) -> Dict[str, int]:
        """
        Calculates linguistic and document metrics:
        total word count, unique words, sentence count, and character count.
        """
        clean_text = self.normalize_whitespace(text)
        words = re.findall(r"\b[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\b", clean_text)
        sentences = self.tokenize_sentences(clean_text)
        unique_words = set(w.lower() for w in words)

        return {
            "total_characters": len(clean_text),
            "total_words": len(words),
            "unique_words": len(unique_words),
            "total_sentences": len(sentences),
            "estimated_reading_time_sec": round((len(words) / 200) * 60) if words else 0
        }

    def lemmatize_word(self, word: str, pos_tag: Optional[str] = None) -> str:
        """
        Lemmatizes a word with proper WordNet POS mapping (noun, verb, adj, adv).
        Preserves technical acronyms.
        """
        if word.upper() in KNOWN_ACRONYMS:
            return word.upper()
            
        wn_pos = "n"
        if pos_tag:
            tag_prefix = pos_tag[0].upper()
            if tag_prefix == "J":
                wn_pos = "a"
            elif tag_prefix == "V":
                wn_pos = "v"
            elif tag_prefix == "R":
                wn_pos = "r"
            elif tag_prefix == "N":
                wn_pos = "n"

        try:
            return self.lemmatizer.lemmatize(word.lower(), pos=wn_pos)
        except Exception:
            return word.lower()

    def is_valid_candidate(self, phrase: str) -> bool:
        """
        Validates whether a candidate term or phrase is a meaningful keyphrase.
        Filters out pure numbers, stopword-led or stopword-ended phrases, and punctuation.
        """
        phrase = phrase.strip()
        if not phrase or len(phrase) < 2:
            return False

        # Exclude pure numbers or single digits
        if re.match(r"^[\d\s.,\-]+$", phrase):
            return False

        tokens = phrase.lower().split()
        if not tokens:
            return False

        # Cannot begin or end with a stopword
        if tokens[0] in self.all_stopwords or tokens[-1] in self.all_stopwords:
            return False

        # Must contain at least one alphabetic letter
        if not re.search(r"[a-zA-Z]", phrase):
            return False

        # Check for invalid internal punctuation sequences
        if re.search(r"[`~@#$%^&*()_=+\[\]{}\\|;:\",<>/?]", phrase):
            return False

        return True

    def extract_candidate_phrases(self, text: str, min_n: int = 1, max_n: int = 3) -> List[str]:
        """
        Generates linguistically viable candidate keywords and keyphrases:
        - Extracts POS-guided noun phrases (Adjective* Noun+)
        - Generates valid n-grams within the given range
        - Filters out stopword-bound candidates
        """
        sentences = self.tokenize_sentences(text)
        candidates = []
        seen = set()

        for sentence in sentences:
            # Tokenize words
            words = self.tokenize_words(sentence)
            if not words:
                continue

            # Attempt POS tagging with NLTK
            try:
                tagged = nltk.pos_tag(words)
            except Exception:
                tagged = [(w, "NN") for w in words]

            num_words = len(tagged)

            # 1. Linguistic Noun Phrase Chunking: (JJ)* (NN|NNS|NNP|NNPS)+
            current_chunk: List[str] = []
            for word, tag in tagged:
                clean_w = word.strip(string.punctuation)
                if not clean_w:
                    if current_chunk:
                        chunk_str = " ".join(current_chunk)
                        if self.is_valid_candidate(chunk_str) and chunk_str.lower() not in seen:
                            candidates.append(chunk_str)
                            seen.add(chunk_str.lower())
                        current_chunk = []
                    continue

                if tag.startswith("JJ") or tag.startswith("NN"):
                    current_chunk.append(clean_w)
                else:
                    if current_chunk:
                        chunk_str = " ".join(current_chunk)
                        if self.is_valid_candidate(chunk_str) and chunk_str.lower() not in seen:
                            candidates.append(chunk_str)
                            seen.add(chunk_str.lower())
                        current_chunk = []
                        
            if current_chunk:
                chunk_str = " ".join(current_chunk)
                if self.is_valid_candidate(chunk_str) and chunk_str.lower() not in seen:
                    candidates.append(chunk_str)
                    seen.add(chunk_str.lower())

            # 2. Generalized n-grams within [min_n, max_n]
            for n in range(min_n, max_n + 1):
                for i in range(num_words - n + 1):
                    ngram_tokens = [tagged[i + k][0].strip(string.punctuation) for k in range(n)]
                    if any(not tok for tok in ngram_tokens):
                        continue
                    ngram_phrase = " ".join(ngram_tokens)
                    ngram_lower = ngram_phrase.lower()
                    
                    if ngram_lower not in seen and self.is_valid_candidate(ngram_phrase):
                        candidates.append(ngram_phrase)
                        seen.add(ngram_lower)

        return candidates
