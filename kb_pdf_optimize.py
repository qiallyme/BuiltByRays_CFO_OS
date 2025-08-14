#!/usr/bin/env python3
"""
PDF Optimization Script for Cloudflare 25MB Limit
Combines compression and splitting functionality
"""

import os
import sys
import argparse
from pathlib import Path
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Optimize PDFs to meet Cloudflare 25MB limit")
    parser.add_argument("--base", type=str, default="public", 
                       help="Base directory to scan for PDFs (default: public)")
    parser.add_argument("--apply", action="store_true", 
                       help="Actually process files (default: dry run)")
    parser.add_argument("--max-size", type=float, default=25,
                       help="Maximum file size in MB (default: 25)")
    
    args = parser.parse_args()
    
    print("PDF Optimization for Cloudflare 25MB Limit")
    print("=" * 50)
    
    # Step 1: Try compression
    print("\nStep 1: Attempting PDF compression...")
    try:
        result = subprocess.run([
            sys.executable, "kb_compress_pdfs.py", 
            "--base", args.base, 
            "--max-size", str(args.max_size)
        ] + (["--apply"] if args.apply else []), 
        capture_output=True, text=True)
        
        if result.returncode == 0:
            print("OK: Compression step completed")
        else:
            print(f"WARN: Compression step had issues: {result.stderr}")
    except Exception as e:
        print(f"ERROR: Compression step failed: {e}")
    
    # Step 2: Split remaining large PDFs
    print("\nStep 2: Splitting remaining large PDFs...")
    try:
        result = subprocess.run([
            sys.executable, "kb_split_large_pdfs.py", 
            "--base", args.base, 
            "--max-size", str(args.max_size)
        ] + (["--apply"] if args.apply else []), 
        capture_output=True, text=True)
        
        if result.returncode == 0:
            print("OK: Splitting step completed")
        else:
            print(f"WARN: Splitting step had issues: {result.stderr}")
    except Exception as e:
        print(f"ERROR: Splitting step failed: {e}")
    
    # Step 3: Final verification
    print("\nStep 3: Final verification...")
    try:
        result = subprocess.run([
            sys.executable, "kb_compress_pdfs.py", 
            "--base", args.base, 
            "--max-size", str(args.max_size)
        ], capture_output=True, text=True)
        
        if "No PDFs found over the size limit" in result.stdout:
            print("OK: All PDFs are now under the size limit!")
        else:
            print("WARN: Some PDFs may still exceed the limit")
            print("Consider manual intervention or online compression tools")
    except Exception as e:
        print(f"ERROR: Verification failed: {e}")
    
    print("\nPDF optimization process completed!")

if __name__ == "__main__":
    main()
