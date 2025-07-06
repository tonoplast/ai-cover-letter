#!/usr/bin/env python3
"""
Debug script to test Brave search functionality
"""

import os
import sys

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.company_research import CompanyResearchService

def debug_brave_search():
    """Debug Brave search functionality"""
    
    print("=== Debugging Brave Search ===")
    
    # Create company research service
    service = CompanyResearchService()
    
    print(f"Available providers: {service.get_available_providers()}")
    print()
    
    # Test company name
    test_company = "Microsoft"
    
    print(f"Testing Brave search for: {test_company}")
    print("-" * 50)
    
    try:
        # Test with Brave specifically
        result = service.search_company(test_company, provider="brave")
        
        if result:
            print("✅ Brave search successful!")
            print(f"Provider used: {result.get('provider_used', 'Unknown')}")
            print(f"Company: {result.get('company_name', 'N/A')}")
            print(f"Industry: {result.get('industry', 'N/A')}")
            print(f"Description: {result.get('description', 'N/A')[:100]}...")
            print(f"Website: {result.get('website', 'N/A')}")
            print(f"Mission: {result.get('mission', 'N/A')}")
            print(f"Vision: {result.get('vision', 'N/A')}")
            print(f"Values: {result.get('values', 'N/A')}")
        else:
            print("❌ Brave search returned no result")
            
    except Exception as e:
        print(f"❌ Brave search failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=== Testing Auto Provider ===")
    print("This should show which provider was actually used:")
    
    try:
        result = service.search_company(test_company)
        
        if result:
            print(f"Provider used: {result.get('provider_used', 'Unknown')}")
            print(f"Company: {result.get('company_name', 'N/A')}")
            print(f"Industry: {result.get('industry', 'N/A')}")
        else:
            print("❌ Auto search returned no result")
            
    except Exception as e:
        print(f"❌ Auto search failed with error: {e}")
    
    print()
    print("=== Environment Check ===")
    brave_key = os.getenv('BRAVE_API_KEY')
    if brave_key:
        print(f"✅ BRAVE_API_KEY found: {brave_key[:10]}...")
    else:
        print("❌ BRAVE_API_KEY not found (this is optional)")
    
    print()
    print("=== Rate Limiting Check ===")
    if 'brave' in service.rate_limiters:
        rate_limiter = service.rate_limiters['brave']
        print(f"Brave rate limiter: {rate_limiter.max_requests} requests per {rate_limiter.time_window} seconds")
        print(f"Can make request: {rate_limiter.can_make_request()}")
    else:
        print("❌ Brave rate limiter not found")

if __name__ == "__main__":
    debug_brave_search() 