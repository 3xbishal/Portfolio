"""
Read-only GitHub repo browser for the admin panel: lists the configured
token's repos (public + private), browses file trees, views file content,
shows commit history, and proxies zip downloads (see main/github_client.py).
"""
import os

from django.contrib import messages
from django.http import StreamingHttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from .admin_views import admin_login_required
from . import github_client as gh
from . import file_manager as fm


@admin_login_required
def github_repo_list(request):
    if not gh.is_configured():
        return render(request, 'admin_panel/github_repo_list.html', {'configured': False})

    page = int(request.GET.get('page') or 1)
    refresh = request.GET.get('refresh') == '1'
    try:
        data = gh.list_repos(page=page, refresh=refresh)
    except gh.GithubError as exc:
        messages.error(request, str(exc))
        data = {'repos': [], 'links': {}}

    return render(request, 'admin_panel/github_repo_list.html', {
        'configured': True,
        'repos': data['repos'],
        'has_next': 'next' in data['links'],
        'has_prev': 'prev' in data['links'],
        'page': page,
    })


@admin_login_required
def github_tree(request, owner, repo):
    if not gh.is_configured():
        return redirect('admin_panel:github_repo_list')

    path = request.GET.get('path', '').strip('/')
    ref = request.GET.get('ref') or None
    refresh = request.GET.get('refresh') == '1'

    try:
        branches = gh.list_branches(owner, repo)
    except gh.GithubError as exc:
        messages.error(request, str(exc))
        branches = []

    try:
        result = gh.get_contents(owner, repo, path, ref, refresh=refresh)
    except gh.GithubError as exc:
        messages.error(request, str(exc))
        return redirect('admin_panel:github_repo_list')

    if result['type'] == 'file':
        url = reverse('admin_panel:github_file', args=[owner, repo])
        qs = f'?path={path}' + (f'&ref={ref}' if ref else '')
        return redirect(url + qs)

    entries = sorted(result['entries'], key=lambda e: (e['type'] != 'dir', e['name'].lower()))
    breadcrumbs = []
    if path:
        parts = path.split('/')
        for i, part in enumerate(parts):
            breadcrumbs.append({'name': part, 'path': '/'.join(parts[:i + 1])})

    return render(request, 'admin_panel/github_tree.html', {
        'owner': owner, 'repo': repo, 'path': path, 'ref': ref,
        'entries': entries, 'breadcrumbs': breadcrumbs, 'branches': branches,
    })


@admin_login_required
def github_file(request, owner, repo):
    path = request.GET.get('path', '').strip('/')
    ref = request.GET.get('ref') or None

    try:
        result = gh.get_contents(owner, repo, path, ref)
    except gh.GithubError as exc:
        messages.error(request, str(exc))
        return redirect('admin_panel:github_repo_list')

    if result['type'] != 'file':
        messages.error(request, 'That path is a folder, not a file.')
        return redirect(f"{reverse('admin_panel:github_tree', args=[owner, repo])}?path={path}")

    meta = result['meta']
    size = meta.get('size', 0)
    ext = os.path.splitext(meta.get('name', ''))[1].lower()
    viewable = ext in fm.TEXT_EXTENSIONS and size <= fm.MAX_EDIT_SIZE

    content = None
    if viewable:
        try:
            content = gh.get_file_raw(owner, repo, path, ref).decode('utf-8', errors='replace')
        except gh.GithubError as exc:
            messages.error(request, str(exc))
            viewable = False

    return render(request, 'admin_panel/github_file.html', {
        'owner': owner, 'repo': repo, 'path': path, 'ref': ref,
        'meta': meta, 'viewable': viewable, 'content': content,
        'parent_path': '/'.join(path.split('/')[:-1]),
    })


@admin_login_required
def github_commits(request, owner, repo):
    ref = request.GET.get('ref') or None
    page = int(request.GET.get('page') or 1)
    try:
        data = gh.list_commits(owner, repo, ref=ref, page=page)
    except gh.GithubError as exc:
        messages.error(request, str(exc))
        data = {'commits': [], 'links': {}}

    return render(request, 'admin_panel/github_commits.html', {
        'owner': owner, 'repo': repo, 'ref': ref,
        'commits': data['commits'],
        'has_next': 'next' in data['links'],
        'has_prev': 'prev' in data['links'],
        'page': page,
    })


@admin_login_required
def github_download(request, owner, repo):
    ref = request.GET.get('ref') or 'HEAD'
    try:
        response = gh.stream_zip(owner, repo, ref)
    except gh.GithubError as exc:
        messages.error(request, str(exc))
        return redirect(reverse('admin_panel:github_tree', args=[owner, repo]))

    streaming = StreamingHttpResponse(
        response.iter_content(chunk_size=8192),
        content_type='application/zip',
    )
    filename = f'{repo}-{ref}.zip'.replace('/', '-')
    streaming['Content-Disposition'] = f'attachment; filename="{filename}"'
    return streaming
