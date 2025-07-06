#!/usr/bin/env python3
"""
Test script to verify LLM provider functionality
"""

import os
import sys

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.llm_service import LLMService

def test_llm_providers():
    """Test LLM provider functionality"""
    
    print("=== Testing LLM Providers ===")
    
    # Create LLM service
    llm_service = LLMService()
    
    print(f"Current provider: {llm_service.current_provider.value}")
    print(f"Current model: {llm_service.current_model}")
    print()
    
    # Test available providers
    print("=== Available Providers ===")
    providers = llm_service.get_available_providers()
    for provider in providers:
        status = "✅ Available" if provider['available'] else "❌ Not Available"
        api_key_required = " (API Key Required)" if provider['requires_api_key'] else ""
        print(f"{provider['display_name']}: {status}{api_key_required}")
        print(f"  Default model: {provider['default_model']}")
    print()
    
    # Test each provider
    test_providers = ['ollama', 'openai', 'anthropic', 'google']
    
    for provider_name in test_providers:
        print(f"=== Testing {provider_name.upper()} ===")
        
        try:
            # Create service with specific provider
            provider_service = LLMService(provider=provider_name)
            print(f"Provider: {provider_service.current_provider.value}")
            print(f"Model: {provider_service.current_model}")
            
            # Test connection
            connection_test = provider_service.test_connection()
            print(f"Connection: {'✅ Connected' if connection_test['connected'] else '❌ Failed'}")
            if connection_test['error']:
                print(f"Error: {connection_test['error']}")
            
            # List models
            models = provider_service.list_models()
            if models:
                print(f"Available models: {', '.join(models[:3])}{'...' if len(models) > 3 else ''}")
            else:
                print("No models available")
            
        except Exception as e:
            print(f"Error testing {provider_name}: {e}")
        
        print()
    
    # Test model listing for each provider
    print("=== Model Lists ===")
    for provider_name in test_providers:
        try:
            provider_service = LLMService(provider=provider_name)
            models = provider_service.list_models()
            if models:
                print(f"{provider_name.upper()}: {len(models)} models available")
                for model in models[:5]:  # Show first 5 models
                    print(f"  - {model}")
                if len(models) > 5:
                    print(f"  ... and {len(models) - 5} more")
            else:
                print(f"{provider_name.upper()}: No models available")
        except Exception as e:
            print(f"{provider_name.upper()}: Error - {e}")
        print()
    
    # Test text generation with different providers
    print("=== Text Generation Test ===")
    test_prompt = "Write a brief professional greeting."
    
    for provider_name in test_providers:
        try:
            provider_service = LLMService(provider=provider_name)
            print(f"Testing {provider_name.upper()}...")
            
            response = provider_service.generate_text(test_prompt, max_tokens=50, temperature=0.1)
            if response:
                print(f"✅ Response: {response[:100]}{'...' if len(response) > 100 else ''}")
            else:
                print("❌ No response")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        print()

if __name__ == "__main__":
    test_llm_providers() 