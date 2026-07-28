import os
import django
from django.urls import get_resolver

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_project.settings')
django.setup()
resolver = get_resolver(None)
keys = list(resolver.reverse_dict.keys())
print('total', len(keys))
print('contains admin_panel', [k for k in keys if 'admin_panel' in repr(k)])
print('first 50 reprkeys:')
for i,k in enumerate(keys[:50]):
    print(i, repr(k))

# if string-based namespaced keys not found, print tuple keys
print('tuple keys containing admin_panel')
for k in keys:
    if isinstance(k, tuple) and 'admin_panel' in k:
        print(k)

# inspect reverse_dict structure if possible
if hasattr(resolver, 'reverse_dict'):
    print('reverse_dict size', len(resolver.reverse_dict))
else:
    print('no reverse_dict attr')
