# LLM-Enhanced Document Upload Implementation

## Overview

This implementation adds LLM provider and model selection options to the document upload functionality, allowing users to choose between basic text extraction and AI-enhanced structured data extraction.

## Features Added

### 1. Frontend Enhancements

#### Document Upload Tab
- **LLM Extraction Toggle**: Checkbox to enable/disable AI-enhanced document parsing
- **Provider Selection**: Dropdown to select LLM provider (Ollama, OpenAI, Anthropic, Google)
- **Model Selection**: Dropdown to select specific model for the chosen provider
- **Auto Mode**: Default option that uses the system's default provider and model

#### UI Components Added
- `useLLMExtraction` checkbox
- `uploadLlmProvider` dropdown
- `uploadLlmModel` dropdown
- Dynamic show/hide logic for provider and model selection

### 2. Backend Enhancements

#### API Endpoint Updates
- Modified `/upload-multiple-documents` endpoint to accept LLM parameters:
  - `use_llm_extraction`: Boolean string ("true"/"false")
  - `llm_provider`: Optional provider name
  - `llm_model`: Optional model name

#### Document Parser Enhancements
- Added `parse_document_with_llm()` method to `DocumentParser` class
- LLM-enhanced extraction for CV, Cover Letter, and LinkedIn documents
- Structured JSON extraction with specific prompts for each document type
- Fallback to basic parsing if LLM extraction fails

### 3. LLM Integration

#### Extraction Prompts
- **CV Extraction**: Extracts personal info, experiences, education, skills, certifications
- **Cover Letter Extraction**: Extracts recipient, company, position, key points, tone
- **LinkedIn Extraction**: Extracts profile info, experiences, education, skills

#### Response Processing
- JSON parsing from LLM responses
- Merging with basic parsed data
- Error handling and fallback mechanisms

## Usage

### Frontend Usage
1. Navigate to the "Upload Documents" tab
2. Check "Use AI for Enhanced Document Parsing" to enable LLM extraction
3. Select your preferred LLM provider (or leave as "Auto")
4. Select a specific model (or leave as "Auto")
5. Upload your documents as usual

### Backend API Usage
```python
# Upload with LLM extraction
files = {'files': open('document.pdf', 'rb')}
data = {
    'document_types': 'cv',
    'use_llm_extraction': 'true',
    'llm_provider': 'ollama',
    'llm_model': 'llama3.2:latest'
}
response = requests.post('/upload-multiple-documents', files=files, data=data)

# Upload without LLM extraction
data = {
    'document_types': 'cv',
    'use_llm_extraction': 'false'
}
```

## Benefits

### Comparison Capability
- Users can now compare results between basic and LLM-enhanced parsing
- Easy A/B testing of different extraction methods
- Transparent visibility into what extraction method was used

### Enhanced Data Quality
- LLM extraction provides more structured and accurate data
- Better extraction of experiences, education, and skills
- Improved parsing of complex document formats

### Flexibility
- Users can choose their preferred LLM provider
- Model selection allows optimization for specific use cases
- Auto mode provides sensible defaults

## Technical Details

### File Structure Changes
- `app/static/upload.html`: Added LLM selection UI components
- `app/api/routes.py`: Modified upload endpoint to accept LLM parameters
- `app/services/document_parser.py`: Added LLM-enhanced parsing methods

### JavaScript Functions Added
- `loadUploadLLMModels()`: Loads available models for upload provider
- Event listeners for LLM extraction toggle and provider selection
- Integration with existing `uploadFiles()` function

### Error Handling
- Graceful fallback to basic parsing if LLM extraction fails
- Clear error messages in parsed data
- No interruption to upload process

## Testing

A test script (`test_llm_upload.py`) has been created to verify:
- Server connectivity
- LLM provider availability
- Upload functionality with and without LLM extraction
- LLM enhancement application verification

## Future Enhancements

1. **Batch Processing**: Process multiple documents with different LLM settings
2. **Custom Prompts**: Allow users to customize extraction prompts
3. **Result Comparison**: Side-by-side comparison of basic vs LLM extraction
4. **Performance Metrics**: Track extraction accuracy and performance
5. **Caching**: Cache LLM responses for similar documents

## Configuration

The implementation respects existing LLM configuration:
- Uses default provider if none specified
- Falls back to default model if none specified
- Maintains compatibility with existing LLM service setup

## Security Considerations

- LLM provider credentials are handled securely through existing LLM service
- No sensitive data is exposed in frontend
- Error messages don't reveal internal system details 