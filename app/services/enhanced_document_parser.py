"""
Enhanced Document Parser with Image Extraction Capabilities

This module extends the basic document parser to handle images in PDFs,
including OCR and vision analysis for extracting text and content from images.
"""

from pathlib import Path
import re
import warnings
from typing import Dict, List, Any, Optional
from datetime import datetime
import PyPDF2
from docx import Document
import pandas as pd
from sqlalchemy.orm import Session
from app.models import Document, Experience, Skill
from app.database import get_db
import json
import io
import base64
import requests
import os

# Suppress torch warnings about pin_memory
warnings.filterwarnings("ignore", message=".*pin_memory.*")

# Try to import image processing libraries
try:
    import fitz  # PyMuPDF for image extraction
    from PIL import Image
    IMAGE_EXTRACTION_AVAILABLE = True
except ImportError:
    IMAGE_EXTRACTION_AVAILABLE = False
    print("PyMuPDF not available. Image extraction will be disabled.")

# Try to import OCR libraries
try:
    import pytesseract
    from pytesseract import Output
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("pytesseract not available. OCR will be disabled.")

# Try to import vision libraries
try:
    import cv2
    import numpy as np
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False
    print("OpenCV not available. Vision analysis will be disabled.")

# Import the original document parser
from app.services.document_parser import DocumentParser, DOCILING_AVAILABLE

# YOLOv8 integration for OpenLogo
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("YOLOv8 not available. Install with: pip install ultralytics")

LOGO_RECOGNITION_APIS = {
    'logolize': 'https://api.logolize.com/v1/detect',
    'logosearch': 'https://api.logosearch.ai/v1/detect',
}

def recognize_logos_public_api(image: Image.Image, api: str = 'logolize') -> list:
    """Send image to a public logo recognition API and return detected logo names."""
    if api not in LOGO_RECOGNITION_APIS:
        return []
    url = LOGO_RECOGNITION_APIS[api]
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    files = {'image': ('image.png', img_bytes, 'image/png')}
    try:
        resp = requests.post(url, files=files, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            # Both APIs return a list of detected logos, but format may differ
            if 'logos' in data:
                return [logo.get('name', logo) for logo in data['logos']]
            elif 'results' in data:
                return [r.get('name', r) for r in data['results']]
        else:
            print(f"Logo API error: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Logo API exception: {e}")
    return []

def recognize_logos_openlogo(image: Image.Image, model_path: str = "openlogo_yolov8.pt") -> list:
    """
    Use YOLOv8 to detect logos in the image. Requires a YOLOv8 model trained on logos.
    Default model path is 'openlogo_yolov8.pt'.
    Returns a list of detected logo names.
    """
    if not YOLO_AVAILABLE:
        print("YOLOv8 not available. Please install ultralytics.")
        return []
    # Convert PIL image to numpy array (RGB)
    img_np = np.array(image.convert('RGB'))
    try:
        model = YOLO(model_path)
        results = model(img_np)
        detected_logos = set()
        for r in results:
            # Each r.boxes.cls is a tensor of class indices
            # Each r.names is a dict mapping class index to name
            if hasattr(r, 'boxes') and hasattr(r.boxes, 'cls'):
                for cls_idx in r.boxes.cls:
                    name = r.names.get(int(cls_idx), str(cls_idx))
                    detected_logos.add(name)
        return list(detected_logos)
    except Exception as e:
        print(f"YOLOv8 logo detection error: {e}")
        return []

def recognize_logos_vision_llm(image: Image.Image, provider: str = "google", model: str = None) -> list:
    """
    Recognize logos using a vision LLM provider. Supports 'google' (Gemini), 'openai', 'claude', 'ollama'.
    Returns a list of detected logo/tool names.
    """
    if provider == "google":
        return recognize_logos_gemini(image, model)
    elif provider == "openai":
        print("[Vision LLM] OpenAI vision model integration not yet implemented.")
        return []
    elif provider == "claude":
        print("[Vision LLM] Claude vision model integration not yet implemented.")
        return []
    elif provider == "ollama":
        print("[Vision LLM] Ollama vision model integration not yet implemented.")
        return []
    else:
        print(f"[Vision LLM] Unknown provider: {provider}")
        return []

def recognize_logos_gemini(image: Image.Image, model: str = None) -> list:
    """
    Use Google Gemini Vision API to recognize logos/tools in the image.
    Requires GOOGLE_GEMINI_API_KEY in environment.
    Uses 'gemini-1.5-flash' as the default model if none specified.
    """
    api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    if not api_key:
        print("[Gemini] GOOGLE_GEMINI_API_KEY not set in environment.")
        return []
    # Convert image to base64
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode()
    # Use gemini-1.5-flash as default model
    model_name = model or "gemini-1.5-flash"
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": "What logos, tools, or software do you see in this image? List only the names, separated by commas."},
                    {"inlineData": {"mimeType": "image/png", "data": img_b64}}
                ]
            }
        ]
    }
    params = {"key": api_key}
    try:
        resp = requests.post(endpoint, headers=headers, params=params, json=payload, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            # Parse Gemini response for logo/tool names
            candidates = data.get("candidates", [])
            if candidates:
                text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                # Split by comma and clean up
                names = [n.strip() for n in text.split(",") if n.strip()]
                return names
            else:
                print("[Gemini] No candidates in response.")
        else:
            print(f"[Gemini] API error: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"[Gemini] API exception: {e}")
    return []

class EnhancedDocumentParser(DocumentParser):
    """
    Enhanced document parser that can extract and analyze images in PDFs.
    Extends the base DocumentParser with image processing capabilities.
    """
    
    def __init__(self):
        super().__init__()
        self.image_extraction_enabled = IMAGE_EXTRACTION_AVAILABLE
        self.ocr_enabled = OCR_AVAILABLE
        self.vision_enabled = VISION_AVAILABLE
        
        if not self.image_extraction_enabled:
            print("Warning: Image extraction is not available. Install PyMuPDF with: pip install PyMuPDF")
        if not self.ocr_enabled:
            print("Warning: OCR is not available. Install pytesseract with: pip install pytesseract")
        if not self.vision_enabled:
            print("Warning: Vision analysis is not available. Install OpenCV with: pip install opencv-python")

    def parse_document_with_images(self, file_path: str, document_type: str, 
                                 extract_images: bool = True,
                                 logo_recognition: str = "vision_llm",
                                 vision_llm_provider: str = "google",
                                 vision_llm_model: str = "gemini-1.5-flash") -> Dict[str, Any]:
        """
        Parse document with optional image extraction and vision LLM logo detection.
        vision_llm_provider: provider for vision LLM (e.g., 'google', 'openai', 'ollama')
        vision_llm_model: model for vision LLM (e.g., 'gemini-1.5-flash', 'gpt-4o', 'llava:latest')
        """
        basic_parsed = self.parse_document(file_path, document_type)
        if extract_images and self.image_extraction_enabled:
            file_extension = Path(file_path).suffix.lower()
            if file_extension == '.pdf':
                image_text = self._extract_text_from_images(file_path)
                images_data = self.extract_images_from_pdf(file_path)
                recognized_logos = set()
                for img_info in images_data:
                    pil_image = img_info.get('analysis', {}).get('pil_image')
                    if pil_image:
                        logos = recognize_logos_vision_llm(pil_image, provider=vision_llm_provider, model=vision_llm_model)
                        recognized_logos.update(logos)
                if image_text:
                    basic_parsed["content"] += f"\n\n--- IMAGE EXTRACTED CONTENT ---\n{image_text}"
                basic_parsed["parsed_data"]["image_analysis"] = {
                    "images_found": bool(images_data),
                    "extracted_text": image_text or "",
                    "ocr_used": self.ocr_enabled,
                    "vision_used": self.vision_enabled,
                    "vision_llm_provider": vision_llm_provider,
                    "vision_llm_model": vision_llm_model,
                    "recognized_logos": list(recognized_logos)
                }
        return basic_parsed

    def extract_images_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        images_data = []
        if not self.image_extraction_enabled:
            print("Image extraction not available")
            return images_data
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        if pix.n - pix.alpha < 4:
                            img_data = pix.tobytes("png")
                        else:
                            pix1 = fitz.Pixmap(fitz.csRGB, pix)
                            img_data = pix1.tobytes("png")
                            pix1 = None
                        pil_image = Image.open(io.BytesIO(img_data))
                        image_analysis = self._analyze_image_content(pil_image, page_num, img_index)
                        # Add pil_image to analysis for logo recognition
                        image_analysis['pil_image'] = pil_image
                        images_data.append({
                            'page': page_num,
                            'image_index': img_index,
                            'size': pil_image.size,
                            'format': pil_image.format,
                            'analysis': image_analysis
                        })
                        pix = None
                    except Exception as e:
                        print(f"Error processing image {img_index} on page {page_num}: {e}")
                        continue
            doc.close()
        except Exception as e:
            print(f"Error extracting images from PDF: {e}")
        return images_data

    def _analyze_image_content(self, image: Image.Image, page_num: int, img_index: int) -> Dict[str, Any]:
        """Analyze image content using OCR and vision analysis"""
        analysis = {
            'ocr_text': '',
            'detected_objects': [],
            'content_type': 'unknown',
            'confidence': 0.0
        }
        
        # OCR Analysis
        if self.ocr_enabled:
            try:
                # Convert PIL image to format suitable for OCR
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Perform OCR
                ocr_result = pytesseract.image_to_data(image, output_type=Output.DICT)
                
                # Extract text from OCR result
                text_parts = []
                for i, conf in enumerate(ocr_result['conf']):
                    if conf > 30:  # Confidence threshold
                        text_parts.append(ocr_result['text'][i])
                
                analysis['ocr_text'] = ' '.join(text_parts).strip()
                
                # Determine content type based on OCR text
                if analysis['ocr_text']:
                    analysis['content_type'] = self._classify_image_content(analysis['ocr_text'])
                    analysis['confidence'] = max(ocr_result['conf']) if ocr_result['conf'] else 0
                
            except Exception as e:
                print(f"OCR analysis failed for image {img_index} on page {page_num}: {e}")
        
        # Vision Analysis (if available)
        if self.vision_enabled and analysis['ocr_text']:
            try:
                # Convert PIL image to OpenCV format
                cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                # Basic object detection (you can enhance this with more sophisticated models)
                # For now, we'll focus on text detection and basic analysis
                analysis['detected_objects'] = self._detect_objects_in_image(cv_image)
                
            except Exception as e:
                print(f"Vision analysis failed for image {img_index} on page {page_num}: {e}")
        
        return analysis

    def _classify_image_content(self, text: str) -> str:
        """Classify the type of content in the image based on text"""
        text_lower = text.lower()
        
        # Check for tools and software
        tool_keywords = ['software', 'tools', 'technologies', 'programming', 'languages', 
                        'frameworks', 'databases', 'platforms', 'applications', 'systems',
                        'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws',
                        'docker', 'kubernetes', 'git', 'agile', 'scrum', 'html', 'css',
                        'typescript', 'angular', 'vue', 'mongodb', 'postgresql', 'mysql']
        
        if any(keyword in text_lower for keyword in tool_keywords):
            return 'tools_and_software'
        
        # Check for skills
        skill_keywords = ['skills', 'competencies', 'expertise', 'proficiencies', 'abilities']
        if any(keyword in text_lower for keyword in skill_keywords):
            return 'skills'
        
        # Check for certifications
        cert_keywords = ['certification', 'certified', 'license', 'accreditation', 'cert']
        if any(keyword in text_lower for keyword in cert_keywords):
            return 'certifications'
        
        # Check for education
        edu_keywords = ['education', 'degree', 'university', 'college', 'school', 'bachelor', 'master', 'phd']
        if any(keyword in text_lower for keyword in edu_keywords):
            return 'education'
        
        # Check for experience
        exp_keywords = ['experience', 'work', 'employment', 'career', 'job', 'position']
        if any(keyword in text_lower for keyword in exp_keywords):
            return 'experience'
        
        return 'general_content'

    def _detect_objects_in_image(self, cv_image) -> List[str]:
        """Detect objects in image using OpenCV (basic implementation)"""
        # This is a basic implementation - you can enhance with more sophisticated models
        objects = []
        
        try:
            # Convert to grayscale for basic analysis
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Basic edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Analyze contours for basic shapes
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Filter small contours
                    # Approximate shape
                    epsilon = 0.02 * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    
                    if len(approx) == 4:
                        objects.append('rectangle')
                    elif len(approx) > 8:
                        objects.append('circle')
                    else:
                        objects.append('polygon')
            
        except Exception as e:
            print(f"Object detection failed: {e}")
        
        return objects

    def _extract_text_from_images(self, file_path: str) -> str:
        """Extract text from all images in a PDF"""
        images_data = self.extract_images_from_pdf(file_path)
        
        extracted_text = []
        for img_data in images_data:
            analysis = img_data['analysis']
            if analysis['ocr_text']:
                content_type = analysis['content_type']
                confidence = analysis['confidence']
                extracted_text.append(f"[{content_type.upper()}] (Confidence: {confidence}%) {analysis['ocr_text']}")
        
        return '\n'.join(extracted_text)

    def get_image_extraction_status(self) -> Dict[str, bool]:
        """Get the status of image extraction capabilities"""
        return {
            'image_extraction_available': self.image_extraction_enabled,
            'ocr_available': self.ocr_enabled,
            'vision_available': self.vision_enabled,
            'fully_available': self.image_extraction_enabled and self.ocr_enabled
        } 