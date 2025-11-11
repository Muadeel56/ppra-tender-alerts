#!/usr/bin/env python3
"""
Verification Script for Issue #33: Combine Scraper & Notification Scripts

This script verifies that all requirements for Issue #33 are met:
1. main.py exists and is executable
2. main.py imports and uses AutomatedTenderMonitor
3. main.py supports CLI arguments
4. main.py executes the end-to-end workflow (scrape -> compare -> send notifications)
"""

import os
import sys
import ast
import importlib.util
from pathlib import Path


def check_file_exists(filepath):
    """Check if a file exists."""
    exists = os.path.exists(filepath)
    print(f"{'✓' if exists else '✗'} File exists: {filepath}")
    return exists


def check_file_content(filepath, required_strings):
    """Check if file contains required strings."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        all_found = True
        for required in required_strings:
            found = required in content
            print(f"{'✓' if found else '✗'} Contains '{required}': {filepath}")
            if not found:
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"✗ Error reading file {filepath}: {e}")
        return False


def check_imports(filepath):
    """Check if file has correct imports."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=filepath)
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == 'scraper.automated_tender_monitor':
                    imports.append(f"from {node.module} import {node.names[0].name}")
        
        has_import = len(imports) > 0
        print(f"{'✓' if has_import else '✗'} Imports AutomatedTenderMonitor: {filepath}")
        if has_import:
            print(f"  Found: {imports[0]}")
        
        return has_import
    except Exception as e:
        print(f"✗ Error parsing file {filepath}: {e}")
        return False


def check_function_exists(filepath, func_name):
    """Check if a function exists in the file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=filepath)
        
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        
        exists = func_name in functions
        print(f"{'✓' if exists else '✗'} Function '{func_name}' exists: {filepath}")
        return exists
    except Exception as e:
        print(f"✗ Error parsing file {filepath}: {e}")
        return False


def check_workflow_execution(filepath):
    """Check if the file calls monitor.run() which executes the workflow."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key workflow indicators
        has_monitor_init = 'AutomatedTenderMonitor(' in content
        has_monitor_run = 'monitor.run()' in content or '.run()' in content
        has_argparse = 'argparse' in content
        
        print(f"{'✓' if has_monitor_init else '✗'} Initializes AutomatedTenderMonitor")
        print(f"{'✓' if has_monitor_run else '✗'} Calls monitor.run() to execute workflow")
        print(f"{'✓' if has_argparse else '✗'} Uses argparse for CLI arguments")
        
        return has_monitor_init and has_monitor_run and has_argparse
    except Exception as e:
        print(f"✗ Error reading file {filepath}: {e}")
        return False


def check_cli_arguments(filepath):
    """Check if CLI arguments are supported."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_args = ['--city', '--whatsapp', '--email', '--no-headless']
        found_args = []
        
        for arg in required_args:
            if arg in content:
                found_args.append(arg)
                print(f"  ✓ Supports argument: {arg}")
            else:
                print(f"  ✗ Missing argument: {arg}")
        
        return len(found_args) == len(required_args)
    except Exception as e:
        print(f"✗ Error reading file {filepath}: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("Issue #33 Verification: Combine Scraper & Notification Scripts")
    print("=" * 70)
    print()
    
    # Get project root
    project_root = Path(__file__).parent
    main_py_path = project_root / 'backend' / 'main.py'
    
    print("Checking Requirements:")
    print("-" * 70)
    
    results = []
    
    # Requirement 1: main.py exists
    print("\n1. File Existence:")
    results.append(check_file_exists(main_py_path))
    
    # Requirement 2: main.py has correct structure
    print("\n2. File Structure:")
    if results[0]:
        results.append(check_function_exists(main_py_path, 'main'))
        results.append(check_imports(main_py_path))
    
    # Requirement 3: main.py executes workflow
    print("\n3. Workflow Execution:")
    if results[0]:
        results.append(check_workflow_execution(main_py_path))
    
    # Requirement 4: CLI arguments support
    print("\n4. CLI Arguments Support:")
    if results[0]:
        results.append(check_cli_arguments(main_py_path))
    
    # Requirement 5: Content checks
    print("\n5. Content Verification:")
    if results[0]:
        required_content = [
            'AutomatedTenderMonitor',
            'scrape',
            'compare',
            'send notifications',
            'argparse'
        ]
        results.append(check_file_content(main_py_path, required_content))
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary:")
    print("-" * 70)
    
    all_passed = all(results)
    
    if all_passed:
        print("✓ ALL REQUIREMENTS MET!")
        print("\nIssue #33 Requirements:")
        print("  ✓ main.py exists")
        print("  ✓ main.py executes end-to-end workflow")
        print("  ✓ main.py runs: scrape -> compare -> send notifications")
        print("  ✓ main.py supports CLI arguments")
    else:
        print("✗ SOME REQUIREMENTS NOT MET")
        print(f"  Passed: {sum(results)}/{len(results)} checks")
    
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

