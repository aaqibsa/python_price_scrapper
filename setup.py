#!/usr/bin/env python3
"""
Setup script for Python Scrapper
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python version: {sys.version.split()[0]}")
    return True


def check_mongodb():
    """Check if MongoDB is available"""
    try:
        result = subprocess.run(['mongod', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ MongoDB is installed")
            return True
    except FileNotFoundError:
        pass
    
    print("⚠ MongoDB not found in PATH")
    print("Please install MongoDB or use a cloud instance like MongoDB Atlas")
    return False


def install_dependencies():
    """Install Python dependencies"""
    if not os.path.exists('requirements.txt'):
        print("✗ requirements.txt not found")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )


def install_playwright():
    """Install Playwright browsers"""
    return run_command(
        f"{sys.executable} -m playwright install chromium",
        "Installing Playwright browsers"
    )


def create_env_file():
    """Create .env file from template"""
    if os.path.exists('.env'):
        print("✓ .env file already exists")
        return True
    
    if not os.path.exists('env.example'):
        print("✗ env.example not found")
        return False
    
    try:
        shutil.copy('env.example', '.env')
        print("✓ Created .env file from template")
        print("⚠ Please edit .env file with your configuration")
        return True
    except Exception as e:
        print(f"✗ Failed to create .env file: {e}")
        return False


def main():
    """Main setup function"""
    print("Python Scrapper Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check MongoDB
    check_mongodb()
    
    # Install dependencies
    if not install_dependencies():
        print("✗ Setup failed at dependency installation")
        sys.exit(1)
    
    # Install Playwright
    if not install_playwright():
        print("✗ Setup failed at Playwright installation")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("✗ Setup failed at .env file creation")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✓ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your configuration")
    print("2. Run 'python main.py --config-check' to verify setup")
    print("3. Start the URL manager: 'python main.py url-manager'")
    print("4. Test Twilio: 'python main.py test-twilio'")
    print("5. Run the scraper: 'python main.py scraper'")


if __name__ == '__main__':
    main()
