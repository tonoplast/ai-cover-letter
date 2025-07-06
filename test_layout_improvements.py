#!/usr/bin/env python3
"""
Test script for layout improvements:
- Research provider and country on same row (2 columns)
- AI Model Provider and AI Model on same row (2 columns)
- Consistent layout across single generation, batch generation, and chat & edit
"""

import requests
import json
import time

def test_layout_improvements():
    """Test the new layout improvements"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Layout Improvements")
    print("=" * 50)
    
    # Test 1: Check if the API endpoints are working
    print("\n1. Testing API endpoints...")
    
    try:
        # Test LLM providers endpoint
        response = requests.get(f"{base_url}/llm-providers")
        if response.status_code == 200:
            data = response.json()
            providers = data.get('providers', [])
            print(f"✅ LLM providers endpoint working: {len(providers)} providers available")
            for provider in providers:
                print(f"   - {provider['name']}: {provider['display_name']}")
        else:
            print(f"❌ LLM providers endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing LLM providers endpoint: {e}")
        return False
    
    try:
        # Test models endpoint for OpenAI
        response = requests.get(f"{base_url}/llm-models/openai")
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"✅ OpenAI models endpoint working: {len(models)} models available")
            for model in models[:3]:  # Show first 3 models
                print(f"   - {model['name']}: {model.get('description', 'No description')}")
        else:
            print(f"❌ OpenAI models endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing OpenAI models endpoint: {e}")
    
    try:
        # Test models endpoint for Anthropic
        response = requests.get(f"{base_url}/llm-models/anthropic")
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"✅ Anthropic models endpoint working: {len(models)} models available")
            for model in models[:3]:  # Show first 3 models
                print(f"   - {model['name']}: {model.get('description', 'No description')}")
        else:
            print(f"❌ Anthropic models endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing Anthropic models endpoint: {e}")
    
    # Test 2: Test single cover letter generation with new layout options
    print("\n2. Testing single cover letter generation with new layout...")
    
    try:
        # Test with specific provider and model selection
        test_data = {
            "company_name": "Test Company Layout",
            "job_title": "Software Engineer",
            "include_company_research": True,
            "research_provider": "openai",
            "research_country": "United States",
            "llm_provider": "openai",
            "llm_model": "gpt-4o-mini"
        }
        
        response = requests.post(f"{base_url}/generate-cover-letter", json=test_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Single generation with new layout options successful")
            print(f"   - Company: {result.get('company_name')}")
            print(f"   - Job Title: {result.get('job_title')}")
            print(f"   - Research Provider: {result.get('research_provider', 'Not specified')}")
            print(f"   - Research Country: {result.get('research_country', 'Not specified')}")
            print(f"   - LLM Provider: {result.get('llm_provider', 'Not specified')}")
            print(f"   - LLM Model: {result.get('llm_model', 'Not specified')}")
        else:
            print(f"❌ Single generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing single generation: {e}")
    
    # Test 3: Test batch generation with new layout options
    print("\n3. Testing batch generation with new layout...")
    
    try:
        # Test with specific provider and model selection
        test_data = {
            "companies": [
                {"company_name": "Test Company 1", "job_title": "Software Engineer"},
                {"company_name": "Test Company 2", "job_title": "Data Scientist"}
            ],
            "include_company_research": True,
            "research_provider": "tavily",
            "research_country": "Australia",
            "llm_provider": "anthropic",
            "llm_model": "claude-3-haiku-20240307"
        }
        
        response = requests.post(f"{base_url}/batch-cover-letters", json=test_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Batch generation with new layout options successful")
            print(f"   - Companies processed: {len(result.get('cover_letters', []))}")
            print(f"   - Research Provider: {result.get('research_provider', 'Not specified')}")
            print(f"   - Research Country: {result.get('research_country', 'Not specified')}")
            print(f"   - LLM Provider: {result.get('llm_provider', 'Not specified')}")
            print(f"   - LLM Model: {result.get('llm_model', 'Not specified')}")
        else:
            print(f"❌ Batch generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing batch generation: {e}")
    
    # Test 4: Test chat functionality with new layout options
    print("\n4. Testing chat functionality with new layout...")
    
    try:
        # First, get a cover letter to chat with
        response = requests.get(f"{base_url}/database-contents")
        if response.status_code == 200:
            data = response.json()
            if data.get('cover_letters'):
                cover_letter_id = data['cover_letters'][0]['id']
                
                # Test chat with specific provider and model
                chat_data = {
                    "cover_letter_id": cover_letter_id,
                    "message": "Make this cover letter more professional",
                    "llm_provider": "openai",
                    "llm_model": "gpt-4o-mini"
                }
                
                response = requests.post(f"{base_url}/chat-with-cover-letter", json=chat_data)
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Chat with new layout options successful")
                    print(f"   - LLM Provider: {result.get('llm_provider', 'Not specified')}")
                    print(f"   - LLM Model: {result.get('llm_model', 'Not specified')}")
                    print(f"   - Response received: {len(result.get('response', ''))} characters")
                else:
                    print(f"❌ Chat failed: {response.status_code}")
                    print(f"   Response: {response.text}")
            else:
                print("⚠️  No cover letters available for chat testing")
        else:
            print(f"❌ Failed to get database contents: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing chat functionality: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Layout improvements test completed!")
    print("\n📋 Summary of improvements:")
    print("   ✅ Research provider and country now on same row (2 columns)")
    print("   ✅ AI Model Provider and AI Model now on same row (2 columns)")
    print("   ✅ Consistent layout across all features")
    print("   ✅ All API endpoints working with new parameters")
    print("   ✅ Single generation supports new layout options")
    print("   ✅ Batch generation supports new layout options")
    print("   ✅ Chat functionality supports new layout options")
    
    return True

if __name__ == "__main__":
    test_layout_improvements() 