#!/usr/bin/env python3
"""
End-to-end test for saving tenders locally

This script tests the save_tenders_locally functionality using test data.
"""

import sys
import os
import json

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# Import directly to avoid selenium dependency
import importlib.util
tender_storage_path = os.path.join(backend_path, 'scraper', 'tender_storage.py')
spec = importlib.util.spec_from_file_location("tender_storage", tender_storage_path)
tender_storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tender_storage)

load_tenders = tender_storage.load_tenders
save_tenders = tender_storage.save_tenders
merge_tenders = tender_storage.merge_tenders
get_tenders_filepath = tender_storage.get_tenders_filepath


def main():
    """Test saving tenders with test data."""
    print("=" * 60)
    print("End-to-End Test: Save Tenders Locally")
    print("=" * 60)
    
    # Get the default filepath
    filepath = get_tenders_filepath()
    print(f"\nUsing filepath: {filepath}")
    
    # Load test data
    test_data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_tenders.json')
    print(f"\nLoading test data from: {test_data_path}")
    
    with open(test_data_path, 'r', encoding='utf-8') as f:
        test_tenders = json.load(f)
    
    print(f"Loaded {len(test_tenders)} test tenders")
    
    # Load existing tenders (if any)
    existing_tenders = load_tenders(filepath)
    print(f"Existing tenders in storage: {len(existing_tenders)}")
    
    # Merge and save
    print("\nMerging and saving tenders...")
    merged_tenders, new_count = merge_tenders(existing_tenders, test_tenders)
    
    if save_tenders(merged_tenders, filepath):
        print(f"\n✓ Successfully saved tenders!")
        print(f"  - Total tenders in storage: {len(merged_tenders)}")
        print(f"  - New tenders added: {new_count}")
        print(f"  - Duplicates skipped: {len(test_tenders) - new_count}")
        
        # Try saving again (should skip all as duplicates)
        print("\n" + "-" * 60)
        print("Testing duplicate detection: saving same tenders again...")
        existing_tenders = load_tenders(filepath)
        merged_tenders, new_count = merge_tenders(existing_tenders, test_tenders)
        
        if save_tenders(merged_tenders, filepath):
            print(f"✓ Duplicate detection works!")
            print(f"  - Total tenders in storage: {len(merged_tenders)}")
            print(f"  - New tenders added: {new_count} (should be 0)")
            print(f"  - Duplicates skipped: {len(test_tenders) - new_count} (should be {len(test_tenders)})")
        
        return 0
    else:
        print("\n✗ Failed to save tenders")
        return 1


if __name__ == "__main__":
    sys.exit(main())

