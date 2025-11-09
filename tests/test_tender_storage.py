#!/usr/bin/env python3
"""
Test Tender Storage Functionality

This script tests the tender storage module to verify:
- Loading tenders from JSON file
- Saving tenders to JSON file
- Duplicate detection based on tender_number
- Merging new tenders with existing ones
"""

import sys
import os
import json
import tempfile
import shutil

# Add backend directory to path to import scraper module
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# Import directly from the module file to avoid __init__.py imports
import importlib.util
tender_storage_path = os.path.join(backend_path, 'scraper', 'tender_storage.py')
spec = importlib.util.spec_from_file_location("tender_storage", tender_storage_path)
tender_storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tender_storage)

load_tenders = tender_storage.load_tenders
save_tenders = tender_storage.save_tenders
is_duplicate = tender_storage.is_duplicate
merge_tenders = tender_storage.merge_tenders
get_tenders_filepath = tender_storage.get_tenders_filepath


def test_load_tenders_empty_file():
    """Test loading from non-existent file."""
    print("\n[Test 1] Loading tenders from non-existent file...")
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        result = load_tenders(temp_file)
        assert result == [], "Should return empty list for non-existent file"
        print("✓ Passed: Returns empty list for non-existent file")
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_load_tenders_valid_file():
    """Test loading from valid JSON file."""
    print("\n[Test 2] Loading tenders from valid JSON file...")
    test_data = [
        {
            "tender_title": "Test Tender 1",
            "tender_number": "TSE-2024-001",
            "category": "IT",
            "department_owner": "Test Dept",
            "start_date": "2024-01-01",
            "closing_date": "2024-02-01",
            "tse": "2024-001",
            "pdf_links": []
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2)
        temp_file = f.name
    
    try:
        result = load_tenders(temp_file)
        assert len(result) == 1, "Should load 1 tender"
        assert result[0]['tender_number'] == "TSE-2024-001", "Should have correct tender number"
        print("✓ Passed: Successfully loaded tenders from valid JSON file")
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_save_tenders():
    """Test saving tenders to file."""
    print("\n[Test 3] Saving tenders to file...")
    test_data = [
        {
            "tender_title": "Test Tender 2",
            "tender_number": "TSE-2024-002",
            "category": "Construction",
            "department_owner": "Test Dept 2",
            "start_date": "2024-01-15",
            "closing_date": "2024-02-15",
            "tse": "2024-002",
            "pdf_links": []
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        result = save_tenders(test_data, temp_file)
        assert result is True, "Should return True on success"
        assert os.path.exists(temp_file), "File should be created"
        
        # Verify content
        with open(temp_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        assert len(loaded_data) == 1, "Should have 1 tender"
        assert loaded_data[0]['tender_number'] == "TSE-2024-002", "Should have correct tender number"
        print("✓ Passed: Successfully saved tenders to file")
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_is_duplicate():
    """Test duplicate detection."""
    print("\n[Test 4] Testing duplicate detection...")
    existing_tenders = [
        {
            "tender_title": "Test Tender 1",
            "tender_number": "TSE-2024-001",
            "category": "IT",
            "department_owner": "Test Dept",
            "start_date": "2024-01-01",
            "closing_date": "2024-02-01",
            "tse": "2024-001",
            "pdf_links": []
        },
        {
            "tender_title": "Test Tender 2",
            "tender_number": "TSE-2024-002",
            "category": "Construction",
            "department_owner": "Test Dept 2",
            "start_date": "2024-01-15",
            "closing_date": "2024-02-15",
            "tse": "2024-002",
            "pdf_links": []
        }
    ]
    
    # Test duplicate (same tender_number)
    duplicate_tender = {
        "tender_title": "Different Title",
        "tender_number": "TSE-2024-001",  # Same number, different format
        "category": "Different Category",
        "department_owner": "Different Dept",
        "start_date": "2024-03-01",
        "closing_date": "2024-04-01",
        "tse": "2024-001",
        "pdf_links": []
    }
    
    assert is_duplicate(duplicate_tender, existing_tenders) is True, "Should detect duplicate (case-insensitive)"
    
    # Test new tender
    new_tender = {
        "tender_title": "New Tender",
        "tender_number": "TSE-2024-003",
        "category": "Healthcare",
        "department_owner": "Health Dept",
        "start_date": "2024-02-01",
        "closing_date": "2024-03-01",
        "tse": "2024-003",
        "pdf_links": []
    }
    
    assert is_duplicate(new_tender, existing_tenders) is False, "Should not detect duplicate for new tender"
    
    # Test tender without tender_number
    tender_no_number = {
        "tender_title": "Tender Without Number",
        "category": "Test",
        "department_owner": "Test Dept",
        "start_date": "2024-01-01",
        "closing_date": "2024-02-01",
        "tse": "",
        "pdf_links": []
    }
    
    assert is_duplicate(tender_no_number, existing_tenders) is False, "Should not detect duplicate if tender_number is missing"
    
    print("✓ Passed: Duplicate detection works correctly")


def test_merge_tenders():
    """Test merging tenders with duplicates."""
    print("\n[Test 5] Testing merge functionality...")
    existing_tenders = [
        {
            "tender_title": "Existing Tender 1",
            "tender_number": "TSE-2024-001",
            "category": "IT",
            "department_owner": "Test Dept",
            "start_date": "2024-01-01",
            "closing_date": "2024-02-01",
            "tse": "2024-001",
            "pdf_links": []
        },
        {
            "tender_title": "Existing Tender 2",
            "tender_number": "TSE-2024-002",
            "category": "Construction",
            "department_owner": "Test Dept 2",
            "start_date": "2024-01-15",
            "closing_date": "2024-02-15",
            "tse": "2024-002",
            "pdf_links": []
        }
    ]
    
    new_tenders = [
        {
            "tender_title": "New Tender 1",
            "tender_number": "TSE-2024-003",  # New
            "category": "Healthcare",
            "department_owner": "Health Dept",
            "start_date": "2024-02-01",
            "closing_date": "2024-03-01",
            "tse": "2024-003",
            "pdf_links": []
        },
        {
            "tender_title": "Duplicate Tender",
            "tender_number": "TSE-2024-001",  # Duplicate
            "category": "IT",
            "department_owner": "Test Dept",
            "start_date": "2024-01-01",
            "closing_date": "2024-02-01",
            "tse": "2024-001",
            "pdf_links": []
        },
        {
            "tender_title": "New Tender 2",
            "tender_number": "TSE-2024-004",  # New
            "category": "Education",
            "department_owner": "Education Dept",
            "start_date": "2024-02-15",
            "closing_date": "2024-03-15",
            "tse": "2024-004",
            "pdf_links": []
        }
    ]
    
    merged, new_count = merge_tenders(existing_tenders, new_tenders)
    
    assert len(merged) == 4, f"Should have 4 tenders (2 existing + 2 new), got {len(merged)}"
    assert new_count == 2, f"Should have added 2 new tenders, got {new_count}"
    
    # Verify all tender numbers are present
    tender_numbers = {t['tender_number'].lower() for t in merged}
    assert 'tse-2024-001' in tender_numbers, "Should contain TSE-2024-001"
    assert 'tse-2024-002' in tender_numbers, "Should contain TSE-2024-002"
    assert 'tse-2024-003' in tender_numbers, "Should contain TSE-2024-003"
    assert 'tse-2024-004' in tender_numbers, "Should contain TSE-2024-004"
    
    print("✓ Passed: Merge functionality works correctly (2 new tenders added, 1 duplicate skipped)")


def test_save_tenders_locally_integration():
    """Test the integrated save workflow using storage functions directly."""
    print("\n[Test 6] Testing save workflow integration...")
    
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # Test data
        test_tenders = [
            {
                "tender_title": "Integration Test Tender 1",
                "tender_number": "TSE-2024-101",
                "category": "IT",
                "department_owner": "Test Dept",
                "start_date": "2024-01-01",
                "closing_date": "2024-02-01",
                "tse": "2024-101",
                "pdf_links": []
            },
            {
                "tender_title": "Integration Test Tender 2",
                "tender_number": "TSE-2024-102",
                "category": "Construction",
                "department_owner": "Test Dept 2",
                "start_date": "2024-01-15",
                "closing_date": "2024-02-15",
                "tse": "2024-102",
                "pdf_links": []
            }
        ]
        
        # First save (should add 2 new tenders)
        existing = load_tenders(temp_file)
        merged, new_count = merge_tenders(existing, test_tenders)
        save_result = save_tenders(merged, temp_file)
        
        assert save_result is True, "Should save successfully"
        assert new_count == 2, f"Should add 2 new tenders, got {new_count}"
        
        # Verify file exists and has correct content
        assert os.path.exists(temp_file), "File should exist"
        with open(temp_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        assert len(loaded) == 2, "Should have 2 tenders"
        
        # Second save with one duplicate and one new
        new_tenders = [
            {
                "tender_title": "Duplicate Tender",
                "tender_number": "TSE-2024-101",  # Duplicate
                "category": "IT",
                "department_owner": "Test Dept",
                "start_date": "2024-01-01",
                "closing_date": "2024-02-01",
                "tse": "2024-101",
                "pdf_links": []
            },
            {
                "tender_title": "New Integration Test Tender",
                "tender_number": "TSE-2024-103",  # New
                "category": "Healthcare",
                "department_owner": "Health Dept",
                "start_date": "2024-02-01",
                "closing_date": "2024-03-01",
                "tse": "2024-103",
                "pdf_links": []
            }
        ]
        
        existing = load_tenders(temp_file)
        merged, new_count = merge_tenders(existing, new_tenders)
        save_result = save_tenders(merged, temp_file)
        
        assert save_result is True, "Should save successfully"
        assert new_count == 1, f"Should add 1 new tender (1 duplicate skipped), got {new_count}"
        
        # Verify final content
        with open(temp_file, 'r', encoding='utf-8') as f:
            final_loaded = json.load(f)
        assert len(final_loaded) == 3, f"Should have 3 tenders total, got {len(final_loaded)}"
        
        print("✓ Passed: Save workflow integration works correctly")
        
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_get_tenders_filepath():
    """Test getting the default tenders filepath."""
    print("\n[Test 7] Testing get_tenders_filepath...")
    
    filepath = get_tenders_filepath()
    
    # Should end with data/tenders.json
    assert filepath.endswith('data/tenders.json') or filepath.endswith('data\\tenders.json'), \
        f"Filepath should end with data/tenders.json, got {filepath}"
    
    # Should be an absolute path
    assert os.path.isabs(filepath), f"Filepath should be absolute, got {filepath}"
    
    print(f"✓ Passed: Default filepath is {filepath}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Tender Storage Functionality")
    print("=" * 60)
    
    tests = [
        test_load_tenders_empty_file,
        test_load_tenders_valid_file,
        test_save_tenders,
        test_is_duplicate,
        test_merge_tenders,
        test_save_tenders_locally_integration,
        test_get_tenders_filepath,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ Failed: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"✗ Error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

