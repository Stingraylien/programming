import ast
import sys
import os

print("=== COMPREHENSIVE SYNTAX VERIFICATION FOR xulink_exporter.py ===\n")

file_path = 'src/xulink_exporter/xulink_exporter.py'

# Step 1: Check if file exists
if not os.path.exists(file_path):
    print(f"✗ [FAIL] File not found: {file_path}")
    sys.exit(1)
print(f"✓ [PASS] File found: {file_path}")

# Step 2: Read file with encoding detection
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    print("✓ [PASS] File read successfully with UTF-8 encoding")
except UnicodeDecodeError as e:
    print(f"✗ [FAIL] Unicode decode error at position {e.start}: {e.reason}")
    sys.exit(1)

# Step 3: AST Parse Check
try:
    ast.parse(code)
    print("✓ [PASS] AST parsing successful - no syntax errors")
except SyntaxError as e:
    print(f"✗ [FAIL] Syntax Error: Line {e.lineno}: {e.msg}")
    lines = code.split('\n')
    if e.lineno and e.lineno <= len(lines):
        print(f"   Problem line: {lines[e.lineno-1]}")
    sys.exit(1)

# Step 4: Compile Check
try:
    compile(code, file_path, 'exec')
    print("✓ [PASS] Compilation successful - no indentation errors")
except Exception as e:
    print(f"✗ [FAIL] Compilation error: {type(e).__name__}: {e}")
    sys.exit(1)

# Step 5: Basic integrity checks
lines = code.split('\n')
print(f"✓ [INFO] Total lines: {len(lines)}")
print(f"✓ [INFO] File size: {len(code)} bytes")

# Check for common issues
if code.count('def ') < 1:
    print("⚠ [WARNING] No function definitions found")
if code.count('class ') < 1:
    print("⚠ [WARNING] No class definitions found")

print("\n=== RESULT ===")
print("✓ File 'src/xulink_exporter/xulink_exporter.py' is SYNTACTICALLY CORRECT")
print("✓ No encoding errors detected")
print("✓ File is ready for execution")
