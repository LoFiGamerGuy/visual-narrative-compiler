import importlib.util
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('serve_library',Path(__file__).resolve().parents[1]/'scripts/serve_library.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'START-HERE.html').write_text('current')
        (self.root/'old.html').write_text('historical')
        (self.root/'.env').write_text('private')
        self.db = self.root/'inventory.sqlite3'
        with closing(sqlite3.connect(self.db)) as db, db:
            db.execute('CREATE TABLE actions (workspace,path,destination)')
            db.execute('INSERT INTO actions VALUES (?,?,?)',('anime-pipeline-old','docs/index.html','old.html'))
        self.library = MODULE.Library(self.root,self.db)

    def test_root_opens_current_library(self):
        self.assertEqual(self.library.resolve('/').read_text(),'current')
        self.assertEqual(self.library.resolve('/anime-pipeline').read_text(),'current')

    def test_historical_route_uses_preserved_version(self):
        self.assertEqual(self.library.resolve('/workspaces/anime-pipeline-old/docs/index.html').read_text(),'historical')

    def test_old_relative_sibling_route_still_resolves(self):
        self.assertEqual(self.library.resolve('/anime-pipeline-old/docs/index.html').read_text(),'historical')

    def test_unknown_snapshot_file_does_not_fall_back_to_current(self):
        self.assertIsNone(self.library.resolve('/workspaces/anime-pipeline-old/START-HERE.html'))

    def test_private_files_and_traversal_are_rejected(self):
        for route in ('/.env','/.git/config','/%2e%2e/old.html','/..%5cold.html','/inventory.sqlite3'):
            with self.subTest(route=route):
                self.assertIsNone(self.library.resolve(route))

    def test_snapshot_cannot_escape_root(self):
        with closing(sqlite3.connect(self.db)) as db, db:
            db.execute('INSERT INTO actions VALUES (?,?,?)',('anime-pipeline-old','escape.html','../escape.html'))
        self.assertIsNone(self.library.resolve('/workspaces/anime-pipeline-old/escape.html'))

    def test_cross_platform_historical_urls(self):
        for source in ('file:///mnt/c/AgentWorkspaces/anime-pipeline-old/docs/index.html','file:///C:/AgentWorkspaces/anime-pipeline-old/docs/index.html'):
            self.assertEqual(MODULE.remap_links(source),'/workspaces/anime-pipeline-old/docs/index.html')

if __name__ == '__main__':
    unittest.main()
