# AlgorithmVisualizer
To install all the project's dependecies run:
            <br>
                 
          pip install -r requirements.txt

Then start the app with `python app.py` and open http://127.0.0.1:5000.

## Algorithms
- **Path Finding:** Dijkstra, A* Search, Greedy Best-First Search, Breadth-First Search, Depth-First Search
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
or subclasses `PriorityFirstSearch` and only defines `priority(node_id, distance)`.

Both can be used without Flask:

```python
swaps = SortAlgorithm.get("Heap Sort")([5, 3, 8, 1]).run()
visited, path = PathFinder.get("A* Search")(Graph(30, 50, walls=["2-3"]), "0-0", "5-5").run()
```
