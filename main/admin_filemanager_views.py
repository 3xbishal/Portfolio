"""
Views for the admin File Manager: sandboxed browsing, upload, download,
copy/cut/paste, rename, delete and lightweight text editing within a
dedicated storage root kept entirely outside the Django project directory
(see main/file_manager.py for the sandboxing rules). All state-changing
actions are classic multipart POST + redirect, matching the rest of the
admin panel -- no AJAX/JSON API.
"""
from urllib.parse import urlencode

from django.contrib import messages
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .admin_views import admin_login_required
from . import file_manager as fm


def _fm_url(root, path=''):
    params = {'root': root}
    if path:
        params['path'] = path
    return f"{reverse('admin_panel:fm_list')}?{urlencode(params)}"


def _get_root_path(request):
    root = request.GET.get('root') or request.POST.get('root') or 'storage'
    path = (request.GET.get('path') or request.POST.get('path') or '').strip('/')
    if root not in fm.ROOTS:
        root, path = 'storage', ''
    return root, path


def _selected_items(request):
    items = request.POST.getlist('selected')
    if not items and request.POST.get('item'):
        items = [request.POST['item']]
    return items


@admin_login_required
def file_manager(request):
    root, path = _get_root_path(request)
    try:
        entries = fm.list_dir(root, path)
    except fm.FileManagerError as exc:
        messages.error(request, str(exc))
        entries, path = [], ''

    breadcrumbs = []
    if path:
        parts = path.split('/')
        for i, part in enumerate(parts):
            breadcrumbs.append({'name': part, 'path': '/'.join(parts[:i + 1])})

    context = {
        'root': root,
        'path': path,
        'entries': entries,
        'breadcrumbs': breadcrumbs,
        'roots': fm.ROOT_LABELS,
        'clipboard': request.session.get('fm_clipboard'),
        'max_upload_mb': fm.max_upload_size() // (1024 * 1024),
    }
    return render(request, 'admin_panel/filemanager_list.html', context)


@admin_login_required
def file_upload(request):
    if request.method != 'POST':
        return redirect('admin_panel:fm_list')
    root, path = _get_root_path(request)
    uploaded_files = request.FILES.getlist('files')
    if not uploaded_files:
        messages.error(request, 'No files selected.')
        return redirect(_fm_url(root, path))

    saved, errors = 0, []
    for f in uploaded_files:
        try:
            fm.save_upload(root, path, f)
            saved += 1
        except fm.FileManagerError as exc:
            errors.append(str(exc))

    if saved:
        messages.success(request, f'Uploaded {saved} file(s).')
    for err in errors:
        messages.error(request, err)
    return redirect(_fm_url(root, path))


@admin_login_required
def file_mkdir(request):
    if request.method != 'POST':
        return redirect('admin_panel:fm_list')
    root, path = _get_root_path(request)
    name = request.POST.get('name', '')
    try:
        fm.make_dir(root, path, name)
        messages.success(request, f'Folder "{name}" created.')
    except fm.FileManagerError as exc:
        messages.error(request, str(exc))
    return redirect(_fm_url(root, path))


@admin_login_required
def file_rename(request):
    if request.method != 'POST':
        return redirect('admin_panel:fm_list')
    root, path = _get_root_path(request)
    item = request.POST.get('item', '')
    new_name = request.POST.get('name', '')
    try:
        fm.rename_path(root, item, new_name)
        messages.success(request, 'Renamed successfully.')
    except fm.FileManagerError as exc:
        messages.error(request, str(exc))
    return redirect(_fm_url(root, path))


@admin_login_required
def file_delete(request):
    if request.method != 'POST':
        return redirect('admin_panel:fm_list')
    root, path = _get_root_path(request)
    items = _selected_items(request)
    if not items:
        messages.error(request, 'Nothing selected.')
        return redirect(_fm_url(root, path))

    deleted, errors = 0, []
    for item in items:
        try:
            fm.delete_path(root, item)
            deleted += 1
        except fm.FileManagerError as exc:
            errors.append(str(exc))

    if deleted:
        messages.success(request, f'Deleted {deleted} item(s).')
    for err in errors:
        messages.error(request, err)
    return redirect(_fm_url(root, path))


@admin_login_required
def file_clipboard(request):
    if request.method != 'POST':
        return redirect('admin_panel:fm_list')
    root, path = _get_root_path(request)
    action = request.POST.get('action')
    items = _selected_items(request)

    if action not in ('copy', 'cut') or not items:
        messages.error(request, 'Nothing selected.')
        return redirect(_fm_url(root, path))

    request.session['fm_clipboard'] = {'mode': action, 'root': root, 'items': items}
    request.session.modified = True
    verb = 'copy' if action == 'copy' else 'cut'
    messages.success(request, f'{len(items)} item(s) marked for {verb}. Browse to a folder and click Paste.')
    return redirect(_fm_url(root, path))


@admin_login_required
def file_paste(request):
    if request.method != 'POST':
        return redirect('admin_panel:fm_list')
    root, path = _get_root_path(request)
    clipboard = request.session.get('fm_clipboard')
    if not clipboard:
        messages.error(request, 'Clipboard is empty.')
        return redirect(_fm_url(root, path))

    src_root = clipboard.get('root')
    mode = clipboard.get('mode')
    items = clipboard.get('items', [])
    if src_root not in fm.ROOTS or mode not in ('copy', 'cut'):
        request.session.pop('fm_clipboard', None)
        messages.error(request, 'Clipboard was invalid and has been cleared.')
        return redirect(_fm_url(root, path))

    done, errors = 0, []
    for item in items:
        try:
            if mode == 'copy':
                fm.copy_into(src_root, item, root, path)
            else:
                fm.move_into(src_root, item, root, path)
            done += 1
        except fm.FileManagerError as exc:
            errors.append(str(exc))

    if done:
        messages.success(request, f'Pasted {done} item(s).')
    for err in errors:
        messages.error(request, err)
    if mode == 'cut':
        request.session.pop('fm_clipboard', None)
    return redirect(_fm_url(root, path))


@admin_login_required
def file_download(request):
    root = request.GET.get('root', 'storage')
    path = request.GET.get('path', '')
    try:
        target = fm.resolve_safe(root, path)
    except fm.FileManagerError:
        raise Http404('File not found.')
    if not target.is_file():
        raise Http404('File not found.')
    return FileResponse(open(target, 'rb'), as_attachment=True, filename=target.name)


@admin_login_required
def file_download_zip(request):
    root, path = _get_root_path(request)
    items = request.POST.getlist('selected') if request.method == 'POST' else request.GET.getlist('selected')
    if not items:
        messages.error(request, 'Nothing selected.')
        return redirect(_fm_url(root, path))

    buffer = fm.build_zip([(root, item) for item in items])
    response = HttpResponse(buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="files.zip"'
    return response


@admin_login_required
def file_edit(request):
    root, path = _get_root_path(request)
    if request.method == 'POST':
        content = request.POST.get('content', '')
        try:
            fm.write_text(root, path, content)
            messages.success(request, 'File saved.')
            return redirect(_fm_url(root, fm.parent_rel(path)))
        except fm.FileManagerError as exc:
            messages.error(request, str(exc))
            return render(request, 'admin_panel/filemanager_edit.html', {
                'root': root, 'path': path, 'content': content,
                'parent_path': fm.parent_rel(path),
                'is_python': path.lower().endswith('.py'),
            })

    try:
        content = fm.read_text(root, path)
    except fm.FileManagerError as exc:
        messages.error(request, str(exc))
        return redirect(_fm_url(root, fm.parent_rel(path)))

    return render(request, 'admin_panel/filemanager_edit.html', {
        'root': root, 'path': path, 'content': content,
        'parent_path': fm.parent_rel(path),
        'is_python': path.lower().endswith('.py'),
    })
