from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import datetime

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False, index=True)  # Index for filename searches
    file_path = Column(String, nullable=False)
    document_type = Column(String, nullable=False, index=True)  # Index for type filtering
    content = Column(Text, nullable=False)
    parsed_data = Column(JSON)  # Structured data from parsing
    uploaded_at = Column(DateTime, default=func.now(), index=True)  # Index for recency queries
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    weight = Column(Float, default=1.0, index=True)  # Index for RAG ranking
    
    experiences = relationship("Experience", back_populates="document")

class Experience(Base):
    __tablename__ = "experiences"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), index=True)  # Index for joins
    title = Column(String, nullable=False, index=True)  # Index for job title searches
    company = Column(String, nullable=False, index=True)  # Index for company searches
    start_date = Column(DateTime, nullable=False, index=True)  # Index for date range queries
    end_date = Column(DateTime, nullable=True, index=True)  # Index for current position queries
    description = Column(Text, nullable=False)
    skills = Column(JSON)  # List of skills
    location = Column(String)
    is_current = Column(Boolean, default=False, index=True)  # Index for current position queries
    weight = Column(Float, default=1.0, index=True)  # Index for weight-based sorting
    created_at = Column(DateTime, default=func.now())
    
    document = relationship("Document", back_populates="experiences")

class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    category = Column(String)  # technical, soft, language, etc.
    proficiency_level = Column(String)  # beginner, intermediate, expert
    first_mentioned = Column(DateTime, default=func.now())
    last_used = Column(DateTime, default=func.now())
    usage_count = Column(Integer, default=1)

class CoverLetter(Base):
    __tablename__ = "cover_letters"
    
    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String, nullable=False, index=True)  # Index for job title searches
    company_name = Column(String, nullable=False, index=True)  # Index for company searches
    job_description = Column(Text, nullable=False)
    generated_content = Column(Text, nullable=False)
    company_research = Column(JSON)  # Company information from research
    used_experiences = Column(JSON)  # Which experiences were highlighted
    writing_style_analysis = Column(JSON)  # Analysis of user's writing style
    generated_at = Column(DateTime, default=func.now(), index=True)  # Index for date queries
    rating = Column(Integer, index=True)  # Index for rating-based queries

class CompanyResearch(Base):
    __tablename__ = "company_research"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False, index=True)  # Index for company name searches
    website = Column(String)
    description = Column(Text)
    industry = Column(String, index=True)  # Index for industry searches
    size = Column(String)
    location = Column(String)
    research_data = Column(JSON)  # Raw research data
    researched_at = Column(DateTime, default=func.now(), index=True)  # Index for recency