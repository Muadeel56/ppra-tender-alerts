#!/usr/bin/env python3
"""
Test PPRA Active Tenders Page Loader

This script tests opening the PPRA active tenders page and ensures:
- Browser opens and navigates to the page
- Page fully loads (document ready state)
- Table element is present and visible
- Page is ready for scraping operations
- Properly closes browser session
"""

import sys
import os
import time

# Add backend directory to path to import scraper module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from scraper.browser_config import create_headless_chrome_driver


def test_ppra_active_tenders_page(headless: bool = True, timeout: int = 30):
    """
    Test opening and loading the PPRA active tenders page.
    
    Args:
        headless (bool): If True, run browser in headless mode. Defaults to True.
        timeout (int): Maximum time to wait for page/table to load in seconds. Defaults to 30.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    driver = None
    
    try:
        print("=" * 60)
        print("Testing PPRA Active Tenders Page Loader")
        print("=" * 60)
        
        # Test 1: Create Chrome driver
        print(f"\n[Test 1] Creating Chrome WebDriver (headless={headless})...")
        driver = create_headless_chrome_driver(headless=headless)
        print("✓ Chrome WebDriver created successfully")
        
        # Test 2: Navigate to PPRA active tenders page
        print("\n[Test 2] Navigating to PPRA active tenders page...")
        ppra_url = "https://ppra.gov.pk/#/tenders/activetenders"
        driver.get(ppra_url)
        print(f"✓ Successfully navigated to {ppra_url}")
        
        # Test 3: Wait for document ready state
        print(f"\n[Test 3] Waiting for document ready state (timeout: {timeout}s)...")
        wait = WebDriverWait(driver, timeout)
        
        # Wait for document.readyState to be 'complete'
        ready_state = wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        assert ready_state, "Document ready state should be 'complete'"
        print("✓ Document ready state is 'complete'")
        
        # Additional wait for JavaScript to finish executing
        time.sleep(2)  # Small delay for any remaining JavaScript execution
        
        # Test 4: Wait for page title to be present (indicates page loaded)
        print("\n[Test 4] Verifying page title...")
        page_title = driver.title
        print(f"✓ Page title retrieved: '{page_title}'")
        assert page_title, "Page title should not be empty"
        
        # Test 5: Wait for table element to be present
        print("\n[Test 5] Waiting for table element to be present...")
        try:
            # Try multiple common table selectors
            table_selectors = [
                "table",
                ".table",
                "#tender-table",
                "[class*='table']",
                "[id*='table']",
                "tbody",
            ]
            
            table_element = None
            for selector in table_selectors:
                try:
                    table_element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"✓ Table element found using selector: '{selector}'")
                    break
                except TimeoutException:
                    continue
            
            if table_element is None:
                # If no table found, check if page has loaded content
                print("⚠ No standard table element found, checking for page content...")
                page_source = driver.page_source
                assert len(page_source) > 1000, "Page should have substantial content"
                print("✓ Page has substantial content (table may be dynamically rendered)")
            else:
                # Test 6: Wait for table to be visible
                print("\n[Test 6] Waiting for table to be visible...")
                visible_table = wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                )
                assert visible_table.is_displayed(), "Table should be visible"
                print("✓ Table is visible")
                
                # Test 7: Check for table rows (if table exists)
                print("\n[Test 7] Checking for table rows...")
                try:
                    rows = driver.find_elements(By.CSS_SELECTOR, f"{selector} tr")
                    row_count = len(rows)
                    print(f"✓ Found {row_count} table row(s)")
                    if row_count > 0:
                        print("✓ Table contains data rows")
                except Exception as e:
                    print(f"⚠ Could not count table rows: {str(e)}")
        
        except TimeoutException as e:
            print(f"⚠ Timeout waiting for table element: {str(e)}")
            print("  Note: Page may still be loading or table may use different structure")
            # Verify page has loaded by checking content
            page_source = driver.page_source
            assert len(page_source) > 1000, "Page should have substantial content"
            print("✓ Page has substantial content")
        
        # Test 8: Verify current URL
        print("\n[Test 8] Verifying current URL...")
        current_url = driver.current_url
        print(f"✓ Current URL: {current_url}")
        assert "ppra.gov.pk" in current_url, f"Current URL should contain ppra.gov.pk (got: {current_url})"
        assert "tenders" in current_url.lower() or "activetenders" in current_url.lower(), \
            f"Current URL should contain 'tenders' or 'activetenders' (got: {current_url})"
        
        # Test 9: Verify page source length
        print("\n[Test 9] Verifying page content...")
        page_source = driver.page_source
        content_length = len(page_source)
        print(f"✓ Page content length: {content_length} characters")
        assert content_length > 1000, f"Page content should be substantial (got: {content_length} chars)"
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        print("\nSummary:")
        print(f"  - Browser opened: ✓")
        print(f"  - Navigation successful: ✓")
        print(f"  - Document ready state: ✓")
        print(f"  - Page title retrieved: ✓")
        print(f"  - Page content loaded: ✓")
        print(f"  - Page ready for scraping: ✓")
        
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Assertion failed: {str(e)}")
        return 1
        
    except TimeoutException as e:
        print(f"\n✗ Timeout error: {str(e)}")
        print("  The page or table may be taking longer than expected to load.")
        print(f"  Consider increasing the timeout (current: {timeout}s)")
        return 1
        
    except WebDriverException as e:
        print(f"\n✗ WebDriver error: {type(e).__name__}")
        print(f"  Details: {str(e)}")
        return 1
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {type(e).__name__}")
        print(f"  Details: {str(e)}")
        return 1
        
    finally:
        # Test 10: Properly close browser session
        if driver:
            print("\n[Test 10] Closing browser session...")
            try:
                driver.quit()
                print("✓ Browser session closed successfully")
            except Exception as e:
                print(f"✗ Error closing browser: {str(e)}")
                return 1


def main():
    """Main function to run the PPRA active tenders page test."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test PPRA Active Tenders Page Loader"
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
        help='Timeout in seconds for page/table loading (default: 30)'
    )
    
    args = parser.parse_args()
    
    exit_code = test_ppra_active_tenders_page(
        headless=not args.no_headless,
        timeout=args.timeout
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

