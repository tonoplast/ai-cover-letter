"""Add manual weight to documents

Revision ID: 0004
Revises: 0003
Create Date: 2025-01-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade():
    # Add manual_weight column to documents table
    op.add_column('documents', sa.Column('manual_weight', sa.Float(), nullable=True, default=1.0))
    
    # Set default value for existing records
    op.execute("UPDATE documents SET manual_weight = 1.0 WHERE manual_weight IS NULL")
    
    # Make the column non-nullable after setting defaults
    op.alter_column('documents', 'manual_weight', nullable=False)
    
    # Add index for manual_weight
    op.create_index('ix_documents_manual_weight', 'documents', ['manual_weight'])
    
    # Add composite index for type and manual weight
    op.create_index('ix_documents_type_manual_weight', 'documents', ['document_type', 'manual_weight'])


def downgrade():
    # Drop indexes first
    op.drop_index('ix_documents_type_manual_weight')
    op.drop_index('ix_documents_manual_weight')
    
    # Drop the column
    op.drop_column('documents', 'manual_weight')