# Research Provider Selection Feature

## Overview

The AI Cover Letter Generator supports multiple company research providers, allowing you to choose the best search service for your needs. This provides flexibility in terms of quality, cost, privacy, and reliability.

## What Was Changed

### 1. **Backend API Updates**

#### `BatchCoverLetterRequest` Schema
- Added `research_provider: Optional[str] = None` field
- Added `research_country: Optional[str] = None` field
- Allows specifying which provider to use for company research and country focus

#### `CoverLetterRequest` Schema  
- Added `research_provider: Optional[str] = None` field
- Added `research_country: Optional[str] = None` field
- Single cover letter generation now also supports provider and country selection

#### Batch Generation Logic
- Updated to use the specified provider: `company_research_service.search_company(company_name, provider=req.research_provider, country=req.research_country)`
- Falls back to default if no provider specified

#### Single Generation Logic
- Updated to use the specified provider: `company_research_service.search_company(req.company_name, provider=req.research_provider, country=req.research_country)`
- Falls back to default if no provider specified

### 2. **Frontend UI Updates**

#### Single Cover Letter Generation
- Added provider selection dropdown (hidden by default)
- Added country selection dropdown (hidden by default)
- Shows when "Include Company Research" is checked
- Sends selected provider and country to backend

#### Batch Cover Letter Generation
- Added provider selection dropdown (hidden by default)  
- Added country selection dropdown (hidden by default)
- Shows when "Include Company Research (Batch)" is checked
- Sends selected provider and country to backend

#### JavaScript Enhancements
- Event listeners to show/hide provider and country selection based on checkbox state
- Provider and country selection is included in API requests

## Available Providers

| Provider | Description | Requirements | Rate Limit | Best For |
|----------|-------------|--------------|------------|----------|
| **Auto** | Best available provider | None | Varies | Automatic selection |
| **Tavily AI** | Highest quality results | API key (`tvly-...`) | 50/min | Best quality |
| **OpenAI** | Intelligent search using GPT | API key | 100/min | AI-powered search |
| **Google AI** | Good quality results | API key | 100/min | Comprehensive results |
| **Brave Search** | Privacy-focused | None (better with API key) | 20/min | Privacy |
| **YaCy** | Self-hosted search | Self-hosted instance | 30/min | Complete control |
| **SearXNG** | Self-hosted search | Self-hosted instance | 30/min | Meta-search |
| **DuckDuckGo** | Free, privacy-focused | None | 10/min | Free option |

## How It Works

### Before (Default Behavior)
```python
# Always used fallback order: Tavily > Google > Brave > DuckDuckGo
research_result = company_research_service.search_company(company_name)
```

### After (Selectable Provider with Country)
```python
# Use specified provider and country or fallback to default
research_result = company_research_service.search_company(
    company_name, 
    provider=req.research_provider,
    country=req.research_country
)
```

## Country-Specific Search

When a country is selected, it's automatically added to the search query for better local relevance:

**Without country focus:**
```
"Microsoft company about us mission vision"
```

**With country focus (Australia):**
```
"Microsoft company about us mission vision Australia"
```

### Available Countries
- **Americas**: United States, Canada
- **Europe**: United Kingdom, Germany, France, Netherlands, Sweden, Norway, Denmark, Finland, Switzerland, Ireland, Belgium, Austria
- **Asia-Pacific**: Australia, Singapore, Japan, South Korea, New Zealand

## Usage Examples

### Single Cover Letter Generation
1. Check "Include Company Research"
2. Select your preferred provider from dropdown
3. Select a country (optional) for country-specific search
4. Generate cover letter
5. Provider will be used for company research with country focus

### Batch Generation
1. Check "Include Company Research (Batch)"
2. Select your preferred provider from dropdown
3. Select a country (optional) for country-specific search
4. Paste job URLs and generate
5. Selected provider will be used for all companies with country focus

### API Usage
```bash
# Single generation with specific provider and country
curl -X POST "http://localhost:8000/generate-cover-letter" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Software Engineer",
    "company_name": "Microsoft",
    "job_description": "...",
    "include_company_research": true,
    "research_provider": "tavily",
    "research_country": "Australia"
  }'

# Batch generation with specific provider and country
curl -X POST "http://localhost:8000/batch-cover-letters" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Software Engineer", 
    "job_description": "...",
    "websites": ["https://example.com/job1", "https://example.com/job2"],
    "include_company_research": true,
    "research_provider": "openai",
    "research_country": "United Kingdom"
  }'
```

## Benefits

1. **Control**: Choose the provider that works best for your needs
2. **Reliability**: If one provider fails, you can try another
3. **Privacy**: Use privacy-focused providers like Brave or DuckDuckGo
4. **Quality**: Use high-quality providers like Tavily for better results
5. **Cost**: Use free providers to avoid API costs
6. **Self-hosted**: Use your own search instances for complete control
7. **Local Relevance**: Use country-specific search for better local information
8. **AI-Powered**: Use OpenAI for intelligent, AI-powered search

## Testing

Run the test script to verify functionality:
```bash
python test_research_provider.py
```

This will test:
- Provider selection for single generation
- Provider selection for batch generation
- Country-specific search functionality
- Fallback behavior when providers fail

## Configuration

Make sure your `.env` file has the necessary API keys:
```env
# For Tavily AI (recommended)
TAVILY_API_KEY=tvly-your-key-here

# For OpenAI (can be used for both LLM and search)
OPENAI_API_KEY=your-openai-key-here

# For Google AI
GOOGLE_API_KEY=your-google-key-here

# For Brave Search (optional, works without key)
BRAVE_API_KEY=your-brave-key-here

# For self-hosted search engines
YACY_URL=http://localhost:8090
SEARXNG_URL=http://localhost:8080
```

The system will automatically detect available providers and show them in the dropdown with their availability status.

## Best Practices

### When to Use Each Provider
- **Tavily AI**: Best overall quality, comprehensive results
- **OpenAI**: AI-powered search, good for complex queries
- **Google AI**: Comprehensive results, good for large companies
- **Brave Search**: Privacy-focused, good for general research
- **DuckDuckGo**: Free option, good for basic research
- **YaCy/SearXNG**: Complete privacy, requires self-hosting

### When to Use Country-Specific Search
- **Local job applications**: Focus on the country where you're applying
- **International companies**: Get regional office information
- **Local companies**: Ensure you get the right company
- **Regional roles**: Understand local market presence 