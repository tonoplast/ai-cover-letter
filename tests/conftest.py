#!/usr/bin/env python3
"""
Shared test fixtures and configuration
"""

import os
import sys
import pytest
from pathlib import Path
from datetime import datetime, timedelta

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.database import get_db, engine
from app.models import Document
from app.services.rag_service import RAGService

@pytest.fixture(scope="function")
def db_session():
    """Fixture to provide a database session for testing"""
    session = next(get_db())
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def rag_service(db_session):
    """Fixture to provide a RAGService instance"""
    # Set up test environment variables
    os.environ['DOCUMENT_BASE_WEIGHT'] = '1.0'
    os.environ['DOCUMENT_RECENCY_PERIOD_DAYS'] = '365'
    os.environ['DOCUMENT_MIN_WEIGHT_MULTIPLIER'] = '0.1'
    os.environ['DOCUMENT_RECENCY_WEIGHTING_ENABLED'] = 'true'
    os.environ['CV_WEIGHT_MULTIPLIER'] = '2.0'
    os.environ['COVER_LETTER_WEIGHT_MULTIPLIER'] = '1.8'
    os.environ['LINKEDIN_WEIGHT_MULTIPLIER'] = '1.2'
    os.environ['OTHER_DOCUMENT_WEIGHT_MULTIPLIER'] = '0.8'
    
    return RAGService(db_session)

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

@pytest.fixture
def test_api_base_url():
    """Fixture to provide the test API base URL"""
    return "http://localhost:8000"

@pytest.fixture
def mock_document_class():
    """Fixture to provide a mock document class for testing"""
    class MockDocument:
        def __init__(self, doc_type, uploaded_at, filename=None, content=None, manual_weight=1.0):
            self.document_type = doc_type
            self.uploaded_at = uploaded_at
            self.filename = filename or f"test_{doc_type}.pdf"
            self.content = content or f"Sample {doc_type} content for testing"
            self.manual_weight = manual_weight
    
    return MockDocument

@pytest.fixture
def sample_documents(mock_document_class):
    """Fixture to provide sample documents for testing"""
    return [
        mock_document_class('cv', datetime.now() - timedelta(days=30)),
        mock_document_class('cv', datetime.now() - timedelta(days=200)),
        mock_document_class('cover_letter', datetime.now() - timedelta(days=10)),
        mock_document_class('linkedin', datetime.now() - timedelta(days=100)),
        mock_document_class('other', datetime.now() - timedelta(days=400))
    ]