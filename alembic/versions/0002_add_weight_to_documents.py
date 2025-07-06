"""Add weight column to documents table

Revision ID: 0002_add_weight_to_documents
Revises: 0001_initial
Create Date: 2024-12-19 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_add_weight_to_documents'
down_revision = '0001_initial'
branch_labels = None
depends_on = None

def upgrade():
    # Add weight column to documents table
    op.add_column('documents', sa.Column('weight', sa.Float(), nullable=True, default=1.0))
    
    # Update existing documents to have default weight
    op.execute("UPDATE documents SET weight = 1.0 WHERE weight IS NULL")
    
    # Make the column not nullable after setting default values
    op.alter_column('documents', 'weight', nullable=False)

def downgrade():
    # Remove weight column from documents table
    op.drop_column('documents', 'weight') 