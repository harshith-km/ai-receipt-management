#!/usr/bin/env python3
"""
Test script to verify Smart Expense Tracker setup
"""

import sys
import subprocess
import importlib.util

def check_python_version():
    """Check if Python version is 3.7+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ {version_line}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ Tesseract OCR is not installed or not in PATH")
    print("   Install with: sudo apt-get install tesseract-ocr")
    return False

def check_python_packages():
    """Check if required Python packages are available"""
    required_packages = [
        'flask', 'flask_cors', 'PIL', 'pytesseract', 'cv2', 'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'PIL':
                importlib.import_module('PIL')
            elif package == 'cv2':
                importlib.import_module('cv2')
            elif package == 'flask_cors':
                importlib.import_module('flask_cors')
            else:
                importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """Run all checks"""
    print("🧾 Smart Expense Tracker - Setup Verification")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Tesseract OCR", check_tesseract),
        ("Python Packages", check_python_packages),
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All checks passed! You're ready to run the Smart Expense Tracker.")
        print("\n🚀 To start the application:")
        print("   ./run.sh")
        print("\n   Or manually:")
        print("   Backend:  cd backend && python app.py")
        print("   Frontend: cd frontend && npm start")
    else:
        print("❌ Some checks failed. Please fix the issues above before running the app.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
