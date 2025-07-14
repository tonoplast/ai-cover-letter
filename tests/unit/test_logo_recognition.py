#!/usr/bin/env python3
"""
Test script for document parsing and logo recognition using LLM and YOLOv8 (OpenLogo) or Vision LLM (Google Gemini)
"""
import os
import pytest
from pathlib import Path
from PIL import Image
from app.services.document_parser import DocumentParser
from app.services.enhanced_document_parser import recognize_logos_openlogo, recognize_logos_vision_llm

@pytest.fixture
def pdf_path():
    """Fixture to provide a test PDF path"""
    uploads_dir = Path("uploads")
    if uploads_dir.exists():
        pdfs = [f for f in uploads_dir.iterdir() if f.suffix.lower() == ".pdf"]
        if pdfs:
            return pdfs[0]
    
    # Create a dummy PDF path for testing
    return Path("test_document.pdf")

def test_llm_document_parsing(pdf_path, document_type="cv"):
    """Test LLM document parsing functionality"""
    if not pdf_path.exists():
        pytest.skip(f"PDF file {pdf_path} not found")
    
    parser = DocumentParser()
    result = parser.parse_document_with_llm(str(pdf_path), document_type, extract_images=False)
    
    # Verify the result structure
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "content" in result, "Result should contain 'content' key"
    assert "parsed_data" in result, "Result should contain 'parsed_data' key"
    
    # Verify content is not empty
    content = result.get("content", "")
    assert len(content) > 0, "Parsed content should not be empty"
    
    # Verify parsed data structure
    parsed_data = result.get("parsed_data", {})
    assert isinstance(parsed_data, dict), "Parsed data should be a dictionary"

def test_logo_recognition(folder="test_logos", method="vision_llm", model_path="openlogo_yolov8.pt", vision_model="gemini-1.5-flash"):
    logo_dir = Path(folder)
    print(f"Checking folder: {logo_dir.resolve()}")
    if not logo_dir.exists():
        print(f"❌ Folder not found: {folder}")
        return
    image_files = [f for f in logo_dir.iterdir() if f.suffix.lower() in [".png", ".jpg", ".jpeg", ".bmp", ".gif"]]
    print(f"Found {len(image_files)} image files: {[f.name for f in image_files]}")
    if not image_files:
        print(f"⚠️  No image files found in {folder}")
        return
    print(f"🔍 Testing logo recognition on {len(image_files)} images using method: {method}")
    for img_path in image_files:
        try:
            print(f"Processing: {img_path.name}")
            img = Image.open(img_path)
            if method == "open_source":
                logos = recognize_logos_openlogo(img, model_path=model_path)
            elif method == "vision_llm":
                logos = recognize_logos_vision_llm(img, provider="google", model=vision_model)
            else:
                print(f"Unknown method: {method}")
                continue
            print(f"\n🖼️ {img_path.name}:")
            if logos:
                print(f"   ✅ Recognized logos: {', '.join(logos)}")
            else:
                print("   ❌ No logos recognized")
        except Exception as e:
            print(f"   ❌ Error processing {img_path.name}: {e}")

def print_logo_detection_results(pdf_path, vision_model="gemini-1.5-flash"):
    print(f"\nTesting Vision LLM logo detection for: {pdf_path}")
    from app.services.enhanced_document_parser import EnhancedDocumentParser
    parser = EnhancedDocumentParser()
    result = parser.parse_document_with_images(str(pdf_path), document_type="cv", extract_images=True, logo_recognition="vision_llm", vision_llm_provider="google", vision_llm_model=vision_model)
    image_analysis = result.get("parsed_data", {}).get("image_analysis", {})
    print("\n--- Logo Detection Results ---\n")
    import json
    print(json.dumps(image_analysis, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # Test LLM document parsing on a PDF in uploads
    uploads_dir = Path("uploads")
    pdfs = [f for f in uploads_dir.iterdir() if f.suffix.lower() == ".pdf"]
    if pdfs:
        test_llm_document_parsing(pdfs[0], document_type="cv")
        print_logo_detection_results(pdfs[0], vision_model="gemini-1.5-flash")
    else:
        print("No PDF files found in uploads for LLM document parsing test.")
    # Uncomment to test logo recognition
    # test_logo_recognition(method="vision_llm", vision_model="gemini-1.5-flash") 