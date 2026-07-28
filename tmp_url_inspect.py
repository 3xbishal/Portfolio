import os
import django
from django.urls import get_resolver

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_project.settings')
django.setup()
resolver = get_resolver(None)
print('resolver type', type(resolver))
print('reverse_dict type', type(resolver.reverse_dict))
print('sample keys', list(resolver.reverse_dict.keys())[:100])
print('has admin_panel:dashboard', 'admin_panel:dashboard' in resolver.reverse_dict)
print('has admin_panel:login', 'admin_panel:login' in resolver.reverse_dict)
print('has home', 'home' in resolver.reverse_dict)
print('has contact', 'contact' in resolver.reverse_dict)
print('has projects', 'projects' in resolver.reverse_dict)
print('namespaces', resolver.namespace_dict.keys())
print('namespace admin_panel', resolver.namespace_dict.get('admin_panel'))
