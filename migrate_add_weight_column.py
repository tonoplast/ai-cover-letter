#!/usr/bin/env python3
"""
Migration script to add weight column to existing documents
"""

import os
import sys
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import get_db, engine
from app.models import Document
from app.services.rag_service import RAGService
from sqlalchemy import text

def migrate_add_weight_column():
    """Add weight column to documents table and populate with default values"""
    
    # Set up test environment variables (same as in .env)
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
        # Check if weight column already exists
        result = db.execute(text("""
            SELECT name FROM pragma_table_info('documents') 
            WHERE name = 'weight'
        """))
        
        if result.fetchone():
            print("Weight column already exists in documents table")
        else:
            # Add weight column
            print("Adding weight column to documents table...")
            db.execute(text("ALTER TABLE documents ADD COLUMN weight REAL DEFAULT 1.0"))
            print("Weight column added successfully")
        
        # Get all documents and update their weights
        documents = db.query(Document).all()
        rag_service = RAGService(db)
        
        print(f"Updating weights for {len(documents)} documents...")
        
        for doc in documents:
            # Calculate weight based on document type and recency
            weight = rag_service.calculate_document_weight(doc)
            doc.weight = weight
            
            print(f"  {doc.filename} ({doc.document_type}): {weight:.3f}")
        
        # Commit changes
        db.commit()
        print("Migration completed successfully!")
        
        # Show summary
        print("\n=== Weight Summary ===")
        for doc_type in ['cv', 'cover_letter', 'linkedin', 'other']:
            docs = db.query(Document).filter(Document.document_type == doc_type).all()
            if docs:
                avg_weight = sum(doc.weight for doc in docs) / len(docs)
                print(f"{doc_type.upper()}: {len(docs)} documents, avg weight: {avg_weight:.3f}")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_add_weight_column() 