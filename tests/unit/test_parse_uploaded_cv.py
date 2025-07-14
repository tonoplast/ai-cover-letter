#!/usr/bin/env python3
import sys
import os
from app.services.document_parser import DocumentParser

if __name__ == "__main__":
    # Path to the problematic file
    file_path = os.path.join("uploads", "20250707_125458_398552_0_2025-05-01_CV_Data-Science.pdf")
    parser = DocumentParser()
    print(f"Parsing file: {file_path}\n")
    result = parser.parse_document(file_path, "cv")
    print("--- Extracted Content (first 1000 chars) ---")
    print(result["content"][:1000])
    print("\n--- Parsed Data ---")
    for k, v in result["parsed_data"].items():
        print(f"{k}: {v if isinstance(v, (str, int, float)) else str(v)[:500]}")
    print("\n--- Full Parsed Data ---")
    print(result["parsed_data"]) 