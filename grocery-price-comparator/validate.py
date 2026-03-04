#!/usr/bin/env python3
"""
Quick validation script to check if all project files are in place
and can be imported/loaded correctly.
"""

import os
import sys
import json
from pathlib import Path

def check_files():
    """Check if all required files exist"""
    print("\n📂 CHECKING PROJECT FILES...")
    print("=" * 60)
    
    required_files = {
        # Backend
        'backend/main.py': 'FastAPI app',
        'backend/data_loader.py': 'CSV manager',
        'backend/utils/helpers.py': 'Utility functions',
        'backend/routes/products.py': 'Products router',
        'backend/routes/stores.py': 'Stores router',
        'backend/routes/budget.py': 'Budget router',
        'backend/routes/ratings.py': 'Ratings router',
        
        # Frontend
        'frontend/index.html': 'Main HTML',
        'frontend/css/style.css': 'Stylesheet',
        'frontend/js/app.js': 'Global JS',
        'frontend/js/search.js': 'Search logic',
        'frontend/js/budget.js': 'Budget logic',
        'frontend/js/map.js': 'Maps logic',
        'frontend/js/ratings.js': 'Ratings logic',
        
        # Data
        'data/stores.csv': 'Stores data',
        'data/products.csv': 'Products data',
        'data/categories.csv': 'Categories data',
        'data/product_prices.csv': 'Prices data',
        'data/price_history.csv': 'Price history',
        'data/store_ratings.csv': 'Ratings data',
        'data/budget_sessions.csv': 'Budget sessions',
        'data/budget_items.csv': 'Budget items',
        
        # Config
        'requirements.txt': 'Dependencies',
        'Dockerfile': 'Docker config',
        '.env': 'Environment vars',
        'README.md': 'Documentation',
    }
    
    missing = []
    found = []
    
    for filepath, description in required_files.items():
        path = Path(filepath)
        if path.exists():
            size = path.stat().st_size
            found.append((filepath, size, description))
            print(f"  ✅ {filepath:40} ({size:,} bytes) - {description}")
        else:
            missing.append((filepath, description))
            print(f"  ❌ {filepath:40} MISSING - {description}")
    
    print("=" * 60)
    print(f"✅ Found: {len(found)}/{len(required_files)} files")
    
    if missing:
        print(f"❌ Missing: {len(missing)} files")
        return False
    
    return True


def check_imports():
    """Check if Python modules can be imported"""
    print("\n🔧 CHECKING PYTHON IMPORTS...")
    print("=" * 60)
    
    # Add project to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    modules = [
        'fastapi',
        'uvicorn',
        'pandas',
        'pydantic',
    ]
    
    missing_deps = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module:20} OK")
        except ImportError:
            missing_deps.append(module)
            print(f"  ❌ {module:20} MISSING - Run: pip install -r requirements.txt")
    
    print("=" * 60)
    
    if missing_deps:
        print(f"❌ Missing {len(missing_deps)} Python packages")
        return False
    
    print("✅ All Python dependencies available")
    return True


def check_csv_files():
    """Validate CSV structure"""
    print("\n📊 CHECKING CSV DATA FILES...")
    print("=" * 60)
    
    try:
        import pandas as pd
        
        csv_files = {
            'data/stores.csv': ['store_id', 'store_name'],
            'data/products.csv': ['product_id', 'product_name'],
            'data/categories.csv': ['category_id', 'category_name'],
            'data/product_prices.csv': ['price_id', 'product_id', 'store_id', 'price'],
            'data/price_history.csv': ['history_id', 'product_id', 'store_id', 'price'],
            'data/store_ratings.csv': ['rating_id', 'store_id', 'rating'],
            'data/budget_sessions.csv': ['session_id'],
            'data/budget_items.csv': ['item_id'],
        }
        
        all_valid = True
        
        for filepath, required_cols in csv_files.items():
            if not Path(filepath).exists():
                print(f"  ⚠️  {filepath:35} NOT FOUND (will be created)")
                continue
            
            try:
                df = pd.read_csv(filepath)
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if missing_cols:
                    print(f"  ❌ {filepath:35} Missing columns: {missing_cols}")
                    all_valid = False
                else:
                    print(f"  ✅ {filepath:35} ({len(df):,} rows)")
            except Exception as e:
                print(f"  ❌ {filepath:35} ERROR: {str(e)}")
                all_valid = False
        
        print("=" * 60)
        return all_valid
        
    except ImportError:
        print("  ⚠️  Pandas not installed - skipping CSV validation")
        return True


def main():
    """Run all checks"""
    print("\n" + "🛒 GROCERY PRICE COMPARATOR - PROJECT VALIDATION".center(60))
    
    checks = [
        ("Project Files", check_files),
        ("Python Imports", check_imports),
        ("CSV Data Files", check_csv_files),
    ]
    
    results = {}
    for name, check_func in checks:
        results[name] = check_func()
    
    print("\n" + "=" * 60)
    print("📋 VALIDATION SUMMARY")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {name:30} {status}")
    
    all_passed = all(results.values())
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 PROJECT VALIDATION SUCCESSFUL!")
        print("\n🚀 Ready to start the application:")
        print("   Terminal 1: uvicorn backend.main:app --reload --port 8000")
        print("   Terminal 2: cd frontend && python -m http.server 8001")
        return 0
    else:
        print("\n❌ VALIDATION FAILED - Some checks did not pass")
        print("   Please review the errors above and fix them")
        return 1


if __name__ == '__main__':
    sys.exit(main())
