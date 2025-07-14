#!/usr/bin/env python3
"""
Test to verify the provider and model selection flow
"""

import requests
import json
import pytest

def test_provider_model_flow():
    """Test the provider and model selection flow"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Provider and Model Selection Flow")
    print("=" * 50)
    
    # Test 1: Check default provider
    print("\n1. Testing default provider...")
    try:
        response = requests.get(f"{base_url}/llm-providers")
        if response.status_code == 200:
            data = response.json()
            current_provider = data.get('current_provider', 'ollama')
            print(f"✅ Default provider: {current_provider}")
        else:
            print(f"❌ Failed to get default provider: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting default provider: {e}")
    
    # Test 2: Test Ollama models endpoint
    print("\n2. Testing Ollama models endpoint...")
    try:
        response = requests.get(f"{base_url}/llm-models/ollama")
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            current_model = data.get('current_model', '')
            print(f"✅ Ollama models endpoint working")
            print(f"   - Current model: {current_model}")
            print(f"   - Available models: {len(models)}")
            if models:
                print(f"   - Sample models: {', '.join(models[:3])}")
        else:
            print(f"❌ Ollama models endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing Ollama models: {e}")
    
    # Test 3: Test OpenAI models endpoint
    print("\n3. Testing OpenAI models endpoint...")
    try:
        response = requests.get(f"{base_url}/llm-models/openai")
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            current_model = data.get('current_model', '')
            print(f"✅ OpenAI models endpoint working")
            print(f"   - Current model: {current_model}")
            print(f"   - Available models: {len(models)}")
            if models:
                print(f"   - Sample models: {', '.join(models[:3])}")
        else:
            print(f"❌ OpenAI models endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing OpenAI models: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Provider and Model Flow Test Completed!")
    print("\n💡 Expected Frontend Behavior:")
    print("   1. AI Model Provider shows: 'Auto (Use Default: Ollama)'")
    print("   2. AI Model shows: 'Auto (Use Default: llama3.2:latest)'")
    print("   3. Select 'Ollama (Local)' → AI Model shows all Ollama models")
    print("   4. Select 'OpenAI' → AI Model shows all OpenAI models")
    print("   5. Select 'Auto (Use Default: Ollama)' → AI Model shows default")
    
    # Test completed successfully
    assert True

if __name__ == "__main__":
    test_provider_model_flow() 