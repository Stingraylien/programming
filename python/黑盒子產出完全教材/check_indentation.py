import re

with open('api/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Check try-except blocks from line 100-150
print("=== Try-Except Indentation Analysis (Lines 100-150) ===\n")
for i in range(99, min(150, len(lines))):
    line = lines[i]
    # Show lines with try, except, finally keywords
    if re.search(r'\b(try|except|finally|else)\b', line):
        indent = len(line) - len(line.lstrip())
        print(f"Line {i+1:3d} (indent={indent:2d}): {line.rstrip()}")

# Check for proper indentation consistency
print("\n=== Indentation Consistency Check ===")
try:
    with open('api/main.py', 'r', encoding='utf-8') as f:
        code = f.read()
    compile(code, 'api/main.py', 'exec')
    print("✓ All indentation is consistent and valid!")
except IndentationError as e:
    print(f"✗ Indentation Error at line {e.lineno}: {e.msg}")
