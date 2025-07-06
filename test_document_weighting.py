#!/usr/bin/env python3
"""
Test script for document weighting system
"""

import os
import sys
from datetime import datetime, timedelta

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import get_db, engine
from app.models import Document
from app.services.rag_service import RAGService

def test_document_weighting():
    """Test the document weighting system"""
    
    # Set up test environment variables
    os.environ['DOCUMENT_BASE_WEIGHT'] = '1.0'
    os.environ['DOCUMENT_RECENCY_PERIOD_DAYS'] = '365'
    os.environ['DOCUMENT_MIN_WEIGHT_MULTIPLIER'] = '0.1'
    os.environ['DOCUMENT_RECENCY_WEIGHTING_ENABLED'] = 'true'
    os.environ['CV_WEIGHT_MULTIPLIER'] = '2.0'
    os.environ['COVER_LETTER_WEIGHT_MULTIPLIER'] = '1.8'
    os.environ['LINKEDIN_WEIGHT_MULTIPLIER'] = '1.2'
    os.environ['OTHER_DOCUMENT_WEIGHT_MULTIPLIER'] = '0.8'
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create RAG service
        rag_service = RAGService(db)
        
        print("=== Document Weighting Configuration ===")
        print(f"Base weight: {rag_service.base_weight}")
        print(f"Recency period (days): {rag_service.recency_period_days}")
        print(f"Min weight multiplier: {rag_service.min_weight_multiplier}")
        print(f"Recency weighting enabled: {rag_service.recency_weighting_enabled}")
        print(f"Document type weights: {rag_service.document_type_weights}")
        print()
        
        # Test document type weights
        print("=== Document Type Weights ===")
        for doc_type in ['cv', 'cover_letter', 'linkedin', 'other']:
            weight = rag_service.get_document_type_weight(doc_type)
            print(f"{doc_type.upper()}: {weight}")
        print()
        
        # Test with sample documents
        print("=== Sample Document Weight Calculations ===")
        
        # Create sample documents with different upload dates
        sample_docs = [
            {
                'document_type': 'cv',
                'uploaded_at': datetime.now() - timedelta(days=30),  # Recent
                'description': 'Recent CV'
            },
            {
                'document_type': 'cv', 
                'uploaded_at': datetime.now() - timedelta(days=200),  # Older
                'description': 'Older CV'
            },
            {
                'document_type': 'cover_letter',
                'uploaded_at': datetime.now() - timedelta(days=10),  # Very recent
                'description': 'Recent Cover Letter'
            },
            {
                'document_type': 'linkedin',
                'uploaded_at': datetime.now() - timedelta(days=100),  # Medium age
                'description': 'LinkedIn Profile'
            },
            {
                'document_type': 'other',
                'uploaded_at': datetime.now() - timedelta(days=400),  # Old
                'description': 'Old Other Document'
            }
        ]
        
        for doc_info in sample_docs:
            # Create a mock document object
            class MockDocument:
                def __init__(self, doc_type, uploaded_at):
                    self.document_type = doc_type
                    self.uploaded_at = uploaded_at
            
            mock_doc = MockDocument(doc_info['document_type'], doc_info['uploaded_at'])
            weight = rag_service.calculate_document_weight(mock_doc)
            
            print(f"{doc_info['description']}:")
            print(f"  Type: {doc_info['document_type']}")
            print(f"  Age: {(datetime.now() - doc_info['uploaded_at']).days} days")
            print(f"  Weight: {weight:.3f}")
            print()
        
        print("=== Weighting Summary ===")
        print("• CV documents get highest weight (2.0x)")
        print("• Cover letters get high weight (1.8x)")
        print("• LinkedIn profiles get medium weight (1.2x)")
        print("• Other documents get lowest weight (0.8x)")
        print("• Recent documents get full weight")
        print("• Older documents get reduced weight based on age")
        print("• Documents older than 365 days get minimum weight (0.1x)")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_document_weighting() 