# Manual Document Weight Feature

## Overview

This feature allows you to manually adjust the importance/weight of specific documents in your database. This is particularly useful for:

- **Successful cover letters** that got you job interviews or offers
- **High-quality examples** that you want to use as templates
- **Recent achievements** that should be prioritized
- **Reducing influence** of outdated or less relevant documents

## How It Works

### Weight Calculation Formula

```
Final Weight = Base Weight × Type Weight × Recency Multiplier × Manual Weight
```

- **Base Weight**: 1.0 (default system base)
- **Type Weight**: CV=2.0, Cover Letter=1.8, LinkedIn=1.2, Other=0.8
- **Recency Multiplier**: Based on document age (newer = higher)
- **Manual Weight**: Your custom multiplier (default: 1.0)

### Weight Guidelines

- **5.0x - 10.0x**: Exceptional documents (got you the job!)
- **2.0x - 3.0x**: Great examples to prioritize
- **1.5x - 2.0x**: Good documents to emphasize
- **1.0x**: Default weight (no adjustment)
- **0.5x - 0.8x**: Reduce influence of less relevant docs
- **0.1x - 0.3x**: Minimize outdated content

## Usage

### Frontend (Database Tab)

1. Go to the **📊 Database** tab
2. Find your document in the list
3. Adjust the **Manual Weight** input field (0.1 - 10.0)
4. Click **ℹ️ Info** to see detailed weight breakdown
5. Changes are saved automatically

### API Endpoints

#### Update Document Weight
```bash
PATCH /documents/{document_id}/weight
Content-Type: application/json

{
  "manual_weight": 2.5
}
```

#### Get Weight Information
```bash
GET /documents/{document_id}/weight
```

Returns detailed weight breakdown including:
- Manual weight
- Type weight
- Base weight
- Final calculated weight
- Weight formula explanation

## Database Schema

### New Field Added
```sql
ALTER TABLE documents ADD COLUMN manual_weight FLOAT DEFAULT 1.0;
CREATE INDEX ix_documents_manual_weight ON documents (manual_weight);
```

### Migration
Run the database migration:
```bash
alembic upgrade head
```

## Implementation Details

### Backend Changes

1. **Models** (`app/models.py`):
   - Added `manual_weight` field to Document model

2. **RAG Service** (`app/services/rag_service.py`):
   - Updated `calculate_document_weight()` to include manual weight
   - Added comprehensive docstring explaining weight calculation

3. **API Routes** (`app/api/routes.py`):
   - `PATCH /documents/{id}/weight` - Update manual weight
   - `GET /documents/{id}/weight` - Get weight information
   - Updated database contents endpoint to include manual weights

4. **Database Migration** (`alembic/versions/0004_add_manual_weight.py`):
   - Adds manual_weight column with default value 1.0
   - Creates indexes for performance

### Frontend Changes

1. **Database Management** (`app/static/upload.html`):
   - Added weight input controls for each document
   - Real-time weight adjustment with validation
   - Weight information popup with detailed breakdown
   - Visual feedback for weight changes

### Testing

1. **Unit Tests** (`tests/unit/test_manual_weight.py`):
   - Weight calculation verification
   - Edge case handling
   - Integration with existing weight system

2. **Integration Tests** (`tests/integration/test_document_weight_api.py`):
   - API endpoint testing
   - Validation testing
   - Error handling

## Example Use Cases

### Scenario 1: Successful Cover Letter
You have a cover letter that got you a great job offer:
```
Manual Weight: 5.0x
Reason: This template was highly successful
Effect: 5x more influence in future cover letter generation
```

### Scenario 2: Outdated Experience
You have an old CV with outdated technologies:
```
Manual Weight: 0.3x
Reason: Contains obsolete information
Effect: Minimal influence while keeping for reference
```

### Scenario 3: Recent Achievement
You just completed an important certification:
```
Manual Weight: 3.0x
Reason: Recent and highly relevant achievement
Effect: Emphasized in cover letter generation
```

## Benefits

1. **Personalized Results**: Tailor AI responses to your preferences
2. **Success Amplification**: Boost proven successful examples
3. **Quality Control**: Reduce influence of lower-quality content
4. **Temporal Relevance**: Emphasize recent achievements
5. **Strategic Positioning**: Highlight specific skills or experiences

## Backward Compatibility

- Existing documents default to manual_weight = 1.0
- No change to existing weight calculation behavior
- All existing functionality preserved
- Migration is non-destructive

## Performance

- Indexed manual_weight field for fast queries
- Minimal overhead in weight calculations
- Efficient frontend updates with real-time feedback

---

This feature gives you fine-grained control over how your documents influence AI-generated cover letters, ensuring the most relevant and successful examples guide the generation process!