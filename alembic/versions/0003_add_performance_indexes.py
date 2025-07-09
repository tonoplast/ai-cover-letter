"""Add performance indexes

Revision ID: 0003
Revises: 0002
Create Date: 2025-01-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    # Add indexes for Documents table
    op.create_index('ix_documents_filename', 'documents', ['filename'])
    op.create_index('ix_documents_document_type', 'documents', ['document_type'])
    op.create_index('ix_documents_uploaded_at', 'documents', ['uploaded_at'])
    op.create_index('ix_documents_weight', 'documents', ['weight'])
    
    # Add composite index for common query patterns
    op.create_index('ix_documents_type_uploaded', 'documents', ['document_type', 'uploaded_at'])
    op.create_index('ix_documents_type_weight', 'documents', ['document_type', 'weight'])
    
    # Add indexes for Experiences table
    op.create_index('ix_experiences_document_id', 'experiences', ['document_id'])
    op.create_index('ix_experiences_title', 'experiences', ['title'])
    op.create_index('ix_experiences_company', 'experiences', ['company'])
    op.create_index('ix_experiences_start_date', 'experiences', ['start_date'])
    op.create_index('ix_experiences_end_date', 'experiences', ['end_date'])
    op.create_index('ix_experiences_is_current', 'experiences', ['is_current'])
    op.create_index('ix_experiences_weight', 'experiences', ['weight'])
    
    # Add composite indexes for Experiences
    op.create_index('ix_experiences_current_start_date', 'experiences', ['is_current', 'start_date'])
    
    # Add indexes for CoverLetters table
    op.create_index('ix_cover_letters_job_title', 'cover_letters', ['job_title'])
    op.create_index('ix_cover_letters_company_name', 'cover_letters', ['company_name'])
    op.create_index('ix_cover_letters_generated_at', 'cover_letters', ['generated_at'])
    op.create_index('ix_cover_letters_rating', 'cover_letters', ['rating'])
    
    # Add composite index for cover letters
    op.create_index('ix_cover_letters_company_generated', 'cover_letters', ['company_name', 'generated_at'])
    
    # Add indexes for CompanyResearch table
    op.create_index('ix_company_research_company_name', 'company_research', ['company_name'])
    op.create_index('ix_company_research_industry', 'company_research', ['industry'])
    op.create_index('ix_company_research_researched_at', 'company_research', ['researched_at'])
    
    # Add composite index for company research
    op.create_index('ix_company_research_name_researched', 'company_research', ['company_name', 'researched_at'])


def downgrade():
    # Drop all the indexes we created
    op.drop_index('ix_company_research_name_researched')
    op.drop_index('ix_company_research_researched_at')
    op.drop_index('ix_company_research_industry')
    op.drop_index('ix_company_research_company_name')
    
    op.drop_index('ix_cover_letters_company_generated')
    op.drop_index('ix_cover_letters_rating')
    op.drop_index('ix_cover_letters_generated_at')
    op.drop_index('ix_cover_letters_company_name')
    op.drop_index('ix_cover_letters_job_title')
    
    op.drop_index('ix_experiences_current_start_date')
    op.drop_index('ix_experiences_weight')
    op.drop_index('ix_experiences_is_current')
    op.drop_index('ix_experiences_end_date')
    op.drop_index('ix_experiences_start_date')
    op.drop_index('ix_experiences_company')
    op.drop_index('ix_experiences_title')
    op.drop_index('ix_experiences_document_id')
    
    op.drop_index('ix_documents_type_weight')
    op.drop_index('ix_documents_type_uploaded')
    op.drop_index('ix_documents_weight')
    op.drop_index('ix_documents_uploaded_at')
    op.drop_index('ix_documents_document_type')
    op.drop_index('ix_documents_filename')