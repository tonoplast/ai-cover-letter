# Manual Weight Feature - Database Migration Instructions

## Problem
The manual weight feature has been implemented, but the database column `manual_weight` doesn't exist yet, causing this error:
```
column documents.manual_weight does not exist
```

## Solution Options

### Option 1: Run SQL Migration Script (Recommended)

1. **Connect to your PostgreSQL database** using your preferred method:
   - pgAdmin (GUI tool)
   - psql command line
   - Database extension in VS Code
   - Any other PostgreSQL client

2. **Run the migration script**:
   ```bash
   # If using psql command line:
   psql -U your_username -d your_database_name -f add_manual_weight_column.sql
   
   # Or copy and paste the contents of add_manual_weight_column.sql into your database client
   ```

3. **Restart your application** to pick up the new column

4. **Uncomment the model field**:
   In `app/models.py`, change:
   ```python
   # manual_weight = Column(Float, default=1.0, index=True)  # User-set manual weight multiplier
   ```
   To:
   ```python
   manual_weight = Column(Float, default=1.0, index=True)  # User-set manual weight multiplier
   ```

### Option 2: Manual SQL Commands

Run these SQL commands in your PostgreSQL database:

```sql
-- Add the column
ALTER TABLE documents ADD COLUMN manual_weight FLOAT DEFAULT 1.0;

-- Set defaults for existing records
UPDATE documents SET manual_weight = 1.0 WHERE manual_weight IS NULL;

-- Make it non-nullable
ALTER TABLE documents ALTER COLUMN manual_weight SET NOT NULL;

-- Add indexes
CREATE INDEX ix_documents_manual_weight ON documents (manual_weight);
CREATE INDEX ix_documents_type_manual_weight ON documents (document_type, manual_weight);
```

### Option 3: Use Alembic (If PostgreSQL is Running)

If you can get PostgreSQL running locally:

```bash
# Run the migration
alembic upgrade head

# This will apply the 0004_add_manual_weight.py migration
```

## Verification

After running the migration:

1. **Check the column exists**:
   ```sql
   SELECT column_name, data_type, column_default 
   FROM information_schema.columns 
   WHERE table_name = 'documents' AND column_name = 'manual_weight';
   ```

2. **Verify data**:
   ```sql
   SELECT id, filename, document_type, manual_weight 
   FROM documents 
   LIMIT 5;
   ```

3. **Test the API** - Go to the Database tab and verify weight controls appear

## Current Status

The application will work normally, but:
- ✅ Database contents will display without manual_weight
- ❌ Weight adjustment controls will show an error message
- ✅ Document weighting still works (defaults to 1.0x)

After migration:
- ✅ Full manual weight functionality enabled
- ✅ Frontend weight controls work
- ✅ API endpoints functional
- ✅ Database includes manual_weight column

## Error Messages

If you see these errors, it means the migration hasn't been run yet:
- `column documents.manual_weight does not exist`
- `Manual weight feature requires database migration`

## Support

The manual weight feature is backwards compatible - existing functionality continues to work even before migration.