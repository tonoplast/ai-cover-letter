# LLM Provider Selection Feature

## Overview

The AI Cover Letter Generator now supports multiple LLM (Large Language Model) providers with dynamic model selection, allowing you to choose between different AI services for cover letter generation. This provides flexibility in terms of cost, performance, privacy, and quality.

## Supported Providers

### 1. **Ollama (Local)**
- **Type**: Local deployment
- **Cost**: Free (runs on your machine)
- **Privacy**: 100% private (no data leaves your machine)
- **Setup**: Requires Ollama installation
- **Models**: llama3.2, llama2, mistral, codellama, etc. (dynamically loaded)
- **Best for**: Privacy-conscious users, offline use, development

### 2. **OpenAI**
- **Type**: Cloud service
- **Cost**: Pay-per-use (varies by model)
- **Privacy**: Data sent to OpenAI servers
- **Setup**: Requires API key
- **Models**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo (dynamically loaded)
- **Best for**: High-quality results, advanced features, AI-powered search

### 3. **Anthropic Claude**
- **Type**: Cloud service
- **Cost**: Pay-per-use (varies by model)
- **Privacy**: Data sent to Anthropic servers
- **Setup**: Requires API key
- **Models**: Claude-3 Opus, Claude-3 Sonnet, Claude-3 Haiku (dynamically loaded)
- **Best for**: High-quality results, safety-focused, advanced reasoning

### 4. **Google Gemini**
- **Type**: Cloud service
- **Cost**: Pay-per-use (varies by model)
- **Privacy**: Data sent to Google servers
- **Setup**: Requires API key
- **Models**: Gemini-1.5 Flash, Gemini-1.5 Pro, Gemini-1.0 Pro (dynamically loaded)
- **Best for**: Fast responses, cost-effective, good quality

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
# Default LLM provider (ollama, openai, anthropic)
LLM_PROVIDER=ollama

# Ollama configuration (local - no API key required)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest

# OpenAI configuration (requires API key)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Anthropic Claude configuration (requires API key)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Google Gemini configuration (requires API key)
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL=gemini-1.5-flash

### API Key Setup

#### OpenAI
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an account and add payment method
3. Generate an API key
4. Add to `.env`: `OPENAI_API_KEY=sk-your-key-here`

#### Anthropic
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create an account and add payment method
3. Generate an API key
4. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-your-key-here`

#### Google Gemini
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an account and add payment method
3. Generate an API key
4. Add to `.env`: `GOOGLE_API_KEY=your-key-here`

#### Ollama
1. Install Ollama: https://ollama.ai/
2. Run: `ollama serve`
3. Pull a model: `ollama pull llama3.2:latest`
4. No API key needed

## Usage

### Single Cover Letter Generation
1. Fill in job details (title, company, description)
2. Select **AI Model Provider** from dropdown (Auto/Ollama/OpenAI/Anthropic/Google)
3. Select **AI Model** (Auto/Provider-specific models)
4. Generate cover letter

### Chat & Edit Interface
1. Select a cover letter from the sidebar
2. Choose **AI Model Provider** in chat settings
3. Choose **AI Model** (optional - uses default if not specified)
4. Send chat message to modify cover letter

### Batch Generation
1. Configure **AI Model Provider** for batch operations
2. Configure **AI Model** for batch operations
3. Run batch generation with consistent model across all jobs

### Provider Selection Logic
- **Auto (Use Default)**: Uses the provider configured in `.env`
- **Specific Provider**: Uses the selected provider with its default model
- **Specific Model**: Uses the selected provider with the specified model

### Google Models
- Attempts to fetch from Google AI API
- Falls back to common models if API fails
- Shows all available Gemini models

## Dynamic Model Loading

The system automatically loads available models for each provider:

### Ollama Models
- Dynamically fetches models using `ollama list` equivalent
- Shows all available local models
- Validates default model is available

### OpenAI Models
- Attempts to fetch from OpenAI API
- Falls back to common models if API fails
- Filters for chat models (excludes instruct models)

### Anthropic Models
- Attempts to fetch from Anthropic API
- Falls back to common models if API fails
- Shows all available Claude models

## Model Comparison

| Provider | Model | Quality | Speed | Cost | Best For |
|----------|-------|---------|-------|------|----------|
| **Ollama** | llama3.2 | Good | Fast | Free | Privacy, local use |
| **Ollama** | llama2 | Good | Fast | Free | Privacy, local use |
| **Ollama** | mistral | Good | Fast | Free | Privacy, local use |
| **OpenAI** | GPT-4 | Excellent | Medium | High | Best quality |
| **OpenAI** | GPT-4 Turbo | Excellent | Fast | High | Best quality, fast |
| **OpenAI** | GPT-3.5 | Good | Fast | Low | Cost-effective |
| **Anthropic** | Claude-3 Opus | Excellent | Slow | High | Best quality |
| **Anthropic** | Claude-3 Sonnet | Good | Medium | Medium | Balanced |
| **Anthropic** | Claude-3 Haiku | Good | Fast | Low | Cost-effective |
| **Google** | Gemini-1.5 Pro | Excellent | Medium | Medium | Best quality |
| **Google** | Gemini-1.5 Flash | Good | Fast | Low | Cost-effective |
| **Google** | Gemini-1.0 Pro | Good | Medium | Low | Balanced |

## Features

### Provider Detection
- Automatically detects available providers
- Shows availability status (✅/❌)
- Disables unavailable providers in UI
- Updates all provider dropdowns simultaneously

### Dynamic Model Loading
- Models load automatically when provider is selected
- Shows default model for each provider
- Handles provider-specific model formats
- Graceful fallback when API calls fail

### Connection Testing
- Tests connection to each provider
- Validates API keys and model availability
- Provides detailed error messages
- Helps troubleshoot configuration issues

### Fallback Handling
- Falls back to default provider if selected provider fails
- Graceful error handling for API failures
- Continues operation even if some providers are unavailable
- Clear error messages for troubleshooting

### Chat Integration
- LLM provider selection in chat & edit interface
- Real-time model loading for chat
- Consistent provider/model selection across all features
- Enhanced chat experience with preferred models

## API Endpoints

### Get Available Providers
```bash
GET /llm-providers
```
Returns list of available providers with their status.

### Get Models for Provider
```bash
GET /llm-models/{provider}
```
Returns available models for a specific provider.

### Test Connection
```bash
POST /test-llm-connection
```
Tests connection to a specific provider and model.

## Testing

Run the test script to verify functionality:
```bash
python test_llm_providers.py
```

This will test:
- Provider availability detection
- Model listing for each provider
- Connection testing
- Text generation with different providers
- Dynamic model loading
- Chat integration

## Benefits

### 1. **Flexibility**
- Choose the provider that best fits your needs
- Switch between providers without changing code
- Use different providers for different use cases
- Dynamic model selection for fine-tuned control

### 2. **Cost Control**
- Use free local Ollama for development
- Use paid services only when needed
- Compare costs between providers
- Choose cost-effective models for different tasks

### 3. **Privacy Options**
- Use local Ollama for complete privacy
- Use cloud providers for convenience
- Choose based on data sensitivity
- Self-hosted options available

### 4. **Performance**
- Use faster models for quick iterations
- Use higher-quality models for final versions
- Optimize for your specific needs
- Dynamic model loading prevents selection of unavailable models

### 5. **Enhanced User Experience**
- Clean, logical interface with all options easily accessible
- Provider availability indicators for clear feedback
- Consistent interface across all features
- Real-time model loading and validation

## Troubleshooting

### Ollama Issues
- **Not running**: Start with `ollama serve`
- **Model not found**: Pull with `ollama pull model-name`
- **Connection error**: Check if Ollama is running on correct port
- **No models showing**: Run `ollama list` to verify models are installed

### OpenAI Issues
- **API key invalid**: Check key format and permissions
- **Rate limited**: Wait or upgrade plan
- **Model not available**: Check model name and availability
- **Models not loading**: Check API key and internet connection

### Anthropic Issues
- **API key invalid**: Check key format and permissions
- **Model not available**: Check model name and availability
- **Rate limited**: Wait or upgrade plan
- **Models not loading**: Check API key and internet connection

### Google Issues
- **API key invalid**: Check key format and permissions
- **Rate limited**: Wait or upgrade plan
- **Model not available**: Check model name and availability
- **Models not loading**: Check API key and internet connection

### General Issues
- **No providers showing**: Check your `.env` configuration
- **Models not loading**: Check provider availability and API keys
- **Chat not working**: Verify LLM provider is configured correctly
- **Generation failing**: Check provider connection and model availability

## Best Practices

### For Development
- Use Ollama for local development
- Test with different providers before production
- Keep API keys secure
- Use dynamic model loading to verify availability

### For Production
- Configure multiple providers for redundancy
- Use appropriate models for different tasks
- Monitor API usage and costs
- Test provider connections regularly

### For Privacy
- Use Ollama for sensitive data
- Consider self-hosted options for complete control
- Review privacy policies of cloud providers
- Use local models when possible

### For Cost Optimization
- Use free providers for development and testing
- Choose cost-effective models for routine tasks
- Use high-quality models only for final versions
- Monitor API usage to control costs

## Future Enhancements

Potential future improvements:
- **More providers**: Google Gemini, Cohere, etc.
- **Model fine-tuning**: Custom models for specific domains
- **Batch processing**: Use different providers for different tasks
- **Cost optimization**: Automatic provider selection based on cost
- **Performance monitoring**: Track response times and quality 