# Document Weighting System

The AI Cover Letter Generator now includes a sophisticated document weighting system that prioritizes more recent and relevant documents when generating cover letters using RAG (Retrieval-Augmented Generation).

## Overview

The weighting system combines two factors:
1. **Document Type Weighting**: Different document types get different importance levels
2. **Recency Weighting**: More recent documents get higher weights

## Configuration

Add these settings to your `.env` file:

```env
# Document weighting configuration
DOCUMENT_BASE_WEIGHT=1.0
DOCUMENT_RECENCY_PERIOD_DAYS=365
DOCUMENT_MIN_WEIGHT_MULTIPLIER=0.1
DOCUMENT_RECENCY_WEIGHTING_ENABLED=true

# Document type specific weights (higher values = more important for RAG)
CV_WEIGHT_MULTIPLIER=2.0
COVER_LETTER_WEIGHT_MULTIPLIER=1.8
LINKEDIN_WEIGHT_MULTIPLIER=1.2
OTHER_DOCUMENT_WEIGHT_MULTIPLIER=0.8
```

## Weight Calculation

### Document Type Weights
- **CV/Resume**: 2.0x (highest priority)
- **Cover Letter**: 1.8x (very high priority)
- **LinkedIn Profile**: 1.2x (medium priority)
- **Other Documents**: 0.8x (lowest priority)

### Recency Weighting
- Documents uploaded within the last 365 days get full weight
- Older documents get progressively reduced weight
- Documents older than 365 days get minimum weight (0.1x)

### Final Weight Formula
```
Final Weight = Base Weight × Type Weight × Recency Multiplier
```

## Examples

| Document | Type | Age | Type Weight | Recency Multiplier | Final Weight |
|----------|------|-----|-------------|-------------------|--------------|
| Recent CV | CV | 30 days | 2.0 | 1.0 | 2.0 |
| Old CV | CV | 400 days | 2.0 | 0.1 | 0.2 |
| Recent Cover Letter | Cover Letter | 10 days | 1.8 | 1.0 | 1.8 |
| Old LinkedIn | LinkedIn | 200 days | 1.2 | 0.55 | 0.66 |

## Migration

If you have existing documents, run the migration script to add weights:

```bash
python migrate_add_weight_column.py
```

## Testing

Test the weighting system:

```bash
python test_document_weighting.py
```

## Benefits

1. **Better RAG Results**: More recent and relevant documents are prioritized
2. **Configurable**: Easy to adjust weights via environment variables
3. **Automatic**: Weights are calculated automatically when documents are uploaded
4. **Flexible**: Can disable recency weighting if desired

## Usage in RAG

The RAG service automatically uses these weights when:
- Finding relevant document chunks for cover letter generation
- Ranking search results by relevance and recency
- Enhancing prompts with the most important context

## Customization

You can customize the weighting by modifying the environment variables:

- Increase `CV_WEIGHT_MULTIPLIER` to give CVs even more importance
- Decrease `DOCUMENT_RECENCY_PERIOD_DAYS` for faster weight decay
- Set `DOCUMENT_RECENCY_WEIGHTING_ENABLED=false` to disable recency weighting
- Adjust `DOCUMENT_MIN_WEIGHT_MULTIPLIER` to change minimum weight for old documents 