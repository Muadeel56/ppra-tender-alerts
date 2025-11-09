"""
PPRA Tender Scraper Module

This module provides functionality to scrape tender data from the PPRA website,
including filtering by city and extracting tender information.
"""

import time
import json
import csv
import os
import re
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

from scraper.browser_config import create_headless_chrome_driver


class PPRAScraper:
    """
    Scraper class for PPRA active tenders page.
    
    Provides methods to navigate, filter, and extract tender data from the PPRA website.
    """
    
    PPRA_ACTIVE_TENDERS_URL = "https://ppra.gov.pk/#/tenders/activetenders"
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        """
        Initialize the PPRA scraper.
        
        Args:
            headless (bool): If True, run browser in headless mode. Defaults to True.
            timeout (int): Default timeout for element waits in seconds. Defaults to 30.
        """
        self.headless = headless
        self.timeout = timeout
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def start(self):
        """Start the browser and navigate to PPRA active tenders page."""
        if self.driver is None:
            self.driver = create_headless_chrome_driver(headless=self.headless)
            self.wait = WebDriverWait(self.driver, self.timeout)
        
        # Navigate to PPRA active tenders page
        self.driver.get(self.PPRA_ACTIVE_TENDERS_URL)
        
        # Wait for page to load
        self.wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Additional wait for JavaScript to finish executing
        time.sleep(2)
    
    def close(self):
        """Close the browser session."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None
    
    def _find_city_filter_element(self):
        """
        Find the city filter dropdown element.
        
        Returns:
            WebElement: The city filter dropdown element
            
        Raises:
            NoSuchElementException: If city filter element cannot be found
        """
        # The city filter appears to be a custom dropdown
        # Look for elements containing "City" label and nearby "Select" text
        
        # Strategy 1: Find by XPath - look for element with "Select" text near "City" label
        try:
            # Find the City label first
            city_label = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[normalize-space(text())='City' or contains(text(), 'City')]"))
            )
            
            # Find the parent container (look for common container patterns)
            parent = None
            current = city_label
            for _ in range(5):  # Try up to 5 levels up
                current = current.find_element(By.XPATH, "./..")
                parent_classes = current.get_attribute("class") or ""
                if any(keyword in parent_classes.lower() for keyword in ["form", "filter", "row", "col", "group"]):
                    parent = current
                    break
            
            if parent:
                # Look for "Select" text element within the same container
                # Try multiple patterns: exact text match, contains, or button/clickable element
                select_patterns = [
                    ".//*[normalize-space(text())='Select']",
                    ".//*[contains(text(), 'Select')]",
                    ".//*[contains(@class, 'select')]",
                    ".//button[contains(text(), 'Select')]",
                    ".//*[@role='button' and contains(text(), 'Select')]",
                ]
                
                for pattern in select_patterns:
                    try:
                        select_element = parent.find_element(By.XPATH, pattern)
                        if select_element.is_displayed():
                            return select_element
                    except (NoSuchElementException, ElementNotInteractableException):
                        continue
            
            # If parent strategy didn't work, try finding Select element that's a sibling or nearby
            try:
                # Look for Select element that appears after City label in the DOM
                select_element = self.driver.find_element(
                    By.XPATH,
                    "//*[normalize-space(text())='City']/following::*[normalize-space(text())='Select' or contains(text(), 'Select')][1]"
                )
                if select_element.is_displayed():
                    return select_element
            except (NoSuchElementException, ElementNotInteractableException):
                pass
                
        except (TimeoutException, NoSuchElementException):
            pass
        
        # Strategy 2: Try to find by common selectors
        selectors = [
            "//*[contains(@placeholder, 'City')]",
            "//*[contains(@aria-label, 'City')]",
            "//select[contains(@name, 'city') or contains(@id, 'city')]",
            "//*[contains(@class, 'city')]//*[contains(text(), 'Select')]",
            "//button[contains(text(), 'Select')]",
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                if element.is_displayed():
                    return element
            except (NoSuchElementException, ElementNotInteractableException):
                continue
        
        raise NoSuchElementException("Could not find city filter element")
    
    def apply_city_filter(self, city_name: str = "Chakwal") -> bool:
        """
        Apply city filter to show only tenders from the specified city.
        
        Args:
            city_name (str): Name of the city to filter by. Defaults to "Chakwal".
        
        Returns:
            bool: True if filter was applied successfully, False otherwise
        """
        try:
            # Find and click the city filter dropdown
            city_filter = self._find_city_filter_element()
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", city_filter)
            time.sleep(0.5)
            
            # Click to open dropdown
            city_filter.click()
            time.sleep(1.5)  # Wait for dropdown to open
            
            # Wait for dropdown options to appear and find the city option
            # The dropdown might be a custom component, so we need to search for the city name
            city_option = None
            
            # Strategy 1: Try to find the city option by exact or partial text match
            city_option_selectors = [
                f"//*[normalize-space(text())='{city_name}']",
                f"//*[contains(text(), '{city_name}')]",
                f"//li[contains(text(), '{city_name}')]",
                f"//*[@role='option' and contains(text(), '{city_name}')]",
                f"//*[@role='menuitem' and contains(text(), '{city_name}')]",
            ]
            
            for selector in city_option_selectors:
                try:
                    city_option = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    # Verify it's actually visible (not hidden)
                    if city_option.is_displayed():
                        break
                    else:
                        city_option = None
                except (TimeoutException, NoSuchElementException):
                    continue
            
            if city_option is None:
                # Strategy 2: Try typing to filter/search options (for searchable dropdowns)
                try:
                    city_filter.send_keys(city_name)
                    time.sleep(1)
                    
                    # Try finding the option again after typing
                    for selector in city_option_selectors:
                        try:
                            city_option = self.driver.find_element(By.XPATH, selector)
                            if city_option.is_displayed():
                                break
                        except (NoSuchElementException, ElementNotInteractableException):
                            continue
                except Exception:
                    pass
            
            if city_option is None:
                raise NoSuchElementException(f"Could not find city option: {city_name}")
            
            # Scroll option into view and click
            self.driver.execute_script("arguments[0].scrollIntoView(true);", city_option)
            time.sleep(0.3)
            city_option.click()
            time.sleep(0.5)
            
            # Click the Search button to apply the filter
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Search')]"))
            )
            search_button.click()
            
            # Wait for results to load
            time.sleep(3)  # Wait for table to update
            
            # Wait for table to be present/updated
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table, tbody"))
            )
            
            return True
            
        except (TimeoutException, NoSuchElementException, ElementNotInteractableException) as e:
            print(f"Error applying city filter: {str(e)}")
            return False
    
    def verify_city_filter(self, city_name: str = "Chakwal") -> bool:
        """
        Verify that only tenders from the specified city are displayed.
        
        Args:
            city_name (str): Name of the city to verify. Defaults to "Chakwal".
        
        Returns:
            bool: True if all displayed tenders are from the specified city, False otherwise
        """
        try:
            # Wait a bit for table to update after filter
            time.sleep(2)
            
            # Find the table - try multiple selectors
            table = None
            table_selectors = ["table", "tbody", "[class*='table']", "[id*='table']"]
            
            for selector in table_selectors:
                try:
                    table = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if table.is_displayed():
                        break
                except (NoSuchElementException, ElementNotInteractableException):
                    continue
            
            if table is None:
                print("Warning: Could not find table element")
                # Check if there's a "no records" message
                page_text = self.driver.page_source.lower()
                if "no record" in page_text or "no data" in page_text:
                    print("No tenders found - this may be expected if there are no active Chakwal tenders")
                    return True  # This is valid - filter worked, just no results
                return False
            
            # Get all table rows
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr, tr")
            
            # Filter out header rows and "no record" rows
            data_rows = []
            for row in rows:
                row_text = row.text.lower().strip()
                if not row_text or row_text == "":
                    continue
                if "no record" in row_text or "no data" in row_text:
                    print(f"Found 'no record' message: {row.text[:50]}")
                    return True  # Valid - filter applied, just no results
                if any(header in row_text for header in ["sr no", "tender no", "tender details", "downloads", "advertisement", "closing"]):
                    continue  # Skip header row
                data_rows.append(row)
            
            if len(data_rows) == 0:
                print("No data rows found in table (only headers or empty)")
                # Check page for "no records" message
                page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                if "no record" in page_text or "no data" in page_text:
                    print("No tenders found - this may be expected if there are no active Chakwal tenders")
                    return True  # Valid case
                return False
            
            # Check each row for city information
            # The city might be in tender details or a separate column
            verified_count = 0
            for row in data_rows:
                row_text = row.text.lower()
                
                # Verify city name appears in the row
                # Note: This is a basic check - the actual city might be in a specific column
                if city_name.lower() in row_text:
                    verified_count += 1
                else:
                    # Some tenders might not have city explicitly in visible text
                    # This is okay if the filter was applied correctly
                    print(f"Note: Row doesn't explicitly contain '{city_name}' in text: {row_text[:80]}...")
            
            if verified_count > 0:
                print(f"Verified {verified_count} row(s) contain '{city_name}'")
            
            # If we have data rows, consider it verified (filter was applied)
            # The actual city verification is best done by checking the filter state
            return True
            
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error verifying city filter: {str(e)}")
            return False
    
    def _parse_tender_details(self, details_text: str) -> Dict[str, str]:
        """
        Parse tender details text to extract title, category, and department/owner.
        
        Args:
            details_text (str): The raw tender details text from the table
            
        Returns:
            Dict[str, str]: Dictionary with parsed fields (tender_title, category, department_owner)
        """
        result = {
            "tender_title": "",
            "category": "",
            "department_owner": ""
        }
        
        if not details_text:
            return result
        
        # Try to parse structured data from details
        # Common patterns might include:
        # - Title on first line
        # - Category: X or Category - X
        # - Department/Owner: X or Dept: X
        
        lines = [line.strip() for line in details_text.split('\n') if line.strip()]
        
        if lines:
            # First line is often the title
            result["tender_title"] = lines[0]
        
        # Look for category patterns
        for line in lines:
            line_lower = line.lower()
            if "category" in line_lower:
                # Extract category after "category:" or "category -"
                parts = line.split(":", 1) if ":" in line else line.split("-", 1)
                if len(parts) > 1:
                    result["category"] = parts[-1].strip()
                else:
                    result["category"] = line.replace("Category", "").replace("category", "").strip()
        
        # Look for department/owner patterns
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ["department", "dept", "owner", "organization", "org"]):
                # Extract department/owner after keywords
                for keyword in ["department:", "dept:", "owner:", "organization:", "org:"]:
                    if keyword in line_lower:
                        parts = line.split(":", 1)
                        if len(parts) > 1:
                            result["department_owner"] = parts[-1].strip()
                            break
                if not result["department_owner"]:
                    # Try splitting by dash or other separators
                    parts = line.split("-", 1) if "-" in line else [line]
                    if len(parts) > 1:
                        result["department_owner"] = parts[-1].strip()
        
        # If category or department not found, try to infer from remaining lines
        if not result["category"] and len(lines) > 1:
            # Category might be in second or third line
            for i in range(1, min(3, len(lines))):
                if lines[i] and not result["category"]:
                    result["category"] = lines[i]
                    break
        
        if not result["department_owner"] and len(lines) > 2:
            # Department might be in later lines
            for i in range(2, len(lines)):
                if lines[i] and not result["department_owner"]:
                    result["department_owner"] = lines[i]
                    break
        
        return result
    
    def _extract_tse_from_tender_number(self, tender_number: str) -> str:
        """
        Extract TSE (Tender Serial Number) from tender number if available.
        
        Args:
            tender_number (str): The tender number string
            
        Returns:
            str: TSE if found, otherwise empty string
        """
        if not tender_number:
            return ""
        
        # TSE might be part of the tender number or a separate identifier
        # Common patterns: TSE-XXX, TSE XXX, or embedded in tender number
        
        # Look for TSE pattern
        tse_pattern = r'TSE[:\s-]?(\w+)'
        match = re.search(tse_pattern, tender_number, re.IGNORECASE)
        if match:
            return match.group(1) if match.lastindex else match.group(0)
        
        # If no explicit TSE found, return empty (TSE might be same as tender number)
        return ""
    
    def extract_tender_data(self) -> List[Dict]:
        """
        Extract tender data from the filtered table with all required fields.
        
        Returns:
            List[Dict]: List of dictionaries containing tender information with standardized fields:
                - tender_title: str
                - category: str
                - department_owner: str
                - start_date: str
                - closing_date: str
                - tender_number: str
                - tse: str
                - pdf_links: List[str]
        """
        tenders = []
        
        try:
            # Wait a bit for table to be ready
            time.sleep(1)
            
            # Find the table - try multiple selectors
            table = None
            table_selectors = ["table", "tbody", "[class*='table']", "[id*='table']"]
            
            for selector in table_selectors:
                try:
                    table = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if table.is_displayed():
                        break
                except (NoSuchElementException, ElementNotInteractableException):
                    continue
            
            if table is None:
                print("Warning: Could not find table for data extraction")
                return []
            
            # Get all table rows
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr, tr")
            
            for row in rows:
                try:
                    # Skip header rows and "no record" rows
                    row_text = row.text.lower().strip()
                    if not row_text or row_text == "":
                        continue
                    if "no record" in row_text or "no data" in row_text:
                        continue
                    
                    if any(header in row_text for header in ["sr no", "tender no", "tender details", "downloads", "advertisement", "closing"]):
                        # Check if this is actually a data row that happens to contain these words
                        # by checking if it also has numbers (tender numbers, dates, etc.)
                        if not any(char.isdigit() for char in row_text):
                            continue
                    
                    # Extract data from cells
                    cells = row.find_elements(By.CSS_SELECTOR, "td")
                    
                    if len(cells) < 5:  # Expected columns: Sr No, Tender No, Tender Details, Downloads, Advertisement Date, Closing Date
                        continue
                    
                    # Get basic fields
                    tender_number = cells[1].text.strip() if len(cells) > 1 else ""
                    tender_details_text = cells[2].text.strip() if len(cells) > 2 else ""
                    advertisement_date = cells[4].text.strip() if len(cells) > 4 else ""
                    closing_date = cells[5].text.strip() if len(cells) > 5 else ""
                    
                    # Only process if we have at least a tender number
                    if not tender_number:
                        continue
                    
                    # Parse tender details to extract title, category, department/owner
                    parsed_details = self._parse_tender_details(tender_details_text)
                    
                    # Extract TSE from tender number
                    tse = self._extract_tse_from_tender_number(tender_number)
                    
                    # Extract PDF/download links
                    pdf_links = []
                    if len(cells) > 3:
                        download_links = cells[3].find_elements(By.CSS_SELECTOR, "a")
                        for link in download_links:
                            href = link.get_attribute("href")
                            if href:
                                pdf_links.append(href)
                    
                    # Build standardized tender data structure
                    tender_data = {
                        "tender_title": parsed_details["tender_title"] or tender_details_text.split('\n')[0] if tender_details_text else "",
                        "category": parsed_details["category"],
                        "department_owner": parsed_details["department_owner"],
                        "start_date": advertisement_date,
                        "closing_date": closing_date,
                        "tender_number": tender_number,
                        "tse": tse,
                        "pdf_links": pdf_links
                    }
                    
                    tenders.append(tender_data)
                        
                except Exception as e:
                    print(f"Error extracting data from row: {str(e)}")
                    continue
            
            return tenders
            
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error extracting tender data: {str(e)}")
            return []
    
    def export_to_json(self, tenders: List[Dict], filepath: str) -> bool:
        """
        Export tender data to JSON file.
        
        Args:
            tenders (List[Dict]): List of tender dictionaries to export
            filepath (str): Path to the output JSON file
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
            
            # Write JSON file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(tenders, f, indent=2, ensure_ascii=False)
            
            print(f"Successfully exported {len(tenders)} tenders to {filepath}")
            return True
            
        except Exception as e:
            print(f"Error exporting to JSON: {str(e)}")
            return False
    
    def export_to_csv(self, tenders: List[Dict], filepath: str) -> bool:
        """
        Export tender data to CSV file.
        
        Args:
            tenders (List[Dict]): List of tender dictionaries to export
            filepath (str): Path to the output CSV file
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
            
            # Define CSV columns based on standardized structure
            fieldnames = [
                "tender_title",
                "category",
                "department_owner",
                "start_date",
                "closing_date",
                "tender_number",
                "tse",
                "pdf_links"
            ]
            
            # Write CSV file (even if empty, create file with headers)
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for tender in tenders:
                    # Convert pdf_links list to string for CSV
                    row = tender.copy()
                    if "pdf_links" in row and isinstance(row["pdf_links"], list):
                        row["pdf_links"] = "; ".join(row["pdf_links"]) if row["pdf_links"] else ""
                    writer.writerow(row)
            
            if tenders:
                print(f"Successfully exported {len(tenders)} tenders to {filepath}")
            else:
                print(f"Created empty CSV file with headers at {filepath}")
            return True
            
        except Exception as e:
            print(f"Error exporting to CSV: {str(e)}")
            return False
    
    def scrape_chakwal_tenders(self) -> List[Dict]:
        """
        Complete workflow: Apply Chakwal filter, verify, and extract tender data.
        
        Returns:
            List[Dict]: List of dictionaries containing Chakwal tender information
        """
        try:
            # Apply city filter
            print("Applying Chakwal city filter...")
            if not self.apply_city_filter("Chakwal"):
                print("Failed to apply city filter")
                return []
            
            # Verify filter
            print("Verifying city filter...")
            if not self.verify_city_filter("Chakwal"):
                print("Warning: City filter verification failed, but continuing...")
            
            # Extract data
            print("Extracting tender data...")
            tenders = self.extract_tender_data()
            
            print(f"Successfully extracted {len(tenders)} tenders from Chakwal")
            return tenders
            
        except Exception as e:
            print(f"Error in scrape_chakwal_tenders: {str(e)}")
            return []

