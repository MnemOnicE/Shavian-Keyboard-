with open('tests/test_frontend.py', 'r') as f:
    content = f.read()

content = content.replace('from src.backend.main import app', 'from backend.main import app')

with open('tests/test_frontend.py', 'w') as f:
    f.write(content)
