# AlgorithmVisualizer
To install all the project's dependecies run:
            <br>
                 
          pip install -r requirements.txt

Then start the app with `python app.py` and open http://127.0.0.1:5000.

## Algorithms
- **Path Finding:** Dijkstra, A* Search, Greedy Best-First Search, Bidirectional Dijkstra, Yen's K Shortest Paths,
  Bellman-Ford, Breadth-First Search, Depth-First Search.
  Cells can have weights (the cost of moving into them), painted one by one or generated from a distribution
  (Uniform, Gaussian, Exponential, Bernoulli); BFS and DFS ignore them. Only Bellman-Ford allows negative weights,
  and it highlights a negative cycle when there is one (then no cheapest path exists).
- **Sorting:** Insertion, Quick, Bubble, Selection, Merge, Heap, Shell, Cocktail Shaker and Comb Sort

## Adding an algorithm
Every algorithm is a small class that registers itself by its `name`, and the pages list every registered algorithm.

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
