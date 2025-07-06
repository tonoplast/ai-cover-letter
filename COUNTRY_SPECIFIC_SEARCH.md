# Country-Specific Search Feature

## Overview

The AI Cover Letter Generator now supports country-specific company research, allowing you to focus search results on specific countries or regions. This is particularly useful for:

- Finding local offices and regional information
- Getting country-specific company details
- Researching companies in specific markets
- Improving relevance for international job applications

## How It Works

### Search Query Enhancement
When a country is selected, it's automatically added to the search query:

**Without country focus:**
```
"Microsoft company about us mission vision"
```

**With country focus (Australia):**
```
"Microsoft company about us mission vision Australia"
```

### Supported Providers
All search providers support country-specific search:
- **Tavily AI** - Adds country to search query
- **Google AI** - Includes country context in AI prompt
- **Brave Search** - Adds country to search parameters
- **DuckDuckGo** - Includes country in search query
- **YaCy** - Adds country to search parameters
- **SearXNG** - Includes country in search query

## Available Countries

The system supports 20 countries across different regions:

### Americas
- United States
- Canada

### Europe
- United Kingdom
- Germany
- France
- Netherlands
- Sweden
- Norway
- Denmark
- Finland
- Switzerland
- Ireland
- Belgium
- Austria

### Asia-Pacific
- Australia
- Singapore
- Japan
- South Korea
- New Zealand

## Usage

### Single Cover Letter Generation
1. Check "Include Company Research"
2. Select your preferred search provider
3. **Select a country** (optional) - Leave empty for global search
4. Generate cover letter
5. Search will focus on the selected country

### Batch Generation
1. Check "Include Company Research (Batch)"
2. Select your preferred search provider
3. **Select a country** (optional) - Leave empty for global search
4. Paste job URLs and generate
5. All companies will be researched with country focus

### Manual Company Research
1. Enter company name
2. Select search provider
3. **Select a country** (optional)
4. Click "Research Company"

## API Usage

### Single Generation with Country Focus
```bash
curl -X POST "http://localhost:8000/generate-cover-letter" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Software Engineer",
    "company_name": "Microsoft",
    "job_description": "...",
    "include_company_research": true,
    "research_provider": "brave",
    "research_country": "Australia"
  }'
```

### Batch Generation with Country Focus
```bash
curl -X POST "http://localhost:8000/batch-cover-letters" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Software Engineer", 
    "job_description": "...",
    "websites": ["https://example.com/job1", "https://example.com/job2"],
    "include_company_research": true,
    "research_provider": "tavily",
    "research_country": "United Kingdom"
  }'
```

## Benefits

### 1. **Local Relevance**
- Find country-specific offices and operations
- Get regional company information
- Understand local market presence

### 2. **Better Context**
- Research companies in your target market
- Get location-specific company details
- Find regional headquarters and offices

### 3. **Improved Accuracy**
- More relevant search results
- Country-specific company information
- Local industry context

### 4. **International Applications**
- Research companies in specific countries
- Get regional office information
- Understand local market presence

## Examples

### Example 1: Australian Job Application
- **Company:** Microsoft
- **Country:** Australia
- **Search Query:** "Microsoft company about us mission vision Australia"
- **Result:** Focuses on Microsoft's Australian operations, local offices, and regional information

### Example 2: UK Job Application
- **Company:** Google
- **Country:** United Kingdom
- **Search Query:** "Google company about us mission vision United Kingdom"
- **Result:** Emphasizes Google's UK presence, London offices, and European operations

### Example 3: Global Search
- **Company:** Apple
- **Country:** (empty)
- **Search Query:** "Apple company about us mission vision"
- **Result:** General global information about Apple

## Configuration

No additional configuration is required. The country selection is available in the UI when company research is enabled.

## Testing

Run the test script to verify functionality:
```bash
python test_country_search.py
```

This will test:
- Global search (no country focus)
- Country-specific searches for multiple countries
- Local company searches
- Different search providers

## Best Practices

### When to Use Country-Specific Search
- **Local job applications** - Focus on the country where you're applying
- **International companies** - Get regional office information
- **Local companies** - Ensure you get the right company (e.g., Woolworths Australia vs UK)
- **Regional roles** - Understand local market presence

### When to Use Global Search
- **Global companies** - Get general company information
- **Remote positions** - Company location doesn't matter
- **Unknown company location** - Start with global search

## Troubleshooting

### No Results with Country Focus
- Try global search first to verify the company exists
- Check if the company has operations in the selected country
- Try a different search provider
- Verify the company name spelling

### Irrelevant Results
- The company might not have significant presence in the selected country
- Try a different country or global search
- Use a different search provider

## Future Enhancements

Potential future improvements:
- **Region selection** (e.g., "Europe", "Asia-Pacific")
- **City-specific search** for major cities
- **Language-specific search** for non-English companies
- **Industry-specific country focus** (e.g., tech companies in specific regions) 