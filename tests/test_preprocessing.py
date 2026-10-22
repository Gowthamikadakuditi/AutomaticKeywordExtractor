"""
Unit tests for NLP preprocessing pipeline.
"""

import unittest
from nlp.preprocessing import TextPreprocessor

class TestTextPreprocessor(unittest.TestCase):

    def setUp(self):
        self.preprocessor = TextPreprocessor(doc_type="academic")
        self.sample_text = (
            "Deep learning and natural language processing have revolutionized automatic text summarization. "
            "State-of-the-art transformer architectures, such as BERT and GPT models, enable rich contextual representations. "
            "In this research paper, we evaluate modern NLP techniques on academic corpora."
        )

    def test_whitespace_normalization(self):
        messy_text = "  Deep   learning \t and \n\n\n natural \r\n language \u00a0 processing.  "
        clean = self.preprocessor.normalize_whitespace(messy_text)
        self.assertEqual(clean, "Deep learning and\n\nnatural language processing.")

    def test_sentence_tokenization(self):
        sentences = self.preprocessor.tokenize_sentences(self.sample_text)
        self.assertEqual(len(sentences), 3)
        self.assertTrue(sentences[0].startswith("Deep learning"))

    def test_word_tokenization_and_hyphens(self):
        text = "State-of-the-art deep-learning models."
        words = self.preprocessor.tokenize_words(text)
        self.assertIn("State-of-the-art", words)

    def test_compute_statistics(self):
        stats = self.preprocessor.compute_statistics(self.sample_text)
        self.assertGreater(stats["total_words"], 20)
        self.assertGreater(stats["unique_words"], 15)
        self.assertEqual(stats["total_sentences"], 3)
        self.assertGreater(stats["total_characters"], 50)

    def test_candidate_validation(self):
        # Stopword bound phrases should be rejected
        self.assertFalse(self.preprocessor.is_valid_candidate("the paper"))
        self.assertFalse(self.preprocessor.is_valid_candidate("learning and"))
        self.assertFalse(self.preprocessor.is_valid_candidate("12345"))
        self.assertFalse(self.preprocessor.is_valid_candidate(""))
        
        # Valid keyphrases should pass
        self.assertTrue(self.preprocessor.is_valid_candidate("natural language processing"))
        self.assertTrue(self.preprocessor.is_valid_candidate("deep learning"))
        self.assertTrue(self.preprocessor.is_valid_candidate("BERT"))

    def test_candidate_phrase_generation(self):
        candidates = self.preprocessor.extract_candidate_phrases(self.sample_text)
        candidates_lower = [c.lower() for c in candidates]
        self.assertIn("natural language processing", candidates_lower)
        self.assertIn("deep learning", candidates_lower)

if __name__ == "__main__":
    unittest.main()
