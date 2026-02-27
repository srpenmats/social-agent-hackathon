#!/usr/bin/env python3
"""Fix all backend. imports to relative imports."""

import os
import re
from pathlib import Path

backend_dir = Path(__file__).parent / "backend"

def fix_imports_in_file(filepath):
    """Replace 'from backend.' with relative import in a Python file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Replace "from backend." with "from "
    content = re.sub(r'from backend\.', 'from ', content)
    
    # Replace "import backend." with "import " (less common)
    content = re.sub(r'import backend\.', 'import ', content)
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

# Find all Python files
python_files = list(backend_dir.rglob("*.py"))

print(f"🔍 Found {len(python_files)} Python files in backend/")
print("🔧 Fixing imports...\n")

fixed_count = 0
for filepath in python_files:
    if fix_imports_in_file(filepath):
        rel_path = filepath.relative_to(Path.cwd())
        print(f"✅ Fixed: {rel_path}")
        fixed_count += 1

print(f"\n{'='*60}")
print(f"✅ Fixed {fixed_count} files!")
print(f"{'='*60}")
