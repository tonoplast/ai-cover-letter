from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import *
from app.models import Document, Experience, CoverLetter, CompanyResearch
from app.services.document_parser import DocumentParser
from app.services.linkedin_scraper import LinkedInScraper
from app.services.company_research import CompanyResearchService
from app.services.llm_service import LLMService
from app.services.cover_letter_gen import CoverLetterGenerator
from app.services.document_export import DocumentExporter
from pathlib import Path
import shutil
import os
from datetime import datetime
from typing import List
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException

class ChatRequest(BaseModel):
    cover_letter_id: int
    message: str

class BatchCoverLetterRequest(BaseModel):
    job_title: str
    companies: List[str]
    job_description: str
    tone: str = "professional"
    websites: List[str] = []
    delay_seconds: int = 3
    include_company_research: bool = True

router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.get("/api")
def read_root():
    """API root endpoint"""
    return {"message": "AI Cover Letter Generator API"}

document_parser = DocumentParser()
company_research_service = CompanyResearchService()
llm_service = LLMService()

@router.post("/upload-document", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    db: Session = Depends(get_db)
):
    file_path = UPLOAD_DIR / (file.filename or "unknown_file")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    parsed = document_parser.parse_document(str(file_path), document_type)
    doc = Document(
        filename=file.filename,
        file_path=str(file_path),
        document_type=document_type,
        content=parsed["content"],
        parsed_data=parsed["parsed_data"]
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@router.post("/import-linkedin", response_model=DocumentResponse)
def import_linkedin(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    scraper = LinkedInScraper(email, password)
    profile_data = scraper.scrape_profile()
    doc = Document(
        filename="linkedin_profile.json",
        file_path="",
        document_type="linkedin",
        content=str(profile_data),
        parsed_data=profile_data
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@router.post("/company-research", response_model=CompanyResearchResponse)
def company_research(
    req: CompanyResearchRequest,
    db: Session = Depends(get_db)
):
    info = company_research_service.search_company(req.company_name, req.provider)
    if not info:
        raise HTTPException(status_code=404, detail="Company not found")
    research = CompanyResearch(
        company_name=info["company_name"],
        website=info.get("website"),
        description=info.get("description"),
        industry=info.get("industry"),
        size=info.get("size"),
        location=info.get("location"),
        research_data=info
    )
    db.add(research)
    db.commit()
    db.refresh(research)
    return research

@router.get("/search-providers")
def get_search_providers():
    """Get available search providers for company research"""
    return {
        "available_providers": company_research_service.get_available_providers(),
        "rate_limits": {
            "duckduckgo": "10 requests per minute",
            "google": "100 requests per minute", 
            "tavily": "50 requests per minute",
            "yacy": "30 requests per minute",
            "searxng": "30 requests per minute",
            "brave": "20 requests per minute"
        }
    }

@router.get("/test-tavily")
def test_tavily_api():
    """Test Tavily API key and connection"""
    import os
    tavily_api_key = os.getenv('TAVILY_API_KEY')
    
    if not tavily_api_key:
        return {
            "status": "error",
            "message": "TAVILY_API_KEY not found in environment variables"
        }
    
    # Check API key format
    if not tavily_api_key.startswith('tvly-'):
        return {
            "status": "error", 
            "message": "Invalid API key format - should start with 'tvly-'",
            "key_preview": tavily_api_key[:10] + "..."
        }
    
    # Test the API
    try:
        import requests
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": tavily_api_key,
            "query": "test query",
            "search_depth": "basic",
            "include_answer": False,
            "include_raw_content": False,
            "max_results": 1
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            return {
                "status": "success",
                "message": "Tavily API key is valid and working",
                "key_preview": tavily_api_key[:10] + "..."
            }
        elif response.status_code == 401:
            return {
                "status": "error",
                "message": "Tavily API key is invalid or expired",
                "key_preview": tavily_api_key[:10] + "..."
            }
        elif response.status_code == 403:
            return {
                "status": "error", 
                "message": "Tavily API access forbidden - check account status",
                "key_preview": tavily_api_key[:10] + "..."
            }
        else:
            return {
                "status": "error",
                "message": f"Tavily API returned status {response.status_code}",
                "response": response.text[:200]
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error testing Tavily API: {str(e)}",
            "key_preview": tavily_api_key[:10] + "..."
        }

@router.get("/test-yacy")
def test_yacy_api():
    """Test YaCy API connection"""
    import os
    yacy_url = os.getenv('YACY_URL')
    
    if not yacy_url:
        return {
            "status": "error",
            "message": "YACY_URL not found in environment variables"
        }
    
    try:
        import requests
        params = {
            "query": "test",
            "maximumRecords": 1,
            "resource": "global"
        }
        
        response = requests.get(f"{yacy_url}/yacysearch.json", params=params, timeout=10)
        
        if response.status_code == 200:
            return {
                "status": "success",
                "message": "YaCy API is working",
                "url": yacy_url
            }
        else:
            return {
                "status": "error",
                "message": f"YaCy API returned status {response.status_code}",
                "response": response.text[:200]
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error testing YaCy API: {str(e)}",
            "url": yacy_url
        }

@router.get("/test-searxng")
def test_searxng_api():
    """Test SearXNG API connection"""
    import os
    searxng_url = os.getenv('SEARXNG_URL')
    
    if not searxng_url:
        return {
            "status": "error",
            "message": "SEARXNG_URL not found in environment variables"
        }
    
    try:
        import requests
        params = {
            "q": "test",
            "format": "json",
            "categories": "general",
            "language": "en"
        }
        
        response = requests.get(f"{searxng_url}/search", params=params, timeout=10)
        
        if response.status_code == 200:
            return {
                "status": "success",
                "message": "SearXNG API is working",
                "url": searxng_url
            }
        else:
            return {
                "status": "error",
                "message": f"SearXNG API returned status {response.status_code}",
                "response": response.text[:200]
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error testing SearXNG API: {str(e)}",
            "url": searxng_url
        }

@router.post("/generate-cover-letter", response_model=CoverLetterResponse)
def generate_cover_letter(
    req: CoverLetterRequest,
    db: Session = Depends(get_db)
):
    """Generate a single cover letter using the same RAG+LLM workflow as batch generation."""
    
    # --- RAG+LLM Consistency: Gather all CVs and cover letters (same as batch) ---
    cv_docs = db.query(Document).filter(Document.document_type == "cv").order_by(Document.uploaded_at.desc()).all()
    all_experiences = []
    for idx, doc in enumerate(cv_docs):
        parsed = doc.parsed_data if isinstance(doc.parsed_data, dict) else {}
        exps = parsed.get("experiences", [])
        # Weight: duplicate recent experiences for more weight
        weight = max(1, len(cv_docs) - idx)  # Most recent gets highest weight
        all_experiences.extend(exps * weight)
    
    # Writing style: merge/average from all cover letters, more weight to recent
    cover_docs = db.query(Document).filter(Document.document_type == "cover_letter").order_by(Document.uploaded_at.desc()).all()
    writing_style = {}
    for idx, doc in enumerate(cover_docs):
        parsed = doc.parsed_data if isinstance(doc.parsed_data, dict) else {}
        style = parsed.get("writing_style", {})
        weight = max(1, len(cover_docs) - idx)
        for k, v in style.items():
            if k not in writing_style:
                writing_style[k] = []
            writing_style[k].extend([v] * weight)
    
    # Average/merge writing style fields
    merged_style = {}
    for k, vlist in writing_style.items():
        if all(isinstance(v, (int, float)) for v in vlist):
            merged_style[k] = sum(vlist) / len(vlist)
        elif all(isinstance(v, str) for v in vlist):
            merged_style[k] = max(set(vlist), key=vlist.count)
        else:
            merged_style[k] = vlist[0] if vlist else None
    
    # Handle company research based on user preference
    company_info = {}
    if req.include_company_research:
        # Check if we already have research for this company
        company_research = db.query(CompanyResearch).filter(CompanyResearch.company_name.ilike(f"%{req.company_name}%")).order_by(CompanyResearch.researched_at.desc()).first()
        
        if company_research:
            company_info = company_research.research_data if company_research else {}
        else:
            # Perform new company research
            try:
                research_result = company_research_service.search_company(req.company_name)
                if research_result:
                    # Save the research to database
                    research = CompanyResearch(
                        company_name=research_result.get("company_name", req.company_name),
                        website=research_result.get("website"),
                        description=research_result.get("description"),
                        industry=research_result.get("industry"),
                        size=research_result.get("size"),
                        location=research_result.get("location"),
                        research_data=research_result
                    )
                    db.add(research)
                    db.commit()
                    company_info = research_result
            except Exception as e:
                print(f"Company research failed: {str(e)}")
                # Continue without company research
                company_info = {}
    
    # Generate cover letter using the same logic as batch generation
    generator = CoverLetterGenerator(db, llm_service)
    content = generator.generate_cover_letter(
        job_title=req.job_title,
        company_name=req.company_name,
        job_description=req.job_description,
        company_info=company_info,
        user_experiences=all_experiences,  # Using recency-weighted experiences from all CVs
        writing_style=merged_style,  # Using merged writing style from all cover letters
        tone=req.tone or "professional",
        include_company_research=req.include_company_research or False
    )
    
    cover = CoverLetter(
        job_title=req.job_title,
        company_name=req.company_name,
        job_description=req.job_description,
        generated_content=content,
        company_research=company_info,
        used_experiences=[],  # Empty since we're using CV data directly
        writing_style_analysis=merged_style
    )
    db.add(cover)
    db.commit()
    db.refresh(cover)
    return cover

@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    return db.query(Document).all()

@router.get("/experience", response_model=List[ExperienceResponse])
def list_experience(db: Session = Depends(get_db)):
    return db.query(Experience).order_by(Experience.start_date.desc()).all()

@router.get("/database-contents")
def get_database_contents(db: Session = Depends(get_db)):
    """Get all database contents for debugging and inspection"""
    documents = db.query(Document).all()
    cover_letters = db.query(CoverLetter).all()
    experiences = db.query(Experience).all()
    company_research = db.query(CompanyResearch).all()
    
    return {
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "document_type": doc.document_type,
                "uploaded_at": doc.uploaded_at,
                "content_preview": doc.content[:200] + "..." if doc.content else "No content",
                "parsed_data_keys": list(doc.parsed_data.keys()) if isinstance(doc.parsed_data, dict) else "Not a dict"
            } for doc in documents
        ],
        "cover_letters": [
            {
                "id": cl.id,
                "job_title": cl.job_title,
                "company_name": cl.company_name,
                "generated_at": cl.generated_at,
                "content_preview": cl.generated_content[:200] + "..." if cl.generated_content else "No content"
            } for cl in cover_letters
        ],
        "experiences": [
            {
                "id": exp.id,
                "title": exp.title,
                "company": exp.company,
                "start_date": exp.start_date,
                "end_date": exp.end_date
            } for exp in experiences
        ],
        "company_research": [
            {
                "id": cr.id,
                "company_name": cr.company_name,
                "researched_at": cr.researched_at
            } for cr in company_research
        ]
    }

@router.get("/cv-data")
def get_cv_data(db: Session = Depends(get_db)):
    """Get detailed CV data from uploaded documents"""
    cv_docs = db.query(Document).filter(Document.document_type == "cv").order_by(Document.uploaded_at.desc()).all()
    
    cv_data = []
    for doc in cv_docs:
        parsed_data = doc.parsed_data if isinstance(doc.parsed_data, dict) else {}
        cv_data.append({
            "id": doc.id,
            "filename": doc.filename,
            "uploaded_at": doc.uploaded_at,
            "content_preview": doc.content[:500] + "..." if doc.content else "No content",
            "parsed_data": {
                "personal_info": parsed_data.get("personal_info", {}),
                "education": parsed_data.get("education", []),
                "skills": parsed_data.get("skills", []),
                "summary": parsed_data.get("summary", "")
            }
        })
    
    return {"cv_documents": cv_data}

@router.get("/document/{document_id}")
def get_document_content(document_id: int, db: Session = Depends(get_db)):
    """Get full content of a specific document"""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": doc.id,
        "filename": doc.filename,
        "document_type": doc.document_type,
        "uploaded_at": doc.uploaded_at,
        "content": doc.content,
        "parsed_data": doc.parsed_data
    }

@router.get("/cover-letter/{cover_letter_id}")
def get_cover_letter_content(cover_letter_id: int, db: Session = Depends(get_db)):
    """Get full content of a specific cover letter"""
    cover_letter = db.query(CoverLetter).filter(CoverLetter.id == cover_letter_id).first()
    if not cover_letter:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    
    return {
        "id": cover_letter.id,
        "job_title": cover_letter.job_title,
        "company_name": cover_letter.company_name,
        "generated_at": cover_letter.generated_at,
        "generated_content": cover_letter.generated_content,
        "company_research": cover_letter.company_research
    }

@router.get("/experience/{experience_id}")
def get_experience_content(experience_id: int, db: Session = Depends(get_db)):
    """Get full content of a specific experience"""
    experience = db.query(Experience).filter(Experience.id == experience_id).first()
    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")
    
    return {
        "id": experience.id,
        "title": experience.title,
        "company": experience.company,
        "start_date": experience.start_date,
        "end_date": experience.end_date,
        "description": experience.description,
        "skills": experience.skills,
        "location": experience.location,
        "is_current": experience.is_current,
        "weight": experience.weight,
        "created_at": experience.created_at
    }

@router.get("/company-research/{research_id}")
def get_company_research_content(research_id: int, db: Session = Depends(get_db)):
    """Get full content of a specific company research entry"""
    research = db.query(CompanyResearch).filter(CompanyResearch.id == research_id).first()
    if not research:
        raise HTTPException(status_code=404, detail="Company research not found")
    
    return {
        "id": research.id,
        "company_name": research.company_name,
        "website": research.website,
        "description": research.description,
        "industry": research.industry,
        "size": research.size,
        "location": research.location,
        "researched_at": research.researched_at,
        "research_data": research.research_data
    }

@router.get("/documents-by-type/{document_type}")
def get_documents_by_type(document_type: str, db: Session = Depends(get_db)):
    """Get all documents of a specific type with full content"""
    docs = db.query(Document).filter(Document.document_type == document_type).order_by(Document.uploaded_at.desc()).all()
    
    return {
        "document_type": document_type,
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "uploaded_at": doc.uploaded_at,
                "content": doc.content,
                "parsed_data": doc.parsed_data
            } for doc in docs
        ]
    }

@router.get("/llm-config")
def get_llm_config():
    """Get current LLM service configuration"""
    return {"base_url": llm_service.base_url, "model": llm_service.model}

@router.post("/refresh-llm-config")
def refresh_llm_config():
    """Refresh LLM service configuration from environment variables"""
    try:
        llm_service.refresh_config()
        return {"message": "LLM configuration refreshed successfully", "config": {"base_url": llm_service.base_url, "model": llm_service.model}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh LLM config: {str(e)}")

@router.get("/export-formats")
def get_export_formats():
    """Get available export formats"""
    exporter = DocumentExporter()
    return exporter.get_available_formats()

@router.post("/export-cover-letter/{cover_letter_id}")
def export_cover_letter(cover_letter_id: int, format: str = "pdf", db: Session = Depends(get_db)):
    """Export a cover letter to the specified format"""
    # Get the cover letter
    cover_letter = db.query(CoverLetter).filter(CoverLetter.id == cover_letter_id).first()
    if not cover_letter:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    
    # Prepare data for export
    cover_letter_data = {
        "job_title": cover_letter.job_title,
        "company_name": cover_letter.company_name,
        "job_description": cover_letter.job_description,
        "generated_content": cover_letter.generated_content,
        "generated_at": cover_letter.generated_at.isoformat() if cover_letter.generated_at else None
    }
    
    # Export to specified format
    exporter = DocumentExporter()
    try:
        if format.lower() == "pdf":
            filepath = exporter.export_to_pdf(cover_letter_data)
        elif format.lower() == "docx":
            filepath = exporter.export_to_docx(cover_letter_data)
        elif format.lower() == "txt":
            filepath = exporter.export_to_txt(cover_letter_data)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
        
        # Return file info
        filename = os.path.basename(filepath)
        return {
            "message": f"Cover letter exported successfully to {format.upper()}",
            "filename": filename,
            "filepath": filepath,
            "format": format
        }
        
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"Export format not available: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.delete("/clear-database")
def clear_database(db: Session = Depends(get_db)):
    """Clear all data from the database (use with caution!)"""
    try:
        # Delete all data from all tables
        db.query(CoverLetter).delete()
        db.query(CompanyResearch).delete()
        db.query(Experience).delete()
        db.query(Document).delete()
        db.commit()
        
        return {
            "message": "Database cleared successfully",
            "deleted_tables": ["cover_letters", "company_research", "experiences", "documents"]
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear database: {str(e)}")

@router.delete("/delete-document/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a specific document"""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Delete associated experiences first
        db.query(Experience).filter(Experience.document_id == document_id).delete()
        
        # Delete the document
        db.delete(doc)
        db.commit()
        
        return {"message": f"Document '{doc.filename}' deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@router.delete("/delete-cover_letter/{cover_letter_id}")
def delete_cover_letter(cover_letter_id: int, db: Session = Depends(get_db)):
    """Delete a specific cover letter"""
    cover_letter = db.query(CoverLetter).filter(CoverLetter.id == cover_letter_id).first()
    if not cover_letter:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    
    try:
        db.delete(cover_letter)
        db.commit()
        
        return {"message": f"Cover letter for {cover_letter.job_title} at {cover_letter.company_name} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete cover letter: {str(e)}")

@router.delete("/delete-experience/{experience_id}")
def delete_experience(experience_id: int, db: Session = Depends(get_db)):
    """Delete a specific experience"""
    experience = db.query(Experience).filter(Experience.id == experience_id).first()
    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")
    
    try:
        db.delete(experience)
        db.commit()
        
        return {"message": f"Experience '{experience.title}' at {experience.company} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete experience: {str(e)}")

@router.delete("/delete-company_research/{research_id}")
def delete_company_research(research_id: int, db: Session = Depends(get_db)):
    """Delete a specific company research entry"""
    research = db.query(CompanyResearch).filter(CompanyResearch.id == research_id).first()
    if not research:
        raise HTTPException(status_code=404, detail="Company research not found")
    
    try:
        db.delete(research)
        db.commit()
        
        return {"message": f"Company research for '{research.company_name}' deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete company research: {str(e)}")

@router.put("/update-cover-letter/{cover_letter_id}")
def update_cover_letter(cover_letter_id: int, req: dict, db: Session = Depends(get_db)):
    """Update a specific cover letter's content"""
    cover_letter = db.query(CoverLetter).filter(CoverLetter.id == cover_letter_id).first()
    if not cover_letter:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    
    try:
        cover_letter.generated_content = req.get("generated_content", cover_letter.generated_content)
        db.commit()
        db.refresh(cover_letter)
        
        return {
            "message": "Cover letter updated successfully",
            "id": cover_letter.id,
            "job_title": cover_letter.job_title,
            "company_name": cover_letter.company_name
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update cover letter: {str(e)}")

@router.post("/create-cover-letter")
def create_cover_letter(req: dict, db: Session = Depends(get_db)):
    """Create a new cover letter manually"""
    try:
        cover_letter = CoverLetter(
            job_title=req.get("job_title", "Unknown Position"),
            company_name=req.get("company_name", "Unknown Company"),
            job_description=req.get("job_description", ""),
            generated_content=req.get("generated_content", ""),
            generated_at=datetime.now()
        )
        db.add(cover_letter)
        db.commit()
        db.refresh(cover_letter)
        
        return {
            "message": "Cover letter created successfully",
            "id": cover_letter.id,
            "job_title": cover_letter.job_title,
            "company_name": cover_letter.company_name
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create cover letter: {str(e)}")

@router.post("/upload-multiple-documents")
def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    document_types: List[str] = Form(...),
    db: Session = Depends(get_db)
):
    """Upload multiple documents at once with specified types"""
    if len(files) != len(document_types):
        raise HTTPException(status_code=400, detail="Number of files must match number of document types")
    
    uploaded_docs = []
    
    for i, (file, document_type) in enumerate(zip(files, document_types)):
        try:
            # Create unique filename to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            safe_filename = f"{timestamp}_{i}_{file.filename or 'unknown_file'}"
            file_path = UPLOAD_DIR / safe_filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Parse document
            parsed = document_parser.parse_document(str(file_path), document_type)
            
            # Create document record
            doc = Document(
                filename=file.filename or f"document_{i}",
                file_path=str(file_path),
                document_type=document_type,
                content=parsed["content"],
                parsed_data=parsed["parsed_data"]
            )
            db.add(doc)
            uploaded_docs.append(doc)
            
        except Exception as e:
            # Rollback on error
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to upload {file.filename}: {str(e)}")
    
    # Commit all documents
    db.commit()
    
    # Refresh all documents to get their IDs
    for doc in uploaded_docs:
        db.refresh(doc)
    
    return {
        "message": f"Successfully uploaded {len(uploaded_docs)} documents",
        "uploaded_documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "document_type": doc.document_type,
                "uploaded_at": doc.uploaded_at
            } for doc in uploaded_docs
        ]
    }

@router.post("/chat-with-cover-letter")
def chat_with_cover_letter(
    req: ChatRequest,
    db: Session = Depends(get_db)
):
    """Chat with the LLM to modify a cover letter"""
    # Get the cover letter
    cover_letter = db.query(CoverLetter).filter(CoverLetter.id == req.cover_letter_id).first()
    if not cover_letter:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    
    try:
        # Create a chat prompt that includes the current cover letter content
        chat_prompt = f"""
You are an AI assistant helping to edit a cover letter. Here's the current cover letter:

{cover_letter.generated_content}

The user wants to make changes. Here's their request: {req.message}

CRITICAL FORMATTING INSTRUCTIONS:
1. Maintain the EXACT same writing style, tone, and language as the original
2. PRESERVE ALL FORMATTING: Keep the exact same paragraph structure, line breaks, spacing, and indentation
3. Only change what the user specifically requests
4. Output ONLY the complete revised cover letter, and NOTHING else. Do NOT add any extra commentary, instructions, or questions
5. If they're asking questions, answer them without modifying the cover letter
6. Preserve the original voice and personality of the writer
7. Maintain proper spacing between paragraphs and sections
8. Keep the same signature format and spacing
9. DO NOT normalize or change any whitespace - keep exactly as it appears in the original
10. If the original has double line breaks between paragraphs, keep them
11. If the original has single line breaks, keep them
12. Preserve any indentation or special formatting

Respond with ONLY the revised cover letter if changes are requested.
"""
        
        # Get response from LLM
        response = llm_service.generate_text(chat_prompt, max_tokens=1024, temperature=0.7)
        if not response:
            raise HTTPException(status_code=500, detail="Failed to generate response from LLM")
        
        # Improved extraction: Preserve formatting and spacing
        updated_content = None
        if "Dear" in response:
            start_index = response.find("Dear")
            # Find the end of the cover letter (look for common closings)
            end_phrases = ["Sincerely,", "Best regards,", "Thank you,", "Yours truly,", "Respectfully,"]
            end_index = -1
            
            for phrase in end_phrases:
                phrase_index = response.find(phrase, start_index)
                if phrase_index != -1:
                    # Find the end of the signature (look for the end of the document)
                    # Take everything up to the closing phrase plus a few lines for signature
                    lines_after = response[phrase_index:].split('\n')
                    signature_lines = 0
                    for i, line in enumerate(lines_after):
                        if i > 0 and line.strip() == "":
                            # Found a blank line, this might be the end
                            signature_lines = i
                            break
                        elif i >= 3:  # Take at most 3 lines after closing
                            signature_lines = i + 1
                            break
                    
                    end_index = phrase_index + len('\n'.join(lines_after[:signature_lines]))
                    break
            
            if end_index == -1:
                # If no closing found, take everything from "Dear" onwards
                end_index = len(response)
            
            if start_index != -1 and end_index > start_index:
                # Extract the cover letter body with preserved formatting
                body = response[start_index:end_index]
                
                # Clean up any trailing meta/instruction lines more carefully
                lines = body.split('\n')
                cleaned_lines = []
                for line in lines:
                    line_lower = line.strip().lower()
                    # Only remove obvious instruction lines, be more conservative
                    if (line_lower.startswith("please let me know") or 
                        line_lower.startswith("if you'd like") or
                        line_lower.startswith("feel free to") or
                        "further changes" in line_lower and "let me know" in line_lower):
                        break
                    cleaned_lines.append(line)
                
                # Join lines while preserving original formatting and normalize line endings
                updated_content = '\n'.join(cleaned_lines).rstrip()
                
                # Ensure consistent line endings and preserve paragraph spacing
                updated_content = _preserve_formatting(updated_content)
                
                # Only update if content actually changed
                if updated_content != cover_letter.generated_content:
                    cover_letter.generated_content = updated_content
                    db.commit()
        
        return {
            "response": response,
            "updated_content": updated_content,
            "cover_letter_id": cover_letter.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.post("/batch-cover-letters")
def batch_cover_letters(
    req: BatchCoverLetterRequest,
    db: Session = Depends(get_db)
):
    """Generate cover letters for multiple companies from websites, using recency-weighted CVs and cover letters for context."""
    results = []
    
    # Process websites to extract job information
    job_info_list = []
    for website in req.websites:
        try:
            job_info = extract_job_info_from_website(website)
            if job_info:
                job_info_list.append(job_info)
        except Exception as e:
            results.append({
                "website": website,
                "error": f"Failed to extract job info: {str(e)}"
            })
    for company in req.companies:
        job_info_list.append({
            "company_name": company,
            "job_title": req.job_title,
            "job_description": req.job_description,
            "website": None
        })
    # --- RAG+LLM Consistency: Gather all CVs and cover letters ---
    cv_docs = db.query(Document).filter(Document.document_type == "cv").order_by(Document.uploaded_at.desc()).all()
    all_experiences = []
    for idx, doc in enumerate(cv_docs):
        parsed = doc.parsed_data if isinstance(doc.parsed_data, dict) else {}
        exps = parsed.get("experiences", [])
        # Weight: duplicate recent experiences for more weight
        weight = max(1, len(cv_docs) - idx)  # Most recent gets highest weight
        all_experiences.extend(exps * weight)
    # Writing style: merge/average from all cover letters, more weight to recent
    cover_docs = db.query(Document).filter(Document.document_type == "cover_letter").order_by(Document.uploaded_at.desc()).all()
    writing_style = {}
    for idx, doc in enumerate(cover_docs):
        parsed = doc.parsed_data if isinstance(doc.parsed_data, dict) else {}
        style = parsed.get("writing_style", {})
        weight = max(1, len(cover_docs) - idx)
        for k, v in style.items():
            if k not in writing_style:
                writing_style[k] = []
            writing_style[k].extend([v] * weight)
    # Average/merge writing style fields
    merged_style = {}
    for k, vlist in writing_style.items():
        if all(isinstance(v, (int, float)) for v in vlist):
            merged_style[k] = sum(vlist) / len(vlist)
        elif all(isinstance(v, str) for v in vlist):
            merged_style[k] = max(set(vlist), key=vlist.count)
        else:
            merged_style[k] = vlist[0] if vlist else None
    # --- Generate cover letters for each job ---
    import time
    for i, job_info in enumerate(job_info_list):
        try:
            if i > 0:
                time.sleep(req.delay_seconds)
            llm_service = LLMService()
            generator = CoverLetterGenerator(db, llm_service)
            company_name = job_info["company_name"] or "the company"
            job_title = job_info["job_title"] or req.job_title or "the position"
            job_description = job_info["job_description"] or req.job_description or ""
            # Handle company research for batch generation
            company_info = {}
            if req.include_company_research and job_info["company_name"]:
                try:
                    research_result = company_research_service.search_company(job_info["company_name"])
                    if research_result:
                        # Save the research to database
                        research = CompanyResearch(
                            company_name=research_result.get("company_name", job_info["company_name"]),
                            website=research_result.get("website"),
                            description=research_result.get("description"),
                            industry=research_result.get("industry"),
                            size=research_result.get("size"),
                            location=research_result.get("location"),
                            research_data=research_result
                        )
                        db.add(research)
                        db.commit()
                        company_info = research_result
                except Exception as e:
                    print(f"Company research failed for {job_info['company_name']}: {str(e)}")
                    # Continue without company research
            
            cover_letter_content = generator.generate_cover_letter(
                company_name=company_name,
                job_title=job_title,
                job_description=job_description,
                company_info=company_info,
                user_experiences=all_experiences,
                writing_style=merged_style,
                tone=req.tone,
                include_company_research=req.include_company_research
            )
            cover_letter = CoverLetter(
                job_title=job_info["job_title"],
                company_name=job_info["company_name"],
                job_description=job_info["job_description"],
                generated_content=cover_letter_content,
                company_research=company_info,  # Save the company research data
                generated_at=datetime.now()
            )
            db.add(cover_letter)
            db.commit()
            results.append({
                "company": job_info["company_name"],
                "job_title": job_info["job_title"],
                "website": job_info.get("website"),
                "cover_letter_id": cover_letter.id,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "company": job_info.get("company_name", "Unknown"),
                "website": job_info.get("website"),
                "error": str(e),
                "status": "error"
            })
    return {
        "results": results,
        "total_processed": len(job_info_list),
        "successful": len([r for r in results if r.get("status") == "success"]),
        "failed": len([r for r in results if r.get("status") == "error"])
    }

def extract_job_info_from_website(url: str) -> dict:
    """Extract job information from a website URL using requests first, then Selenium as fallback"""
    job_info = {
        "website": url,
        "company_name": None,
        "job_title": None,
        "job_description": ""
    }
    
    # Try requests first (faster)
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        return _parse_job_info_from_soup(soup, job_info)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code in [403, 429, 503]:  # Blocked or rate limited
            # Fall back to Selenium
            return _extract_with_selenium(url, job_info)
        else:
            raise Exception(f"HTTP error {e.response.status_code} for {url}: {str(e)}")
    except Exception as e:
        # For other errors (timeout, connection, etc.), try Selenium
        return _extract_with_selenium(url, job_info)

def _extract_with_selenium(url: str, job_info: dict) -> dict:
    """Extract job information using Selenium (headless browser)"""
    driver = None
    try:
        # Setup Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set page load timeout
        driver.set_page_load_timeout(30)
        
        # Navigate to the URL
        driver.get(url)
        
        # Wait a bit for dynamic content to load
        import time
        time.sleep(3)
        
        # Get the page source
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        return _parse_job_info_from_soup(soup, job_info)
        
    except WebDriverException as e:
        raise Exception(f"Selenium failed for {url}: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to extract job info from {url}: {str(e)}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def _parse_job_info_from_soup(soup: BeautifulSoup, job_info: dict) -> dict:
    """Parse job information from BeautifulSoup object"""
    
    # Try to extract company name (Seek-specific selectors first)
    company_selectors = [
        # Seek.com.au specific - company name near job title
        '[data-automation="job-details-company-name"]',
        '.job-details-company-name',
        '[data-testid="job-details-company-name"]',
        # Look for company name after job title (common Seek pattern)
        'h1 + div',  # Direct sibling after h1 (job title)
        'h1 ~ div',  # Any sibling div after h1
        '.job-title + div',  # Direct sibling after job title
        '.job-title ~ div',  # Any sibling div after job title
        '[data-automation="job-details-title"] + div',  # After Seek job title
        '[data-automation="job-details-title"] ~ div',  # Any div after Seek job title
        # General selectors
        '[data-company]',
        '.company-name',
        '.employer-name',
        '[class*="company"]',
        '[class*="employer"]',
        '[data-testid*="company"]',
        '.job-company',
        '.employer',
        # Additional Seek patterns
        'a[href*="/company/"]',
        '.job-company-link',
        # Look for company links near the top
        '.job-header a[href*="/company/"]',
        '.job-details-header a[href*="/company/"]'
    ]
    
    for selector in company_selectors:
        company_elem = soup.select_one(selector)
        if company_elem:
            company_text = company_elem.get_text(separator=' ', strip=True)
            # Remove anything after the company name (e.g., numbers, reviews, View all jobs, etc.)
            company_name = re.split(r'\d|reviews|View all jobs|\·|\||\*|\(|\)|\[|\]|\n|\r', company_text)[0].strip()
            # Remove trailing punctuation or symbols
            company_name = re.sub(r'[\s\-\|\·\*\.,;:]+$', '', company_name)
            # Remove leading/trailing whitespace
            company_name = company_name.strip()
            if company_name:
                job_info["company_name"] = company_name
                break
    
    # Try to extract job title (Seek-specific selectors first)
    title_selectors = [
        # Seek.com.au specific
        '[data-automation="job-details-title"]',
        '.job-details-title',
        '[data-testid="job-details-title"]',
        # General selectors
        'h1',
        '.job-title',
        '.position-title',
        '[class*="title"]',
        '[data-job-title]',
        '[data-testid*="title"]',
        '.job-header h1',
        '.job-name',
        # Additional Seek patterns
        '.job-title h1',
        '.job-header .title'
    ]
    
    for selector in title_selectors:
        title_elem = soup.select_one(selector)
        if title_elem:
            job_info["job_title"] = title_elem.get_text(strip=True)
            break
    
    # Try to extract job description (Seek-specific selectors first)
    desc_selectors = [
        # Seek.com.au specific
        '[data-automation="job-details-description"]',
        '.job-details-description',
        '[data-testid="job-details-description"]',
        # General selectors
        '.job-description',
        '.position-description',
        '[class*="description"]',
        '[class*="details"]',
        '.job-details',
        '[data-testid*="description"]',
        '.job-content',
        '.job-body',
        # Additional Seek patterns
        '.job-description-content',
        '.job-details-content'
    ]
    
    for selector in desc_selectors:
        desc_elem = soup.select_one(selector)
        if desc_elem:
            job_info["job_description"] = desc_elem.get_text(strip=True)
            break
    
    # If no specific description found, try to get main content
    if not job_info["job_description"]:
        main_content = soup.find('main') or soup.find('body')
        if main_content:
            # Remove script and style elements
            for script in main_content(["script", "style"]):
                script.decompose()
            job_info["job_description"] = main_content.get_text(strip=True)[:2000]  # Limit length
    
    # Clean up extracted text
    if job_info["company_name"]:
        job_info["company_name"] = re.sub(r'\s+', ' ', job_info["company_name"]).strip()
    if job_info["job_title"]:
        job_info["job_title"] = re.sub(r'\s+', ' ', job_info["job_title"]).strip()
    if job_info["job_description"]:
        job_info["job_description"] = re.sub(r'\s+', ' ', job_info["job_description"]).strip()
    
    return job_info 

def _preserve_formatting(content: str) -> str:
    """Preserve formatting and normalize line endings while maintaining structure"""
    if not content:
        return content
    
    # Normalize line endings to \n
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    
    # Split into lines and preserve empty lines (paragraph breaks)
    lines = content.split('\n')
    
    # Remove trailing empty lines but preserve internal empty lines
    while lines and lines[-1].strip() == '':
        lines.pop()
    
    # Join back with \n, preserving internal empty lines
    return '\n'.join(lines) 