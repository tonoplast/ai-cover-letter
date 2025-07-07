#!/usr/bin/env python3
"""
Test script for image extraction functionality
"""

import os
from pathlib import Path

def test_image_extraction():
    """Test the image extraction functionality"""
    
    print("🔍 Testing Image Extraction Capabilities")
    print("=" * 50)
    
    # Test 1: Check if enhanced parser can be imported
    try:
        from app.services.enhanced_document_parser import EnhancedDocumentParser
        print("✅ Enhanced document parser imported successfully")
        
        # Create parser instance
        parser = EnhancedDocumentParser()
        status = parser.get_image_extraction_status()
        
        print(f"📊 Image extraction status:")
        print(f"   - Image extraction available: {status['image_extraction_available']}")
        print(f"   - OCR available: {status['ocr_available']}")
        print(f"   - Vision available: {status['vision_available']}")
        print(f"   - Fully available: {status['fully_available']}")
        
    except ImportError as e:
        print(f"❌ Failed to import enhanced parser: {e}")
        return
    
    # Test 2: Check if we can extract images from a PDF
    # Use the first available PDF in uploads
    uploads_dir = Path("uploads")
    pdf_files = [f for f in uploads_dir.iterdir() if f.suffix.lower() == ".pdf"]
    if pdf_files:
        test_pdf = pdf_files[0]
        print(f"\n📄 Testing with PDF: {test_pdf}")
        try:
            # Test basic parsing with image extraction
            result = parser.parse_document_with_images(str(test_pdf), "cv", extract_images=True)
            print("✅ Document parsed successfully")
            print(f"   - Content length: {len(result.get('content', ''))}")
            print(f"   - Has image analysis: {'image_analysis' in result.get('parsed_data', {})}")
            if 'image_analysis' in result.get('parsed_data', {}):
                img_analysis = result['parsed_data']['image_analysis']
                print(f"   - Images found: {img_analysis.get('images_found', False)}")
                print(f"   - OCR used: {img_analysis.get('ocr_used', False)}")
                print(f"   - Vision used: {img_analysis.get('vision_used', False)}")
                if img_analysis.get('extracted_text'):
                    print(f"   - Extracted text: {img_analysis['extracted_text'][:100]}...")
                else:
                    print("   - No text extracted from images")
        except Exception as e:
            print(f"❌ Error parsing document: {e}")
    else:
        print(f"⚠️  No PDF files found in uploads directory.")
    
    # Test 3: Check Tesseract installation
    print(f"\n🔍 Tesseract OCR Status:")
    if status['ocr_available']:
        try:
            import pytesseract
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract OCR available: {version}")
        except Exception as e:
            print(f"❌ Tesseract OCR error: {e}")
    else:
        print("❌ Tesseract OCR not available")
        print("📋 To install Tesseract OCR on Windows:")
        print("   1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   2. Install and add to PATH")
    
    print("\n" + "=" * 50)
    print("📖 Summary:")
    if status['image_extraction_available']:
        print("✅ Image extraction is available")
        if status['ocr_available']:
            print("✅ OCR is available - full functionality")
        else:
            print("⚠️  OCR not available - images can be extracted but text recognition limited")
    else:
        print("❌ Image extraction not available")

if __name__ == "__main__":
    test_image_extraction() 