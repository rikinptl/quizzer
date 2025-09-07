#!/usr/bin/env python3
"""
Text extraction script for PDF and PowerPoint files
"""

import sys
import os
import json
from pathlib import Path

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        import PyPDF2
        
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        return text.strip()
    except ImportError:
        return f"PyPDF2 not available. Install with: pip install PyPDF2"
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"

def extract_text_from_ppt(file_path):
    """Extract text from PowerPoint file"""
    try:
        from pptx import Presentation
        
        text = ""
        prs = Presentation(file_path)
        
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
        
        return text.strip()
    except ImportError:
        return f"python-pptx not available. Install with: pip install python-pptx"
    except Exception as e:
        return f"Error extracting PPT text: {str(e)}"

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_text.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        sys.exit(1)
    
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif file_ext in ['.ppt', '.pptx']:
        text = extract_text_from_ppt(file_path)
    else:
        print(f"Error: Unsupported file type {file_ext}")
        sys.exit(1)
    
    if not text:
        print("Error: No text extracted from file")
        sys.exit(1)
    
    print(text)

if __name__ == "__main__":
    main()