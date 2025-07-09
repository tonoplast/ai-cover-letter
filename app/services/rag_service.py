import os
import json
import logging
import hashlib
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from app.models import Document
import re
from datetime import datetime
from app.services.filename_parser import FilenameParser
from app.exceptions import RAGServiceError, EmbeddingError, ConfigurationError

logger = logging.getLogger(__name__)

class RAGService:
    _embedding_model = None  # Class-level singleton
    _embedding_cache = {}  # Simple in-memory cache
    _max_cache_size = 1000
    
    def __init__(self, db: Session):
        self.db = db
        # Use singleton pattern for embedding model to save memory
        if RAGService._embedding_model is None:
            try:
                RAGService._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.error(f"Could not load embedding model: {e}")
                RAGService._embedding_model = None
        
        self.embedding_model = RAGService._embedding_model
        
        # Load document weighting configuration with proper validation
        try:
            self.base_weight = float(os.getenv('DOCUMENT_BASE_WEIGHT', '1.0'))
            if self.base_weight <= 0:
                raise ValueError("Base weight must be positive")
        except ValueError as e:
            logger.warning(f"Invalid DOCUMENT_BASE_WEIGHT, using default 1.0: {e}")
            self.base_weight = 1.0
        
        # Robust parsing for recency period days
        try:
            self.recency_period_days = int(os.getenv('DOCUMENT_RECENCY_PERIOD_DAYS', '365'))
            if self.recency_period_days <= 0:
                raise ValueError("Recency period must be positive")
        except ValueError as e:
            logger.warning(f"Invalid DOCUMENT_RECENCY_PERIOD_DAYS, using default 365: {e}")
            self.recency_period_days = 365
        
        try:
            self.min_weight_multiplier = float(os.getenv('DOCUMENT_MIN_WEIGHT_MULTIPLIER', '0.1'))
            if self.min_weight_multiplier <= 0 or self.min_weight_multiplier > 1:
                raise ValueError("Min weight multiplier must be between 0 and 1")
        except ValueError as e:
            logger.warning(f"Invalid DOCUMENT_MIN_WEIGHT_MULTIPLIER, using default 0.1: {e}")
            self.min_weight_multiplier = 0.1
        
        self.recency_weighting_enabled = os.getenv('DOCUMENT_RECENCY_WEIGHTING_ENABLED', 'true').lower() == 'true'
        
        # Document type specific weights with validation
        try:
            self.document_type_weights = {
                'cv': float(os.getenv('CV_WEIGHT_MULTIPLIER', '2.0')),
                'cover_letter': float(os.getenv('COVER_LETTER_WEIGHT_MULTIPLIER', '1.8')),
                'linkedin': float(os.getenv('LINKEDIN_WEIGHT_MULTIPLIER', '1.2')),
                'other': float(os.getenv('OTHER_DOCUMENT_WEIGHT_MULTIPLIER', '0.8'))
            }
            # Validate all weights are positive
            for doc_type, weight in self.document_type_weights.items():
                if weight <= 0:
                    logger.warning(f"Invalid weight for {doc_type}, using default")
                    self.document_type_weights[doc_type] = 1.0
        except Exception as e:
            logger.error(f"Error loading document type weights: {e}")
            self.document_type_weights = {'cv': 2.0, 'cover_letter': 1.8, 'linkedin': 1.2, 'other': 0.8}
    
    def create_embeddings(self, text: str) -> Optional[List[float]]:
        """Create embeddings for a given text with caching"""
        if not self.embedding_model:
            raise EmbeddingError("Embedding model not available")
        
        if not text or not text.strip():
            raise EmbeddingError("Text cannot be empty")
        
        # Create cache key
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Check cache first
        if text_hash in RAGService._embedding_cache:
            return RAGService._embedding_cache[text_hash]
        
        try:
            embedding = self.embedding_model.encode(text).tolist()
            
            # Add to cache (with size limit)
            if len(RAGService._embedding_cache) >= self._max_cache_size:
                # Remove oldest entry (simple FIFO)
                oldest_key = next(iter(RAGService._embedding_cache))
                del RAGService._embedding_cache[oldest_key]
            
            RAGService._embedding_cache[text_hash] = embedding
            return embedding
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise EmbeddingError(f"Failed to create embeddings: {str(e)}")
    
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
        """Find the most relevant chunks for a given query with enhanced scoring"""
        if not self.embedding_model:
            logger.warning("Embedding model not available for RAG")
            return []
        
        if not query or not query.strip():
            raise RAGServiceError("Query cannot be empty")
        
        if top_k <= 0 or top_k > 50:
            raise RAGServiceError("top_k must be between 1 and 50")
        
        try:
            # Get all documents ordered by recency (most recent first)
            documents = self.db.query(Document).order_by(Document.uploaded_at.desc()).all()
            
            # Create query embedding
            query_embedding = self.create_embeddings(query)
            if not query_embedding:
                return []
        
        except Exception as e:
            logger.error(f"Error in find_relevant_chunks: {e}")
            raise RAGServiceError(f"Failed to find relevant chunks: {str(e)}")
        
        # Process each document and find relevant chunks
        all_results = []
        
        for doc in documents:
            processed = self.process_document(doc)
            
            for i, (chunk, embedding) in enumerate(zip(processed["chunks"], processed["embeddings"])):
                if embedding:
                    # Calculate enhanced relevance score
                    relevance_score = self._calculate_enhanced_relevance(
                        query_embedding, embedding, doc, chunk, query
                    )
                    
                    all_results.append({
                        "chunk": chunk,
                        "relevance_score": relevance_score["total_score"],
                        "semantic_score": relevance_score["semantic_score"],
                        "temporal_score": relevance_score["temporal_score"],
                        "domain_score": relevance_score["domain_score"],
                        "document_id": doc.id,
                        "document_type": doc.document_type,
                        "uploaded_at": doc.uploaded_at,
                        "chunk_index": i
                    })
        
        # Sort by relevance score and return top_k
        all_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return all_results[:top_k]
    
    def _calculate_enhanced_relevance(self, query_embedding: List[float], chunk_embedding: List[float], 
                                     document: Document, chunk: str, query: str) -> Dict[str, float]:
        """Calculate enhanced relevance score combining multiple signals"""
        try:
            # 1. Semantic similarity (cosine similarity)
            semantic_score = self.cosine_similarity(query_embedding, chunk_embedding)
            
            # 2. Temporal relevance (recency of document)
            temporal_score = self._calculate_temporal_relevance(document)
            
            # 3. Domain relevance (document type importance)
            domain_score = self._calculate_domain_relevance(document)
            
            # 4. Content quality score (length, keywords, etc.)
            content_score = self._calculate_content_quality(chunk, query)
            
            # 5. Frequency score (how often terms appear)
            frequency_score = self._calculate_frequency_score(chunk, query)
            
            # Weighted combination of scores
            total_score = (
                semantic_score * 0.40 +     # Primary semantic matching
                temporal_score * 0.25 +     # Recency matters
                domain_score * 0.20 +       # Document type importance
                content_score * 0.10 +      # Content quality
                frequency_score * 0.05      # Term frequency
            )
            
            return {
                "total_score": total_score,
                "semantic_score": semantic_score,
                "temporal_score": temporal_score,
                "domain_score": domain_score,
                "content_score": content_score,
                "frequency_score": frequency_score
            }
            
        except Exception as e:
            logger.error(f"Error calculating enhanced relevance: {e}")
            # Fallback to basic cosine similarity
            semantic_score = self.cosine_similarity(query_embedding, chunk_embedding)
            return {
                "total_score": semantic_score,
                "semantic_score": semantic_score,
                "temporal_score": 0.0,
                "domain_score": 0.0,
                "content_score": 0.0,
                "frequency_score": 0.0
            }
    
    def _calculate_temporal_relevance(self, document: Document) -> float:
        """Calculate temporal relevance based on document date"""
        try:
            if not self.recency_weighting_enabled:
                return 1.0
            
            filename_str = str(document.filename) if document.filename else ""
            content_str = str(document.content) if document.content else ""
            
            # Try to get date from filename first
            filename_date = FilenameParser.extract_date_from_filename(filename_str)
            
            if filename_date:
                days_since_document = (datetime.now() - filename_date).days
            else:
                # Try to extract date from content
                content_date = self._extract_date_from_content(content_str)
                if content_date:
                    days_since_document = (datetime.now() - content_date).days
                else:
                    # Fall back to upload date
                    days_since_document = (datetime.now() - document.uploaded_at).days
            
            # Calculate recency score (more recent = higher score)
            recency_score = max(
                self.min_weight_multiplier, 
                1.0 - (days_since_document / self.recency_period_days)
            )
            
            return recency_score
            
        except Exception as e:
            logger.error(f"Error calculating temporal relevance: {e}")
            return 1.0
    
    def _calculate_domain_relevance(self, document: Document) -> float:
        """Calculate domain relevance based on document type"""
        try:
            doc_type = str(document.document_type).lower()
            type_weight = self.document_type_weights.get(doc_type, self.document_type_weights['other'])
            
            # Normalize to 0-1 range (assuming max weight is 2.0)
            normalized_score = min(1.0, type_weight / 2.0)
            
            return normalized_score
            
        except Exception as e:
            logger.error(f"Error calculating domain relevance: {e}")
            return 0.5  # Default middle score
    
    def _calculate_content_quality(self, chunk: str, query: str) -> float:
        """Calculate content quality score based on various factors"""
        try:
            if not chunk or not chunk.strip():
                return 0.0
            
            score = 0.0
            
            # Length factor (prefer chunks with sufficient content)
            chunk_length = len(chunk.strip())
            if chunk_length >= 50:
                score += 0.3
            elif chunk_length >= 20:
                score += 0.1
            
            # Sentence completeness (prefer complete sentences)
            sentences = re.split(r'[.!?]+', chunk)
            complete_sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
            if len(complete_sentences) >= 2:
                score += 0.3
            elif len(complete_sentences) >= 1:
                score += 0.2
            
            # Keyword density (avoid keyword stuffing)
            query_words = set(query.lower().split())
            chunk_words = chunk.lower().split()
            if chunk_words:
                keyword_density = sum(1 for word in chunk_words if word in query_words) / len(chunk_words)
                if 0.05 <= keyword_density <= 0.3:  # Optimal range
                    score += 0.4
                elif keyword_density > 0:
                    score += 0.2
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating content quality: {e}")
            return 0.5
    
    def _calculate_frequency_score(self, chunk: str, query: str) -> float:
        """Calculate frequency score based on term overlap"""
        try:
            if not chunk or not query:
                return 0.0
            
            query_words = set(word.lower().strip() for word in query.split() if len(word.strip()) > 2)
            chunk_words = [word.lower().strip() for word in chunk.split()]
            
            if not query_words or not chunk_words:
                return 0.0
            
            # Calculate term frequency score
            matches = sum(1 for word in chunk_words if word in query_words)
            max_possible_matches = len(query_words) * 3  # Allow for some repetition
            
            frequency_score = min(1.0, matches / max_possible_matches) if max_possible_matches > 0 else 0.0
            
            return frequency_score
            
        except Exception as e:
            logger.error(f"Error calculating frequency score: {e}")
            return 0.0
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            if not vec1 or not vec2 or len(vec1) != len(vec2):
                return 0.0
            
            vec1_array = np.array(vec1)
            vec2_array = np.array(vec2)
            
            # Calculate norms
            norm1 = np.linalg.norm(vec1_array)
            norm2 = np.linalg.norm(vec2_array)
            
            # Avoid division by zero
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = float(np.dot(vec1_array, vec2_array) / (norm1 * norm2))
            
            # Ensure result is in valid range
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
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