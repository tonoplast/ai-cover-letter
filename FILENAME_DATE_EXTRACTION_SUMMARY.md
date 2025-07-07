# Filename-Based Date Extraction Implementation Summary

## Overview

This document summarizes the implementation of filename-based date extraction for the AI Cover Letter Generator. This feature automatically extracts dates and document types from filenames to improve the recency weighting system used in RAG (Retrieval-Augmented Generation).

## Problem Statement

The user has a large collection of CVs and cover letters with filenames following a specific format:
- `YYYY-MM-DD_Type_Company-Name.ext`
- Examples: `2025-05-01_CV_Data-Science.pdf`, `2024-10-21_Cover-Letter_Lookahead.pdf`

The current system only used upload dates for recency weighting, but the actual document dates (from filenames) would provide more accurate weighting for better RAG performance.

## Solution Implemented

### 1. Filename Parser Service (`app/services/filename_parser.py`)

Created a comprehensive filename parsing service that:

- **Extracts dates** from filenames in various formats (YYYY-MM-DD, DD-MM-YYYY, etc.)
- **Detects document types** (CV, Cover-Letter, LinkedIn, etc.)
- **Extracts company names** from filenames
- **Validates filename format** and provides fallback behavior
- **Generates properly formatted filenames** for new documents

**Key Methods:**
- `parse_filename()` - Comprehensive parsing of filename components
- `extract_date_from_filename()` - Extract just the date
- `extract_document_type_from_filename()` - Extract document type
- `extract_company_from_filename()` - Extract company name
- `generate_filename()` - Create new filenames in the correct format

### 2. Enhanced RAG Service (`app/services/rag_service.py`)

Modified the `calculate_document_weight()` method to:

- **Use filename dates for recency weighting** when available
- **Fall back to upload date** when filename doesn't contain a date
- **Maintain backward compatibility** with existing documents

**Key Changes:**
```python
# Try to extract date from filename first, fallback to upload date
filename_date = FilenameParser.extract_date_from_filename(document.filename)
if filename_date:
    # Use filename date for recency calculation
    days_since_document = (datetime.now() - filename_date).days
    recency_multiplier = max(self.min_weight_multiplier, 
                           1.0 - (days_since_document / self.recency_period_days))
else:
    # Fallback to upload date
    days_since_upload = (datetime.now() - document.uploaded_at).days
    recency_multiplier = max(self.min_weight_multiplier, 
                           1.0 - (days_since_upload / self.recency_period_days))
```

### 3. Enhanced Document Upload (`app/api/routes.py`)

Modified both single and multiple document upload functions to:

- **Automatically detect document types** from filenames
- **Use detected types** when valid, fallback to manual selection
- **Calculate weights** using filename dates for better accuracy
- **Maintain existing functionality** for files without proper formatting

**Key Changes:**
```python
# Parse filename for date and document type information
filename_info = FilenameParser.parse_filename(file.filename or "unknown_file")

# Use filename document type if available and valid, otherwise use provided type
detected_document_type = filename_info.get('document_type')
if detected_document_type and detected_document_type in ['cv', 'cover_letter', 'linkedin', 'other']:
    final_document_type = detected_document_type
else:
    final_document_type = document_type
```

## Supported Filename Format

The system recognizes filenames in the format:
```
YYYY-MM-DD_Type_Company-Name.ext
```

**Examples:**
- `2025-05-01_CV_Data-Science.pdf` - CV from May 1, 2025 for Data Science role
- `2024-10-21_Cover-Letter_Lookahead.pdf` - Cover letter from October 21, 2024 for Lookahead
- `2023-09-01_CV_Neuroscience.pdf` - CV from September 1, 2023 for Neuroscience role
- `2022-01-01_CV.pdf` - CV from January 1, 2022 (no company specified)

## Document Type Mapping

The system automatically maps these document types:
- `CV` or `Resume` → `cv`
- `Cover-Letter` or `CoverLetter` → `cover_letter`
- `LinkedIn` or `Profile` → `linkedin`
- Other types → `other`

## Benefits

1. **More Accurate Recency Weighting**: Uses actual document dates instead of upload dates
2. **Automatic Document Type Detection**: Reduces manual selection errors
3. **Better RAG Performance**: More recent documents get higher weights for better context
4. **Consistent Formatting**: Generated documents follow the same naming convention
5. **Backward Compatibility**: Existing documents continue to work without changes

## Fallback Behavior

If a filename doesn't follow the expected format:
- Document type falls back to the manually selected type
- Date falls back to the upload timestamp
- Recency weighting uses the upload date
- No functionality is lost

## Testing

Created comprehensive test scripts:

1. **`test_filename_parsing.py`** - Tests filename parsing functionality
2. **`test_filename_upload.py`** - Tests upload simulation with filename parsing

Both tests verify:
- ✅ Date extraction from various formats
- ✅ Document type detection
- ✅ Company name extraction
- ✅ Fallback behavior for invalid formats
- ✅ Weight calculation simulation

## Documentation Updates

Updated the README.md with:

1. **New feature description** in the features list
2. **Detailed section** explaining the filename format and benefits
3. **Usage instructions** for the upload interface
4. **Examples** of supported filename formats
5. **Fallback behavior** explanation

## Files Modified

### New Files:
- `app/services/filename_parser.py` - Filename parsing service
- `test_filename_parsing.py` - Filename parsing tests
- `test_filename_upload.py` - Upload simulation tests
- `FILENAME_DATE_EXTRACTION_SUMMARY.md` - This summary document

### Modified Files:
- `app/services/rag_service.py` - Enhanced weight calculation
- `app/api/routes.py` - Enhanced document upload
- `README.md` - Added comprehensive documentation

## Usage Instructions

### For Users:

1. **Upload documents** with filenames in the format `YYYY-MM-DD_Type_Company-Name.ext`
2. **The system automatically detects** document types and dates
3. **Recency weighting** uses the filename date for better accuracy
4. **Manual type selection** still works for files without proper formatting

### For Developers:

1. **Import the parser**: `from app.services.filename_parser import FilenameParser`
2. **Parse filenames**: `result = FilenameParser.parse_filename(filename)`
3. **Extract specific data**: `date = FilenameParser.extract_date_from_filename(filename)`
4. **Generate filenames**: `new_filename = FilenameParser.generate_filename(date, doc_type, company)`

## Future Enhancements

Potential improvements for future versions:

1. **Additional date formats** (MM/DD/YYYY, DD-MM-YYYY, etc.)
2. **More document type mappings** (Resume, Portfolio, etc.)
3. **Company name normalization** (handling special characters, abbreviations)
4. **Bulk filename validation** for existing documents
5. **Filename format migration** tools for existing documents

## Conclusion

The filename-based date extraction feature has been successfully implemented and provides:

- ✅ **Improved accuracy** in recency weighting
- ✅ **Automatic document type detection**
- ✅ **Better RAG performance**
- ✅ **Backward compatibility**
- ✅ **Comprehensive testing**
- ✅ **Complete documentation**

The system now intelligently uses document dates from filenames when available, falling back to upload dates when necessary, ensuring optimal performance for the AI cover letter generation system. 