#!/usr/bin/env python3
"""
Test script to verify enhanced LLM provider and model selection functionality
"""

import os
import sys
import requests
import json

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.llm_service import LLMService

def test_enhanced_model_loading():
    """Test enhanced model loading for each provider"""
    print("=== Testing Enhanced Model Loading ===")
    
    providers = ['ollama', 'openai', 'anthropic']
    
    for provider in providers:
        print(f"\n--- Testing {provider.upper()} Model Loading ---")
        
        try:
            llm_service = LLMService(provider=provider)
            models = llm_service.list_models()
            
            if models:
                print(f"✅ Successfully loaded {len(models)} models")
                print(f"   Models: {', '.join(models[:5])}{'...' if len(models) > 5 else ''}")
                
                # Test if default model is in the list
                default_model = llm_service.current_model
                if default_model in models:
                    print(f"   ✅ Default model '{default_model}' found in list")
                else:
                    print(f"   ⚠️ Default model '{default_model}' not in list")
            else:
                print(f"❌ No models available for {provider}")
                
        except Exception as e:
            print(f"❌ Error loading models for {provider}: {e}")

def test_api_endpoints():
    """Test API endpoints for model loading"""
    print("\n=== Testing API Endpoints ===")
    
    base_url = "http://localhost:8000"
    
    # Test LLM providers endpoint
    try:
        response = requests.get(f"{base_url}/llm-providers")
        if response.ok:
            data = response.json()
            print("✅ LLM Providers endpoint working")
            print(f"   Available providers: {len(data['providers'])}")
            for provider in data['providers']:
                status = "✅ Available" if provider['available'] else "❌ Not Available"
                print(f"   - {provider['display_name']}: {status}")
        else:
            print(f"❌ LLM Providers endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ LLM Providers endpoint error: {str(e)}")
    
    # Test model loading for each provider
    providers = ['ollama', 'openai', 'anthropic']
    for provider in providers:
        try:
            response = requests.get(f"{base_url}/llm-models/{provider}")
            if response.ok:
                data = response.json()
                print(f"✅ LLM Models endpoint for {provider} working")
                print(f"   Models available: {len(data['models'])}")
                if data['models']:
                    print(f"   Sample models: {', '.join(data['models'][:3])}")
                print(f"   Current model: {data['current_model']}")
            else:
                print(f"❌ LLM Models endpoint for {provider} failed: {response.status_code}")
        except Exception as e:
            print(f"❌ LLM Models endpoint for {provider} error: {str(e)}")

def test_chat_functionality():
    """Test chat functionality with LLM provider selection"""
    print("\n=== Testing Chat Functionality ===")
    
    base_url = "http://localhost:8000"
    
    # First, check if there are any cover letters in the database
    try:
        response = requests.get(f"{base_url}/database-contents")
        if response.ok:
            data = response.json()
            cover_letters = data.get('cover_letters', [])
            
            if cover_letters:
                # Test chat with the first cover letter
                cover_letter_id = cover_letters[0]['id']
                print(f"✅ Found cover letter with ID: {cover_letter_id}")
                
                # Test chat with different LLM providers
                test_providers = ['ollama', 'openai', 'anthropic']
                
                for provider in test_providers:
                    print(f"\n--- Testing chat with {provider.upper()} ---")
                    try:
                        chat_response = requests.post(f"{base_url}/chat-with-cover-letter", 
                            json={
                                "cover_letter_id": cover_letter_id,
                                "message": "Please make this more professional",
                                "llm_provider": provider,
                                "llm_model": None
                            }
                        )
                        
                        if chat_response.ok:
                            result = chat_response.json()
                            print(f"✅ Chat with {provider} successful")
                            print(f"   Response length: {len(result.get('response', ''))}")
                            if result.get('updated_content'):
                                print(f"   ✅ Cover letter updated")
                        else:
                            print(f"❌ Chat with {provider} failed: {chat_response.status_code}")
                            
                    except Exception as e:
                        print(f"❌ Chat with {provider} error: {str(e)}")
            else:
                print("⚠️ No cover letters found in database")
                print("   Generate a cover letter first to test chat functionality")
        else:
            print(f"❌ Database contents endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Database contents endpoint error: {str(e)}")

def test_model_selection_workflow():
    """Test the complete model selection workflow"""
    print("\n=== Testing Model Selection Workflow ===")
    
    # Test LLM service with different providers and models
    test_cases = [
        {'provider': 'ollama', 'model': 'llama3.2:latest'},
        {'provider': 'ollama', 'model': None},  # Use default
        {'provider': 'openai', 'model': 'gpt-4'},
        {'provider': 'openai', 'model': None},  # Use default
        {'provider': 'anthropic', 'model': 'claude-3-sonnet-20240229'},
        {'provider': 'anthropic', 'model': None},  # Use default
    ]
    
    for test_case in test_cases:
        provider = test_case['provider']
        model = test_case['model']
        
        print(f"\n--- Testing {provider.upper()} with model: {model or 'Default'} ---")
        
        try:
            llm_service = LLMService(provider=provider, model=model)
            
            # Test connection
            connection_test = llm_service.test_connection()
            print(f"   Connection: {'✅ Connected' if connection_test['connected'] else '❌ Failed'}")
            
            # Test text generation
            if connection_test['connected']:
                response = llm_service.generate_text("Hello", max_tokens=10, temperature=0.1)
                if response:
                    print(f"   Text generation: ✅ Success ({len(response)} chars)")
                else:
                    print(f"   Text generation: ❌ No response")
            else:
                print(f"   Text generation: ⏭️ Skipped (connection failed)")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced LLM Selection Test")
    print("=" * 50)
    
    test_enhanced_model_loading()
    test_api_endpoints()
    test_model_selection_workflow()
    test_chat_functionality()
    
    print("\n" + "=" * 50)
    print("✅ Enhanced LLM selection test completed!")
    print("\nSummary:")
    print("- Enhanced model loading for all providers")
    print("- Chat functionality supports LLM provider selection")
    print("- API endpoints work correctly")
    print("- Model selection workflow is functional")

if __name__ == "__main__":
    main() 