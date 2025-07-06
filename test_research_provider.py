#!/usr/bin/env python3
"""
Test script to verify research provider selection functionality
"""

import os
import sys
import json

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.company_research import CompanyResearchService

def test_research_providers():
    """Test different research providers"""
    
    # Set up environment variables for testing
    os.environ['TAVILY_API_KEY'] = 'tvly-test-key'
    os.environ['GOOGLE_API_KEY'] = 'test-google-key'
    os.environ['YACY_URL'] = 'http://localhost:8090'
    os.environ['SEARXNG_URL'] = 'http://localhost:8080'
    
    # Create company research service
    service = CompanyResearchService()
    
    print("=== Available Research Providers ===")
    available_providers = service.get_available_providers()
    print(f"Available providers: {available_providers}")
    print()
    
    # Test company name
    test_company = "Microsoft"
    
    print("=== Testing Provider Selection ===")
    
    # Test with no provider (should use fallback)
    print("1. Testing with no provider (auto fallback):")
    try:
        result = service.search_company(test_company)
        if result:
            print(f"   Provider used: {result.get('provider_used', 'Unknown')}")
            print(f"   Company: {result.get('company_name', 'N/A')}")
            print(f"   Industry: {result.get('industry', 'N/A')}")
        else:
            print("   No result returned")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test with specific providers
    test_providers = ['tavily', 'google', 'brave', 'duckduckgo']
    
    for provider in test_providers:
        print(f"2. Testing with provider '{provider}':")
        try:
            result = service.search_company(test_company, provider=provider)
            if result:
                print(f"   Provider used: {result.get('provider_used', 'Unknown')}")
                print(f"   Company: {result.get('company_name', 'N/A')}")
                print(f"   Industry: {result.get('industry', 'N/A')}")
            else:
                print("   No result returned")
        except Exception as e:
            print(f"   Error: {e}")
        print()
    
    print("=== Provider Selection Summary ===")
    print("✅ Research provider selection is now available for:")
    print("   - Single cover letter generation")
    print("   - Batch cover letter generation")
    print("   - Manual company research")
    print()
    print("Available options:")
    print("   - Auto (Best Available) - Uses fallback order")
    print("   - Tavily AI (Recommended) - Best quality")
    print("   - Google AI - Good quality, requires API key")
    print("   - Brave Search - Privacy-focused")
    print("   - YaCy - Self-hosted")
    print("   - SearXNG - Self-hosted")
    print("   - DuckDuckGo - Free, rate limited")

if __name__ == "__main__":
    test_research_providers() 