# AlgorithmVisualizer

Interactive sorting and pathfinding algorithms, implemented in Python with JavaScript animations.

**Live demo:** https://dimpap99.github.io/AlgorithmVisualizer/

## Browser version / GitHub Pages

The hosted version runs the existing Python algorithms through Pyodide in a Web Worker.
It needs no Flask server. The Python runtime, JavaScript dependencies, and algorithm source
are included in the static build and served from the same site. The first visit downloads
the Python runtime. Subsequent loads can reuse the browser cache.

Requirements: Python 3.12+ and Node.js 22+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm ci
npm run build
python3 -m http.server 8000 --directory dist
```

Open <http://localhost:8000>. Serve the build over HTTP. Opening the HTML files directly
will not load the module worker. `dist/` is generated and should not be committed.

## Deploy an update

After committing your source changes on `master`, run:

```bash
npm run deploy
```

This runs the Python and WebAssembly tests, builds `dist/`, pushes the source to
`master`, and publishes the generated files to `gh-pages`. GitHub Pages automatically
deploys that branch. A normal push to `master` updates the source repository.
Run `npm run deploy` when you want the live demo updated.

The repository's Pages source is **Deploy from a branch → gh-pages → /(root)**.
This uses GitHub's built-in Pages deployment and does not require permission to
create custom Actions workflows. The deployment helper refuses uncommitted source
changes and uses a temporary checkout without replacing your working files.

New algorithm classes and distribution parameters appear in the generated controls
on the next build. Keep changes in the Python source. Do not edit generated files.

## Flask version

After installing the Python dependencies above:

```bash
python app.py
```

Open <http://127.0.0.1:5000>. Flask and the browser worker call the same functions in
`visualizer_api.py`. The Flask version continues to use its JSON endpoints.

## Tests

```bash
python -m unittest discover -s tests
npm run build
npm test
```

The Node tests execute the exported Python source with the actual Pyodide WebAssembly
runtime, exercise the packaged worker, and check cancellation and startup errors.

## Algorithms

Each selected algorithm shows pseudocode, its worst-case time complexity, and notes
about the implementation. The [algorithm guide review](docs/algorithm-guide-review.md)
records the bounds, implementation differences, and standard references.
Start and End have separate colors and S/E markers.
Weights use blue above 1 and amber below 1.

- **Path Finding:** Dijkstra, A* Search, Greedy Best-First Search, Bidirectional Dijkstra, Yen's K Shortest Paths,
  Bellman-Ford, Breadth-First Search, Depth-First Search.
  Cells can have weights (the cost of moving into them), painted one by one or generated from a distribution
  (Uniform, Gaussian, Exponential, Bernoulli). BFS and DFS ignore them. Only Bellman-Ford allows negative weights,
  and it highlights a negative cycle when there is one (then no cheapest path exists).
- **Sorting:** Insertion, Quick, Bubble, Selection, Merge, Heap, Shell, Cocktail Shaker and Comb Sort

## Adding an algorithm
Every algorithm is a small class that registers itself by its `name`, and the pages list every registered algorithm. Add its pseudocode and complexity to `static/data/algorithm-guides.json` as well. The tests check that every registered algorithm has an entry.

A sort algorithm subclasses `SortAlgorithm` (`Algorithms/SortAlgorithms.py`) and moves elements only through
`self.swap(i, j)`, which records the swaps that the page animates:

```python
class GnomeSort(SortAlgorithm):
    name = "Gnome Sort"

    def sort(self):
        i = 1
        while i < len(self.num_array):
            if i > 0 and self.num_array[i - 1] > self.num_array[i]:
                self.swap(i - 1, i)
                i -= 1
            else:
                i += 1
```

A path finding algorithm subclasses `PathFinder` (`Algorithms/PathFindingAlgorithms.py`) and implements `search()`,
or subclasses `PriorityFirstSearch` and only defines `priority(node_id, distance)`. Like distributions it can take
`params` (Yen's takes the number of paths), and it sets `min_weight = float('-inf')` if it handles negative weights.

A weight distribution subclasses `WeightDistribution` (`WeightDistributions.py`) with its parameters and their defaults
(the page shows an input for every parameter):

```python
class Triangular(WeightDistribution):
    name = "Triangular"
    params = {'low': 1, 'high': 20, 'mode': 5}

    def sample(self):
        return random.triangular(self.low, self.high, self.mode)
```

All of them can be used without Flask:

```python
swaps = SortAlgorithm.get("Heap Sort")([5, 3, 8, 1]).run()
weights = WeightDistribution.get("Gaussian")({'mean': 10, 'std': 4}).weights(Graph(30, 50).nodes_dict)
visited, paths = PathFinder.get("Yen's K Shortest Paths")(Graph(30, 50, ["2-3"], weights), "0-0", "5-5", {'paths': 3}).run()
```
