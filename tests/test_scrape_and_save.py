#!/usr/bin/env python3
"""
Test Scraping and Saving Tenders

This script scrapes tenders from a specified city and saves them locally
to verify the complete workflow is working.
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from scraper.ppra_scraper import PPRAScraper


def scrape_and_save_city(city_name: str, headless: bool = True):
    """
    Scrape tenders from a city and save them locally.
    
    Args:
        city_name (str): Name of the city to scrape
        headless (bool): Run browser in headless mode
    """
    print("=" * 60)
    print(f"Scraping and Saving Tenders for {city_name}")
    print("=" * 60)
    
    scraper = None
    try:
        # Initialize scraper
        print(f"\n[1] Initializing scraper (headless={headless})...")
        scraper = PPRAScraper(headless=headless, timeout=30)
        scraper.start()
        print("✓ Scraper initialized")
        
        # Apply city filter
        print(f"\n[2] Applying {city_name} city filter...")
        if not scraper.apply_city_filter(city_name):
            print(f"✗ Failed to apply city filter for {city_name}")
            return 1
        print(f"✓ City filter applied successfully")
        
        # Extract tender data
        print(f"\n[3] Extracting tender data...")
        tenders = scraper.extract_tender_data()
        print(f"✓ Extracted {len(tenders)} tenders")
        
        if len(tenders) == 0:
            print(f"\n⚠ No tenders found for {city_name}. This may be expected if there are no active tenders.")
            print("   The setup is working correctly, just no data available.")
            return 0
        
        # Display sample data
        print(f"\n[4] Sample tender data:")
        for i, tender in enumerate(tenders[:3], 1):
            print(f"\n  Tender {i}:")
            print(f"    Title: {tender.get('tender_title', 'N/A')[:60]}...")
            print(f"    Number: {tender.get('tender_number', 'N/A')}")
            print(f"    Category: {tender.get('category', 'N/A')}")
            print(f"    Department: {tender.get('department_owner', 'N/A')[:50]}...")
            print(f"    Closing Date: {tender.get('closing_date', 'N/A')}")
        
        # Save tenders locally
        print(f"\n[5] Saving tenders to local storage...")
        new_count = scraper.save_tenders_locally(tenders)
        
        if new_count >= 0:
            print(f"✓ Successfully saved tenders!")
            print(f"   - {new_count} new tenders added to storage")
            if new_count < len(tenders):
                print(f"   - {len(tenders) - new_count} duplicates were skipped")
        else:
            print(f"✗ Failed to save tenders")
            return 1
        
        print("\n" + "=" * 60)
        print("✓ Complete workflow test successful!")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        if scraper:
            print("\n[Cleanup] Closing browser session...")
            try:
                scraper.close()
                print("✓ Browser session closed")
            except Exception as e:
                print(f"⚠ Error closing browser: {str(e)}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Scrape and save tenders from a city"
    )
    parser.add_argument(
        '--city',
        type=str,
        default='Islamabad',
        help='City name to scrape (default: Islamabad)'
    )
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Run browser in visible mode (default: headless)'
    )
    
    args = parser.parse_args()
    
    exit_code = scrape_and_save_city(
        city_name=args.city,
        headless=not args.no_headless
    )
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

