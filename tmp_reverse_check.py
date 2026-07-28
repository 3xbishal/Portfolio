import os
import django
from django.urls import reverse, get_resolver

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_project.settings')
django.setup()

for name in [
    'home', 'about', 'projects', 'project_detail', 'contact',
    'admin_panel:login', 'admin_panel:logout', 'admin_panel:dashboard',
    'admin_panel:skill_list', 'admin_panel:skill_add', 'admin_panel:skill_edit',
    'admin_panel:project_list', 'admin_panel:project_add', 'admin_panel:project_edit',
    'admin_panel:experience_list', 'admin_panel:experience_add', 'admin_panel:experience_edit',
    'admin_panel:education_list', 'admin_panel:testimonial_list', 'admin_panel:service_list',
    'admin_panel:contactmessage_list', 'admin_panel:contactmessage_detail', 'admin_panel:message_mark_read',
]:
    try:
        kwargs = {}
        if 'pk' in name or 'detail' in name or 'read' in name or 'unread' in name:
            kwargs = {'pk': 1}
        if name == 'project_detail':
            kwargs = {'slug': 'test'}
        print(name, reverse(name, kwargs=kwargs))
    except Exception as e:
        print('ERROR', name, type(e).__name__, e)

resolver = get_resolver(None)
print('has admin_panel:dashboard', 'admin_panel:dashboard' in resolver.reverse_dict)
print('has admin_panel:login', 'admin_panel:login' in resolver.reverse_dict)
print('namespace_dict keys', resolver.namespace_dict.keys())
admin_tuple = resolver.namespace_dict.get('admin_panel')
print('admin_panel tuple', admin_tuple)
print('admin_panel tuple type', type(admin_tuple))
print('admin_panel resolver repr', repr(admin_tuple))
