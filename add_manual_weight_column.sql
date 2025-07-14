-- Manual Weight Feature Database Migration
-- Run this SQL script in your PostgreSQL database to add the manual_weight column

-- Step 1: Add the manual_weight column with default value
ALTER TABLE documents ADD COLUMN IF NOT EXISTS manual_weight FLOAT DEFAULT 1.0;

-- Step 2: Set default values for any existing records that might be NULL
UPDATE documents SET manual_weight = 1.0 WHERE manual_weight IS NULL;

-- Step 3: Make the column non-nullable (optional, but recommended)
ALTER TABLE documents ALTER COLUMN manual_weight SET NOT NULL;

-- Step 4: Add indexes for performance
CREATE INDEX IF NOT EXISTS ix_documents_manual_weight ON documents (manual_weight);
CREATE INDEX IF NOT EXISTS ix_documents_type_manual_weight ON documents (document_type, manual_weight);

-- Verify the changes
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'documents' AND column_name = 'manual_weight';

-- Show sample data
SELECT id, filename, document_type, manual_weight 
FROM documents 
LIMIT 5;