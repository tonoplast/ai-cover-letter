#!/usr/bin/env python3
"""
Fix database by adding weight column to documents table
"""

import os
import sys
from sqlalchemy import text, create_engine

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import DATABASE_URL

def fix_database():
    """Add weight column to documents table"""
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            print("Adding weight column to documents table...")
            
            # Add the weight column
            conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS weight REAL DEFAULT 1.0"))
            
            # Update any existing NULL values
            conn.execute(text("UPDATE documents SET weight = 1.0 WHERE weight IS NULL"))
            
            # Make the column NOT NULL
            conn.execute(text("ALTER TABLE documents ALTER COLUMN weight SET NOT NULL"))
            
            # Commit the changes
            conn.commit()
            
            print("Weight column added successfully!")
            
            # Verify the column was added
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default 
                FROM information_schema.columns 
                WHERE table_name = 'documents' AND column_name = 'weight'
            """))
            
            row = result.fetchone()
            if row:
                print(f"Column verified: {row}")
            else:
                print("Warning: Column not found in schema")
                
            # Show current documents and their weights
            result = conn.execute(text("SELECT id, filename, document_type, weight FROM documents"))
            documents = result.fetchall()
            
            print(f"\nFound {len(documents)} documents:")
            for doc in documents:
                print(f"  ID {doc[0]}: {doc[1]} ({doc[2]}) - weight: {doc[3]}")
                
        except Exception as e:
            print(f"Error: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    fix_database() 