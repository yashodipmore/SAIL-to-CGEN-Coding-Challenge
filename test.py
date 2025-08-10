#!/usr/bin/env python3
"""
Test script for SAIL to CGEN converter
"""

import subprocess
import sys
from pathlib import Path


def run_test(input_file: str, expected_patterns: list):
    """Run converter and check output"""
    print(f"\n{'='*50}")
    print(f"Testing: {input_file}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(
            [sys.executable, "converter.py", input_file],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.returncode != 0:
            print(f"ERROR: {result.stderr}")
            return False
        
        output = result.stdout.strip()
        print("Output:")
        print(output)
        
        # Check for expected patterns
        success = True
        for pattern in expected_patterns:
            if pattern not in output:
                print(f"WARNING: Expected pattern not found: {pattern}")
                success = False
        
        return success
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    """Run all tests"""
    print("SAIL to CGEN - Converter Tests")
    
    # Test YAML
    yaml_patterns = [
        "(yaml:receipt",
        "Oz-Ware Purchase Invoice",
        "(yaml:date (make-date 2012 08 06))",
        "(yaml:customer",
        "(yaml:first_name \"Dorothy\")",
        "(yaml:family_name \"Gale\")",
        "(yaml:items",
        "(yaml:item",
        "'A4786",
        "Water Bucket (Filled)",
        "'E1628",
        "High Heeled"
    ]
    
    # Test JSON
    json_patterns = [
        "(json:receipt",
        "Oz-Ware Purchase Invoice",
        "(json:date (make-date 2012 08 06))",
        "(json:customer",
        "(json:first_name \"Dorothy\")",
        "(json:family_name \"Gale\")",
        "(json:items",
        "(json:item",
        "'A4786",
        "Water Bucket (Filled)",
        "'E1628"
    ]
    
    yaml_success = run_test("sample.yaml", yaml_patterns)
    json_success = run_test("sample.json", json_patterns)
    
    print(f"\n{'='*50}")
    print("TEST RESULTS:")
    print(f"YAML Test: {'PASS' if yaml_success else 'FAIL'}")
    print(f"JSON Test: {'PASS' if json_success else 'FAIL'}")
    print(f"{'='*50}")
    
    if yaml_success and json_success:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
