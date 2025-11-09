"""
Tender Storage Module

This module provides functionality to store and manage tender data locally,
including duplicate detection and merging of new tenders with existing ones.
"""

import json
import os
from typing import List, Dict, Optional, Tuple


def load_tenders(filepath: str) -> List[Dict]:
    """
    Load existing tenders from a JSON file.
    
    Args:
        filepath (str): Path to the JSON file containing tenders
        
    Returns:
        List[Dict]: List of tender dictionaries. Returns empty list if file doesn't exist or is invalid.
    """
    try:
        if not os.path.exists(filepath):
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Ensure data is a list
        if not isinstance(data, list):
            print(f"Warning: {filepath} does not contain a JSON array. Returning empty list.")
            return []
            
        return data
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {str(e)}")
        return []
    except Exception as e:
        print(f"Error loading tenders from {filepath}: {str(e)}")
        return []


def save_tenders(tenders: List[Dict], filepath: str) -> bool:
    """
    Save tenders to a JSON file.
    
    Args:
        tenders (List[Dict]): List of tender dictionaries to save
        filepath (str): Path to the output JSON file
        
    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        
        # Write JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(tenders, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        print(f"Error saving tenders to {filepath}: {str(e)}")
        return False


def is_duplicate(tender: Dict, existing_tenders: List[Dict]) -> bool:
    """
    Check if a tender already exists in the existing tenders list.
    
    Duplicate detection is based on tender_number field (case-insensitive comparison).
    
    Args:
        tender (Dict): Tender dictionary to check
        existing_tenders (List[Dict]): List of existing tender dictionaries
        
    Returns:
        bool: True if tender is a duplicate, False otherwise
    """
    if not tender or 'tender_number' not in tender:
        return False
    
    tender_number = str(tender['tender_number']).strip().lower()
    
    for existing_tender in existing_tenders:
        if 'tender_number' in existing_tender:
            existing_number = str(existing_tender['tender_number']).strip().lower()
            if existing_number == tender_number:
                return True
    
    return False


def merge_tenders(existing_tenders: List[Dict], new_tenders: List[Dict]) -> Tuple[List[Dict], int]:
    """
    Merge new tenders with existing tenders, skipping duplicates.
    
    Args:
        existing_tenders (List[Dict]): List of existing tender dictionaries
        new_tenders (List[Dict]): List of new tender dictionaries to merge
        
    Returns:
        tuple[List[Dict], int]: Tuple containing:
            - Merged list of tenders (existing + new non-duplicates)
            - Count of new tenders added
    """
    merged = existing_tenders.copy()
    new_count = 0
    
    for new_tender in new_tenders:
        if not is_duplicate(new_tender, merged):
            merged.append(new_tender)
            new_count += 1
    
    return merged, new_count


def get_tenders_filepath(project_root: Optional[str] = None) -> str:
    """
    Get the absolute path to the tenders.json file.
    
    Args:
        project_root (Optional[str]): Path to project root. If None, attempts to detect it.
        
    Returns:
        str: Absolute path to data/tenders.json
    """
    if project_root is None:
        # Try to detect project root by looking for common markers
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up from backend/scraper/ to project root
        project_root = os.path.dirname(os.path.dirname(current_dir))
    
    return os.path.join(project_root, 'data', 'tenders.json')

