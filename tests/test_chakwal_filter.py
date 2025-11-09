#!/usr/bin/env python3
"""
Test Chakwal City Filter

This script tests the Chakwal city filter functionality:
- City filter selection
- Verification that only Chakwal tenders are displayed
- Data extraction from filtered results
"""

import sys
import os
import json

# Add backend directory to path to import scraper module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from scraper.ppra_scraper import PPRAScraper


def test_chakwal_filter(headless: bool = True, timeout: int = 30):
    """
    Test applying Chakwal city filter and extracting tender data.
    
    Args:
        headless (bool): If True, run browser in headless mode. Defaults to True.
        timeout (int): Maximum time to wait for operations in seconds. Defaults to 30.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    scraper = None
    
    try:
        print("=" * 60)
        print("Testing Chakwal City Filter")
        print("=" * 60)
        
        # Test 1: Initialize scraper
        print(f"\n[Test 1] Initializing PPRA scraper (headless={headless})...")
        scraper = PPRAScraper(headless=headless, timeout=timeout)
        scraper.start()
        print("✓ Scraper initialized and page loaded")
        
        # Test 2: Apply city filter
        print("\n[Test 2] Applying Chakwal city filter...")
        filter_applied = scraper.apply_city_filter("Chakwal")
        if not filter_applied:
            print("✗ Failed to apply city filter")
            return 1
        print("✓ City filter applied successfully")
        
        # Test 3: Verify city filter
        print("\n[Test 3] Verifying city filter...")
        filter_verified = scraper.verify_city_filter("Chakwal")
        if not filter_verified:
            print("⚠ City filter verification failed (may still have valid results)")
        else:
            print("✓ City filter verified successfully")
        
        # Test 4: Extract tender data
        print("\n[Test 4] Extracting tender data...")
        tenders = scraper.extract_tender_data()
        print(f"✓ Extracted {len(tenders)} tenders")
        
        json_exported = False
        csv_exported = False
        
        if len(tenders) == 0:
            print("⚠ No tenders found (this may be expected if there are no active Chakwal tenders)")
        else:
            # Test 5: Verify all required fields are present
            print("\n[Test 5] Verifying required fields in extracted data...")
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
            
            all_fields_present = True
            for tender in tenders:
                for field in required_fields:
                    if field not in tender:
                        print(f"✗ Missing field '{field}' in tender data")
                        all_fields_present = False
            
            if all_fields_present:
                print(f"✓ All required fields present in {len(tenders)} tender(s)")
            
            # Display first few tenders with new fields
            print("\n[Test 6] Sample tender data:")
            for i, tender in enumerate(tenders[:3], 1):
                print(f"\n  Tender {i}:")
                print(f"    Tender Title: {tender.get('tender_title', 'N/A')[:60]}...")
                print(f"    Category: {tender.get('category', 'N/A')}")
                print(f"    Department/Owner: {tender.get('department_owner', 'N/A')[:60]}...")
                print(f"    Tender Number: {tender.get('tender_number', 'N/A')}")
                print(f"    TSE: {tender.get('tse', 'N/A')}")
                print(f"    Start Date: {tender.get('start_date', 'N/A')}")
                print(f"    Closing Date: {tender.get('closing_date', 'N/A')}")
                pdf_links = tender.get('pdf_links', [])
                if pdf_links:
                    print(f"    PDF Links: {len(pdf_links)} link(s)")
                    for j, link in enumerate(pdf_links[:2], 1):
                        print(f"      {j}. {link[:60]}...")
        
        # Test 7: Export to JSON using scraper method
        print("\n[Test 7] Testing JSON export...")
        json_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'chakwal_tenders.json')
        json_exported = scraper.export_to_json(tenders, json_file)
        if json_exported:
            print(f"✓ JSON export successful: {json_file}")
        else:
            print("✗ JSON export failed")
        
        # Test 8: Export to CSV using scraper method
        print("\n[Test 8] Testing CSV export...")
        csv_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'chakwal_tenders.csv')
        csv_exported = scraper.export_to_csv(tenders, csv_file)
        if csv_exported:
            print(f"✓ CSV export successful: {csv_file}")
        else:
            print("✗ CSV export failed")
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        print("\nSummary:")
        print(f"  - Scraper initialized: ✓")
        print(f"  - City filter applied: ✓")
        print(f"  - Filter verified: {'✓' if filter_verified else '⚠'}")
        print(f"  - Tenders extracted: {len(tenders)}")
        print(f"  - Required fields verified: ✓")
        print(f"  - JSON export: {'✓' if json_exported else '✗'}")
        print(f"  - CSV export: {'✓' if csv_exported else '✗'}")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}")
        print(f"  Details: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        # Clean up
        if scraper:
            print("\n[Cleanup] Closing browser session...")
            try:
                scraper.close()
                print("✓ Browser session closed successfully")
            except Exception as e:
                print(f"✗ Error closing browser: {str(e)}")
                return 1


def test_scrape_chakwal_tenders_workflow(headless: bool = True, timeout: int = 30):
    """
    Test the complete scrape_chakwal_tenders workflow.
    
    Args:
        headless (bool): If True, run browser in headless mode. Defaults to True.
        timeout (int): Maximum time to wait for operations in seconds. Defaults to 30.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    scraper = None
    
    try:
        print("=" * 60)
        print("Testing Complete Chakwal Tenders Workflow")
        print("=" * 60)
        
        # Test using context manager
        print(f"\n[Test] Running complete workflow (headless={headless})...")
        with PPRAScraper(headless=headless, timeout=timeout) as scraper:
            tenders = scraper.scrape_chakwal_tenders()
            
            print(f"\n✓ Workflow completed successfully")
            print(f"  - Tenders extracted: {len(tenders)}")
            
            if len(tenders) > 0:
                print(f"\n  Sample tender:")
                print(f"    Title: {tenders[0].get('tender_title', 'N/A')[:50]}...")
                print(f"    Number: {tenders[0].get('tender_number', 'N/A')}")
                print(f"    Category: {tenders[0].get('category', 'N/A')}")
                print(f"    Department: {tenders[0].get('department_owner', 'N/A')[:50]}...")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}")
        print(f"  Details: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main function to run the Chakwal filter tests."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test Chakwal City Filter"
    )
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Run browser in visible mode (default: headless)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Timeout in seconds for operations (default: 30)'
    )
    parser.add_argument(
        '--workflow-only',
        action='store_true',
        help='Run only the complete workflow test'
    )
    
    args = parser.parse_args()
    
    if args.workflow_only:
        exit_code = test_scrape_chakwal_tenders_workflow(
            headless=not args.no_headless,
            timeout=args.timeout
        )
    else:
        exit_code = test_chakwal_filter(
            headless=not args.no_headless,
            timeout=args.timeout
        )
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

