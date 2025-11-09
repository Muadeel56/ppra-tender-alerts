"""
Browser configuration module for Selenium WebDriver.

This module provides functions to create and configure Chrome WebDriver instances
for headless browser automation in the PPRA Tender Alerts project.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from typing import Optional


def create_headless_chrome_driver(headless: bool = True) -> webdriver.Chrome:
    """
    Create a configured Chrome WebDriver instance for headless browser automation.
    
    Args:
        headless (bool): If True, run browser in headless mode. Defaults to True.
    
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
    
    Raises:
        Exception: If WebDriver initialization fails
    """
    try:
        # Configure Chrome options
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        
        # Performance optimizations
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-images')  # Disable image loading for faster scraping
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        
        # User agent to avoid detection
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Window size (useful even in headless mode)
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Disable logging
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # Use webdriver-manager to automatically handle ChromeDriver
        service = Service(ChromeDriverManager().install())
        
        # Create and return the WebDriver instance
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        return driver
        
    except Exception as e:
        raise Exception(f"Failed to initialize Chrome WebDriver: {str(e)}")


def create_chrome_driver(headless: bool = False) -> webdriver.Chrome:
    """
    Create a Chrome WebDriver instance (non-headless by default).
    
    This is a convenience function that calls create_headless_chrome_driver
    with headless=False.
    
    Args:
        headless (bool): If True, run browser in headless mode. Defaults to False.
    
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
    """
    return create_headless_chrome_driver(headless=headless)

