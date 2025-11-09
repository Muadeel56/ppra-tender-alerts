#!/usr/bin/env python3
"""
Test Headless Browser Functionality

This script tests the Selenium WebDriver configuration to ensure:
- Browser opens in headless mode without errors
- Can navigate to a test URL
- Can retrieve page title/content
- Properly closes browser session
"""

import sys
import os

# Add backend directory to path to import scraper module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from scraper.browser_config import create_headless_chrome_driver


def test_headless_browser():
    """Test headless browser functionality."""
    driver = None
    
    try:
        print("=" * 60)
        print("Testing Headless Browser Configuration")
        print("=" * 60)
        
        # Test 1: Create headless Chrome driver
        print("\n[Test 1] Creating headless Chrome WebDriver...")
        driver = create_headless_chrome_driver(headless=True)
        print("✓ Headless Chrome WebDriver created successfully")
        
        # Test 2: Navigate to a test URL
        print("\n[Test 2] Navigating to test URL (http://example.com)...")
        test_url = "http://example.com"
        driver.get(test_url)
        print(f"✓ Successfully navigated to {test_url}")
        
        # Test 3: Retrieve page title
        print("\n[Test 3] Retrieving page title...")
        page_title = driver.title
        print(f"✓ Page title retrieved: '{page_title}'")
        assert page_title, "Page title should not be empty"
        
        # Test 4: Retrieve page content
        print("\n[Test 4] Retrieving page content...")
        page_source = driver.page_source
        content_length = len(page_source)
        print(f"✓ Page content retrieved: {content_length} characters")
        assert content_length > 0, "Page content should not be empty"
        
        # Test 5: Check current URL
        print("\n[Test 5] Verifying current URL...")
        current_url = driver.current_url
        print(f"✓ Current URL: {current_url}")
        # Allow for HTTP to HTTPS redirects
        assert "example.com" in current_url, f"Current URL should contain example.com (got: {current_url})"
        
        # Test 6: Browser capabilities
        print("\n[Test 6] Checking browser capabilities...")
        capabilities = driver.capabilities
        browser_name = capabilities.get('browserName', 'unknown')
        browser_version = capabilities.get('browserVersion', 'unknown')
        print(f"✓ Browser: {browser_name} {browser_version}")
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        print("\nSummary:")
        print(f"  - Browser opened in headless mode: ✓")
        print(f"  - Navigation successful: ✓")
        print(f"  - Page title retrieved: ✓")
        print(f"  - Page content retrieved: ✓")
        print(f"  - Browser session working: ✓")
        
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Assertion failed: {str(e)}")
        return 1
        
    except Exception as e:
        print(f"\n✗ Error occurred: {type(e).__name__}")
        print(f"  Details: {str(e)}")
        return 1
        
    finally:
        # Test 7: Properly close browser session
        if driver:
            print("\n[Test 7] Closing browser session...")
            try:
                driver.quit()
                print("✓ Browser session closed successfully")
            except Exception as e:
                print(f"✗ Error closing browser: {str(e)}")
                return 1


def main():
    """Main function to run the headless browser test."""
    exit_code = test_headless_browser()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

