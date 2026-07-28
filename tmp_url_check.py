import os
import re
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_project.settings')
import django
django.setup()
from django.urls import get_resolver

root = Path('templates')
urls = set()
for p in root.rglob('*.html'):
    text = p.read_text(encoding='utf-8')
    for m in re.finditer(r"\{\%\s*url\s+['\"]([^'\"]+)['\"]", text):
        urls.add(m.group(1))

resolver = get_resolver(None)
missing = sorted(n for n in urls if n not in resolver.reverse_dict)
print('USED URL NAMES:', len(urls))
for name in sorted(urls):
    print(name)
print('---')
print('MISSING:', len(missing))
for name in missing:
    print(name)
