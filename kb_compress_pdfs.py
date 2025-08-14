#!/usr/bin/env python3
"""
PDF Compression Script for Cloudflare 25MB Limit
Scans for PDFs over 25MB and compresses them using PyPDF2 and Pillow
"""

import os
import sys
import argparse
from pathlib import Path
import subprocess
import shutil
from typing import List, Tuple

# Constants
MAX_SIZE_MB = 25
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    try:
        import PyPDF2
        from PIL import Image
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Installing required packages...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2", "Pillow"])
            return True
        except subprocess.CalledProcessError:
            print("Failed to install dependencies. Please install manually:")
            print("pip install PyPDF2 Pillow")
            return False

def get_pdf_size_mb(file_path: Path) -> float:
    """Get PDF file size in MB."""
    return file_path.stat().st_size / (1024 * 1024)

def find_large_pdfs(base_dir: Path, max_size_mb: float = MAX_SIZE_MB) -> List[Tuple[Path, float]]:
    """Find PDFs larger than the specified size."""
    large_pdfs = []
    max_size_bytes = max_size_mb * 1024 * 1024
    
    for pdf_file in base_dir.rglob("*.pdf"):
        if pdf_file.is_file() and not pdf_file.name.endswith('.backup') and 'large_pdfs_archive' not in str(pdf_file):
            size_bytes = pdf_file.stat().st_size
            if size_bytes > max_size_bytes:
                size_mb = size_bytes / (1024 * 1024)
                large_pdfs.append((pdf_file, size_mb))
    
    return sorted(large_pdfs, key=lambda x: x[1], reverse=True)

def compress_pdf_with_pypdf2(input_path: Path, output_path: Path, target_size_mb: float) -> bool:
    """Compress PDF using PyPDF2 by removing metadata and optimizing."""
    try:
        import PyPDF2
        
        with open(input_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()
            
            # Copy pages without metadata
            for page in reader.pages:
                writer.add_page(page)
            
            # Write compressed PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
        
        # Check if compression was successful
        new_size_mb = get_pdf_size_mb(output_path)
        if new_size_mb <= target_size_mb:
            return True
        else:
            print(f"  PyPDF2 compression insufficient: {new_size_mb:.2f}MB > {target_size_mb:.2f}MB")
            return False
            
    except Exception as e:
        print(f"  PyPDF2 compression failed: {e}")
        return False

def compress_pdf_aggressive(input_path: Path, output_path: Path, target_size_mb: float) -> bool:
    """Aggressive PDF compression using multiple techniques."""
    try:
        import PyPDF2
        import io
        import zlib
        
        with open(input_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()
            
            # Copy pages and try to optimize
            for page in reader.pages:
                # Try to compress page content
                try:
                    # Get page content and compress it
                    if '/Contents' in page:
                        content = page['/Contents'].get_data()
                        # Compress content using zlib
                        compressed_content = zlib.compress(content, level=9)
                        if len(compressed_content) < len(content):
                            # Create new page with compressed content
                            new_page = PyPDF2.generic.PageObject.create_blank_page(
                                width=page.mediabox.width,
                                height=page.mediabox.height
                            )
                            new_page.merge_page(page)
                            writer.add_page(new_page)
                        else:
                            writer.add_page(page)
                    else:
                        writer.add_page(page)
                except:
                    writer.add_page(page)
            
            # Write with maximum compression
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
        
        # Check if compression was successful
        new_size_mb = get_pdf_size_mb(output_path)
        if new_size_mb <= target_size_mb:
            print(f"  Aggressive compression successful: {new_size_mb:.2f}MB")
            return True
        else:
            print(f"  Aggressive compression insufficient: {new_size_mb:.2f}MB > {target_size_mb:.2f}MB")
            return False
            
    except Exception as e:
        print(f"  Aggressive compression failed: {e}")
        return False

def compress_pdf_with_qpdf(input_path: Path, output_path: Path, target_size_mb: float) -> bool:
    """Compress PDF using qpdf if available."""
    try:
        # Try to find qpdf
        qpdf_path = None
        for qpdf_name in ['qpdf', 'qpdf.exe']:
            try:
                result = subprocess.run([qpdf_name, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    qpdf_path = qpdf_name
                    break
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        if not qpdf_path:
            print("  qpdf not found, skipping qpdf compression")
            return False
        
        # qpdf compression command with linearization and optimization
        cmd = [
            qpdf_path,
            '--linearize',  # Optimize for web viewing
            '--object-streams=generate',  # Enable object streams
            '--compress-streams=y',  # Compress streams
            '--recompress-flate',  # Recompress flate streams
            str(input_path),
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and output_path.exists():
            new_size_mb = get_pdf_size_mb(output_path)
            if new_size_mb <= target_size_mb:
                print(f"  qpdf compression successful: {new_size_mb:.2f}MB")
                return True
            else:
                print(f"  qpdf compression insufficient: {new_size_mb:.2f}MB > {target_size_mb:.2f}MB")
                return False
        else:
            print(f"  qpdf compression failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  qpdf compression error: {e}")
        return False

def compress_pdf_with_ghostscript(input_path: Path, output_path: Path, target_size_mb: float) -> bool:
    """Compress PDF using Ghostscript if available."""
    try:
        # Try to find ghostscript
        gs_path = None
        for gs_name in ['gswin64c', 'gswin32c', 'gs']:
            try:
                result = subprocess.run([gs_name, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    gs_path = gs_name
                    break
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        if not gs_path:
            print("  Ghostscript not found, skipping Ghostscript compression")
            return False
        
        # Calculate quality based on target size
        current_size_mb = get_pdf_size_mb(input_path)
        quality_ratio = target_size_mb / current_size_mb
        quality = max(10, min(100, int(quality_ratio * 100)))
        
        # Ghostscript compression command
        cmd = [
            gs_path,
            '-sDEVICE=pdfwrite',
            '-dPDFSETTINGS=/ebook',  # Use ebook settings for good compression
            '-dCompatibilityLevel=1.4',
            '-dNOPAUSE',
            '-dQUIET',
            '-dBATCH',
            f'-sOutputFile={output_path}',
            str(input_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and output_path.exists():
            new_size_mb = get_pdf_size_mb(output_path)
            if new_size_mb <= target_size_mb:
                print(f"  Ghostscript compression successful: {new_size_mb:.2f}MB")
                return True
            else:
                print(f"  Ghostscript compression insufficient: {new_size_mb:.2f}MB > {target_size_mb:.2f}MB")
                return False
        else:
            print(f"  Ghostscript compression failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  Ghostscript compression error: {e}")
        return False

def compress_pdf(input_path: Path, target_size_mb: float = MAX_SIZE_MB) -> bool:
    """Compress a PDF file to meet the target size."""
    print(f"Compressing: {input_path.name} ({get_pdf_size_mb(input_path):.2f}MB)")
    
    # Create backup
    backup_path = input_path.with_suffix('.pdf.backup')
    shutil.copy2(input_path, backup_path)
    
    # Create temporary output path
    temp_path = input_path.with_suffix('.pdf.temp')
    
    try:
        # Try Ghostscript first (best compression)
        if compress_pdf_with_ghostscript(input_path, temp_path, target_size_mb):
            shutil.move(temp_path, input_path)
            backup_path.unlink()  # Remove backup since compression succeeded
            return True
        
        # Try qpdf (good compression)
        if compress_pdf_with_qpdf(input_path, temp_path, target_size_mb):
            shutil.move(temp_path, input_path)
            backup_path.unlink()  # Remove backup since compression succeeded
            return True
        
        # Try aggressive compression
        if compress_pdf_aggressive(input_path, temp_path, target_size_mb):
            shutil.move(temp_path, input_path)
            backup_path.unlink()  # Remove backup since compression succeeded
            return True
        
        # Fall back to PyPDF2 (basic compression)
        if compress_pdf_with_pypdf2(input_path, temp_path, target_size_mb):
            shutil.move(temp_path, input_path)
            backup_path.unlink()  # Remove backup since compression succeeded
            return True
        
        # If all methods fail, restore backup
        print(f"  All compression methods failed, keeping original")
        if temp_path.exists():
            temp_path.unlink()
        return False
        
    except Exception as e:
        print(f"  Compression error: {e}")
        # Restore backup
        if temp_path.exists():
            temp_path.unlink()
        return False

def main():
    parser = argparse.ArgumentParser(description="Compress PDFs to meet Cloudflare 25MB limit")
    parser.add_argument("--base", type=str, default="public", 
                       help="Base directory to scan for PDFs (default: public)")
    parser.add_argument("--apply", action="store_true", 
                       help="Actually compress files (default: dry run)")
    parser.add_argument("--max-size", type=float, default=MAX_SIZE_MB,
                       help=f"Maximum file size in MB (default: {MAX_SIZE_MB})")
    
    args = parser.parse_args()
    
    base_dir = Path(args.base)
    if not base_dir.exists():
        print(f"Error: Directory '{base_dir}' does not exist")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print(f"Scanning for PDFs over {args.max_size}MB in: {base_dir}")
    print()
    
    # Find large PDFs
    large_pdfs = find_large_pdfs(base_dir, args.max_size)
    
    if not large_pdfs:
        print("OK: No PDFs found over the size limit.")
        return
    
    print(f"Found {len(large_pdfs)} PDF(s) over {args.max_size}MB:")
    for pdf_path, size_mb in large_pdfs:
        print(f"  {pdf_path.name}: {size_mb:.2f}MB")
    print()
    
    if not args.apply:
        print("Dry run mode. Use --apply to actually compress files.")
        return
    
    # Compress PDFs
    success_count = 0
    for pdf_path, size_mb in large_pdfs:
        if compress_pdf(pdf_path, args.max_size):
            success_count += 1
        print()
    
    print(f"Compression complete: {success_count}/{len(large_pdfs)} PDFs successfully compressed")
    
    if success_count < len(large_pdfs):
        print("\n⚠️  Some PDFs could not be compressed to meet the size limit.")
        print("Consider:")
        print("1. Using online PDF compressors (e.g., SmallPDF, ILovePDF)")
        print("2. Splitting large PDFs into smaller files")
        print("3. Converting to images and creating a new PDF")
        print("4. Using Ghostscript or qpdf if available")

if __name__ == "__main__":
    main()
