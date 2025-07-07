#!/usr/bin/env python3
"""
Installation script for image extraction dependencies
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a Python package using uv"""
    try:
        # Try uv first
        subprocess.check_call(["uv", "add", package])
        print(f"✅ Successfully installed {package}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Fallback to pip if uv not available
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Successfully installed {package}")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR is available: {version}")
        return True
    except ImportError:
        print("❌ pytesseract Python package not installed")
        return False
    except Exception as e:
        print(f"❌ Tesseract OCR not found: {e}")
        print("\n📋 To install Tesseract OCR:")
        print("Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        print("macOS: brew install tesseract")
        print("Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        return False

def main():
    print("🔧 Installing Image Extraction Dependencies")
    print("=" * 50)
    
    # List of packages to install
    packages = [
        "PyMuPDF==1.23.8",
        "Pillow==10.1.0", 
        "pytesseract==0.3.10",
        "opencv-python==4.8.1.78",
        "numpy==1.24.3"
    ]
    
    print("\n📦 Installing Python packages...")
    success_count = 0
    
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Installation Summary: {success_count}/{len(packages)} packages installed")
    
    print("\n🔍 Checking Tesseract OCR installation...")
    tesseract_ok = check_tesseract()
    
    print("\n" + "=" * 50)
    if success_count == len(packages) and tesseract_ok:
        print("🎉 All dependencies installed successfully!")
        print("✅ Image extraction feature is now available")
    else:
        print("⚠️  Some dependencies may not be fully installed")
        print("📋 Please check the installation guide for manual steps")
    
    print("\n📖 Next steps:")
    print("1. Restart your application")
    print("2. Enable 'Extract Text from Images in PDFs' in the upload form")
    print("3. Upload a PDF with images to test the feature")

if __name__ == "__main__":
    main() 