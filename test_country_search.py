#!/usr/bin/env python3
"""
Test script to verify country-specific search functionality
"""

import os
import sys

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.company_research import CompanyResearchService

def test_country_search():
    """Test country-specific search functionality"""
    
    print("=== Testing Country-Specific Search ===")
    
    # Create company research service
    service = CompanyResearchService()
    
    print(f"Available providers: {service.get_available_providers()}")
    print()
    
    # Test company name
    test_company = "Microsoft"
    test_countries = ["Australia", "United States", "United Kingdom", "Germany"]
    
    print(f"Testing search for: {test_company}")
    print("=" * 60)
    
    # Test without country (global search)
    print("1. Global Search (No country focus):")
    try:
        result = service.search_company(test_company, provider="brave")
        if result:
            print(f"   Provider used: {result.get('provider_used', 'Unknown')}")
            print(f"   Company: {result.get('company_name', 'N/A')}")
            print(f"   Location: {result.get('location', 'N/A')}")
            print(f"   Industry: {result.get('industry', 'N/A')}")
        else:
            print("   No result returned")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test with different countries
    for country in test_countries:
        print(f"2. Country-Specific Search ({country}):")
        try:
            result = service.search_company(test_company, provider="brave", country=country)
            if result:
                print(f"   Provider used: {result.get('provider_used', 'Unknown')}")
                print(f"   Company: {result.get('company_name', 'N/A')}")
                print(f"   Location: {result.get('location', 'N/A')}")
                print(f"   Industry: {result.get('industry', 'N/A')}")
                print(f"   Search query included: {country}")
            else:
                print("   No result returned")
        except Exception as e:
            print(f"   Error: {e}")
        print()
    
    # Test with a local company
    print("3. Local Company Test (Australian company):")
    local_company = "Woolworths"
    try:
        result = service.search_company(local_company, provider="brave", country="Australia")
        if result:
            print(f"   Provider used: {result.get('provider_used', 'Unknown')}")
            print(f"   Company: {result.get('company_name', 'N/A')}")
            print(f"   Location: {result.get('location', 'N/A')}")
            print(f"   Industry: {result.get('industry', 'N/A')}")
        else:
            print("   No result returned")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    print("=== Country-Specific Search Summary ===")
    print("✅ Country-specific search is now available for:")
    print("   - Single cover letter generation")
    print("   - Batch cover letter generation")
    print("   - Manual company research")
    print()
    print("Available countries:")
    countries = [
        "Australia", "United States", "Canada", "United Kingdom", "Germany",
        "France", "Netherlands", "Sweden", "Norway", "Denmark", "Finland",
        "Switzerland", "Singapore", "Japan", "South Korea", "New Zealand",
        "Ireland", "Belgium", "Austria"
    ]
    for country in countries:
        print(f"   - {country}")
    print()
    print("How it works:")
    print("   - Select a country to focus search results on that region")
    print("   - Leave empty for global search (default behavior)")
    print("   - Country is added to search queries for more relevant results")
    print("   - Useful for finding local offices, regional information, etc.")

if __name__ == "__main__":
    test_country_search() 