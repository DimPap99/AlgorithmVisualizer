#!/usr/bin/env python3
"""Publish a tested static build from master to the gh-pages branch."""

from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def git(directory, *arguments):
    result = subprocess.run(['git', '-C', str(directory), *arguments], text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def deploy(root=ROOT):
    output = root / 'dist'
    if not (output / '.algorithm-visualizer-build').is_file() or not (output / 'index.html').is_file():
        raise RuntimeError('Build the demo first: npm run build')
    if git(root, 'branch', '--show-current') != 'master':
        raise RuntimeError('Deploy from the master branch.')
    if git(root, 'status', '--porcelain'):
        raise RuntimeError('Commit your source changes before deploying.')

    remote = git(root, 'remote', 'get-url', 'origin')
    revision = git(root, 'rev-parse', '--short', 'HEAD')
    author = git(root, 'log', '-1', '--format=%an%n%ae').splitlines()
    git(root, 'push', 'origin', 'master')

    with tempfile.TemporaryDirectory(prefix='algorithm-visualizer-deploy-') as temporary:
        checkout = Path(temporary)
        git(checkout, 'init', '--initial-branch=gh-pages')
        git(checkout, 'remote', 'add', 'origin', remote)
        git(checkout, 'config', 'user.name', author[0])
        git(checkout, 'config', 'user.email', author[1])
        if git(root, 'ls-remote', '--heads', 'origin', 'gh-pages'):
            git(checkout, 'fetch', '--depth=1', 'origin', 'gh-pages')
            git(checkout, 'reset', '--hard', 'FETCH_HEAD')
        for path in checkout.iterdir():
            if path.name != '.git':
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
        shutil.copytree(output, checkout, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('.algorithm-visualizer-build'))
        git(checkout, 'add', '--all')
        if not git(checkout, 'status', '--porcelain'):
            print('The published build is already up to date.')
            return
        git(checkout, 'commit', '-m', f'Deploy browser demo from {revision}')
        # A regular push protects against overwriting a concurrent deployment.
        git(checkout, 'push', 'origin', 'HEAD:gh-pages')
    print(f'Published build from {revision} to gh-pages.')
    print('GitHub Pages will deploy it at https://dimpap99.github.io/AlgorithmVisualizer/')


if __name__ == '__main__':
    deploy()
