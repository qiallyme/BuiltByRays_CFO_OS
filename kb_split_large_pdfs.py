#!/usr/bin/env python3
"""
PDF Splitter for Cloudflare 25MB Limit
Splits large PDFs into smaller chunks that meet the size limit
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
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Installing required packages...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
            return True
        except subprocess.CalledProcessError:
            print("Failed to install dependencies. Please install manually:")
            print("pip install PyPDF2")
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

def split_pdf_by_pages(input_path: Path, output_dir: Path, pages_per_chunk: int = 10) -> List[Path]:
    """Split PDF into chunks by page count."""
    try:
        import PyPDF2
        
        with open(input_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            
            if total_pages <= pages_per_chunk:
                print(f"  PDF has {total_pages} pages, no splitting needed")
                return []
            
            chunks = []
            for i in range(0, total_pages, pages_per_chunk):
                writer = PyPDF2.PdfWriter()
                end_page = min(i + pages_per_chunk, total_pages)
                
                for page_num in range(i, end_page):
                    writer.add_page(reader.pages[page_num])
                
                # Create output filename
                base_name = input_path.stem
                chunk_num = i // pages_per_chunk + 1
                output_filename = f"{base_name}_part{chunk_num:02d}.pdf"
                output_path = output_dir / output_filename
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                chunks.append(output_path)
                print(f"  Created chunk {chunk_num}: {output_filename} ({end_page - i} pages)")
            
            return chunks
            
    except Exception as e:
        print(f"  PDF splitting failed: {e}")
        return []

def split_pdf_by_size(input_path: Path, output_dir: Path, target_size_mb: float) -> List[Path]:
    """Split PDF into chunks by target size."""
    try:
        import PyPDF2
        
        with open(input_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            
            chunks = []
            current_writer = PyPDF2.PdfWriter()
            current_chunk = 1
            current_size = 0
            
            for page_num, page in enumerate(reader.pages):
                # Create temporary writer to test size
                test_writer = PyPDF2.PdfWriter()
                for existing_page in current_writer.pages:
                    test_writer.add_page(existing_page)
                test_writer.add_page(page)
                
                # Write to temporary file to check size
                temp_path = output_dir / f"temp_{current_chunk}.pdf"
                with open(temp_path, 'wb') as temp_file:
                    test_writer.write(temp_file)
                
                temp_size_mb = get_pdf_size_mb(temp_path)
                temp_path.unlink()  # Remove temp file
                
                if temp_size_mb > target_size_mb and current_writer.pages:
                    # Current chunk would be too large, save it and start new chunk
                    output_filename = f"{input_path.stem}_part{current_chunk:02d}.pdf"
                    output_path = output_dir / output_filename
                    
                    with open(output_path, 'wb') as output_file:
                        current_writer.write(output_file)
                    
                    chunks.append(output_path)
                    print(f"  Created chunk {current_chunk}: {output_filename} ({len(current_writer.pages)} pages, {current_size:.2f}MB)")
                    
                    # Start new chunk
                    current_writer = PyPDF2.PdfWriter()
                    current_chunk += 1
                    current_size = 0
                
                # Add page to current chunk
                current_writer.add_page(page)
                current_size = temp_size_mb
            
            # Save final chunk
            if current_writer.pages:
                output_filename = f"{input_path.stem}_part{current_chunk:02d}.pdf"
                output_path = output_dir / output_filename
                
                with open(output_path, 'wb') as output_file:
                    current_writer.write(output_file)
                
                chunks.append(output_path)
                print(f"  Created chunk {current_chunk}: {output_filename} ({len(current_writer.pages)} pages, {current_size:.2f}MB)")
            
            return chunks
            
    except Exception as e:
        print(f"  PDF size-based splitting failed: {e}")
        return []

def split_pdf(input_path: Path, target_size_mb: float = MAX_SIZE_MB) -> bool:
    """Split a large PDF into smaller chunks."""
    print(f"Splitting: {input_path.name} ({get_pdf_size_mb(input_path):.2f}MB)")
    
    # Create backup
    backup_path = input_path.with_suffix('.pdf.backup')
    shutil.copy2(input_path, backup_path)
    
    # Create output directory for chunks
    output_dir = input_path.parent / f"{input_path.stem}_chunks"
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Try size-based splitting first
        chunks = split_pdf_by_size(input_path, output_dir, target_size_mb)
        
        if not chunks:
            # Fall back to page-based splitting
            print("  Size-based splitting failed, trying page-based splitting...")
            chunks = split_pdf_by_pages(input_path, output_dir, pages_per_chunk=5)
        
        if chunks:
            # Verify all chunks are under the limit
            oversized_chunks = []
            for chunk in chunks:
                size_mb = get_pdf_size_mb(chunk)
                if size_mb > target_size_mb:
                    oversized_chunks.append((chunk, size_mb))
            
            if oversized_chunks:
                print(f"  ⚠️  {len(oversized_chunks)} chunks still exceed {target_size_mb}MB:")
                for chunk, size_mb in oversized_chunks:
                    print(f"    {chunk.name}: {size_mb:.2f}MB")
                return False
            
            # Move original to archive and create index file
            archive_dir = input_path.parent / "large_pdfs_archive"
            archive_dir.mkdir(exist_ok=True)
            
            archive_path = archive_dir / input_path.name
            shutil.move(str(input_path), str(archive_path))
            
            # Create index file
            index_path = output_dir / "README.md"
            with open(index_path, 'w') as f:
                f.write(f"# Split PDF: {input_path.name}\n\n")
                f.write(f"Original file ({get_pdf_size_mb(archive_path):.2f}MB) was too large for Cloudflare.\n")
                f.write(f"Split into {len(chunks)} smaller chunks:\n\n")
                for i, chunk in enumerate(chunks, 1):
                    size_mb = get_pdf_size_mb(chunk)
                    f.write(f"{i}. [{chunk.name}]({chunk.name}) ({size_mb:.2f}MB)\n")
            
            print(f"  ✅ Successfully split into {len(chunks)} chunks")
            print(f"  📁 Original moved to: {archive_path}")
            print(f"  📄 Chunks available in: {output_dir}")
            return True
        else:
            print("  ❌ Failed to split PDF")
            return False
            
    except Exception as e:
        print(f"  ❌ Splitting error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Split large PDFs to meet Cloudflare 25MB limit")
    parser.add_argument("--base", type=str, default="public", 
                       help="Base directory to scan for PDFs (default: public)")
    parser.add_argument("--apply", action="store_true", 
                       help="Actually split files (default: dry run)")
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
        print("Dry run mode. Use --apply to actually split files.")
        return
    
    # Split PDFs
    success_count = 0
    for pdf_path, size_mb in large_pdfs:
        if split_pdf(pdf_path, args.max_size):
            success_count += 1
        print()
    
    print(f"Splitting complete: {success_count}/{len(large_pdfs)} PDFs successfully split")

if __name__ == "__main__":
    main()
