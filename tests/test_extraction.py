"""
Unit tests for Keyword and Keyphrase Extraction Algorithms.
"""

import unittest
from nlp.yake_extractor import YakeExtractor
from nlp.tfidf_extractor import TfidfExtractor
from nlp.rake_extractor import RakeExtractor
from nlp import extract_keywords_pipeline

class TestExtractionAlgorithms(unittest.TestCase):

    def setUp(self):
        self.sample_doc = (
            "Natural language processing and machine learning have advanced rapidly in recent years. "
            "Keyword extraction is an essential NLP task that identifies the most important phrases in documents. "
            "Keyphrase extraction helps in document summarization, information retrieval, and search engine optimization. "
            "Statistical methods like YAKE and vector space models like TF-IDF analyze word frequency and sentence dispersion. "
            "These machine learning techniques produce high quality keyphrase candidates without requiring labeled training datasets."
        )

    def test_yake_extraction(self):
        extractor = YakeExtractor(doc_type="academic")
        results = extractor.extract(self.sample_doc, top_n=5, candidate_type="both")
        
        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), 5)
        
        first = results[0]
        self.assertIn("text", first)
        self.assertIn("score", first)
        self.assertIn("raw_score", first)
        self.assertIn("frequency", first)
        self.assertIn("type", first)
        self.assertGreaterEqual(first["score"], 0.0)
        self.assertLessEqual(first["score"], 1.0)
        self.assertGreaterEqual(first["frequency"], 1)

    def test_tfidf_extraction(self):
        extractor = TfidfExtractor(doc_type="academic")
        results = extractor.extract(self.sample_doc, top_n=5, candidate_type="both")

        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), 5)

        first = results[0]
        self.assertIn("text", first)
        self.assertIn("score", first)
        self.assertIn("frequency", first)
        self.assertIn("type", first)
        self.assertGreater(first["score"], 0.0)

        
    def test_rake_extraction(self):
        extractor = RakeExtractor(doc_type="academic")
        results = extractor.extract(
            self.sample_doc,
            top_n=5,
            candidate_type="both"
        )

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), 5)

        first = results[0]
        self.assertIn("text", first)
        self.assertIn("score", first)
        self.assertIn("frequency", first)
        self.assertIn("type", first)


    def test_candidate_type_filter(self):
        # Single words only
        extractor = YakeExtractor(doc_type="academic")
        single_results = extractor.extract(self.sample_doc, top_n=10, candidate_type="single")
        for item in single_results:
            self.assertEqual(item["word_count"], 1)
            self.assertEqual(item["type"], "keyword")

        # Multi-word keyphrases only
        multi_results = extractor.extract(self.sample_doc, top_n=10, candidate_type="multi")
        for item in multi_results:
            self.assertGreater(item["word_count"], 1)
            self.assertEqual(item["type"], "keyphrase")

    def test_pipeline_integration(self):
        pipeline_res = extract_keywords_pipeline(
            text=self.sample_doc,
            method="yake",
            top_n=5,
            doc_type="academic",
            candidate_type="both"
        )
        self.assertTrue(pipeline_res["success"])
        self.assertEqual(pipeline_res["algorithm"], "YAKE")
        self.assertIn("statistics", pipeline_res)
        self.assertIn("keywords", pipeline_res)
        self.assertIn("processing_time_ms", pipeline_res["statistics"])
        self.assertGreater(len(pipeline_res["keywords"]), 0)


if __name__ == "__main__":
    unittest.main()
