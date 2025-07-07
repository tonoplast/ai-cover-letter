import os
import json
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from app.models import Document
import re
from datetime import datetime
from app.services.filename_parser import FilenameParser

class RAGService:
    def __init__(self, db: Session):
        self.db = db
        # Use a lightweight model for embeddings
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Could not load embedding model: {e}")
            self.embedding_model = None
        
        # Load document weighting configuration
        self.base_weight = float(os.getenv('DOCUMENT_BASE_WEIGHT', '1.0'))
        # Robust parsing for recency period days
        try:
            self.recency_period_days = int(os.getenv('DOCUMENT_RECENCY_PERIOD_DAYS', '365'))
        except Exception as e:
            print(f"Warning: Invalid DOCUMENT_RECENCY_PERIOD_DAYS env var: {os.getenv('DOCUMENT_RECENCY_PERIOD_DAYS')}. Defaulting to 365.")
            self.recency_period_days = 365
        self.min_weight_multiplier = float(os.getenv('DOCUMENT_MIN_WEIGHT_MULTIPLIER', '0.1'))
        self.recency_weighting_enabled = os.getenv('DOCUMENT_RECENCY_WEIGHTING_ENABLED', 'true').lower() == 'true'
        
        # Document type specific weights
        self.document_type_weights = {
            'cv': float(os.getenv('CV_WEIGHT_MULTIPLIER', '2.0')),
            'cover_letter': float(os.getenv('COVER_LETTER_WEIGHT_MULTIPLIER', '1.8')),
            'linkedin': float(os.getenv('LINKEDIN_WEIGHT_MULTIPLIER', '1.2')),
            'other': float(os.getenv('OTHER_DOCUMENT_WEIGHT_MULTIPLIER', '0.8'))
        }
    
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
        content: str = document.content
        chunks = self.extract_chunks(content)
        
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
                    
                    # Calculate document weight based on type and recency
                    doc_type = str(doc.document_type).lower()
                    type_weight = self.document_type_weights.get(doc_type, self.document_type_weights['other'])
                    
                    # Apply recency weighting if enabled
                    if self.recency_weighting_enabled:
                        filename_str = str(doc.filename) if doc.filename is not None else ""
                        content_str = str(doc.content) if doc.content is not None else ""
                        filename_date = FilenameParser.extract_date_from_filename(filename_str)
                        content_date = None
                        if not filename_date:
                            # Try to extract date from content (for CVs and cover letters)
                            content_date = self._extract_date_from_content(content_str)
                        if filename_date:
                            days_since_document = (datetime.now() - filename_date).days
                        elif content_date:
                            days_since_document = (datetime.now() - content_date).days
                        else:
                            days_since_upload = (datetime.now() - doc.uploaded_at).days
                            days_since_document = days_since_upload
                        recency_multiplier = max(self.min_weight_multiplier, 1.0 - (days_since_document / self.recency_period_days))
                    else:
                        recency_multiplier = 1.0
                    
                    # Calculate final weight combining type and recency
                    final_weight = self.base_weight * type_weight * recency_multiplier
                    
                    # Combine similarity with document weight
                    adjusted_similarity = similarity * final_weight
                    
                    all_results.append({
                        "chunk": chunk,
                        "similarity": similarity,
                        "adjusted_similarity": adjusted_similarity,
                        "document_id": doc.id,
                        "document_type": doc.document_type,
                        "uploaded_at": doc.uploaded_at,
                        "type_weight": type_weight,
                        "recency_multiplier": recency_multiplier,
                        "final_weight": final_weight,
                        "chunk_index": i
                    })
        
        # Sort by adjusted similarity (combines relevance + recency) and return top_k
        all_results.sort(key=lambda x: x["adjusted_similarity"], reverse=True)
        return all_results[:top_k]
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1_array = np.array(vec1)
        vec2_array = np.array(vec2)
        return float(np.dot(vec1_array, vec2_array) / (np.linalg.norm(vec1_array) * np.linalg.norm(vec2_array)))
    
    def get_relevant_context(self, job_title: str, job_description: str, company_name: str) -> str:
        """Get relevant context from uploaded documents and company research for cover letter generation"""
        query = f"{job_title} {job_description} {company_name}"
        relevant_chunks = self.find_relevant_chunks(query, top_k=3)
        
        context_parts = []
        
        # Add document chunks
        for chunk_data in relevant_chunks:
            chunk = chunk_data["chunk"]
            doc_type = chunk_data["document_type"]
            context_parts.append(f"[From {doc_type.upper()}]: {chunk[:300]}...")
        
        # Add company research data if available
        try:
            from app.models import CompanyResearch
            company_research = self.db.query(CompanyResearch).filter(
                CompanyResearch.company_name.ilike(f"%{company_name}%")
            ).order_by(CompanyResearch.researched_at.desc()).first()
            
            if company_research is not None and company_research.research_data is not None:
                research_data = company_research.research_data
                research_context = []
                
                if research_data.get('mission'):
                    research_context.append(f"Mission: {research_data['mission']}")
                if research_data.get('vision'):
                    research_context.append(f"Vision: {research_data['vision']}")
                if research_data.get('values'):
                    research_context.append(f"Values: {research_data['values']}")
                if research_data.get('industry'):
                    research_context.append(f"Industry: {research_data['industry']}")
                if research_data.get('description'):
                    research_context.append(f"Description: {research_data['description'][:200]}...")
                
                if research_context:
                    context_parts.append(f"[From COMPANY RESEARCH]: {' | '.join(research_context)}")
        except Exception as e:
            print(f"Error adding company research to RAG context: {e}")
        
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

    def calculate_document_weight(self, document: Document) -> float:
        """Calculate the weight for a document based on type and recency.
        Recency is determined by (in order of precedence):
        1. Date in filename (YYYY-MM-DD etc)
        2. Date in document content (first YYYY-MM-DD or similar)
        3. Upload date (database timestamp)
        """
        # Get document type weight
        doc_type = str(document.document_type).lower()
        type_weight = self.document_type_weights.get(doc_type, self.document_type_weights['other'])

        # Apply recency weighting if enabled
        if self.recency_weighting_enabled:
            filename_str = str(document.filename) if document.filename is not None else ""
            content_str = str(document.content) if document.content is not None else ""
            filename_date = FilenameParser.extract_date_from_filename(filename_str)
            content_date = None
            if not filename_date:
                # Try to extract date from content (for CVs and cover letters)
                content_date = self._extract_date_from_content(content_str)
            if filename_date:
                days_since_document = (datetime.now() - filename_date).days
            elif content_date:
                days_since_document = (datetime.now() - content_date).days
            else:
                days_since_upload = (datetime.now() - document.uploaded_at).days
                days_since_document = days_since_upload
            recency_multiplier = max(self.min_weight_multiplier, 1.0 - (days_since_document / self.recency_period_days))
        else:
            recency_multiplier = 1.0

        # Calculate final weight combining type and recency
        final_weight = self.base_weight * type_weight * recency_multiplier
        return final_weight

    @staticmethod
    def _extract_date_from_content(content: str):
        """Extract the first date in YYYY-MM-DD, YYYY/MM/DD, DD-MM-YYYY, or similar from the content string."""
        # Try several date patterns
        date_patterns = [
            r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})',  # YYYY-MM-DD or YYYY/MM/DD
            r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})',  # DD-MM-YYYY or MM-DD-YYYY
        ]
        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    if len(match.groups()) == 3:
                        parts = [int(x) for x in match.groups()]
                        # Heuristic: if first part is 4 digits, it's year
                        if len(match.group(1)) == 4:
                            return datetime(parts[0], parts[1], parts[2])
                        else:
                            # Could be DD-MM-YYYY or MM-DD-YYYY; try both
                            for order in [(2,1,0), (2,0,1)]:
                                try:
                                    return datetime(parts[order[0]], parts[order[1]], parts[order[2]])
                                except:
                                    continue
                except Exception:
                    continue
        return None

    def get_document_type_weight(self, document_type: str) -> float:
        """Get the weight multiplier for a specific document type"""
        doc_type = document_type.lower()
        return self.document_type_weights.get(doc_type, self.document_type_weights['other']) 