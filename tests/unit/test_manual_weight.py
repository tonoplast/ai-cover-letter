#!/usr/bin/env python3
"""
Test manual weight functionality
"""

import pytest
from datetime import datetime, timedelta

def test_manual_weight_calculation(rag_service, mock_document_class):
    """Test that manual weight is properly included in document weight calculation"""
    
    # Test document with default manual weight (1.0)
    doc_default = mock_document_class('cv', datetime.now() - timedelta(days=30))
    default_weight = rag_service.calculate_document_weight(doc_default)
    
    # Test document with higher manual weight (2.0)
    doc_boosted = mock_document_class('cv', datetime.now() - timedelta(days=30))
    doc_boosted.manual_weight = 2.0
    boosted_weight = rag_service.calculate_document_weight(doc_boosted)
    
    # Test document with lower manual weight (0.5)
    doc_reduced = mock_document_class('cv', datetime.now() - timedelta(days=30))
    doc_reduced.manual_weight = 0.5
    reduced_weight = rag_service.calculate_document_weight(doc_reduced)
    
    # Verify weight relationships
    assert boosted_weight == default_weight * 2.0, f"Boosted weight should be 2x default weight"
    assert reduced_weight == default_weight * 0.5, f"Reduced weight should be 0.5x default weight"
    assert boosted_weight > default_weight > reduced_weight, "Weight ordering should be correct"

def test_manual_weight_edge_cases(rag_service, mock_document_class):
    """Test edge cases for manual weight"""
    
    # Test with None manual weight (should default to 1.0)
    doc_none = mock_document_class('cv', datetime.now() - timedelta(days=30))
    doc_none.manual_weight = None
    weight_none = rag_service.calculate_document_weight(doc_none)
    
    # Test with 0 manual weight (should default to 1.0)
    doc_zero = mock_document_class('cv', datetime.now() - timedelta(days=30))
    doc_zero.manual_weight = 0
    weight_zero = rag_service.calculate_document_weight(doc_zero)
    
    # Test with default manual weight
    doc_default = mock_document_class('cv', datetime.now() - timedelta(days=30))
    doc_default.manual_weight = 1.0
    weight_default = rag_service.calculate_document_weight(doc_default)
    
    # All should be equal (defaulting to 1.0)
    assert weight_none == weight_default, "None manual weight should default to 1.0"
    assert weight_zero == weight_default, "Zero manual weight should default to 1.0"

def test_manual_weight_with_different_document_types(rag_service, mock_document_class):
    """Test manual weight with different document types"""
    
    # Test CV with manual weight
    cv_doc = mock_document_class('cv', datetime.now() - timedelta(days=30))
    cv_doc.manual_weight = 3.0
    cv_weight = rag_service.calculate_document_weight(cv_doc)
    
    # Test cover letter with same manual weight
    cover_letter_doc = mock_document_class('cover_letter', datetime.now() - timedelta(days=30))
    cover_letter_doc.manual_weight = 3.0
    cover_letter_weight = rag_service.calculate_document_weight(cover_letter_doc)
    
    # CV should still have higher base weight than cover letter, but both should be boosted
    expected_cv_base = rag_service.get_document_type_weight('cv')
    expected_cover_letter_base = rag_service.get_document_type_weight('cover_letter')
    
    # Both should be 3x their respective base weights
    assert cv_weight > cover_letter_weight, "CV should still have higher weight than cover letter"
    
    # Test that manual weight multiplier is applied correctly
    cv_no_manual = mock_document_class('cv', datetime.now() - timedelta(days=30))
    cv_no_manual.manual_weight = 1.0
    cv_no_manual_weight = rag_service.calculate_document_weight(cv_no_manual)
    
    expected_ratio = cv_weight / cv_no_manual_weight
    assert abs(expected_ratio - 3.0) < 0.001, f"Manual weight ratio should be 3.0, got {expected_ratio}"

def test_manual_weight_with_recency(rag_service, mock_document_class):
    """Test that manual weight works correctly with recency weighting"""
    
    # Test recent document
    recent_doc = mock_document_class('cv', datetime.now() - timedelta(days=10))
    recent_doc.manual_weight = 2.0
    recent_weight = rag_service.calculate_document_weight(recent_doc)
    
    # Test old document
    old_doc = mock_document_class('cv', datetime.now() - timedelta(days=300))
    old_doc.manual_weight = 2.0
    old_weight = rag_service.calculate_document_weight(old_doc)
    
    # Recent document should have higher weight than old document
    assert recent_weight > old_weight, "Recent document should have higher weight than old document"
    
    # But both should be boosted by the 2.0 manual weight
    recent_no_manual = mock_document_class('cv', datetime.now() - timedelta(days=10))
    recent_no_manual.manual_weight = 1.0
    recent_no_manual_weight = rag_service.calculate_document_weight(recent_no_manual)
    
    old_no_manual = mock_document_class('cv', datetime.now() - timedelta(days=300))
    old_no_manual.manual_weight = 1.0
    old_no_manual_weight = rag_service.calculate_document_weight(old_no_manual)
    
    # Check that the manual weight ratio is preserved
    recent_ratio = recent_weight / recent_no_manual_weight
    old_ratio = old_weight / old_no_manual_weight
    
    assert abs(recent_ratio - 2.0) < 0.001, f"Recent document manual weight ratio should be 2.0, got {recent_ratio}"
    assert abs(old_ratio - 2.0) < 0.001, f"Old document manual weight ratio should be 2.0, got {old_ratio}"

def test_manual_weight_extreme_values(rag_service, mock_document_class):
    """Test manual weight with extreme values"""
    
    # Test very high manual weight
    doc_high = mock_document_class('cv', datetime.now() - timedelta(days=30))
    doc_high.manual_weight = 10.0
    high_weight = rag_service.calculate_document_weight(doc_high)
    
    # Test very low manual weight
    doc_low = mock_document_class('cv', datetime.now() - timedelta(days=30))
    doc_low.manual_weight = 0.1
    low_weight = rag_service.calculate_document_weight(doc_low)
    
    # Test default weight
    doc_default = mock_document_class('cv', datetime.now() - timedelta(days=30))
    doc_default.manual_weight = 1.0
    default_weight = rag_service.calculate_document_weight(doc_default)
    
    # Verify extreme values work correctly
    assert high_weight == default_weight * 10.0, "High manual weight should multiply correctly"
    assert low_weight == default_weight * 0.1, "Low manual weight should multiply correctly"
    assert high_weight > default_weight > low_weight, "Weight ordering should be correct"