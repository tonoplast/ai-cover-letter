from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import datetime

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    document_type = Column(String, nullable=False)  # cv, cover_letter, linkedin, other
    content = Column(Text, nullable=False)
    parsed_data = Column(JSON)  # Structured data from parsing
    uploaded_at = Column(DateTime, default=func.now())
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    
    experiences = relationship("Experience", back_populates="document")

class Experience(Base):
    __tablename__ = "experiences"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)  # Null for current position
    description = Column(Text, nullable=False)
    skills = Column(JSON)  # List of skills
    location = Column(String)
    is_current = Column(Boolean, default=False)
    weight = Column(Float, default=1.0)  # Temporal weight for recent experience
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
    job_title = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    job_description = Column(Text, nullable=False)
    generated_content = Column(Text, nullable=False)
    company_research = Column(JSON)  # Company information from research
    used_experiences = Column(JSON)  # Which experiences were highlighted
    writing_style_analysis = Column(JSON)  # Analysis of user's writing style
    generated_at = Column(DateTime, default=func.now())
    rating = Column(Integer)  # User rating of the generated letter (1-5)

class CompanyResearch(Base):
    __tablename__ = "company_research"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    website = Column(String)
    description = Column(Text)
    industry = Column(String)
    size = Column(String)
    location = Column(String)
    research_data = Column(JSON)  # Raw research data
    researched_at = Column(DateTime, default=func.now()) 