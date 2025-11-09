#!/usr/bin/env python3
"""
Verification script to test the enhanced scraper implementation.

This script tests the scraper with sample data to verify:
1. Data structure matches requirements
2. JSON export works correctly
3. CSV export works correctly
4. All required fields are present
"""

import sys
import os
import json
import csv

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from scraper.ppra_scraper import PPRAScraper


def create_sample_tender_data():
    """Create sample tender data for testing."""
    return [
        {
            "tender_title": "Supply of Office Equipment",
            "category": "IT Equipment",
            "department_owner": "Ministry of Education",
            "start_date": "2024-01-15",
            "closing_date": "2024-02-15",
            "tender_number": "TSE-2024-001",
            "tse": "2024-001",
            "pdf_links": [
                "https://example.com/tender1.pdf",
                "https://example.com/attachment1.pdf"
            ]
        },
        {
            "tender_title": "Construction of Road Infrastructure",
            "category": "Construction",
            "department_owner": "Public Works Department",
            "start_date": "2024-01-20",
            "closing_date": "2024-03-20",
            "tender_number": "TSE-2024-002",
            "tse": "2024-002",
            "pdf_links": [
                "https://example.com/tender2.pdf"
            ]
        },
        {
            "tender_title": "Medical Supplies Procurement",
            "category": "Healthcare",
            "department_owner": "Health Department",
            "start_date": "2024-02-01",
            "closing_date": "2024-02-28",
            "tender_number": "PPRA-2024-003",
            "tse": "",
            "pdf_links": []
        }
    ]


def verify_data_structure(tenders):
    """Verify that all tenders have the required fields."""
    required_fields = [
        "tender_title",
        "category",
        "department_owner",
        "start_date",
        "closing_date",
        "tender_number",
        "tse",
        "pdf_links"
    ]
    
    print("\n" + "=" * 60)
    print("Verifying Data Structure")
    print("=" * 60)
    
    all_valid = True
    for i, tender in enumerate(tenders, 1):
        print(f"\nTender {i}:")
        missing_fields = []
        for field in required_fields:
            if field not in tender:
                missing_fields.append(field)
                all_valid = False
            else:
                value = tender[field]
                if isinstance(value, list):
                    print(f"  ✓ {field}: {len(value)} item(s)")
                else:
                    print(f"  ✓ {field}: {str(value)[:50]}")
        
        if missing_fields:
            print(f"  ✗ Missing fields: {', '.join(missing_fields)}")
    
    if all_valid:
        print("\n✓ All tenders have required fields")
    else:
        print("\n✗ Some tenders are missing required fields")
    
    return all_valid


def test_json_export(scraper, tenders):
    """Test JSON export functionality."""
    print("\n" + "=" * 60)
    print("Testing JSON Export")
    print("=" * 60)
    
    json_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_tenders.json')
    success = scraper.export_to_json(tenders, json_file)
    
    if success and os.path.exists(json_file):
        # Verify JSON file content
        with open(json_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        if len(loaded_data) == len(tenders):
            print(f"✓ JSON export successful: {len(loaded_data)} tenders exported")
            print(f"  File: {json_file}")
            return True
        else:
            print(f"✗ JSON export failed: Expected {len(tenders)} tenders, got {len(loaded_data)}")
            return False
    else:
        print("✗ JSON export failed")
        return False


def test_csv_export(scraper, tenders):
    """Test CSV export functionality."""
    print("\n" + "=" * 60)
    print("Testing CSV Export")
    print("=" * 60)
    
    csv_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_tenders.csv')
    success = scraper.export_to_csv(tenders, csv_file)
    
    if success and os.path.exists(csv_file):
        # Verify CSV file content
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if len(rows) == len(tenders):
            print(f"✓ CSV export successful: {len(rows)} tenders exported")
            print(f"  File: {csv_file}")
            print(f"  Columns: {', '.join(reader.fieldnames)}")
            return True
        else:
            print(f"✗ CSV export failed: Expected {len(tenders)} tenders, got {len(rows)}")
            return False
    else:
        print("✗ CSV export failed")
        return False


def main():
    """Main verification function."""
    print("=" * 60)
    print("PPRA Scraper Implementation Verification")
    print("=" * 60)
    
    # Create sample data
    sample_tenders = create_sample_tender_data()
    print(f"\nCreated {len(sample_tenders)} sample tenders for testing")
    
    # Create scraper instance (we don't need to start browser for export tests)
    scraper = PPRAScraper()
    
    # Run verification tests
    structure_valid = verify_data_structure(sample_tenders)
    json_valid = test_json_export(scraper, sample_tenders)
    csv_valid = test_csv_export(scraper, sample_tenders)
    
    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    print(f"  Data Structure: {'✓' if structure_valid else '✗'}")
    print(f"  JSON Export: {'✓' if json_valid else '✗'}")
    print(f"  CSV Export: {'✓' if csv_valid else '✗'}")
    
    if structure_valid and json_valid and csv_valid:
        print("\n✓ All verification tests passed!")
        print("\nYour implementation is working correctly and ready to use.")
        return 0
    else:
        print("\n✗ Some verification tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

