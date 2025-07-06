# API Key Migration Guide

## Overview

This guide explains the recent changes to API key variable names in the AI Cover Letter Generator to resolve naming conflicts between different Google services.

## Changes Made

### 🔄 **API Key Variable Updates**

| Service | Old Variable | New Variable | Purpose |
|---------|-------------|--------------|---------|
| **Google Gemini LLM** | `GOOGLE_API_KEY` | `GOOGLE_GEMINI_API_KEY` | Text generation and chat |
| **Google Search** | `GOOGLE_API_KEY` | `GOOGLE_SEARCH_API_KEY` | Company research (future use) |

### 📁 **Files Updated**

#### Backend Services
- `app/services/llm_service.py` - Uses `GOOGLE_GEMINI_API_KEY`
- `app/services/company_research.py` - Uses `GOOGLE_GEMINI_API_KEY`

#### Configuration Files
- `env.template` - Updated variable names and descriptions
- `setup.py` - Updated API key references

#### Documentation
- `README.md` - Added Google Gemini to LLM providers and examples
- `LLM_PROVIDER_SELECTION.md` - Updated API key setup instructions
- `RESEARCH_PROVIDER_SELECTION.md` - Updated Google API references
- `IMPLEMENTATION_SUMMARY.md` - Updated configuration examples
- `COUNTRY_SPECIFIC_SEARCH.md` - Updated API key references

#### Test Files
- `test_research_provider.py` - Updated test environment variables
- `test_complete_functionality.py` - Updated API key checks

## Migration Steps

### 1. **Update Your `.env` File**

**Before:**
```env
GOOGLE_API_KEY=your_actual_google_api_key_here
```

**After:**
```env
GOOGLE_GEMINI_API_KEY=your_actual_google_api_key_here
```

### 2. **Verify Configuration**

Run the test script to verify everything works:
```bash
python test_llm_providers.py
```

You should see:
```
=== Testing GOOGLE ===
Connection: ✅ Connected
Available models: 39 models available
```

### 3. **Test the Application**

1. Start the application: `python app/main.py`
2. Go to the "Generate Cover Letter" tab
3. Select "Google Gemini" as the AI Model Provider
4. Verify that models load correctly
5. Test the chat & edit interface

## Why This Change Was Necessary

### 🚨 **The Problem**
- Both Google Gemini (LLM) and Google Search (company research) were using the same `GOOGLE_API_KEY` variable
- This caused conflicts and confusion about which service the API key was for
- Different Google services might require different types of API keys

### ✅ **The Solution**
- **`GOOGLE_GEMINI_API_KEY`**: Specifically for Google Gemini AI (text generation, chat)
- **`GOOGLE_SEARCH_API_KEY`**: Reserved for future Google Search API integration
- Clear separation of concerns and purposes

## Current Google Services Usage

### 🤖 **Google Gemini (LLM Service)**
- **Purpose**: Text generation for cover letters and chat
- **API Key**: `GOOGLE_GEMINI_API_KEY`
- **Source**: https://makersuite.google.com/app/apikey
- **Models**: Gemini-1.5 Flash, Gemini-1.5 Pro, etc.

### 🔍 **Google Gemini (Company Research)**
- **Purpose**: Company information research
- **API Key**: `GOOGLE_GEMINI_API_KEY` (same as LLM)
- **Source**: https://makersuite.google.com/app/apikey
- **Method**: Uses Gemini AI to research companies

### 🔍 **Google Search (Future)**
- **Purpose**: Web search for company information
- **API Key**: `GOOGLE_SEARCH_API_KEY` (reserved for future)
- **Source**: https://developers.google.com/custom-search/v1/overview
- **Status**: Not currently implemented

## API Key Setup Instructions

### Google Gemini API Key

1. **Visit Google AI Studio**: https://makersuite.google.com/app/apikey
2. **Sign in** with your Google account
3. **Click "Create API Key"**
4. **Copy the generated key** (starts with `AIzaSyC...`)
5. **Add to `.env` file**:
   ```env
   GOOGLE_GEMINI_API_KEY=AIzaSyC...your_actual_key_here
   ```

### Other API Keys (Optional)

```env
# For company research
TAVILY_API_KEY=tvly-your_tavily_api_key_here

# For other LLM providers
OPENAI_API_KEY=sk-your_openai_api_key_here
ANTHROPIC_API_KEY=sk-ant-your_anthropic_api_key_here

# For local LLM (no API key needed)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
```

## Troubleshooting

### ❌ **"API key not valid" Error**
- Ensure you're using the correct API key from Google AI Studio
- Check that the key starts with `AIzaSyC...`
- Verify the key is not truncated or corrupted

### ❌ **"GOOGLE_GEMINI_API_KEY not found" Warning**
- Add the API key to your `.env` file
- Restart the application after adding the key
- Check for typos in the variable name

### ❌ **Models Not Loading**
- Verify your API key is valid
- Check your internet connection
- Ensure Google AI Studio is accessible

### ❌ **Chat & Edit Model Selection Issues**
- The recent fix should resolve model selection persistence
- Try refreshing the page if issues persist
- Check browser console for JavaScript errors

## Benefits of This Change

### 🎯 **Clarity**
- Clear distinction between different Google services
- No more confusion about API key purposes
- Better documentation and examples

### 🔧 **Flexibility**
- Easy to add Google Search API in the future
- Independent configuration for each service
- Better error handling and debugging

### 📚 **Documentation**
- Updated all documentation to reflect changes
- Clear setup instructions for each service
- Consistent examples throughout

## Future Enhancements

### 🔍 **Google Search API Integration**
When Google Search API is implemented:
```env
GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
```

### 🔧 **Additional Google Services**
Future Google services can use their own dedicated variables:
```env
GOOGLE_VISION_API_KEY=your_google_vision_api_key_here
GOOGLE_TRANSLATE_API_KEY=your_google_translate_api_key_here
```

## Support

If you encounter any issues during migration:

1. **Check the troubleshooting section** above
2. **Run the test script**: `python test_llm_providers.py`
3. **Review the logs** for detailed error messages
4. **Open an issue** with specific error details

---

**Migration completed successfully! 🎉**

Your Google Gemini integration should now work perfectly with the new variable names. 