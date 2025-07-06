#!/usr/bin/env python3
"""
Update existing documents with proper weights based on type and recency
"""

import os
import sys
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import get_db
from app.models import Document
from app.services.rag_service import RAGService

def update_existing_weights():
    """Update weights for all existing documents"""
    
    # Set up environment variables for weighting
    os.environ['DOCUMENT_BASE_WEIGHT'] = '1.0'
    os.environ['DOCUMENT_RECENCY_PERIOD_DAYS'] = '365'
    os.environ['DOCUMENT_MIN_WEIGHT_MULTIPLIER'] = '0.1'
    os.environ['DOCUMENT_RECENCY_WEIGHTING_ENABLED'] = 'true'
    os.environ['CV_WEIGHT_MULTIPLIER'] = '2.0'
    os.environ['COVER_LETTER_WEIGHT_MULTIPLIER'] = '1.8'
    os.environ['LINKEDIN_WEIGHT_MULTIPLIER'] = '1.2'
    os.environ['OTHER_DOCUMENT_WEIGHT_MULTIPLIER'] = '0.8'
    
    db = next(get_db())
    
    try:
        # Get all documents
        documents = db.query(Document).all()
        
        if not documents:
            print("No documents found in database")
            return
        
        print(f"Found {len(documents)} documents to update")
        
        # Create RAG service for weight calculation
        rag_service = RAGService(db)
        
        # Update each document
        for doc in documents:
            old_weight = doc.weight
            new_weight = rag_service.calculate_document_weight(doc)
            doc.weight = new_weight
            
            print(f"  {doc.filename} ({doc.document_type}): {old_weight:.3f} → {new_weight:.3f}")
        
        # Commit changes
        db.commit()
        print("\nAll document weights updated successfully!")
        
        # Show summary by document type
        print("\n=== Weight Summary by Document Type ===")
        for doc_type in ['cv', 'cover_letter', 'linkedin', 'other']:
            docs = db.query(Document).filter(Document.document_type == doc_type).all()
            if docs:
                weights = [float(doc.weight) for doc in docs]
                avg_weight = sum(weights) / len(weights)
                min_weight = min(weights)
                max_weight = max(weights)
                print(f"{doc_type.upper()}: {len(docs)} documents")
                print(f"  Average weight: {avg_weight:.3f}")
                print(f"  Weight range: {min_weight:.3f} - {max_weight:.3f}")
        
    except Exception as e:
        print(f"Error updating weights: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_existing_weights() 