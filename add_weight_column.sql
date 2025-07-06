-- Add weight column to documents table
-- Run this script directly in your PostgreSQL database

-- Add the weight column with a default value
ALTER TABLE documents ADD COLUMN IF NOT EXISTS weight REAL DEFAULT 1.0;

-- Update any existing NULL values to the default
UPDATE documents SET weight = 1.0 WHERE weight IS NULL;

-- Make the column NOT NULL after setting default values
ALTER TABLE documents ALTER COLUMN weight SET NOT NULL;

-- Verify the column was added
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'documents' AND column_name = 'weight'; 