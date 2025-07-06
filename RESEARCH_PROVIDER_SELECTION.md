# Research Provider Selection Feature

## Overview

You were absolutely right! The batch generation was using a default fallback provider instead of allowing you to select which research provider to use. This has now been fixed.

## What Was Changed

### 1. **Backend API Updates**

#### `BatchCoverLetterRequest` Schema
- Added `research_provider: Optional[str] = None` field
- Allows specifying which provider to use for company research

#### `CoverLetterRequest` Schema  
- Added `research_provider: Optional[str] = None` field
- Single cover letter generation now also supports provider selection

#### Batch Generation Logic
- Updated to use the specified provider: `company_research_service.search_company(company_name, provider=req.research_provider)`
- Falls back to default if no provider specified

#### Single Generation Logic
- Updated to use the specified provider: `company_research_service.search_company(req.company_name, provider=req.research_provider)`
- Falls back to default if no provider specified

### 2. **Frontend UI Updates**

#### Single Cover Letter Generation
- Added provider selection dropdown (hidden by default)
- Shows when "Include Company Research" is checked
- Sends selected provider to backend

#### Batch Cover Letter Generation
- Added provider selection dropdown (hidden by default)  
- Shows when "Include Company Research (Batch)" is checked
- Sends selected provider to backend

#### JavaScript Enhancements
- Event listeners to show/hide provider selection based on checkbox state
- Provider selection is included in API requests

## Available Providers

| Provider | Description | Requirements | Rate Limit |
|----------|-------------|--------------|------------|
| **Auto** | Best available provider | None | Varies |
| **Tavily AI** | Highest quality results | API key (`tvly-...`) | 50/min |
| **Google AI** | Good quality results | API key | 100/min |
| **Brave Search** | Privacy-focused | None | 20/min |
| **YaCy** | Self-hosted search | Self-hosted instance | 30/min |
| **SearXNG** | Self-hosted search | Self-hosted instance | 30/min |
| **DuckDuckGo** | Free, privacy-focused | None | 10/min |

## How It Works

### Before (Default Behavior)
```python
# Always used fallback order: Tavily > Google > Brave > DuckDuckGo
research_result = company_research_service.search_company(company_name)
```

### After (Selectable Provider)
```python
# Use specified provider or fallback to default
research_result = company_research_service.search_company(
    company_name, 
    provider=req.research_provider
)
```

## Usage Examples

### Single Cover Letter Generation
1. Check "Include Company Research"
2. Select your preferred provider from dropdown
3. Generate cover letter
4. Provider will be used for company research

### Batch Generation
1. Check "Include Company Research (Batch)"
2. Select your preferred provider from dropdown
3. Paste job URLs and generate
4. Selected provider will be used for all companies

### API Usage
```bash
# Single generation with specific provider
curl -X POST "http://localhost:8000/generate-cover-letter" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Software Engineer",
    "company_name": "Microsoft",
    "job_description": "...",
    "include_company_research": true,
    "research_provider": "tavily"
  }'

# Batch generation with specific provider
curl -X POST "http://localhost:8000/batch-cover-letters" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Software Engineer", 
    "job_description": "...",
    "websites": ["https://example.com/job1", "https://example.com/job2"],
    "include_company_research": true,
    "research_provider": "brave"
  }'
```

## Benefits

1. **Control**: Choose the provider that works best for your needs
2. **Reliability**: If one provider fails, you can try another
3. **Privacy**: Use privacy-focused providers like Brave or DuckDuckGo
4. **Quality**: Use high-quality providers like Tavily for better results
5. **Cost**: Use free providers to avoid API costs
6. **Self-hosted**: Use your own search instances for complete control

## Testing

Run the test script to verify functionality:
```bash
python test_research_provider.py
```

## Configuration

Make sure your `.env` file has the necessary API keys:
```env
# For Tavily AI (recommended)
TAVILY_API_KEY=tvly-your-key-here

# For Google AI
GOOGLE_API_KEY=your-google-key-here

# For self-hosted search engines
YACY_URL=http://localhost:8090
SEARXNG_URL=http://localhost:8080
```

The system will automatically detect available providers and show them in the dropdown. 