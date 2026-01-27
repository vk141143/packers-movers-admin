#!/usr/bin/env python3
"""
Deployment verification script for crew_admin_backend
Run this on your deployment server to check if everything is configured correctly
"""

import sys
import os
from pathlib import Path

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("=" * 60)
    print("1. Checking .env file...")
    print("=" * 60)
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found in current directory")
        print(f"   Looking for: {env_file.absolute()}")
        return False
    
    print(f"✅ .env file found at: {env_file.absolute()}")
    
    # Check required variables
    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY",
        "SMTP_SERVER",
        "SMTP_PORT",
        "SMTP_USER",
        "SMTP_PASSWORD"
    ]
    
    with open(env_file) as f:
        content = f.read()
        missing = []
        for var in required_vars:
            if f"{var}=" not in content:
                missing.append(var)
        
        if missing:
            print(f"❌ Missing variables in .env: {', '.join(missing)}")
            return False
        else:
            print(f"✅ All required variables present in .env")
    
    return True

def check_database_connection():
    """Check if database connection works"""
    print("\n" + "=" * 60)
    print("2. Checking database connection...")
    print("=" * 60)
    
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            print("❌ DATABASE_URL not loaded from .env")
            return False
        
        print(f"✅ DATABASE_URL loaded: {DATABASE_URL[:50]}...")
        
        # Try to import and connect
        from app.database.db import engine
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Database connection successful")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def check_required_packages():
    """Check if all required packages are installed"""
    print("\n" + "=" * 60)
    print("3. Checking required packages...")
    print("=" * 60)
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "psycopg2",
        "python-dotenv",
        "pydantic",
        "python-jose",
        "passlib",
        "python-multipart"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"   Install with: pip install {' '.join(missing)}")
        return False
    
    return True

def check_app_structure():
    """Check if app structure is correct"""
    print("\n" + "=" * 60)
    print("4. Checking app structure...")
    print("=" * 60)
    
    required_dirs = [
        "app",
        "app/routers",
        "app/models",
        "app/schemas",
        "app/core",
        "app/database"
    ]
    
    required_files = [
        "main.py",
        "app/__init__.py",
        "app/database/db.py",
        "app/core/security.py"
    ]
    
    all_good = True
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ not found")
            all_good = False
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} not found")
            all_good = False
    
    return all_good

def check_main_app():
    """Check if main app can be imported"""
    print("\n" + "=" * 60)
    print("5. Checking main application...")
    print("=" * 60)
    
    try:
        from main import app
        print("✅ Main application imported successfully")
        print(f"✅ App title: {app.title}")
        return True
    except Exception as e:
        print(f"❌ Failed to import main app: {str(e)}")
        return False

def check_email_configuration():
    """Check if email/OTP is configured correctly"""
    print("\n" + "=" * 60)
    print("6. Checking email/OTP configuration...")
    print("=" * 60)
    
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = os.getenv("SMTP_PORT")
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        
        if not smtp_server:
            print("❌ SMTP_SERVER not configured")
            return False
        print(f"✅ SMTP_SERVER: {smtp_server}")
        
        if not smtp_port:
            print("❌ SMTP_PORT not configured")
            return False
        print(f"✅ SMTP_PORT: {smtp_port}")
        
        if not smtp_user:
            print("❌ SMTP_USER not configured")
            return False
        print(f"✅ SMTP_USER: {smtp_user}")
        
        if not smtp_password:
            print("❌ SMTP_PASSWORD not configured")
            return False
        print(f"✅ SMTP_PASSWORD: {'*' * len(smtp_password)}")
        
        # Test SMTP connection
        print("\nTesting SMTP connection...")
        import smtplib
        try:
            server = smtplib.SMTP(smtp_server, int(smtp_port), timeout=10)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.quit()
            print("✅ SMTP connection successful")
            return True
        except Exception as e:
            print(f"❌ SMTP connection failed: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking email configuration: {str(e)}")
        return False

def main():
    print("\n" + "=" * 60)
    print("CREW ADMIN BACKEND DEPLOYMENT VERIFICATION")
    print("=" * 60)
    print(f"Current directory: {Path.cwd()}")
    print(f"Python version: {sys.version}")
    print()
    
    checks = [
        ("Environment file", check_env_file),
        ("Required packages", check_required_packages),
        ("App structure", check_app_structure),
        ("Database connection", check_database_connection),
        ("Main application", check_main_app),
        ("Email/OTP configuration", check_email_configuration)
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ Error during {name} check: {str(e)}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Your deployment is ready.")
        print("\nTo start the server, run:")
        print("  uvicorn main:app --host 0.0.0.0 --port 8001")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
