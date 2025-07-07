#!/usr/bin/env python3
"""
Test script for LLM-enhanced document upload functionality
"""

import requests
import json
import os
from pathlib import Path

def test_llm_upload():
    """Test the LLM-enhanced document upload functionality"""
    
    # Test server connection
    try:
        response = requests.get('http://localhost:8000/api')
        print("✅ Server is running")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return
    
    # Test LLM providers endpoint
    try:
        response = requests.get('http://localhost:8000/llm-providers')
        providers = response.json()
        print(f"✅ LLM providers available: {providers}")
    except Exception as e:
        print(f"❌ LLM providers test failed: {e}")
    
    # Test upload endpoint with LLM parameters
    test_file = Path("uploads/SungWookChung_CV.pdf")
    if test_file.exists():
        print(f"✅ Test file found: {test_file}")
        
        # Test upload with LLM extraction disabled
        print("\n--- Testing upload WITHOUT LLM extraction ---")
        with open(test_file, 'rb') as f:
            files = {'files': f}
            data = {
                'document_types': 'cv',
                'use_llm_extraction': 'false'
            }
            
            try:
                response = requests.post('http://localhost:8000/upload-multiple-documents', 
                                       files=files, data=data)
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Upload without LLM successful: {result['message']}")
                else:
                    print(f"❌ Upload without LLM failed: {response.text}")
            except Exception as e:
                print(f"❌ Upload without LLM failed: {e}")
        
        # Test upload with LLM extraction enabled
        print("\n--- Testing upload WITH LLM extraction ---")
        with open(test_file, 'rb') as f:
            files = {'files': f}
            data = {
                'document_types': 'cv',
                'use_llm_extraction': 'true',
                'llm_provider': 'ollama',
                'llm_model': 'llama3.2:latest'
            }
            
            try:
                response = requests.post('http://localhost:8000/upload-multiple-documents', 
                                       files=files, data=data)
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Upload with LLM successful: {result['message']}")
                    
                    # Check if LLM enhancement was applied
                    if result.get('uploaded_documents'):
                        doc_id = result['uploaded_documents'][0]['id']
                        doc_response = requests.get(f'http://localhost:8000/document/{doc_id}')
                        if doc_response.status_code == 200:
                            doc_data = doc_response.json()
                            parsed_data = doc_data.get('parsed_data', {})
                            if parsed_data.get('llm_enhanced'):
                                print(f"✅ LLM enhancement applied successfully")
                                print(f"   Provider: {parsed_data.get('llm_provider')}")
                                print(f"   Model: {parsed_data.get('llm_model')}")
                            else:
                                print(f"⚠️  LLM enhancement not applied: {parsed_data.get('llm_error', 'Unknown error')}")
                else:
                    print(f"❌ Upload with LLM failed: {response.text}")
            except Exception as e:
                print(f"❌ Upload with LLM failed: {e}")
    else:
        print(f"❌ Test file not found: {test_file}")

if __name__ == "__main__":
    test_llm_upload() 