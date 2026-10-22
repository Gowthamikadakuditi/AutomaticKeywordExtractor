"""
Flask Application for Automatic Keyword and Keyphrase Extractor.

Serves the web dashboard, RESTful extraction endpoints, document upload handling,
and multi-format export utilities.
"""

import io
import os
import sys
from typing import Dict, Any
from flask import Flask, render_template, request, jsonify, Response, send_file
from werkzeug.exceptions import RequestEntityTooLarge

from nlp import extract_keywords_pipeline
from utils.document_reader import extract_text_from_stream, DocumentReaderError
from utils.exporters import export_to_csv, export_to_json, export_to_txt

# Initialize Flask application
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024  # 15 MB payload limit
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_env.auto_reload = True

# Minimum text criteria for meaningful NLP analysis
MIN_CHAR_COUNT = 30
MIN_WORD_COUNT = 8
MAX_CHAR_COUNT = 500000

@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(e):
    return jsonify({
        "success": False,
        "error": "The uploaded payload or file is too large (Maximum allowed size is 10 MB)."
    }), 413

@app.errorhandler(404)
def handle_not_found(e):
    return jsonify({"success": False, "error": "Endpoint not found."}), 404

@app.errorhandler(500)
def handle_internal_error(e):
    return jsonify({
        "success": False,
        "error": "An internal server error occurred while processing the document."
    }), 500

@app.route("/")
def index():
    """Renders the main dashboard."""
    return render_template("index.html")

@app.route("/about")
def about():
    """Renders the academic documentation and methodology guide."""
    return render_template("about.html")

@app.route("/api/health", methods=["GET"])
def health():
    """ 
    Health check endpoint returning system status and module capabilities.
    """
    

    return jsonify({
        "status": "healthy",
        "service": "Automatic Keyword and Keyphrase Extractor",
        "python_version": sys.version.split()[0],
               "algorithms": {
            "yake": {
                "available": True,
                "type": "Statistical"
            },
            "tfidf": {
                "available": True,
                "type": "Vector Space / Sentence-level"
            },
            "rake": {
                "available": True,
                "type": "Statistical"
            },
        }
    }), 200

@app.route("/api/extract", methods=["POST"])
def extract():
    """
    Main extraction endpoint.
    Accepts text or uploaded files (PDF, DOCX, TXT) via JSON or multipart/form-data.
    """
    try:
        raw_text = ""
        filename = None
        method = "yake"
        top_n = 10
        doc_type = "academic"
        candidate_type = "both"

        # Check if request is multipart (file upload or form)
        if request.content_type and "multipart/form-data" in request.content_type:
            # Check for uploaded file
            if "file" in request.files and request.files["file"].filename:
                uploaded_file = request.files["file"]
                file_bytes = uploaded_file.read()
                filename = uploaded_file.filename

                if not file_bytes:
                    return jsonify({
                        "success": False,
                        "error": "The uploaded file is empty. Please select a document containing text."
                    }), 400

                try:
                    raw_text, filename = extract_text_from_stream(filename, file_bytes)
                except DocumentReaderError as dre:
                    return jsonify({"success": False, "error": str(dre)}), 400

            else:
                raw_text = request.form.get("text", "")

            method = request.form.get("method", "yake")
            try:
                top_n = int(request.form.get("top_n", 10))
            except ValueError:
                top_n = 10
            doc_type = request.form.get("doc_type", "academic")
            candidate_type = request.form.get("candidate_type", "both")

        elif request.is_json:
            data = request.get_json() or {}
            raw_text = data.get("text", "")
            method = data.get("method", "yake")
            try:
                top_n = int(data.get("top_n", 10))
            except (ValueError, TypeError):
                top_n = 10
            doc_type = data.get("doc_type", "academic")
            candidate_type = data.get("candidate_type", "both")

        else:
            return jsonify({
                "success": False,
                "error": "Invalid request format. Please submit JSON or multipart form data."
            }), 400

        # Validate input text
        if not raw_text or not raw_text.strip():
            return jsonify({
                "success": False,
                "error": "No text provided. Please paste text or upload a document."
            }), 400

        text_str = raw_text.strip()

        if len(text_str) > MAX_CHAR_COUNT:
            return jsonify({
                "success": False,
                "error": f"Text exceeds maximum character limit of {MAX_CHAR_COUNT:,} characters."
            }), 400

        words = text_str.split()
        if len(words) < MIN_WORD_COUNT or len(text_str) < MIN_CHAR_COUNT:
            return jsonify({
                "success": False,
                "error": (
                    f"Input text is too short ({len(words)} words, {len(text_str)} chars). "
                    f"Please provide at least {MIN_WORD_COUNT} words for meaningful keyword extraction."
                )
            }), 400

        # Bounds check on top_n
        top_n = max(3, min(top_n, 50))
        print("Selected method received by backend:", method)
        result = extract_keywords_pipeline(
            text=text_str,
            method=method,
            top_n=top_n,
            doc_type=doc_type,
            candidate_type=candidate_type
        )

        if filename:
            result["source_filename"] = filename

        status_code = 200 if result.get("success", False) else 400
        return jsonify(result), status_code

    except Exception as e:
        # Prevent leaking raw tracebacks while returning readable message
        return jsonify({
            "success": False,
            "error": f"An error occurred during keyword extraction: {str(e)}"
        }), 500

@app.route("/api/export/<export_format>", methods=["POST"])
def export_results(export_format: str):
    """
    Exports keyword analysis data to CSV, JSON, or TXT.
    """
    export_format = export_format.lower().strip()
    if export_format not in ["csv", "json", "txt"]:
        return jsonify({"success": False, "error": "Supported export formats are 'csv', 'json', and 'txt'."}), 400

    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({"success": False, "error": "Invalid or missing analysis data payload."}), 400

    timestamp = "report"
    if export_format == "csv":
        content = export_to_csv(data)
        return Response(
            content,
            mimetype="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=keywords_{timestamp}.csv"}
        )
    elif export_format == "json":
        content = export_to_json(data)
        return Response(
            content,
            mimetype="application/json; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=keywords_{timestamp}.json"}
        )
    elif export_format == "txt":
        content = export_to_txt(data)
        return Response(
            content,
            mimetype="text/plain; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=keywords_{timestamp}.txt"}
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Automatic Keyword and Keyphrase Extractor on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)