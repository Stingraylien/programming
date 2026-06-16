import ast

try:
    with open('api/main.py', 'r', encoding='utf-8') as f:
        code = f.read()
    ast.parse(code)
    print('✓ File is syntactically correct!')
except SyntaxError as e:
    print('✗ Syntax Error found:')
    print(f'  Line {e.lineno}: {e.msg}')
    print(f'  Text: {e.text}')
    if e.offset:
        print(f'  Offset: {" " * (e.offset - 1)}^')
except Exception as e:
    print(f'✗ Error: {str(e)}')
