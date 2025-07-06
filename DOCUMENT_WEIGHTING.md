# Document Weighting System

The AI Cover Letter Generator includes a sophisticated document weighting system that prioritizes more recent and relevant documents when generating cover letters using RAG (Retrieval-Augmented Generation). This system ensures that the most important and up-to-date information is used to create personalized cover letters.

## Overview

The weighting system combines two factors:
1. **Document Type Weighting**: Different document types get different importance levels
2. **Recency Weighting**: More recent documents get higher weights

This creates a comprehensive scoring system that helps the RAG system retrieve the most relevant content for cover letter generation.

## Configuration

Add these settings to your `.env` file:

```env
# Document weighting configuration
CV_WEIGHT=1.0                    # Weight for CV/Resume documents
COVER_LETTER_WEIGHT=0.8          # Weight for cover letter documents
LINKEDIN_WEIGHT=0.6              # Weight for LinkedIn profile documents
OTHER_WEIGHT=0.4                 # Weight for other document types
RECENCY_PERIOD_DAYS=365          # Period for recency weighting (days)
```

## Weight Calculation

### Document Type Weights
- **CV/Resume**: 1.0x (highest priority) - Your most important documents
- **Cover Letter**: 0.8x (very high priority) - Shows your writing style
- **LinkedIn Profile**: 0.6x (medium priority) - Additional context
- **Other Documents**: 0.4x (lowest priority) - Supporting materials

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
| Recent CV | CV | 30 days | 1.0 | 1.0 | 1.0 |
| Old CV | CV | 400 days | 1.0 | 0.1 | 0.1 |
| Recent Cover Letter | Cover Letter | 10 days | 0.8 | 1.0 | 0.8 |
| Old LinkedIn | LinkedIn | 200 days | 0.6 | 0.55 | 0.33 |
| Recent Other | Other | 50 days | 0.4 | 1.0 | 0.4 |

## Database Integration

### Automatic Weight Calculation
When documents are uploaded, weights are automatically calculated and stored in the database:

```python
def calculate_document_weight(document: Document) -> float:
    base_weight = 1.0
    type_weight = get_type_weight(document.document_type)
    recency_weight = calculate_recency_weight(document.upload_date)
    return base_weight * type_weight * recency_weight
```

### Database Schema
The `Document` model includes a `weight` field that stores the calculated weight:

```python
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    document_type = Column(String)
    weight = Column(Float, default=1.0)  # Calculated weight
    upload_date = Column(DateTime, default=datetime.utcnow)
    # ... other fields
```

## Migration

If you have existing documents, run the migration script to add weights:

```bash
python migrate_add_weight_column.py
```

This script will:
1. Add the `weight` column to the documents table
2. Calculate weights for all existing documents
3. Update the database with the new weights

## Usage in RAG

The RAG service automatically uses these weights when:

### Document Retrieval
- Finding relevant document chunks for cover letter generation
- Ranking search results by relevance and recency
- Enhancing prompts with the most important context

### RAG Pipeline Integration
```python
def get_relevant_documents(query: str, top_k: int = 5) -> List[Document]:
    # Get documents with embeddings
    documents = get_documents_with_embeddings()
    
    # Calculate similarity scores
    similarity_scores = calculate_similarity(query, documents)
    
    # Apply document weights
    weighted_scores = []
    for doc, score in zip(documents, similarity_scores):
        weighted_score = score * doc.weight
        weighted_scores.append((doc, weighted_score))
    
    # Sort by weighted scores and return top_k
    weighted_scores.sort(key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in weighted_scores[:top_k]]
```

### Enhanced Prompt Generation
The system uses weighted document content to create more relevant prompts:

```python
def create_enhanced_prompt(job_info: dict, relevant_docs: List[Document]) -> str:
    # Sort documents by weight for better context ordering
    sorted_docs = sorted(relevant_docs, key=lambda x: x.weight, reverse=True)
    
    # Include high-weight documents first in the prompt
    context = ""
    for doc in sorted_docs:
        context += f"\n--- {doc.document_type.upper()} (Weight: {doc.weight:.2f}) ---\n"
        context += doc.content[:1000] + "\n"
    
    return f"""
    Job Information:
    Title: {job_info['title']}
    Company: {job_info['company']}
    Description: {job_info['description']}
    
    Relevant Experience and Background:
    {context}
    
    Please generate a cover letter that incorporates the most relevant information from the above documents, prioritizing recent CVs and cover letters.
    """
```

## Testing

Test the weighting system:

```bash
python test_document_weighting.py
```

This script will test:
- Weight calculation for different document types
- Recency weighting calculations
- RAG integration with weighted documents
- Database migration and weight updates

## Benefits

### 1. **Better RAG Results**
- More recent and relevant documents are prioritized
- CVs and cover letters get higher importance
- Improved context for cover letter generation

### 2. **Configurable System**
- Easy to adjust weights via environment variables
- Can fine-tune for different use cases
- Flexible recency period configuration

### 3. **Automatic Operation**
- Weights are calculated automatically when documents are uploaded
- No manual intervention required
- Consistent weighting across all documents

### 4. **Enhanced Performance**
- Better document retrieval for RAG
- More relevant context in generated cover letters
- Improved writing style adaptation

### 5. **Flexible Configuration**
- Can disable recency weighting if desired
- Adjustable weights for different document types
- Configurable recency period

## Customization

You can customize the weighting by modifying the environment variables:

### Adjust Document Type Weights
```env
# Give CVs even more importance
CV_WEIGHT=1.2

# Reduce importance of other documents
OTHER_WEIGHT=0.3

# Increase LinkedIn profile importance
LINKEDIN_WEIGHT=0.7
```

### Adjust Recency Period
```env
# Faster weight decay (6 months)
RECENCY_PERIOD_DAYS=180

# Slower weight decay (2 years)
RECENCY_PERIOD_DAYS=730
```

### Disable Recency Weighting
If you want to use only document type weighting:
```env
# Set all documents to same recency weight
RECENCY_PERIOD_DAYS=999999
```

## Best Practices

### Document Upload Order
1. **Upload your most recent CV first** - Gets highest weight
2. **Upload recent cover letters** - Shows your writing style
3. **Upload LinkedIn profile** - Provides additional context
4. **Upload supporting documents** - For comprehensive coverage

### Weight Configuration
- **Keep CV weight high** (1.0) for best results
- **Adjust cover letter weight** based on writing style importance
- **Set appropriate recency period** for your use case
- **Test different configurations** to find optimal settings

### Maintenance
- **Regularly upload updated CVs** to maintain high weights
- **Archive old documents** if they're no longer relevant
- **Monitor RAG performance** with different weight configurations
- **Update weights** when document types change

## Troubleshooting

### Weights Not Updating
- Check if migration script was run
- Verify environment variables are set correctly
- Restart the application after configuration changes

### Poor RAG Results
- Ensure you have recent CVs uploaded
- Check document type assignments
- Verify weights are being calculated correctly
- Consider adjusting weight configuration

### Migration Issues
- Backup database before running migration
- Check for any existing weight columns
- Verify database permissions
- Test migration on a copy first 