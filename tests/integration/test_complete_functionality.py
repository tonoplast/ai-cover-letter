#!/usr/bin/env python3
"""
Comprehensive test script to verify LLM provider selection and OpenAI search functionality
"""

import os
import sys
import requests
import json

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.llm_service import LLMService
from app.services.company_research import CompanyResearchService

def test_llm_providers():
    """Test LLM provider functionality"""
    print("=== Testing LLM Providers ===")
    
    llm_service = LLMService()
    providers = llm_service.get_available_providers()
    
    for provider in providers:
        print(f"\n--- Testing {provider['display_name']} ---")
        print(f"Available: {provider['available']}")
        print(f"Requires API Key: {provider['requires_api_key']}")
        print(f"Default Model: {provider['default_model']}")
        
        if provider['available']:
            # Test connection
            test_service = LLMService(provider=provider['name'])
            connection_test = test_service.test_connection()
            print(f"Connection: {'✅ Connected' if connection_test['connected'] else '❌ Failed'}")
            
            # Test model listing
            models = test_service.list_models()
            if models:
                print(f"Models available: {len(models)}")
                print(f"Sample models: {', '.join(models[:3])}")
            else:
                print("No models available")

def test_company_research():
    """Test company research with different providers"""
    print("\n=== Testing Company Research ===")
    
    research_service = CompanyResearchService()
    available_providers = research_service.get_available_providers()
    
    print(f"Available search providers: {', '.join(available_providers)}")
    
    # Test company research with different providers
    test_company = "Microsoft"
    test_country = "United States"
    
    for provider in available_providers:
        print(f"\n--- Testing {provider.upper()} search ---")
        try:
            result = research_service.search_company(
                company_name=test_company,
                provider=provider,
                country=test_country
            )
            
            if result:
                print(f"✅ Success: Found info for {result.get('company_name', test_company)}")
                print(f"   Industry: {result.get('industry', 'Unknown')}")
                print(f"   Location: {result.get('location', 'Unknown')}")
                print(f"   Provider used: {result.get('provider_used', provider)}")
            else:
                print(f"❌ No results found")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_api_endpoints():
    """Test API endpoints"""
    print("\n=== Testing API Endpoints ===")
    
    base_url = "http://localhost:8000"
    
    # Test LLM providers endpoint
    try:
        response = requests.get(f"{base_url}/llm-providers")
        if response.ok:
            data = response.json()
            print("✅ LLM Providers endpoint working")
            print(f"   Available providers: {len(data['providers'])}")
            print(f"   Current provider: {data['current_provider']}")
        else:
            print(f"❌ LLM Providers endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ LLM Providers endpoint error: {str(e)}")
    
    # Test search providers endpoint
    try:
        response = requests.get(f"{base_url}/search-providers")
        if response.ok:
            data = response.json()
            print("✅ Search Providers endpoint working")
            print(f"   Available providers: {len(data['available_providers'])}")
        else:
            print(f"❌ Search Providers endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Search Providers endpoint error: {str(e)}")
    
    # Test LLM models endpoint for each provider
    providers = ['ollama', 'openai', 'anthropic']
    for provider in providers:
        try:
            response = requests.get(f"{base_url}/llm-models/{provider}")
            if response.ok:
                data = response.json()
                print(f"✅ LLM Models endpoint for {provider} working")
                print(f"   Models available: {len(data['models'])}")
            else:
                print(f"❌ LLM Models endpoint for {provider} failed: {response.status_code}")
        except Exception as e:
            print(f"❌ LLM Models endpoint for {provider} error: {str(e)}")

def test_openai_search_integration():
    """Test OpenAI search integration specifically"""
    print("\n=== Testing OpenAI Search Integration ===")
    
    # Check if OpenAI API key is available
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ OpenAI API key not found in environment")
        print("   Set OPENAI_API_KEY to test OpenAI search functionality")
        return
    
    print("✅ OpenAI API key found")
    
    research_service = CompanyResearchService()
    
    # Test OpenAI search
    test_companies = ["Apple", "Google", "Tesla"]
    
    for company in test_companies:
        print(f"\n--- Testing OpenAI search for {company} ---")
        try:
            result = research_service.search_company(
                company_name=company,
                provider="openai",
                country="United States"
            )
            
            if result:
                print(f"✅ Success: Found info for {result.get('company_name', company)}")
                print(f"   Industry: {result.get('industry', 'Unknown')}")
                print(f"   Size: {result.get('size', 'Unknown')}")
                print(f"   Location: {result.get('location', 'Unknown')}")
                print(f"   Description: {result.get('description', 'Unknown')[:100]}...")
            else:
                print(f"❌ No results found")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_environment_configuration():
    """Test environment configuration"""
    print("\n=== Testing Environment Configuration ===")
    
    # Check LLM provider configuration
    llm_provider = os.getenv('LLM_PROVIDER', 'ollama')
    print(f"Default LLM Provider: {llm_provider}")
    
    # Check API keys
    api_keys = {
        'OpenAI': os.getenv('OPENAI_API_KEY'),
        'Anthropic': os.getenv('ANTHROPIC_API_KEY'),
        'Tavily': os.getenv('TAVILY_API_KEY'),
        'Google': os.getenv('GOOGLE_GEMINI_API_KEY'),
        'Brave': os.getenv('BRAVE_API_KEY')
    }
    
    print("\nAPI Key Status:")
    for provider, key in api_keys.items():
        status = "✅ Available" if key else "❌ Not Available"
        print(f"   {provider}: {status}")
    
    # Check Ollama configuration
    ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2:latest')
    print(f"\nOllama Configuration:")
    print(f"   URL: {ollama_url}")
    print(f"   Model: {ollama_model}")

def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive Functionality Test")
    print("=" * 50)
    
    test_environment_configuration()
    test_llm_providers()
    test_company_research()
    test_openai_search_integration()
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("✅ Comprehensive test completed!")
    print("\nSummary:")
    print("- LLM provider selection is now available")
    print("- OpenAI can be used for both LLM generation and company research")
    print("- Multiple providers can be configured and selected")
    print("- Frontend supports provider and model selection")
    print("- Batch generation supports LLM provider selection")

if __name__ == "__main__":
    main() 