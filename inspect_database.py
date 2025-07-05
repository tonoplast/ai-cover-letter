#!/usr/bin/env python3
"""
Database Inspection Script for AI Cover Letter Application
Run this script to inspect the database contents directly.
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models import Document, CoverLetter, Experience, CompanyResearch
from app.database import get_db

load_dotenv()

def inspect_database():
    """Inspect all database contents"""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/ai_cover_letter")
    
    # Create engine and session
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("DATABASE INSPECTION REPORT")
        print("=" * 80)
        
        # Get all documents
        documents = db.query(Document).all()
        print(f"\n📄 DOCUMENTS ({len(documents)} total):")
        print("-" * 40)
        
        for doc in documents:
            print(f"ID: {doc.id}")
            print(f"Filename: {doc.filename}")
            print(f"Type: {doc.document_type}")
            print(f"Uploaded: {doc.uploaded_at}")
            print(f"Content Length: {len(doc.content) if doc.content else 0} characters")
            
            if isinstance(doc.parsed_data, dict):
                print(f"Parsed Data Keys: {list(doc.parsed_data.keys())}")
                if 'experiences' in doc.parsed_data:
                    exp_count = len(doc.parsed_data['experiences'])
                    print(f"Experiences Found: {exp_count}")
                    for i, exp in enumerate(doc.parsed_data['experiences'][:3]):  # Show first 3
                        print(f"  {i+1}. {exp.get('title', 'Unknown')} at {exp.get('company', 'Unknown')}")
                    if exp_count > 3:
                        print(f"  ... and {exp_count - 3} more")
            else:
                print(f"Parsed Data Type: {type(doc.parsed_data)}")
            
            print(f"Content Preview: {doc.content[:200] if doc.content else 'No content'}...")
            print("-" * 40)
        
        # Get all cover letters
        cover_letters = db.query(CoverLetter).all()
        print(f"\n📝 COVER LETTERS ({len(cover_letters)} total):")
        print("-" * 40)
        
        for cl in cover_letters:
            print(f"ID: {cl.id}")
            print(f"Job: {cl.job_title}")
            print(f"Company: {cl.company_name}")
            print(f"Generated: {cl.generated_at}")
            print(f"Content Length: {len(cl.generated_content) if cl.generated_content else 0} characters")
            print(f"Content Preview: {cl.generated_content[:200] if cl.generated_content else 'No content'}...")
            print("-" * 40)
        
        # Get all experiences
        experiences = db.query(Experience).all()
        print(f"\n💼 EXPERIENCES ({len(experiences)} total):")
        print("-" * 40)
        
        for exp in experiences:
            print(f"ID: {exp.id}")
            print(f"Title: {exp.title}")
            print(f"Company: {exp.company}")
            print(f"Start: {exp.start_date}")
            print(f"End: {exp.end_date}")
            print(f"Description: {exp.description[:100] if exp.description else 'No description'}...")
            print("-" * 40)
        
        # Get all company research
        company_research = db.query(CompanyResearch).all()
        print(f"\n🏢 COMPANY RESEARCH ({len(company_research)} total):")
        print("-" * 40)
        
        for cr in company_research:
            print(f"ID: {cr.id}")
            print(f"Company: {cr.company_name}")
            print(f"Researched: {cr.researched_at}")
            print(f"Website: {cr.website}")
            print(f"Industry: {cr.industry}")
            print("-" * 40)
        
        # Document ordering analysis
        print(f"\n📊 DOCUMENT ORDERING ANALYSIS:")
        print("-" * 40)
        print("Documents are ordered by uploaded_at DESC (most recent first)")
        print("Higher ID numbers are NOT necessarily more recent")
        print("Use uploaded_at timestamp to determine recency")
        
        cv_docs = [d for d in documents if d.document_type == "cv"]
        if cv_docs:
            print(f"\nCV Documents (most recent first):")
            for i, doc in enumerate(cv_docs):
                print(f"  {i+1}. ID {doc.id}: {doc.filename} (uploaded {doc.uploaded_at})")
        
    finally:
        db.close()

if __name__ == "__main__":
    inspect_database() 