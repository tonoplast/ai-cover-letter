# LLM Provider Selection Feature

## Overview

The AI Cover Letter Generator now supports multiple LLM (Large Language Model) providers, allowing you to choose between different AI services for cover letter generation. This provides flexibility in terms of cost, performance, and privacy.

## Supported Providers

### 1. **Ollama (Local)**
- **Type**: Local deployment
- **Cost**: Free (runs on your machine)
- **Privacy**: 100% private (no data leaves your machine)
- **Setup**: Requires Ollama installation
- **Models**: llama3.2, llama2, mistral, codellama, etc.
- **Best for**: Privacy-conscious users, offline use

### 2. **OpenAI**
- **Type**: Cloud service
- **Cost**: Pay-per-use (varies by model)
- **Privacy**: Data sent to OpenAI servers
- **Setup**: Requires API key
- **Models**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
- **Best for**: High-quality results, advanced features

### 3. **Anthropic Claude**
- **Type**: Cloud service
- **Cost**: Pay-per-use (varies by model)
- **Privacy**: Data sent to Anthropic servers
- **Setup**: Requires API key
- **Models**: Claude-3 Opus, Claude-3 Sonnet, Claude-3 Haiku
- **Best for**: High-quality results, safety-focused

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
```

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

#### Ollama
1. Install Ollama: https://ollama.ai/
2. Run: `ollama serve`
3. Pull a model: `ollama pull llama3.2:latest`
4. No API key needed

## Usage

### Single Cover Letter Generation
1. Fill in job details (title, company, description)
2. Select **AI Model Provider** from dropdown
3. Select **AI Model** (optional - uses default if not specified)
4. Generate cover letter

### Provider Selection Logic
- **Auto (Use Default)**: Uses the provider configured in `.env`
- **Specific Provider**: Uses the selected provider with its default model
- **Specific Model**: Uses the selected provider with the specified model

## Model Comparison

| Provider | Model | Quality | Speed | Cost | Best For |
|----------|-------|---------|-------|------|----------|
| **Ollama** | llama3.2 | Good | Fast | Free | Privacy, local use |
| **Ollama** | llama2 | Good | Fast | Free | Privacy, local use |
| **OpenAI** | GPT-4 | Excellent | Medium | High | Best quality |
| **OpenAI** | GPT-3.5 | Good | Fast | Low | Cost-effective |
| **Anthropic** | Claude-3 Opus | Excellent | Slow | High | Best quality |
| **Anthropic** | Claude-3 Sonnet | Good | Medium | Medium | Balanced |

## Features

### Provider Detection
- Automatically detects available providers
- Shows availability status (✅/❌)
- Disables unavailable providers in UI

### Model Listing
- Dynamically loads available models for each provider
- Shows default model for each provider
- Handles provider-specific model formats

### Connection Testing
- Tests connection to each provider
- Validates API keys and model availability
- Provides detailed error messages

### Fallback Handling
- Falls back to default provider if selected provider fails
- Graceful error handling for API failures
- Continues operation even if some providers are unavailable

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

## Benefits

### 1. **Flexibility**
- Choose the provider that best fits your needs
- Switch between providers without changing code
- Use different providers for different use cases

### 2. **Cost Control**
- Use free local Ollama for development
- Use paid services only when needed
- Compare costs between providers

### 3. **Privacy Options**
- Use local Ollama for complete privacy
- Use cloud providers for convenience
- Choose based on data sensitivity

### 4. **Performance**
- Use faster models for quick iterations
- Use higher-quality models for final versions
- Optimize for your specific needs

## Troubleshooting

### Ollama Issues
- **Not running**: Start with `ollama serve`
- **Model not found**: Pull with `ollama pull model-name`
- **Connection error**: Check if Ollama is running on correct port

### OpenAI Issues
- **API key invalid**: Check key format and permissions
- **Rate limited**: Wait or upgrade plan
- **Model not available**: Check model name and availability

### Anthropic Issues
- **API key invalid**: Check key format and permissions
- **Model not available**: Check model name and availability
- **Rate limited**: Wait or upgrade plan

## Best Practices

### For Development
- Use Ollama for local development
- Test with different providers before production
- Keep API keys secure

### For Production
- Use reliable cloud providers
- Implement proper error handling
- Monitor API usage and costs

### For Privacy
- Use Ollama for sensitive data
- Review privacy policies of cloud providers
- Consider data retention policies

## Future Enhancements

Potential future improvements:
- **More providers**: Google Gemini, Cohere, etc.
- **Model fine-tuning**: Custom models for specific domains
- **Batch processing**: Use different providers for different tasks
- **Cost optimization**: Automatic provider selection based on cost
- **Performance monitoring**: Track response times and quality 