#!/usr/bin/env python3
"""
Test to verify Ollama model loading in the frontend
"""

import requests
import json

def test_ollama_frontend():
    """Test Ollama model loading behavior"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Ollama Frontend Model Loading")
    print("=" * 50)
    
    # Test 1: Check if Ollama models endpoint returns data
    print("\n1. Testing Ollama models endpoint...")
    try:
        response = requests.get(f"{base_url}/llm-models/ollama")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ollama models endpoint working")
            print(f"   - Provider: {data.get('provider')}")
            print(f"   - Models count: {len(data.get('models', []))}")
            print(f"   - Current model: {data.get('current_model')}")
            print(f"   - Sample models: {', '.join(data.get('models', [])[:3])}")
            
            if not data.get('models'):
                print("   ⚠️  No models returned - this might be the issue!")
            else:
                print("   ✅ Models are being returned correctly")
        else:
            print(f"❌ Ollama models endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing Ollama models endpoint: {e}")
    
    # Test 2: Check if Ollama is running locally
    print("\n2. Testing Ollama local connection...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ollama is running locally")
            print(f"   - Available models: {len(data.get('models', []))}")
            if data.get('models'):
                print(f"   - Model names: {[m.get('name') for m in data.get('models', [])[:3]]}")
        else:
            print(f"❌ Ollama local connection failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Ollama local connection error: {e}")
        print("   💡 Make sure Ollama is running: ollama serve")
    
    # Test 3: Check LLM providers endpoint
    print("\n3. Testing LLM providers endpoint...")
    try:
        response = requests.get(f"{base_url}/llm-providers")
        if response.status_code == 200:
            data = response.json()
            providers = data.get('providers', [])
            print(f"✅ LLM providers endpoint working")
            for provider in providers:
                print(f"   - {provider['name']}: {provider['display_name']} (Available: {provider['available']})")
        else:
            print(f"❌ LLM providers endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing LLM providers endpoint: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Ollama frontend test completed!")
    print("\n💡 Troubleshooting steps:")
    print("   1. Make sure Ollama is running: ollama serve")
    print("   2. Check browser console for JavaScript errors")
    print("   3. Try selecting 'ollama' in the AI Model Provider dropdown")
    print("   4. The AI Model dropdown should appear with available models")
    
    return True

if __name__ == "__main__":
    test_ollama_frontend() 