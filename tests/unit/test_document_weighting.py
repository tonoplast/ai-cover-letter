#!/usr/bin/env python3
"""
Test script for document weighting system
"""

import pytest
from datetime import datetime, timedelta

def test_document_weighting(rag_service, mock_document_class):
    """Test the document weighting system"""
    
    # Test configuration
    assert rag_service.base_weight == 1.0
    assert rag_service.recency_period_days == 365
    assert rag_service.min_weight_multiplier == 0.1
    assert rag_service.recency_weighting_enabled == True
    
    # Test document type weights
    expected_weights = {
        'cv': 2.0,
        'cover_letter': 1.8,
        'linkedin': 1.2,
        'other': 0.8
    }
    
    for doc_type, expected_weight in expected_weights.items():
        actual_weight = rag_service.get_document_type_weight(doc_type)
        assert actual_weight == expected_weight, f"Expected {doc_type} weight {expected_weight}, got {actual_weight}"
    
    # Test recent CV document
    recent_cv = mock_document_class('cv', datetime.now() - timedelta(days=30))
    recent_cv_weight = rag_service.calculate_document_weight(recent_cv)
    assert recent_cv_weight > 1.8, f"Recent CV should have high weight, got {recent_cv_weight}"
    
    # Test older CV document
    older_cv = mock_document_class('cv', datetime.now() - timedelta(days=200))
    older_cv_weight = rag_service.calculate_document_weight(older_cv)
    assert older_cv_weight < recent_cv_weight, f"Older CV should have lower weight than recent CV"
    
    # Test very recent cover letter
    recent_cover_letter = mock_document_class('cover_letter', datetime.now() - timedelta(days=10))
    recent_cover_letter_weight = rag_service.calculate_document_weight(recent_cover_letter)
    assert recent_cover_letter_weight > 1.6, f"Recent cover letter should have high weight, got {recent_cover_letter_weight}"
    
    # Test LinkedIn profile
    linkedin_profile = mock_document_class('linkedin', datetime.now() - timedelta(days=100))
    linkedin_weight = rag_service.calculate_document_weight(linkedin_profile)
    assert 0.8 < linkedin_weight < 1.5, f"LinkedIn profile should have medium weight, got {linkedin_weight}"
    
    # Test old other document
    old_other = mock_document_class('other', datetime.now() - timedelta(days=400))
    old_other_weight = rag_service.calculate_document_weight(old_other)
    assert old_other_weight < 0.5, f"Old other document should have low weight, got {old_other_weight}"
    
    # Test weight ordering: recent CV > recent cover letter > LinkedIn > old other
    assert recent_cv_weight > recent_cover_letter_weight > linkedin_weight > old_other_weight

if __name__ == "__main__":
    test_document_weighting() 