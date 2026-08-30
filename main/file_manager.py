"""
Sandboxed filesystem operations backing the admin File Manager.

Pure pathlib/shutil logic with no Django view/request dependencies (only
`django.conf.settings` for root paths and the upload size limit), so the
path-safety rules here -- the File Manager's core security boundary -- can
be unit-tested in isolation. Views translate FileManagerError into HTTP
responses / messages, never a raw traceback.
"""
import os
import shutil
import zipfile
import io
from datetime import datetime
from pathlib import Path, PurePosixPath

from django.conf import settings

# The only directory the File Manager may ever touch: a dedicated storage
# folder deliberately kept OUTSIDE the Django project directory (a sibling
# folder, same pattern as MEDIA_ROOT) -- browsing/uploading here can never
# reach the app's own source code, settings, or database file, because
# they simply aren't inside this tree at all.
ROOTS = {
    'storage': Path(settings.FILE_MANAGER_STORAGE_ROOT),
}

ROOT_LABELS = {
    'storage': 'Files',
}

# Path segments blocked everywhere, checked case-insensitively -- generic
# hygiene for a general-purpose storage folder (hide generated/junk dirs
# someone might copy in). Anything starting with '.' is blocked
# categorically regardless of this set (see _is_blocked_segment).
BLOCKED_SEGMENTS = {
    '__pycache__', 'node_modules',
}

TEXT_EXTENSIONS = {
    '.txt', '.md', '.py', '.html', '.htm', '.css', '.js', '.json',
    '.xml', '.yml', '.yaml', '.csv', '.ini', '.cfg',
}
MAX_EDIT_SIZE = 512 * 1024  # 512 KB


class FileManagerError(Exception):
    """Raised for any invalid, unsafe or forbidden file manager operation."""


def max_upload_size():
    return getattr(settings, 'FILE_MANAGER_MAX_UPLOAD_SIZE', 50 * 1024 * 1024)


def _is_blocked_segment(segment):
    return segment.startswith('.') or segment.lower() in BLOCKED_SEGMENTS


def parent_rel(rel_path):
    """Posix-style parent of a '/'-separated relative path ('' at the root)."""
    parent = str(PurePosixPath(rel_path or '').parent)
    return '' if parent in ('.', '/') else parent


def join_rel(rel_path, name):
    return f'{rel_path}/{name}' if rel_path else name


def sanitize_name(name):
    """Reduce a user-supplied name to a single safe path segment."""
    name = (name or '').strip().replace('\\', '/')
    name = os.path.basename(name)
    if not name or name in ('.', '..') or '\x00' in name:
        raise FileManagerError('Invalid name.')
    return name


def resolve_safe(root_key, rel_path):
    """
    Resolve `rel_path` (a '/'-separated string, possibly empty) against the
    named root and guarantee the result stays inside that root, never
    crosses a blocked segment, and never passes through a symlink.

    Applied identically to read targets (list/download/delete/copy-from)
    AND write destinations (rename target, mkdir name, upload filename,
    paste target) -- a destination must be exactly as safe as a source, or
    an admin could rename/create a path into existence that becomes a
    permanently hidden orphan (e.g. renaming a folder to '.git').
    """
    if root_key not in ROOTS:
        raise FileManagerError(f'Unknown root "{root_key}".')
    root = ROOTS[root_key].resolve()

    rel_path = (rel_path or '').strip()

    # Reject backslashes and absolute paths *before* they ever reach
    # Path(), rather than relying only on the downstream containment check.
    # pathlib treats '\' as a separator on Windows (dev) but as a literal
    # character on Linux (production) -- the same traversal string would
    # otherwise be blocked on one platform and not the other. Likewise,
    # `root / rel_path` silently discards `root` if rel_path is absolute,
    # so absolute paths / drive letters / UNC paths must be caught here.
    if rel_path:
        if '\\' in rel_path:
            raise FileManagerError('Invalid path.')
        if PurePosixPath(rel_path).is_absolute():
            raise FileManagerError('Invalid path.')
        if Path(rel_path).drive:
            raise FileManagerError('Invalid path.')

    candidate = (root / rel_path) if rel_path else root
    try:
        resolved = candidate.resolve()
    except OSError as exc:
        raise FileManagerError('Invalid path.') from exc

    try:
        relative = resolved.relative_to(root)
    except ValueError:
        # Not is_relative_to() -- that requires Python 3.9+ and this
        # project's deployment target documents Python 3.8+.
        raise FileManagerError('Path escapes the allowed directory.')

    # Validate every segment from the root down to the target, and refuse
    # to operate through any symlink encountered along the way (shutil
    # operations elsewhere would otherwise dereference it and pull content
    # in from outside the sandbox).
    walked = root
    for segment in relative.parts:
        if _is_blocked_segment(segment):
            raise FileManagerError('Access to this path is not allowed.')
        walked = walked / segment
        if walked.is_symlink():
            raise FileManagerError('Symlinks are not supported by the file manager.')

    return resolved


def list_dir(root_key, rel_path=''):
    """Return a list of entry dicts for a directory, or [] if it doesn't exist yet."""
    target = resolve_safe(root_key, rel_path)
    if not target.exists():
        return []
    if not target.is_dir():
        raise FileManagerError('Not a directory.')

    try:
        children = sorted(
            target.iterdir(),
            key=lambda p: (not p.is_dir(), p.name.lower()),
        )
    except OSError as exc:
        raise FileManagerError(f'Could not list folder: {exc}') from exc

    entries = []
    for child in children:
        if _is_blocked_segment(child.name) or child.is_symlink():
            continue
        try:
            stat = child.stat()
        except OSError:
            continue
        is_dir = child.is_dir()
        size = None if is_dir else stat.st_size
        entries.append({
            'name': child.name,
            'is_dir': is_dir,
            'size': size,
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'rel_path': join_rel(rel_path, child.name),
            'editable': (
                not is_dir
                and child.suffix.lower() in TEXT_EXTENSIONS
                and size is not None and size <= MAX_EDIT_SIZE
            ),
        })
    return entries


def make_dir(root_key, rel_path, name):
    name = sanitize_name(name)
    dest = resolve_safe(root_key, join_rel(rel_path, name))
    if dest.exists():
        raise FileManagerError(f'"{name}" already exists.')
    try:
        dest.mkdir(parents=True, exist_ok=False)
    except OSError as exc:
        raise FileManagerError(f'Could not create folder: {exc}') from exc
    return dest


def rename_path(root_key, rel_path, new_name):
    new_name = sanitize_name(new_name)
    source = resolve_safe(root_key, rel_path)
    root = ROOTS[root_key].resolve()
    if source == root:
        raise FileManagerError('Cannot rename a root folder.')
    if not source.exists():
        raise FileManagerError('Item not found.')

    dest = resolve_safe(root_key, join_rel(parent_rel(rel_path), new_name))
    if dest == source:
        return source
    if dest.exists():
        raise FileManagerError(f'"{new_name}" already exists.')
    try:
        source.rename(dest)
    except OSError as exc:
        raise FileManagerError(f'Could not rename: {exc}') from exc
    return dest


def delete_path(root_key, rel_path):
    target = resolve_safe(root_key, rel_path)
    root = ROOTS[root_key].resolve()
    if target == root:
        raise FileManagerError('Cannot delete a root folder.')
    if not target.exists():
        raise FileManagerError('Item not found.')
    try:
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        else:
            target.unlink()
    except OSError as exc:
        raise FileManagerError(f'Could not delete "{target.name}": {exc}') from exc


def unique_name_in(dest_dir, desired_name):
    """Return `desired_name`, or a ' (1)', ' (2)', ... variant if it collides."""
    if not (dest_dir / desired_name).exists():
        return desired_name
    stem, suffix = os.path.splitext(desired_name)
    i = 1
    while True:
        candidate = f'{stem} ({i}){suffix}'
        if not (dest_dir / candidate).exists():
            return candidate
        i += 1


def copy_into(src_root, src_rel, dest_root, dest_rel_dir):
    source = resolve_safe(src_root, src_rel)
    if not source.exists():
        raise FileManagerError('Source no longer exists.')
    if source.is_symlink():
        raise FileManagerError('Symlinks are not supported.')

    dest_dir = resolve_safe(dest_root, dest_rel_dir)
    if not dest_dir.is_dir():
        raise FileManagerError('Destination is not a folder.')

    name = unique_name_in(dest_dir, source.name)
    dest = resolve_safe(dest_root, join_rel(dest_rel_dir, name))
    try:
        if source.is_dir():
            shutil.copytree(source, dest, symlinks=False, ignore_dangling_symlinks=True)
        else:
            shutil.copy2(source, dest)
    except (OSError, shutil.Error) as exc:
        raise FileManagerError(f'Could not copy "{source.name}": {exc}') from exc
    return dest


def move_into(src_root, src_rel, dest_root, dest_rel_dir):
    source = resolve_safe(src_root, src_rel)
    if not source.exists():
        raise FileManagerError('Source no longer exists.')
    if source.is_symlink():
        raise FileManagerError('Symlinks are not supported.')

    src_root_path = ROOTS[src_root].resolve()
    if source == src_root_path:
        raise FileManagerError('Cannot move a root folder.')

    dest_dir = resolve_safe(dest_root, dest_rel_dir)
    if not dest_dir.is_dir():
        raise FileManagerError('Destination is not a folder.')
    if dest_dir == source or str(dest_dir).startswith(str(source) + os.sep):
        raise FileManagerError('Cannot move a folder into itself.')

    name = unique_name_in(dest_dir, source.name)
    dest = resolve_safe(dest_root, join_rel(dest_rel_dir, name))
    try:
        shutil.move(str(source), str(dest))
    except (OSError, shutil.Error) as exc:
        raise FileManagerError(f'Could not move "{source.name}": {exc}') from exc
    return dest


def save_upload(root_key, rel_path, uploaded_file):
    dest_dir = resolve_safe(root_key, rel_path)
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise FileManagerError(f'Could not prepare destination folder: {exc}') from exc
    if not dest_dir.is_dir():
        raise FileManagerError('Destination is not a folder.')

    if uploaded_file.size > max_upload_size():
        raise FileManagerError(
            f'"{uploaded_file.name}" is too large '
            f'(max {max_upload_size() // (1024 * 1024)} MB).'
        )

    name = unique_name_in(dest_dir, sanitize_name(uploaded_file.name))
    dest = resolve_safe(root_key, join_rel(rel_path, name))
    try:
        with open(dest, 'wb') as fh:
            for chunk in uploaded_file.chunks():
                fh.write(chunk)
    except OSError as exc:
        raise FileManagerError(f'Could not save "{uploaded_file.name}": {exc}') from exc
    return dest


def read_text(root_key, rel_path):
    target = resolve_safe(root_key, rel_path)
    if not target.is_file():
        raise FileManagerError('Not a file.')
    if target.suffix.lower() not in TEXT_EXTENSIONS:
        raise FileManagerError('This file type cannot be edited here.')
    if target.stat().st_size > MAX_EDIT_SIZE:
        raise FileManagerError('File is too large to edit here.')
    try:
        return target.read_text(encoding='utf-8', errors='replace')
    except OSError as exc:
        raise FileManagerError(f'Could not read file: {exc}') from exc


def write_text(root_key, rel_path, content):
    target = resolve_safe(root_key, rel_path)
    if not target.is_file():
        raise FileManagerError('Not a file.')
    if target.suffix.lower() not in TEXT_EXTENSIONS:
        raise FileManagerError('This file type cannot be edited here.')
    try:
        target.write_text(content, encoding='utf-8')
    except OSError as exc:
        raise FileManagerError(f'Could not save file: {exc}') from exc


def build_zip(items):
    """items: iterable of (root_key, rel_path) tuples. Returns a seek(0)'d BytesIO."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root_key, rel_path in items:
            try:
                target = resolve_safe(root_key, rel_path)
            except FileManagerError:
                continue
            if not target.exists() or target.is_symlink():
                continue
            if target.is_file():
                zf.write(target, arcname=target.name)
                continue
            base_len = len(str(target))
            for dirpath, dirnames, filenames in os.walk(target, followlinks=False):
                dirnames[:] = [d for d in dirnames if not _is_blocked_segment(d)]
                for fn in filenames:
                    if _is_blocked_segment(fn):
                        continue
                    full = Path(dirpath) / fn
                    if full.is_symlink():
                        continue
                    arcname = (target.name + str(full)[base_len:]).replace(os.sep, '/')
                    zf.write(full, arcname=arcname)
    buffer.seek(0)
    return buffer
