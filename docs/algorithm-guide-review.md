# Algorithm guide review

The displayed pseudocode describes the Python implementation, with animation recording
omitted. It uses standard algorithm terminology, zero-based arrays and inclusive ranges.
An empty range executes no iterations. Heap ties may be broken arbitrarily unless noted.
The time field is a worst-case upper bound for this implementation, rather than an
average-case claim or a generic bound for every variant with the same name.

`n` counts array elements. `V` counts grid vertices and `E` counts traversable directed
edges. A move `u → v` costs `weight(v)`. The starting cell contributes no cost. The grid
has four neighbors per vertex, so `E = O(V)`. Comparisons, numeric arithmetic and hash
table operations are treated as constant time. Bounds exclude graph construction,
serialization, runtime loading and animation playback.

## Sorting

| Algorithm | Displayed worst case | Reason and implementation details |
| --- | --- | --- |
| Insertion | O(n²) | Adjacent swaps remove inversions. Sorted input makes one comparison per insertion: O(n). |
| Quick | O(n²) | Lomuto partition with the last element as pivot can repeatedly split off an empty partition. Expected O(n log n) assumes a uniformly random ordering of distinct keys. There is no random shuffle in this code. Recursing on the smaller side bounds stack depth, not total work. |
| Bubble | O(n²) | At most n shrinking passes. Early exit gives O(n) on sorted input. |
| Selection | O(n²) | Every unsorted suffix is scanned, regardless of order. |
| Merge | O(n²) | The merge shifts elements using adjacent swaps. A merge of m items can make O(m²) swaps. T(n) = 2T(n/2) + O(n²) = O(n²). Sorted input takes O(n log n). **Standard buffered merge sort is O(n log n)**. That is not the merge implemented here. |
| Heap | O(n log n) | Bottom-up heap construction is O(n). Each of the n removals each take O(log n). |
| Shell | O(n²) | This is Shell's original halving sequence, not Knuth's sequence. The gap sequence determines the bound. Sorted input still makes O(log n) passes: O(n log n). |
| Cocktail shaker | O(n²) | Forward and backward bubble passes shrink the active interval. Sorted input completes in O(n). |
| Comb | O(n²) | There are O(log n) shrinking-gap passes, each O(n), followed by ordinary bubble passes at gap 1. Those final passes can take O(n²). Sorted input still takes O(n log n). |

References: Princeton's [elementary sorts](https://algs4.cs.princeton.edu/21elementary/),
[quicksort](https://algs4.cs.princeton.edu/23quicksort/index.php),
[buffered merge sort](https://algs4.cs.princeton.edu/22mergesort/index.php) and
[heapsort](https://algs4.cs.princeton.edu/code/javadoc/edu/princeton/cs/algs4/Heap.html).
Stewart Weiss's [sorting notes, including Shell's original gap sequence](https://www.cs.hunter.cuny.edu/~sweiss/course_materials/csci335/lecture_notes/chapter07.pdf).
NIST's [bubble sort](https://xlinux.nist.gov/dads/HTML/bubblesort.html),
[cocktail shaker sort](https://xlinux.nist.gov/dads/HTML/bidirectionalBubbleSort.html) and
[comb sort](https://xlinux.nist.gov/dads/HTML/combSort.html).
The adjacent-swap merge bound above follows from this repository's code, rather than
the buffered implementation in the reference.

## Pathfinding

| Algorithm | Displayed worst case | Conditions and guarantee |
| --- | --- | --- |
| Dijkstra | O((V + E) log V) | Binary heap. Each vertex expanded once, with at most one queue insertion per successful edge relaxation. Standard Dijkstra permits nonnegative costs. The app requires weights ≥ 1. Returns minimum cost. |
| A* | O((V + E) log V) | Same heap structure. Manhattan distance is consistent on this four-neighbor grid when costs are ≥ 1: h(u) ≤ weight(v) + h(v). No vertex needs reopening. Returns minimum cost. Ties favor smaller h. This bound describes finite graph search, not the exponential search-tree formulation. |
| Greedy best-first | O((V + E) log V) | Priority is h alone. Vertices are expanded once. The code still relaxes distances, but never reopens an expanded vertex. Finds a path, with no shortest-path guarantee. |
| Bidirectional Dijkstra | O((V + E) log V) | Two heap searches change only a constant factor. Backward traversal uses the original edge cost in reverse: backward u → v costs weight(u). Stops at min(Qf) + min(Qb) ≥ best, not at the first intersection. Returns minimum cost. |
| Yen | O(KV((V + E) log V + KV)) | Up to K rounds and V spur searches per round, using heap-based A*. Python list-prefix comparisons add O(K²V²) total work. Returns up to K distinct simple paths by nondecreasing cost. K is capped at 10. |
| Bellman–Ford | O(V(V + E)) | The frontier implementation uses synchronous distance snapshots and O(E) relaxations per round. Checking predecessor chains adds O(V) per round, with O(V) rounds before convergence or cycle detection. On this grid the bound is O(V²). Reports reachable negative cycles. |
| Breadth-first | O(V + E) | FIFO queue. Vertices are marked when enqueued. Returns the fewest edges, which need not minimize weighted cost. |
| Depth-first | O(V + E) | Stack. Vertices are marked when popped, and each adjacency list is expanded once. Duplicate stack entries add at most O(E) work. Returns a path, with no shortest-path guarantee. |

The heap implementations allow duplicate entries and skip already expanded vertices.
There are at most O(E) insertions. Since the grid is a simple graph, log E = O(log V).
All algorithms except Bellman–Ford inherit the app's weight ≥ 1 validation, including
BFS and DFS even though their search order ignores weights.

For Yen, writing S = O((V + E) log V) gives O(KVS) shortest-path work. For each of
O(KV) spur positions, the code compares a prefix of length up to V against up to K
accepted paths: O(KV) per spur, or O(K²V²) total. Candidate construction, cost summation,
hashing and min-heap operations are covered by the displayed bound. Candidates persist
across rounds and a generated-path set prevents duplicates. Both directions of an
undirected grid connection are distinct directed edges when temporarily blocking a spur.

The commonly quoted Bellman–Ford bound is O(VE). The displayed O(V(V + E)) also counts
the predecessor-cycle scans performed here. One scan visits each predecessor at most
once because completed walks share a `done` set. Synchronous rounds discover all
shortest paths of up to one additional edge per round. A reachable negative cycle
prevents convergence. The predecessor cycle is reported rather than returning a path.

References: Princeton's [shortest paths](https://algs4.cs.princeton.edu/44sp/),
[graph algorithm bounds](https://algs4.cs.princeton.edu/cheatsheet/) and
[bidirectional Dijkstra and A* lecture](https://www.cs.princeton.edu/courses/archive/spr06/cos423/Handouts/EPP%20shortest%20path%20algorithms.pdf).
[Berkeley's A* consistency notes](https://inst.eecs.berkeley.edu/~cs188/sp24/assets/notes/cs188-sp24-note03.pdf).
[Yen's original paper](https://pubsonline.informs.org/doi/10.1287/mnsc.17.11.712) and
[NetworkX's Yen implementation](https://networkx.org/documentation/stable/_modules/networkx/algorithms/simple_paths.html#shortest_simple_paths).
The Python prefix overhead is derived from this repository, rather than attributed
to the original paper's implementation.

## Verification

`tests/test_algorithm_correctness.py` checks all nine sorters on every input of length
0–5 over {-1, 0, 1}, plus longer boundary cases. It validates the recorded swap replay.
Path tests enumerate every simple path on small weighted grids to check minimum cost,
BFS step counts, and Yen's distinct paths and ordering, including tied costs,
disconnected targets, asymmetric directed costs and identical endpoints.
Bellman–Ford is compared with a separate textbook V−1-pass implementation on negative
and zero weights, including reachable and unreachable negative cycles. These tests
check correctness guarantees. The asymptotic bounds above come from algorithm analysis,
not timing measurements.
