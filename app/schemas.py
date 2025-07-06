from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime

class DocumentUpload(BaseModel):
    filename: str
    document_type: str

class DocumentResponse(BaseModel):
    id: int
    filename: str
    document_type: str
    uploaded_at: datetime
    last_updated: datetime
    
    class Config:
        from_attributes = True

class ExperienceCreate(BaseModel):
    title: str
    company: str
    start_date: datetime
    end_date: Optional[datetime] = None
    description: str
    skills: Optional[List[str]] = []
    location: Optional[str] = None
    is_current: bool = False

class ExperienceResponse(BaseModel):
    id: int
    title: str
    company: str
    start_date: datetime
    end_date: Optional[datetime]
    description: str
    skills: List[str]
    location: Optional[str]
    is_current: bool
    weight: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class CoverLetterRequest(BaseModel):
    job_title: str
    company_name: str
    job_description: str
    job_posting_url: Optional[HttpUrl] = None
    focus_areas: Optional[List[str]] = []
    tone: Optional[str] = "professional"  # professional, enthusiastic, formal, casual
    include_company_research: Optional[bool] = True  # Whether to include company research in the cover letter
    research_provider: Optional[str] = None  # Provider for company research (tavily, google, brave, etc.)
    research_country: Optional[str] = None  # Country to focus search on (e.g., "Australia", "United States", etc.)

class CoverLetterResponse(BaseModel):
    id: int
    job_title: str
    company_name: str
    generated_content: str
    company_research: Dict[str, Any]
    used_experiences: List[int]
    generated_at: datetime
    
    class Config:
        from_attributes = True

class LinkedInImport(BaseModel):
    email: str
    password: str

class CompanyResearchRequest(BaseModel):
    company_name: str
    website: Optional[HttpUrl] = None
    provider: Optional[str] = None  # "duckduckgo", "google", "tavily", or None for auto

class CompanyResearchResponse(BaseModel):
    id: int
    company_name: str
    website: Optional[str]
    description: Optional[str]
    industry: Optional[str]
    size: Optional[str]
    location: Optional[str]
    researched_at: datetime
    
    class Config:
        from_attributes = True

class SkillResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    proficiency_level: Optional[str]
    first_mentioned: datetime
    last_used: datetime
    usage_count: int
    
    class Config:
        from_attributes = True 