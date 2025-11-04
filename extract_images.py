#!/usr/bin/env python3
"""
HTML Image Extractor
Extracts base64-encoded images from HTML files and replaces them with external references.
"""

import re
import base64
import os
from pathlib import Path

def extract_base64_images(html_content, output_dir="images"):
    """
    Extract all base64-encoded images from HTML and replace with file references.
    
    Args:
        html_content: The HTML content as a string
        output_dir: Directory name for extracted images (default: "images")
    
    Returns:
        Modified HTML content with external image references
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)
    
    # Pattern to match base64 images in src attributes and CSS
    # Matches: data:image/[type];base64,[base64_string]
    pattern = r'data:image/(png|jpeg|jpg|gif|webp|svg\+xml);base64,([A-Za-z0-9+/=]+)'
    
    image_count = 0
    
    def replace_base64(match):
        nonlocal image_count
        image_count += 1
        
        # Get image type and base64 data
        img_type = match.group(1)
        base64_data = match.group(2)
        
        # Convert svg+xml to svg for file extension
        if img_type == 'svg+xml':
            extension = 'svg'
        else:
            extension = img_type
        
        # Generate filename
        filename = f"image_{image_count:04d}.{extension}"
        filepath = os.path.join(output_dir, filename)
        
        # Decode and save the image
        try:
            image_data = base64.b64decode(base64_data)
            with open(filepath, 'wb') as f:
                f.write(image_data)
            print(f"Extracted: {filename} ({len(image_data) / 1024 / 1024:.2f} MB)")
        except Exception as e:
            print(f"Error extracting image {image_count}: {e}")
            return match.group(0)  # Return original if error
        
        # Return the new image reference
        return f"./{output_dir}/{filename}"
    
    # Replace all base64 images
    print("Extracting base64 images...")
    modified_html = re.sub(pattern, replace_base64, html_content)
    
    print(f"\nTotal images extracted: {image_count}")
    
    return modified_html

def process_html_file(input_file, output_file=None):
    """
    Process an HTML file to extract images.
    
    Args:
        input_file: Path to input HTML file
        output_file: Path to output HTML file (default: input_file with '_optimized' suffix)
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"Error: File '{input_file}' not found!")
        return
    
    # Generate output filename if not provided
    if output_file is None:
        output_file = input_path.stem + "_optimized" + input_path.suffix
    
    output_path = Path(output_file)
    
    # Get original file size
    original_size = input_path.stat().st_size
    print(f"Original file size: {original_size / 1024 / 1024:.2f} MB")
    print(f"Reading '{input_file}'...")
    
    # Read HTML file
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        with open(input_path, 'r', encoding='latin-1') as f:
            html_content = f.read()
    
    # Extract images
    modified_html = extract_base64_images(html_content)
    
    # Write optimized HTML
    print(f"\nWriting optimized HTML to '{output_file}'...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(modified_html)
    
    # Get new file size
    new_size = output_path.stat().st_size
    reduction = ((original_size - new_size) / original_size) * 100
    
    print(f"\n✓ Done!")
    print(f"  New file size: {new_size / 1024 / 1024:.2f} MB")
    print(f"  Reduction: {reduction:.1f}%")
    print(f"\nTo use:")
    print(f"  1. Upload '{output_file}' to GitHub")
    print(f"  2. Upload the 'images/' folder to GitHub")
    print(f"  3. Make sure they're in the same directory")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python extract_images.py <input_html_file> [output_html_file]")
        print("\nExample:")
        print("  python extract_images.py mypage.html")
        print("  python extract_images.py mypage.html mypage_optimized.html")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    process_html_file(input_file, output_file)
