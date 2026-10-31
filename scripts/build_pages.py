#!/usr/bin/env python3
"""Render the shared templates and package Python for static GitHub Pages hosting."""

import json
from pathlib import Path
import shutil
import sys

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from visualizer_api import (  # noqa: E402
    GRID_COLUMNS, GRID_ROWS, MAX_WEIGHT, Graph, PathFinder, SortAlgorithm, WeightDistribution,
)


def build(output=ROOT / "dist"):
    runtime = ROOT / "node_modules/pyodide"
    if not (runtime / "pyodide.mjs").is_file():
        raise RuntimeError("Install the pinned browser runtime first: npm ci")
    if output.exists():
        if not (output / ".algorithm-visualizer-build").is_file():
            raise RuntimeError(f"Refusing to replace an unrecognized build directory: {output}")
        shutil.rmtree(output)
    output.mkdir(parents=True)
    (output / ".algorithm-visualizer-build").touch()
    (output / ".nojekyll").touch()
    shutil.copytree(ROOT / "static", output / "static")
    runtime_output = output / "runtime"
    runtime_output.mkdir()
    for name in ("pyodide.mjs", "pyodide.asm.mjs", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json"):
        shutil.copy2(runtime / name, runtime_output / name)
    shutil.copy2(ROOT / "static/vendor/pyodide-LICENSE", runtime_output / "LICENSE")
    (runtime_output / "NOTICE.txt").write_text(
        "Pyodide 314.0.7 — https://github.com/pyodide/pyodide/tree/314.0.7\n"
        "Distributed under the Mozilla Public License 2.0.\n"
        "Python and other bundled components retain their respective licenses.\n",
        encoding="utf-8",
    )

    sources = [ROOT / name for name in ("Node.py", "Graph.py", "WeightDistributions.py", "visualizer_api.py")]
    sources.extend(sorted((ROOT / "Algorithms").glob("*.py")))
    python_output = output / "python"
    python_output.mkdir()
    (python_output / "sources.json").write_text(json.dumps(
        {str(path.relative_to(ROOT)): path.read_text(encoding="utf-8") for path in sources}
    ), encoding="utf-8")

    environment = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape(["html"]))
    pages = (
        ("index.html", "mainpage.html", {"algorithm": "Algorithm"}),
        ("PathFinding/index.html", "pathFinding.html", {
            "algorithm": "Path Finding", "algorithms": PathFinder.registry,
            "distributions": WeightDistribution.registry, "max_weight": MAX_WEIGHT,
            "nodes": Graph(GRID_ROWS, GRID_COLUMNS).nodes_dict, "rows": GRID_ROWS, "columns": GRID_COLUMNS,
        }),
        ("SortAlgorithms/index.html", "sortAlgorithms.html", {
            "algorithm": "Sort Algorithms", "algorithms": SortAlgorithm.registry,
        }),
    )
    for filename, template, context in pages:
        prefix = "../" if "/" in filename else "./"

        def url_for(endpoint, filename=None):
            if endpoint == "static":
                return prefix + "static/" + filename
            return prefix + {"mainPage": "", "pathFinding": "PathFinding/", "sortAlgorithms": "SortAlgorithms/"}[endpoint]

        target = output / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(environment.get_template(template).render(
            **context, runtime="browser", url_for=url_for,
        ), encoding="utf-8")
    shutil.copy2(ROOT / "LICENSE", output / "LICENSE")
    print(f"Built {len(pages)} pages and {len(sources)} Python source files in {output}")
    return output


if __name__ == "__main__":
    build()
