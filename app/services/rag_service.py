import os
import json
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from app.models import Document
import re

class RAGService:
    def __init__(self, db: Session):
        self.db = db
        # Use a lightweight model for embeddings
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Could not load embedding model: {e}")
            self.embedding_model = None
    
    def create_embeddings(self, text: str) -> Optional[List[float]]:
        """Create embeddings for a given text"""
        if not self.embedding_model:
            return None
        try:
            return self.embedding_model.encode(text).tolist()
        except Exception as e:
            print(f"Error creating embeddings: {e}")
            return None
    
    def extract_chunks(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """Extract overlapping chunks from text"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    def process_document(self, document: Document) -> Dict[str, Any]:
        """Process a document and create embeddings for its chunks"""
        if not self.embedding_model:
            return {"chunks": [], "embeddings": []}
        
        # Extract chunks from document content
        chunks = self.extract_chunks(document.content)
        
        # Create embeddings for each chunk
        embeddings = []
        for chunk in chunks:
            embedding = self.create_embeddings(chunk)
            if embedding:
                embeddings.append(embedding)
        
        return {
            "chunks": chunks,
            "embeddings": embeddings,
            "document_id": document.id,
            "document_type": document.document_type
        }
    
    def find_relevant_chunks(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find the most relevant chunks for a given query"""
        if not self.embedding_model:
            return []
        
        # Get all documents ordered by recency (most recent first)
        documents = self.db.query(Document).order_by(Document.uploaded_at.desc()).all()
        
        # Create query embedding
        query_embedding = self.create_embeddings(query)
        if not query_embedding:
            return []
        
        # Process each document and find relevant chunks
        all_results = []
        
        for doc in documents:
            processed = self.process_document(doc)
            
            for i, (chunk, embedding) in enumerate(zip(processed["chunks"], processed["embeddings"])):
                if embedding:
                    # Calculate cosine similarity
                    similarity = self.cosine_similarity(query_embedding, embedding)
                    
                    # Apply recency boost (more recent documents get higher weight)
                    # Calculate days since upload (newer = higher boost)
                    from datetime import datetime
                    days_since_upload = (datetime.now() - doc.uploaded_at).days
                    recency_boost = max(0.1, 1.0 - (days_since_upload / 365))  # Boost decreases over time
                    
                    # Combine similarity with recency boost
                    adjusted_similarity = similarity * recency_boost
                    
                    all_results.append({
                        "chunk": chunk,
                        "similarity": similarity,
                        "adjusted_similarity": adjusted_similarity,
                        "document_id": doc.id,
                        "document_type": doc.document_type,
                        "uploaded_at": doc.uploaded_at,
                        "recency_boost": recency_boost,
                        "chunk_index": i
                    })
        
        # Sort by adjusted similarity (combines relevance + recency) and return top_k
        all_results.sort(key=lambda x: x["adjusted_similarity"], reverse=True)
        return all_results[:top_k]
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def get_relevant_context(self, job_title: str, job_description: str, company_name: str) -> str:
        """Get relevant context from uploaded documents for cover letter generation"""
        query = f"{job_title} {job_description} {company_name}"
        relevant_chunks = self.find_relevant_chunks(query, top_k=3)
        
        if not relevant_chunks:
            return ""
        
        context_parts = []
        for chunk_data in relevant_chunks:
            chunk = chunk_data["chunk"]
            doc_type = chunk_data["document_type"]
            context_parts.append(f"[From {doc_type.upper()}]: {chunk[:300]}...")
        
        return "\n\n".join(context_parts)
    
    def enhance_cover_letter_prompt(self, base_prompt: str, job_title: str, job_description: str, company_name: str) -> str:
        """Enhance the cover letter prompt with relevant context from documents"""
        relevant_context = self.get_relevant_context(job_title, job_description, company_name)
        
        if not relevant_context:
            return base_prompt
        
        enhanced_prompt = f"""
{base_prompt}

ADDITIONAL RELEVANT CONTEXT FROM YOUR DOCUMENTS:
{relevant_context}

Use this additional context to make your cover letter more specific and relevant to your actual background and experience.
"""
        return enhanced_prompt 