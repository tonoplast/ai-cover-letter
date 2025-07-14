#!/usr/bin/env python3
"""
Test runner script to demonstrate different test execution options
"""

import subprocess
import sys
import os

def run_command(cmd):
    """Run a command and return the result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0

def main():
    """Main test runner"""
    print("🧪 AI Cover Letter Test Runner")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
    else:
        test_type = "unit"
    
    if test_type == "unit":
        print("Running unit tests only...")
        success = run_command("python -m pytest tests/unit/ -v")
        
    elif test_type == "integration":
        print("Running integration tests (requires API server)...")
        print("Make sure the API server is running on localhost:8000")
        success = run_command("python -m pytest tests/integration/ -v")
        
    elif test_type == "all":
        print("Running all tests...")
        success = run_command("python -m pytest tests/ -v")
        
    elif test_type == "fast":
        print("Running unit tests only (fast)...")
        success = run_command("python -m pytest tests/unit/ -v --tb=short")
        
    else:
        print(f"Unknown test type: {test_type}")
        print("Available options:")
        print("  unit        - Run unit tests only")
        print("  integration - Run integration tests (requires API server)")
        print("  all         - Run all tests")
        print("  fast        - Run unit tests with minimal output")
        sys.exit(1)
    
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()