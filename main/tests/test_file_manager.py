"""
Unit tests for main/file_manager.py -- the sandboxing core of the admin
File Manager and the feature's actual security boundary. These monkeypatch
fm.ROOTS to a throwaway temp directory so they never touch the real
project/media/static roots, and need no database (SimpleTestCase).
"""
import sys
import tempfile
import unittest
from pathlib import Path

from django.test import SimpleTestCase

from main import file_manager as fm


class FileManagerSafetyTests(SimpleTestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / 'sandbox'
        self.root.mkdir()
        self._orig_roots = fm.ROOTS
        fm.ROOTS = {'test': self.root}
        self.addCleanup(self._restore_roots)

    def _restore_roots(self):
        fm.ROOTS = self._orig_roots

    # -- resolve_safe: traversal / injection matrix --------------------

    def test_unknown_root_rejected(self):
        with self.assertRaises(fm.FileManagerError):
            fm.resolve_safe('nope', '')

    def test_parent_traversal_rejected(self):
        for bad in ('../secret', '..', 'a/../../secret', '../../etc/passwd'):
            with self.subTest(bad=bad):
                with self.assertRaises(fm.FileManagerError):
                    fm.resolve_safe('test', bad)

    def test_absolute_paths_rejected(self):
        for bad in ('/etc/passwd', '/', 'C:/Windows', '//server/share'):
            with self.subTest(bad=bad):
                with self.assertRaises(fm.FileManagerError):
                    fm.resolve_safe('test', bad)

    def test_backslash_rejected(self):
        for bad in ('..\\..\\secret', 'sub\\..\\..\\secret', 'a\\b'):
            with self.subTest(bad=bad):
                with self.assertRaises(fm.FileManagerError):
                    fm.resolve_safe('test', bad)

    def test_blocked_segments_rejected_at_any_depth(self):
        for bad in (
            '.env', '.git/config', 'sub/.git/config', '__pycache__/x.pyc',
            'venv/bin/python', 'db.sqlite3', 'a/b/.hidden',
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(fm.FileManagerError):
                    fm.resolve_safe('test', bad)

    def test_valid_nested_path_allowed(self):
        (self.root / 'a' / 'b').mkdir(parents=True)
        resolved = fm.resolve_safe('test', 'a/b')
        self.assertEqual(resolved, (self.root / 'a' / 'b').resolve())

    # -- destination-side enforcement (not just reads) ------------------

    def test_mkdir_rejects_blocked_destination_name(self):
        with self.assertRaises(fm.FileManagerError):
            fm.make_dir('test', '', '.git')
        with self.assertRaises(fm.FileManagerError):
            fm.make_dir('test', '', '__pycache__')

    def test_rename_rejects_blocked_destination_name(self):
        target = self.root / 'notes.txt'
        target.write_text('hi')
        with self.assertRaises(fm.FileManagerError):
            fm.rename_path('test', 'notes.txt', '.env')

    def test_rename_cannot_target_root(self):
        with self.assertRaises(fm.FileManagerError):
            fm.rename_path('test', '', 'whatever')

    def test_cannot_delete_root(self):
        with self.assertRaises(fm.FileManagerError):
            fm.delete_path('test', '')

    # -- collisions, copy/move, delete ----------------------------------

    def test_unique_name_in_avoids_collision(self):
        (self.root / 'a.txt').write_text('x')
        name = fm.unique_name_in(self.root, 'a.txt')
        self.assertEqual(name, 'a (1).txt')
        (self.root / 'a (1).txt').write_text('y')
        self.assertEqual(fm.unique_name_in(self.root, 'a.txt'), 'a (2).txt')

    def test_copy_and_move(self):
        (self.root / 'src').mkdir()
        (self.root / 'dst').mkdir()
        f = self.root / 'src' / 'hello.txt'
        f.write_text('hello')

        fm.copy_into('test', 'src/hello.txt', 'test', 'dst')
        self.assertTrue((self.root / 'dst' / 'hello.txt').exists())
        self.assertTrue(f.exists())  # original untouched by copy

        fm.move_into('test', 'src/hello.txt', 'test', 'dst')
        self.assertFalse(f.exists())
        # moved with a unique name since 'hello.txt' already exists in dst
        self.assertTrue((self.root / 'dst' / 'hello (1).txt').exists())

    def test_cannot_move_folder_into_itself(self):
        (self.root / 'a' / 'b').mkdir(parents=True)
        with self.assertRaises(fm.FileManagerError):
            fm.move_into('test', 'a', 'test', 'a/b')

    def test_delete_file_and_dir(self):
        f = self.root / 'gone.txt'
        f.write_text('x')
        fm.delete_path('test', 'gone.txt')
        self.assertFalse(f.exists())

        d = self.root / 'gonedir'
        (d / 'sub').mkdir(parents=True)
        fm.delete_path('test', 'gonedir')
        self.assertFalse(d.exists())

    # -- missing root handling -------------------------------------------

    def test_missing_root_lists_empty(self):
        fm.ROOTS = {'test': Path(self._tmp.name) / 'does-not-exist-yet'}
        self.assertEqual(fm.list_dir('test', ''), [])

    def test_mkdir_creates_missing_root_on_demand(self):
        missing = Path(self._tmp.name) / 'not-created-yet'
        fm.ROOTS = {'test': missing}
        fm.make_dir('test', '', 'first')
        self.assertTrue((missing / 'first').is_dir())

    # -- text edit allowlist / size cap -----------------------------------

    def test_text_edit_size_and_extension_limits(self):
        big = self.root / 'big.txt'
        big.write_text('x' * (fm.MAX_EDIT_SIZE + 1))
        with self.assertRaises(fm.FileManagerError):
            fm.read_text('test', 'big.txt')

        binary = self.root / 'image.png'
        binary.write_bytes(b'\x89PNG\r\n\x1a\n')
        with self.assertRaises(fm.FileManagerError):
            fm.read_text('test', 'image.png')

        small = self.root / 'notes.md'
        small.write_text('hello')
        self.assertEqual(fm.read_text('test', 'notes.md'), 'hello')

    # -- symlinks ----------------------------------------------------------

    @unittest.skipIf(sys.platform.startswith('win'), 'symlink creation needs elevated privileges on Windows')
    def test_symlink_escape_rejected(self):
        outside = Path(self._tmp.name) / 'outside'
        outside.mkdir()
        (outside / 'secret.txt').write_text('nope')
        link = self.root / 'escape'
        link.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(fm.FileManagerError):
            fm.resolve_safe('test', 'escape/secret.txt')
