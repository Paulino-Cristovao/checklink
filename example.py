#!/usr/bin/env python3
"""
CheckLink - Example Usage Script

This script demonstrates how to use CheckLink programmatically
and provides examples for different use cases.
"""

import subprocess
import sys
from pathlib import Path

def run_example(description, command):
    """Run an example command with description"""
    print(f"\n{'='*60}")
    print(f"Example: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    # Ask for confirmation
    response = input("Run this example? (y/n): ").lower().strip()
    if response == 'y':
        try:
            subprocess.run(command.split(), check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {e}")
        except KeyboardInterrupt:
            print("\nExample interrupted by user")
    else:
        print("Example skipped")

def main():
    """Main example runner"""
    print("CheckLink - Example Usage")
    print("This script shows different ways to use CheckLink")
    
    # Check if checklink.py exists
    if not Path("checklink.py").exists():
        print("Error: checklink.py not found in current directory")
        sys.exit(1)
    
    examples = [
        {
            "description": "Quick health check (homepage only)",
            "command": "python checklink.py https://example.com --depth 0 --output-dir quick_check"
        },
        {
            "description": "Embassy website analysis (multi-language)",
            "command": "python checklink.py https://ambassademozambiquefrance.fr/?lang=PT --depth 1 --output-dir embassy_analysis --delay 0.5"
        },
        {
            "description": "Comprehensive analysis with AI",
            "command": "python checklink.py https://example.com --depth 2 --output-dir comprehensive_analysis --delay 1.0"
        },
        {
            "description": "Fast scan for development",
            "command": "python checklink.py https://localhost:3000 --depth 1 --delay 0.1 --output-dir dev_check"
        }
    ]
    
    for example in examples:
        run_example(example["description"], example["command"])
    
    print(f"\n{'='*60}")
    print("Examples completed!")
    print("Check the generated output directories for PDF reports.")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()