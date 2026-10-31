from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO
import tempfile
import unittest

from scripts.deploy_pages import deploy, git


class PublishingTests(unittest.TestCase):
    def deploy_test_build(self):
        # These deployments only touch temporary local bare repositories.
        with redirect_stdout(StringIO()):
            deploy(self.root)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        directory = Path(self.temporary.name)
        self.remote = directory / 'remote.git'
        self.remote.mkdir()
        git(self.remote, 'init', '--bare', '--initial-branch=master')
        self.root = directory / 'source'
        self.root.mkdir()
        git(self.root, 'init', '--initial-branch=master')
        git(self.root, 'config', 'user.name', 'Deployment test')
        git(self.root, 'config', 'user.email', 'test@example.invalid')
        git(self.root, 'remote', 'add', 'origin', str(self.remote))
        (self.root / '.gitignore').write_text('dist/\n')
        git(self.root, 'add', '.gitignore')
        git(self.root, 'commit', '-m', 'Test source')
        self.output = self.root / 'dist'
        self.output.mkdir()
        (self.output / '.algorithm-visualizer-build').touch()
        (self.output / '.nojekyll').touch()
        (self.output / 'index.html').write_text('First build')

    def test_first_publication_and_updates_preserve_history(self):
        self.deploy_test_build()
        first = git(self.remote, 'rev-parse', 'gh-pages')
        self.assertEqual(git(self.remote, 'show', 'gh-pages:index.html'), 'First build')
        (self.output / 'index.html').write_text('Second build')
        self.deploy_test_build()
        self.assertEqual(git(self.remote, 'show', 'gh-pages:index.html'), 'Second build')
        self.assertEqual(git(self.remote, 'rev-parse', 'gh-pages^'), first)
        self.deploy_test_build()
        self.assertEqual(git(self.root, 'status', '--porcelain'), '')

    def test_uncommitted_source_is_not_published(self):
        (self.root / 'unfinished.txt').write_text('An unfinished change')
        with self.assertRaisesRegex(RuntimeError, 'Commit your source'):
            deploy(self.root)
        self.assertEqual(git(self.remote, 'ls-remote', '.', 'gh-pages'), '')
