"""Check the guarantees stated in the guides against independent small-input oracles."""

import itertools
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from Algorithms.PathFindingAlgorithms import PathFinder
from Algorithms.SortAlgorithms import SortAlgorithm
from Graph import Graph


def all_simple_paths(graph, start, goal):
    """Exhaustive oracle: no priority queues, relaxations or Yen spur searches."""
    paths = []

    def extend(path):
        if path[-1] == goal:
            paths.append(path[:])
            return
        for neighbor in graph.openNeighbors(path[-1]):
            if neighbor not in path:
                extend(path + [neighbor])

    extend([start])
    return paths


def reference_bellman_ford(graph, start):
    """Textbook V−1 full-edge passes, followed by a negative-cycle pass."""
    vertices = [key for key, node in graph.nodes_dict.items() if not node.is_wall]
    edges = [(u, v, graph.cost(u, v)) for u in vertices for v in graph.openNeighbors(u)]
    distance = {v: float('inf') for v in vertices}
    distance[start] = 0
    for _ in range(len(vertices) - 1):
        for u, v, weight in edges:
            distance[v] = min(distance[v], distance[u] + weight)
    negative_cycle = any(distance[u] + weight < distance[v] for u, v, weight in edges)
    return distance, negative_cycle


class AlgorithmCorrectnessTests(unittest.TestCase):
    def assert_valid_path(self, graph, path, start, goal):
        self.assertEqual((path[0], path[-1]), (start, goal))
        self.assertEqual(len(path), len(set(path)), 'A returned path contains a cycle')
        for u, v in zip(path, path[1:]):
            self.assertIn(v, graph.openNeighbors(u))

    def test_all_sorters_on_exhaustive_short_inputs_and_boundary_cases(self):
        cases = [values for size in range(6) for values in itertools.product((-1, 0, 1), repeat=size)]
        cases += [tuple(range(64)), tuple(reversed(range(64))), (4,) * 64, (3, 1, 3, 1) * 16]
        for name, sorter in SortAlgorithm.registry.items():
            for values in cases:
                with self.subTest(algorithm=name, values=values):
                    original = list(values)
                    algorithm = sorter(original)
                    replay = original[:]
                    for left, right in algorithm.run():
                        replay[left], replay[right] = replay[right], replay[left]
                    self.assertEqual(replay, sorted(values))
                    self.assertEqual(algorithm.num_array, sorted(values))
                    self.assertEqual(original, list(values))

    def test_search_guarantees_against_exhaustive_simple_paths(self):
        fixtures = []
        keys = list(Graph(2, 3).nodes_dict)
        # Includes asymmetric edge costs: entering a vertex has a different cost
        # from leaving it. This catches reversed-cost errors in bidirectional search.
        for weights in itertools.product((1, 7), repeat=len(keys)):
            for start, goal in [('0-0', '1-2'), ('0-2', '1-0'), ('0-1', '0-1')]:
                fixtures.append((Graph(2, 3, weights=dict(zip(keys, weights))), start, goal))
        rng = random.Random(8261)
        keys = list(Graph(3, 3).nodes_dict)
        for _ in range(48):
            start, goal = rng.sample(keys, 2)
            walls = [key for key in keys if key not in (start, goal) and rng.random() < 0.3]
            weights = {key: rng.randint(1, 15) for key in keys}
            fixtures.append((Graph(3, 3, walls, weights), start, goal))
        # Explicit disconnected target, rather than relying on the seeded cases.
        fixtures.append((Graph(2, 3, ['0-1', '1-1']), '0-0', '0-2'))

        optimal = {'Dijkstra', 'A* Search', 'Bidirectional Dijkstra', 'Bellman-Ford'}
        for graph, start, goal in fixtures:
            possible = all_simple_paths(graph, start, goal)
            for name, search in PathFinder.registry.items():
                if name == "Yen's K Shortest Paths":
                    continue
                with self.subTest(algorithm=name, start=start, goal=goal, weights=[n.weight for n in graph.nodes_dict.values()]):
                    _, paths = search(graph, start, goal).run()
                    self.assertEqual(bool(paths), bool(possible))
                    if not paths:
                        continue
                    self.assertEqual(len(paths), 1)
                    self.assert_valid_path(graph, paths[0], start, goal)
                    if name in optimal:
                        self.assertEqual(graph.pathCost(paths[0]), min(map(graph.pathCost, possible)))
                    if name == 'Breadth-First Search':
                        self.assertEqual(len(paths[0]), min(map(len, possible)))

    def test_yen_returns_distinct_loopless_paths_in_cost_order(self):
        fixtures = []
        keys = list(Graph(2, 3).nodes_dict)
        for weights in itertools.product((1, 5), repeat=len(keys)):
            fixtures.append((Graph(2, 3, weights=dict(zip(keys, weights))), '0-0', '1-2'))
        rng = random.Random(912)
        keys = list(Graph(3, 3).nodes_dict)
        for _ in range(24):
            walls = [key for key in keys if key not in ('0-0', '2-2') and rng.random() < 0.2]
            fixtures.append((Graph(3, 3, walls, {key: rng.randint(1, 9) for key in keys}), '0-0', '2-2'))
        fixtures += [(Graph(2, 3), '0-0', '0-0'), (Graph(2, 3, ['0-1', '1-1']), '0-0', '0-2')]

        for graph, start, goal in fixtures:
            possible = all_simple_paths(graph, start, goal)
            for count in (1, 3, 10):
                with self.subTest(start=start, goal=goal, count=count, weights=[n.weight for n in graph.nodes_dict.values()]):
                    _, paths = PathFinder.get("Yen's K Shortest Paths")(graph, start, goal, {'paths': count}).run()
                    self.assertEqual(len(paths), min(count, len(possible)))
                    self.assertEqual(len(paths), len({tuple(path) for path in paths}))
                    for path in paths:
                        self.assert_valid_path(graph, path, start, goal)
                    expected_costs = sorted(map(graph.pathCost, possible))[:count]
                    self.assertEqual(list(map(graph.pathCost, paths)), expected_costs)

    def test_bellman_ford_with_negative_and_zero_weights(self):
        keys = list(Graph(2, 2).nodes_dict)
        fixtures = [Graph(2, 2, weights=dict(zip(keys, values)))
                    for values in itertools.product((-2, -1, 0, 1, 2), repeat=4)]
        rng = random.Random(301)
        keys = list(Graph(3, 3).nodes_dict)
        for _ in range(96):
            walls = [key for key in keys if key not in ('0-0', '2-2') and rng.random() < 0.25]
            fixtures.append(Graph(3, 3, walls, {key: rng.randint(-3, 7) for key in keys}))
        # Negative cycles in disconnected components must not be reported.
        fixtures.append(Graph(3, 3, ['0-1', '1-1', '2-1'], {'0-2': -10}))

        for graph in fixtures:
            start = '0-0'
            goal = f'{graph.rows - 1}-{graph.columns - 1}'
            distance, has_negative_cycle = reference_bellman_ford(graph, start)
            algorithm = PathFinder.get('Bellman-Ford')(graph, start, goal)
            with self.subTest(weights=[n.weight for n in graph.nodes_dict.values()]):
                _, paths = algorithm.run()
                self.assertEqual(bool(algorithm.negative_cycle), has_negative_cycle)
                if has_negative_cycle:
                    self.assertEqual(paths, [])
                    cycle = algorithm.negative_cycle
                    self.assertLess(graph.pathCost(cycle + cycle[:1]), 0)
                    for u, v in zip(cycle, cycle[1:] + cycle[:1]):
                        self.assertIn(v, graph.openNeighbors(u))
                elif distance[goal] == float('inf'):
                    self.assertEqual(paths, [])
                else:
                    self.assert_valid_path(graph, paths[0], start, goal)
                    self.assertEqual(graph.pathCost(paths[0]), distance[goal])


if __name__ == '__main__':
    unittest.main()
