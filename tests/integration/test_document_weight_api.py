#!/usr/bin/env python3
"""
Integration tests for document weight API endpoints
"""

import pytest
import requests

def test_update_document_weight_api(test_api_base_url):
    """Test the document weight update API endpoint"""
    base_url = test_api_base_url
    
    # Skip if API server is not running
    try:
        response = requests.get(f"{base_url}/database-contents", timeout=5)
        if response.status_code != 200:
            pytest.skip("API server not responding properly")
    except requests.exceptions.ConnectionError:
        pytest.skip("API server not running on localhost:8000. Start the server to run integration tests.")
    
    # Get list of documents
    response = requests.get(f"{base_url}/database-contents")
    data = response.json()
    
    if not data.get('documents'):
        pytest.skip("No documents in database for testing weight update")
    
    # Get the first document
    document = data['documents'][0]
    document_id = document['id']
    original_weight = document.get('manual_weight', 1.0)
    
    # Test updating weight to 2.5
    new_weight = 2.5
    update_response = requests.patch(
        f"{base_url}/documents/{document_id}/weight",
        json={"manual_weight": new_weight}
    )
    
    assert update_response.status_code == 200, f"Weight update failed: {update_response.text}"
    
    update_result = update_response.json()
    assert update_result['new_manual_weight'] == new_weight
    assert update_result['document_id'] == document_id
    assert 'filename' in update_result
    
    # Verify the weight was actually updated
    get_response = requests.get(f"{base_url}/documents/{document_id}/weight")
    assert get_response.status_code == 200
    
    get_result = get_response.json()
    assert get_result['manual_weight'] == new_weight
    assert get_result['document_id'] == document_id
    assert 'calculated_weight' in get_result
    assert 'weight_info' in get_result
    
    # Verify weight info structure
    weight_info = get_result['weight_info']
    assert 'manual_weight' in weight_info
    assert 'type_weight' in weight_info
    assert 'base_weight' in weight_info
    assert 'final_calculated_weight' in weight_info
    
    # Restore original weight
    restore_response = requests.patch(
        f"{base_url}/documents/{document_id}/weight",
        json={"manual_weight": original_weight}
    )
    assert restore_response.status_code == 200

def test_get_document_weight_info_api(test_api_base_url):
    """Test the document weight info API endpoint"""
    base_url = test_api_base_url
    
    # Skip if API server is not running
    try:
        response = requests.get(f"{base_url}/database-contents", timeout=5)
        if response.status_code != 200:
            pytest.skip("API server not responding properly")
    except requests.exceptions.ConnectionError:
        pytest.skip("API server not running on localhost:8000. Start the server to run integration tests.")
    
    # Get list of documents
    response = requests.get(f"{base_url}/database-contents")
    data = response.json()
    
    if not data.get('documents'):
        pytest.skip("No documents in database for testing weight info")
    
    # Get the first document
    document = data['documents'][0]
    document_id = document['id']
    
    # Get weight info
    get_response = requests.get(f"{base_url}/documents/{document_id}/weight")
    assert get_response.status_code == 200
    
    result = get_response.json()
    
    # Verify response structure
    assert 'document_id' in result
    assert 'filename' in result
    assert 'document_type' in result
    assert 'manual_weight' in result
    assert 'calculated_weight' in result
    assert 'weight_info' in result
    
    # Verify weight_info structure
    weight_info = result['weight_info']
    assert isinstance(weight_info['manual_weight'], (int, float))
    assert isinstance(weight_info['type_weight'], (int, float))
    assert isinstance(weight_info['base_weight'], (int, float))
    assert isinstance(weight_info['final_calculated_weight'], (int, float))
    
    # Verify calculated weight is positive
    assert result['calculated_weight'] > 0
    assert weight_info['final_calculated_weight'] > 0

def test_update_document_weight_validation(test_api_base_url):
    """Test document weight update validation"""
    base_url = test_api_base_url
    
    # Skip if API server is not running
    try:
        response = requests.get(f"{base_url}/database-contents", timeout=5)
        if response.status_code != 200:
            pytest.skip("API server not responding properly")
    except requests.exceptions.ConnectionError:
        pytest.skip("API server not running on localhost:8000. Start the server to run integration tests.")
    
    # Get list of documents
    response = requests.get(f"{base_url}/database-contents")
    data = response.json()
    
    if not data.get('documents'):
        pytest.skip("No documents in database for testing weight validation")
    
    document_id = data['documents'][0]['id']
    
    # Test negative weight (should fail)
    negative_response = requests.patch(
        f"{base_url}/documents/{document_id}/weight",
        json={"manual_weight": -1.0}
    )
    assert negative_response.status_code == 400
    
    # Test zero weight (should fail)
    zero_response = requests.patch(
        f"{base_url}/documents/{document_id}/weight",
        json={"manual_weight": 0.0}
    )
    assert zero_response.status_code == 400
    
    # Test valid weight (should succeed)
    valid_response = requests.patch(
        f"{base_url}/documents/{document_id}/weight",
        json={"manual_weight": 1.5}
    )
    assert valid_response.status_code == 200

def test_nonexistent_document_weight(test_api_base_url):
    """Test weight operations on nonexistent document"""
    base_url = test_api_base_url
    
    # Skip if API server is not running
    try:
        response = requests.get(f"{base_url}/database-contents", timeout=5)
        if response.status_code != 200:
            pytest.skip("API server not responding properly")
    except requests.exceptions.ConnectionError:
        pytest.skip("API server not running on localhost:8000. Start the server to run integration tests.")
    
    nonexistent_id = 99999
    
    # Test updating weight for nonexistent document
    update_response = requests.patch(
        f"{base_url}/documents/{nonexistent_id}/weight",
        json={"manual_weight": 2.0}
    )
    assert update_response.status_code == 404
    
    # Test getting weight info for nonexistent document
    get_response = requests.get(f"{base_url}/documents/{nonexistent_id}/weight")
    assert get_response.status_code == 404