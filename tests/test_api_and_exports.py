"""
Integration tests for Flask Web Endpoints and Exporters.
"""

import json
import unittest
from app import app

class TestApiAndExports(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.valid_text = (
            "Machine learning algorithms and natural language processing pipelines "
            "provide powerful automated solutions for academic document indexing. "
            "In this study, we extract keywords and keyphrases to evaluate information retrieval."
        )

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("algorithms", data)

    def test_extract_endpoint_valid_json(self):
        payload = {
            "text": self.valid_text,
            "method": "yake",
            "top_n": 5,
            "doc_type": "academic",
            "candidate_type": "both"
        }
        response = self.client.post("/api/extract", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["algorithm"], "YAKE")
        self.assertGreater(len(data["keywords"]), 0)

    def test_extract_endpoint_empty_text(self):
        payload = {"text": ""}
        response = self.client.post("/api/extract", json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data["success"])

    def test_extract_endpoint_short_text(self):
        payload = {"text": "Too short text."}
        response = self.client.post("/api/extract", json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertIn("too short", data["error"].lower())

    def test_export_csv_endpoint(self):
        extract_resp = self.client.post("/api/extract", json={"text": self.valid_text, "top_n": 3})
        analysis_data = extract_resp.get_json()

        export_resp = self.client.post("/api/export/csv", json=analysis_data)
        self.assertEqual(export_resp.status_code, 200)
        self.assertIn("text/csv", export_resp.content_type)
        content = export_resp.data.decode("utf-8")
        self.assertIn("Rank,Keyword / Keyphrase", content)

    def test_export_json_endpoint(self):
        extract_resp = self.client.post("/api/extract", json={"text": self.valid_text, "top_n": 3})
        analysis_data = extract_resp.get_json()

        export_resp = self.client.post("/api/export/json", json=analysis_data)
        self.assertEqual(export_resp.status_code, 200)
        self.assertIn("application/json", export_resp.content_type)
        exported_obj = json.loads(export_resp.data.decode("utf-8"))
        self.assertIn("keywords", exported_obj)

    def test_export_txt_endpoint(self):
        extract_resp = self.client.post("/api/extract", json={"text": self.valid_text, "top_n": 3})
        analysis_data = extract_resp.get_json()

        export_resp = self.client.post("/api/export/txt", json=analysis_data)
        self.assertEqual(export_resp.status_code, 200)
        self.assertIn("text/plain", export_resp.content_type)
        content = export_resp.data.decode("utf-8")
        self.assertIn("AUTOMATIC KEYWORD AND KEYPHRASE EXTRACTOR", content)

    def test_home_page_rendering(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Automatic Keyword and Keyphrase Extractor", response.data)

    def test_about_page_rendering(self):
        response = self.client.get("/about")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Project Documentation & Viva Guide", response.data)

if __name__ == "__main__":
    unittest.main()
