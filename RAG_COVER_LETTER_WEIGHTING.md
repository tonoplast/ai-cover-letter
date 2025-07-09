# RAG Cover Letter Weighting: Uploaded vs Generated

## Overview

The AI Cover Letter Generator uses two different types of cover letters for different purposes in the RAG (Retrieval-Augmented Generation) system. Understanding how these are weighted and used is crucial for optimizing your cover letter generation results.

## Two Types of Cover Letters

### 1. **Uploaded Cover Letters** (Documents Table)
- **Source**: Files you upload with `document_type = "cover_letter"`
- **Storage**: Stored in the `documents` table
- **Content**: Your actual written cover letters, CVs, and other documents
- **Purpose**: Primary source for RAG context and content relevance

### 2. **Generated Cover Letters** (Cover Letters Table)
- **Source**: AI-generated cover letters from the system
- **Storage**: Stored in the `cover_letters` table
- **Content**: AI-generated content based on your uploaded documents
- **Purpose**: Writing style analysis and pattern recognition

## RAG System Behavior

### ✅ **Uploaded Cover Letters in RAG**

Uploaded cover letters **ARE used** in the RAG system and get the following weighting:

#### **Document Type Weight**
```python
document_type_weights = {
    'cv': 2.0,           # Highest priority
    'cover_letter': 1.8, # Very high priority (second highest)
    'linkedin': 1.2,     # Medium priority
    'other': 0.8         # Lowest priority
}
```

**Uploaded cover letters get a weight multiplier of 1.8x** - the second highest weight after CVs.

#### **Recency Weighting**
Uploaded cover letters get recency weighting based on:
1. **Filename date** (if filename contains a date like `2024-10-21_Cover-Letter_Company.pdf`)
2. **Content date** (if date found in document content)
3. **Upload date** (fallback)

**Recency Formula:**
```python
recency_multiplier = max(0.1, 1.0 - (days_since_document / 365))
```

#### **Final Weight Calculation**
```python
final_weight = base_weight × type_weight × recency_multiplier
final_weight = 1.0 × 1.8 × recency_multiplier
```

#### **Weight Examples for Uploaded Cover Letters**

| Scenario | Age | Recency Multiplier | Final Weight |
|----------|-----|-------------------|--------------|
| Recent uploaded cover letter | 10 days | 1.0 | **1.8** |
| Medium age uploaded cover letter | 100 days | 0.73 | **1.31** |
| Old uploaded cover letter | 400 days | 0.1 | **0.18** |

### ❌ **Generated Cover Letters in RAG**

**Generated cover letters are NOT used in the RAG system at all.**

The RAG service only queries the `Document` table:
```python
# In RAGService.find_relevant_chunks()
documents = self.db.query(Document).order_by(Document.uploaded_at.desc()).all()
```

This means generated cover letters stored in the `cover_letters` table are completely excluded from RAG context retrieval.

## How Generated Cover Letters Are Used

Generated cover letters serve a different purpose - **writing style analysis**:

```python
# In cover letter generation process
cover_docs = db.query(Document).filter(Document.document_type == "cover_letter").order_by(Document.uploaded_at.desc()).all()
writing_style = {}
for idx, doc in enumerate(cover_docs):
    parsed = doc.parsed_data if isinstance(doc.parsed_data, dict) else {}
    style = parsed.get("writing_style", {})
    weight = max(1, len(cover_docs) - idx)  # Most recent gets highest weight
```

### **Writing Style Analysis Features**
- **Vocabulary patterns**: Common words and phrases you use
- **Sentence structure**: Average sentence length and complexity
- **Voice and tone**: Personal vs formal writing style
- **Professional elements**: Use of transitions, action verbs, etc.
- **Recency weighting**: More recent cover letters influence style more

## Why This Design Makes Sense

### **1. Content Authenticity**
- **Uploaded cover letters** contain your actual experiences and writing
- **Generated cover letters** are AI-created and shouldn't influence future AI generations

### **2. Avoid Circular Influence**
- Using generated content to generate more content could create feedback loops
- The system prioritizes human-written content for RAG context

### **3. Style vs Content Separation**
- **Uploaded documents** → Provide content context (experiences, skills, achievements)
- **Generated cover letters** → Provide style context (writing patterns, tone, structure)

## Database Schema

### **Documents Table** (Uploaded Content)
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    filename VARCHAR NOT NULL,
    document_type VARCHAR NOT NULL,  -- 'cv', 'cover_letter', 'linkedin', 'other'
    content TEXT NOT NULL,
    parsed_data JSON,
    uploaded_at DATETIME DEFAULT NOW(),
    weight FLOAT DEFAULT 1.0  -- RAG weight
);
```

### **Cover Letters Table** (Generated Content)
```sql
CREATE TABLE cover_letters (
    id INTEGER PRIMARY KEY,
    job_title VARCHAR NOT NULL,
    company_name VARCHAR NOT NULL,
    job_description TEXT NOT NULL,
    generated_content TEXT NOT NULL,
    company_research JSON,
    used_experiences JSON,
    writing_style_analysis JSON,
    generated_at DATETIME DEFAULT NOW()
);
```

## Configuration

### **Environment Variables**
```env
# Document type weights for RAG
CV_WEIGHT_MULTIPLIER=2.0
COVER_LETTER_WEIGHT_MULTIPLIER=1.8
LINKEDIN_WEIGHT_MULTIPLIER=1.2
OTHER_DOCUMENT_WEIGHT_MULTIPLIER=0.8

# Recency weighting
DOCUMENT_RECENCY_PERIOD_DAYS=365
DOCUMENT_MIN_WEIGHT_MULTIPLIER=0.1
DOCUMENT_RECENCY_WEIGHTING_ENABLED=true
```

## Best Practices

### **For Optimal RAG Performance**

1. **Upload Recent Cover Letters**
   - Upload your most recent cover letters for highest RAG weight
   - Use filenames with dates: `2024-10-21_Cover-Letter_Company.pdf`

2. **Upload Diverse Content**
   - Upload CVs, cover letters, LinkedIn profiles, and other relevant documents
   - Each document type gets different weighting

3. **Maintain Fresh Content**
   - Regularly upload new documents to maintain high recency weights
   - Remove or update old documents that are no longer relevant

### **For Writing Style Analysis**

1. **Generate Multiple Cover Letters**
   - Generate cover letters for different companies/roles
   - This helps the system learn your writing patterns

2. **Rate Generated Cover Letters**
   - Provide ratings (1-5 stars) on generated cover letters
   - This helps improve future generations

3. **Use Consistent Tone**
   - Maintain consistent writing style across generated cover letters
   - This helps the system better understand your preferences

## Troubleshooting

### **Low RAG Context**
If you're getting generic cover letters with little personal context:

1. **Check uploaded documents**: Ensure you have recent CVs and cover letters uploaded
2. **Verify document types**: Make sure documents are properly categorized
3. **Check weights**: Use the database view to see document weights
4. **Upload more content**: Add more relevant documents to increase context

### **Poor Style Matching**
If generated cover letters don't match your writing style:

1. **Generate more cover letters**: Create more examples for style analysis
2. **Rate your preferences**: Provide feedback on generated cover letters
3. **Upload writing samples**: Add more of your own writing for style reference

## Summary

| Aspect | Uploaded Cover Letters | Generated Cover Letters |
|--------|----------------------|------------------------|
| **RAG Usage** | ✅ Used with 1.8x weight | ❌ Not used |
| **Recency Weighting** | ✅ Applied | ❌ Not applicable |
| **Content Context** | ✅ Provides experiences/skills | ❌ Not used |
| **Style Analysis** | ✅ Writing patterns | ✅ Style matching |
| **Database Table** | `documents` | `cover_letters` |
| **Primary Purpose** | Content relevance | Style consistency |

This design ensures that your authentic content drives the RAG system while AI-generated content helps maintain consistent writing style. 