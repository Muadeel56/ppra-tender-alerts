#!/usr/bin/env python3
"""
Test API Connectivity Script

This script tests connectivity to the PPRA API endpoint by making a POST request
and handling responses gracefully, including 405 Method Not Allowed errors.
"""

import os
import sys
import requests
from dotenv import load_dotenv


def main():
    """Main function to test PPRA API connectivity."""
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Get PPRA API URL from environment variable or use default placeholder
    ppra_api_url = os.getenv('PPRA_API_URL', 'https://ppra.gov.pk/api/tenders')
    
    print(f"Testing connectivity to PPRA API endpoint...")
    print(f"URL: {ppra_api_url}")
    print("-" * 60)
    
    try:
        # Make POST request with appropriate headers
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'PPRA-Tender-Alerts/1.0'
        }
        
        # Sample payload (can be empty or minimal for testing)
        payload = {}
        
        # Make the POST request
        response = requests.post(
            ppra_api_url,
            json=payload,
            headers=headers,
            timeout=10  # 10 second timeout
        )
        
        # Check response status
        print(f"Status Code: {response.status_code}")
        
        # Handle 405 Method Not Allowed gracefully
        if response.status_code == 405:
            print("Response: 405 Method Not Allowed")
            print("Note: The endpoint does not accept POST requests.")
            print("This is expected behavior - the endpoint may only accept GET requests.")
            return 0
        
        # Handle other HTTP errors
        if response.status_code >= 400:
            print(f"Error: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error Details: {error_data}")
            except ValueError:
                print(f"Error Message: {response.text[:200]}")
            return 1
        
        # Success case
        print("Response: Success")
        print(f"Response Headers: {dict(response.headers)}")
        
        # Try to print response body (limit to first 500 chars)
        try:
            response_data = response.json()
            print(f"Response Body (first 500 chars): {str(response_data)[:500]}")
        except ValueError:
            print(f"Response Body (first 500 chars): {response.text[:500]}")
        
        return 0
        
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: Could not connect to {ppra_api_url}")
        print(f"Details: {str(e)}")
        print("Please check:")
        print("  - Internet connectivity")
        print("  - The API endpoint URL is correct")
        print("  - The API server is running")
        return 1
        
    except requests.exceptions.Timeout as e:
        print(f"Timeout Error: Request to {ppra_api_url} timed out")
        print(f"Details: {str(e)}")
        return 1
        
    except requests.exceptions.RequestException as e:
        print(f"Request Error: An error occurred while making the request")
        print(f"Details: {str(e)}")
        return 1
        
    except Exception as e:
        print(f"Unexpected Error: {type(e).__name__}")
        print(f"Details: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

