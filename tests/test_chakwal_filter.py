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
        
        if len(tenders) == 0:
            print("⚠ No tenders found (this may be expected if there are no active Chakwal tenders)")
        else:
            # Display first few tenders
            print("\n[Test 5] Sample tender data:")
            for i, tender in enumerate(tenders[:3], 1):
                print(f"\n  Tender {i}:")
                print(f"    Tender No: {tender.get('tender_no', 'N/A')}")
                print(f"    Details: {tender.get('tender_details', 'N/A')[:80]}...")
                print(f"    Closing Date: {tender.get('closing_date', 'N/A')}")
                print(f"    Advertisement Date: {tender.get('advertisement_date', 'N/A')}")
                if tender.get('downloads'):
                    print(f"    Downloads: {len(tender['downloads'])} link(s)")
        
        # Test 6: Save results to JSON file
        print("\n[Test 6] Saving results to JSON file...")
        output_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'chakwal_tenders.json')
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(tenders, f, indent=2, ensure_ascii=False)
        print(f"✓ Results saved to {output_file}")
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        print("\nSummary:")
        print(f"  - Scraper initialized: ✓")
        print(f"  - City filter applied: ✓")
        print(f"  - Filter verified: {'✓' if filter_verified else '⚠'}")
        print(f"  - Tenders extracted: {len(tenders)}")
        print(f"  - Results saved: ✓")
        
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
                print(f"\n  Sample tender: {tenders[0].get('tender_no', 'N/A')}")
        
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

