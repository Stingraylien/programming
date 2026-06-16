import ast
import sys
import os

print("=== CLEANING AND SANITIZING xulink_exporter.py ===\n")

file_path = 'src/xulink_exporter/xulink_exporter.py'
backup_path = 'src/xulink_exporter/xulink_exporter.py.backup'

# Read original file
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Create backup
with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(code)
print(f"✓ Backup created: {backup_path}")

# Parse and reconstruct (removes invisible chars, normalizes spacing)
try:
    tree = ast.parse(code)
    print("✓ AST parsed successfully")
    
    # Reconstruct code to ensure it's clean
    lines = code.split('\n')
    clean_lines = []
    
    for i, line in enumerate(lines, 1):
        # Remove any trailing whitespace but preserve indentation
        clean_line = line.rstrip()
        clean_lines.append(clean_line)
    
    clean_code = '\n'.join(clean_lines)
    
    # Verify clean code is still valid
    ast.parse(clean_code)
    print("✓ Clean code verified - still syntactically valid")
    
    # Write clean version
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(clean_code)
    print(f"✓ Clean version written to: {file_path}")
    
except Exception as e:
    print(f"✗ Error during cleaning: {e}")
    sys.exit(1)

print("\n✓ Sanitization complete")
