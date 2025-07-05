"""Initial migration

Revision ID: 0001_initial
Revises: 
Create Date: 2024-05-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('documents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('document_type', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('parsed_data', sa.JSON()),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.Column('last_updated', sa.DateTime(), nullable=False)
    )
    op.create_table('experiences',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('document_id', sa.Integer(), sa.ForeignKey('documents.id')),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('company', sa.String(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime()),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('skills', sa.JSON()),
        sa.Column('location', sa.String()),
        sa.Column('is_current', sa.Boolean(), default=False),
        sa.Column('weight', sa.Float(), default=1.0),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )
    op.create_table('skills',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('category', sa.String()),
        sa.Column('proficiency_level', sa.String()),
        sa.Column('first_mentioned', sa.DateTime(), nullable=False),
        sa.Column('last_used', sa.DateTime(), nullable=False),
        sa.Column('usage_count', sa.Integer(), default=1)
    )
    op.create_table('cover_letters',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('job_title', sa.String(), nullable=False),
        sa.Column('company_name', sa.String(), nullable=False),
        sa.Column('job_description', sa.Text(), nullable=False),
        sa.Column('generated_content', sa.Text(), nullable=False),
        sa.Column('company_research', sa.JSON()),
        sa.Column('used_experiences', sa.JSON()),
        sa.Column('writing_style_analysis', sa.JSON()),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.Column('rating', sa.Integer())
    )
    op.create_table('company_research',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('company_name', sa.String(), nullable=False),
        sa.Column('website', sa.String()),
        sa.Column('description', sa.Text()),
        sa.Column('industry', sa.String()),
        sa.Column('size', sa.String()),
        sa.Column('location', sa.String()),
        sa.Column('research_data', sa.JSON()),
        sa.Column('researched_at', sa.DateTime(), nullable=False)
    )

def downgrade():
    op.drop_table('company_research')
    op.drop_table('cover_letters')
    op.drop_table('skills')
    op.drop_table('experiences')
    op.drop_table('documents') 