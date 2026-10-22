"""
Exporters Module.

Generates CSV, JSON, and clean human-readable TXT reports
from keyword extraction results.
"""

import csv
import io
import json
from datetime import datetime
from typing import Dict, Any

def export_to_csv(result_data: Dict[str, Any]) -> str:
    """
    Exports keywords and statistics to CSV format.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Metadata header
    writer.writerow(["# Automatic Keyword and Keyphrase Extractor - Report"])
    writer.writerow(["# Algorithm", result_data.get("algorithm", "N/A")])
    writer.writerow(["# Document Type", result_data.get("document_type", "N/A")])
    writer.writerow(["# Generated At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    
    stats = result_data.get("statistics", {})
    writer.writerow(["# Total Words", stats.get("total_words", 0)])
    writer.writerow(["# Unique Words", stats.get("unique_words", 0)])
    writer.writerow(["# Processing Time (ms)", stats.get("processing_time_ms", 0)])
    writer.writerow([])  # Blank line

    # Column headers
    writer.writerow(["Rank", "Keyword / Keyphrase", "Relevance Score", "Raw Score", "Frequency", "Word Count", "Type"])

    keywords = result_data.get("keywords", [])
    for kw in keywords:
        writer.writerow([
            kw.get("rank", ""),
            kw.get("text", ""),
            kw.get("score", ""),
            kw.get("raw_score", ""),
            kw.get("frequency", ""),
            kw.get("word_count", ""),
            kw.get("type", "")
        ])

    return output.getvalue()

def export_to_json(result_data: Dict[str, Any]) -> str:
    """
    Exports result data to clean, formatted JSON string.
    """
    payload = {
        "project": "Automatic Keyword and Keyphrase Extractor",
        "generated_at": datetime.now().isoformat(),
        "algorithm": result_data.get("algorithm"),
        "algorithm_info": result_data.get("algorithm_info"),
        "document_type": result_data.get("document_type"),
        "statistics": result_data.get("statistics"),
        "keywords": result_data.get("keywords")
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)

def export_to_txt(result_data: Dict[str, Any]) -> str:
    """
    Generates a clean, professional TXT summary report suitable for academic project reports.
    """
    stats = result_data.get("statistics", {})
    keywords = result_data.get("keywords", [])
    algo = result_data.get("algorithm", "Unknown")
    doc_type = result_data.get("document_type", "General")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "=" * 70,
        "   AUTOMATIC KEYWORD AND KEYPHRASE EXTRACTOR - ANALYSIS REPORT",
        "=" * 70,
        f"Generated On       : {timestamp}",
        f"Algorithm Used     : {algo}",
        f"Document Category  : {doc_type}",
        f"Processing Time    : {stats.get('processing_time_ms', 0)} ms",
        "-" * 70,
        "DOCUMENT CORPUS STATISTICS:",
        f"  - Total Words             : {stats.get('total_words', 0)}",
        f"  - Unique Words            : {stats.get('unique_words', 0)}",
        f"  - Sentences               : {stats.get('total_sentences', 0)}",
        f"  - Total Characters        : {stats.get('total_characters', 0)}",
        f"  - Est. Reading Time       : {stats.get('estimated_reading_time_sec', 0)} seconds",
        f"  - Total Keywords Extracted: {len(keywords)}",
        "-" * 70,
        f"{'RANK':<6} {'KEYWORD / KEYPHRASE':<30} {'SCORE':<10} {'FREQ':<8} {'TYPE':<12}",
        "-" * 70,
    ]

    for kw in keywords:
        rank_str = f"#{kw.get('rank', '-')}"
        phrase_str = str(kw.get('text', ''))[:28]
        score_str = f"{kw.get('score', 0):.4f}"
        freq_str = str(kw.get('frequency', 0))
        type_str = str(kw.get('type', 'keyword')).capitalize()
        lines.append(f"{rank_str:<6} {phrase_str:<30} {score_str:<10} {freq_str:<8} {type_str:<12}")

    lines.extend([
        "=" * 70,
        "Note: In YAKE, lower raw scores indicate higher relevance; displayed scores",
"are normalized to a [0, 1] range. In TF-IDF, higher scores indicate higher relevance.",
        "=" * 70,
    ])

    return "\n".join(lines)
