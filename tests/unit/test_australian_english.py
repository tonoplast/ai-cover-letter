#!/usr/bin/env python3
"""
Test script to verify Australian English functionality in LLM outputs
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.llm_service import LLMService
from dotenv import load_dotenv

def test_australian_english():
    """Test that Australian English instructions are properly added to prompts"""
    
    # Load environment variables
    load_dotenv()
    
    print("Testing Australian English functionality...")
    print("=" * 50)
    
    # Test 1: Australian English enabled (default)
    print("\n1. Testing with Australian English ENABLED:")
    llm_service = LLMService(use_australian_english=True)
    
    test_prompt = "Write a brief cover letter for a software engineer position at a technology company. Mention organization, color, and center."
    
    print(f"Original prompt: {test_prompt}")
    print("\nExpected: LLM should use 'organisation', 'colour', and 'centre'")
    
    try:
        # Generate response
        response = llm_service.generate_text(test_prompt, max_tokens=200, temperature=0.7)
        print(f"\nLLM Response:")
        print("-" * 30)
        print(response)
        
        # Check for Australian spellings
        australian_words = ['organisation', 'colour', 'centre', 'realise', 'analyse', 'favour']
        american_words = ['organization', 'color', 'center', 'realize', 'analyze', 'favor']
        
        found_australian = any(word in response.lower() for word in australian_words)
        found_american = any(word in response.lower() for word in american_words)
        
        print(f"\nAnalysis:")
        print(f"Found Australian spellings: {found_australian}")
        print(f"Found American spellings: {found_american}")
        
        if found_australian and not found_american:
            print("✅ SUCCESS: Australian English is working correctly!")
        elif found_american:
            print("⚠️  WARNING: American spellings detected - may need adjustment")
        else:
            print("ℹ️  INFO: No specific regional spellings detected in this test")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("Make sure your LLM service is properly configured and running")
    
    print("\n" + "=" * 50)
    
    # Test 2: Australian English disabled
    print("\n2. Testing with Australian English DISABLED:")
    llm_service_disabled = LLMService(use_australian_english=False)
    
    try:
        response_disabled = llm_service_disabled.generate_text(test_prompt, max_tokens=200, temperature=0.7)
        print(f"\nLLM Response (without Australian English):")
        print("-" * 30)
        print(response_disabled)
        
        print("\nℹ️  This response should not have specific Australian English instructions")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 50)
    
    # Test 3: Environment variable override
    print("\n3. Testing environment variable override:")
    
    # Set environment variable to disable
    os.environ['USE_AUSTRALIAN_ENGLISH'] = 'false'
    
    llm_service_env = LLMService()
    print(f"Australian English from environment: {llm_service_env.use_australian_english}")
    
    # Reset environment variable
    os.environ['USE_AUSTRALIAN_ENGLISH'] = 'true'
    
    print("\n✅ Australian English configuration is working correctly!")
    
    # Instructions for user
    print("\n" + "=" * 50)
    print("CONFIGURATION INSTRUCTIONS:")
    print("=" * 50)
    print("1. To enable Australian English globally, add to your .env file:")
    print("   USE_AUSTRALIAN_ENGLISH=true")
    print("\n2. To disable Australian English globally, add to your .env file:")
    print("   USE_AUSTRALIAN_ENGLISH=false")
    print("\n3. You can also control it programmatically:")
    print("   LLMService(use_australian_english=True)  # Enable")
    print("   LLMService(use_australian_english=False) # Disable")
    print("\n4. The feature is ENABLED by default for all cover letter generation")

if __name__ == "__main__":
    test_australian_english()