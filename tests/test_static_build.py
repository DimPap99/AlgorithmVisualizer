from html.parser import HTMLParser
import json
from pathlib import Path
import tempfile
import unittest
from urllib.parse import urlsplit

from scripts.build_pages import build
from Algorithms.PathFindingAlgorithms import PathFinder
from Algorithms.SortAlgorithms import SortAlgorithm


class Links(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.targets = []
        self.feed(html)

    def handle_starttag(self, tag, attributes):
        for name, value in attributes:
            if name in ('src', 'href') and value:
                self.targets.append(value)


class StaticBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.output = build(Path(cls.temporary.name) / 'site')

    def test_links_work_at_a_project_subdirectory(self):
        for page in self.output.rglob('*.html'):
            for link in Links(page.read_text()).targets:
                url = urlsplit(link)
                if url.scheme or url.netloc or not url.path:
                    continue
                self.assertFalse(url.path.startswith('/'), f'Root-relative link: {page}: {link}')
                target = (page.parent / url.path).resolve()
                if target.is_dir():
                    target = target / 'index.html'
                self.assertTrue(target.is_file(), f'Missing asset: {page}: {link}')

    def test_the_runtime_and_algorithms_are_packaged(self):
        for name in ('pyodide.mjs', 'pyodide.asm.mjs', 'pyodide.asm.wasm', 'python_stdlib.zip', 'pyodide-lock.json', 'LICENSE'):
            self.assertTrue((self.output / 'runtime' / name).is_file(), name)
        self.assertTrue((self.output / '.nojekyll').is_file())
        self.assertIn('visualizer_api.py', (self.output / 'python/sources.json').read_text())
        self.assertEqual((self.output / 'PathFinding/index.html').read_text().count('class="cell"'), 1500)
        self.assertIn('data-runtime="browser"', (self.output / 'SortAlgorithms/index.html').read_text())
        self.assertFalse((self.output / 'app.py').exists())

    def test_build_does_not_replace_an_unrelated_directory(self):
        other = Path(self.temporary.name) / 'unrelated'
        other.mkdir()
        (other / 'keep.txt').write_text('User data')
        with self.assertRaises(RuntimeError):
            build(other)
        self.assertEqual((other / 'keep.txt').read_text(), 'User data')

    def test_every_available_algorithm_has_pseudocode_and_complexity(self):
        guides = json.loads((self.output / 'static/data/algorithm-guides.json').read_text())
        self.assertEqual(set(guides['algorithms']), set(SortAlgorithm.registry) | set(PathFinder.registry))
        for name, guide in guides['algorithms'].items():
            with self.subTest(algorithm=name):
                self.assertTrue(guide['time'].startswith('O('))
                self.assertGreater(len(guide['pseudocode']), 3)
                self.assertTrue(guide['note'])
                self.assertIn(guide['group'], guides['notation'])
        for path in ('PathFinding/index.html', 'SortAlgorithms/index.html'):
            html = (self.output / path).read_text()
            self.assertEqual(html.count('id="algorithm-guide"'), 1)
            self.assertIn('algorithm-guide.js', html)
