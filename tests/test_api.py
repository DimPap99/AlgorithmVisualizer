from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import app
from visualizer_api import dispatch
from Algorithms.SortAlgorithms import SortAlgorithm
from Algorithms.PathFindingAlgorithms import PathFinder
from WeightDistributions import WeightDistribution


class SharedApiTests(unittest.TestCase):
    def test_all_sort_animations_produce_sorted_arrays(self):
        original = [7, -2, 3, 3, 0, 11, 1.5, -2]
        for name in SortAlgorithm.registry:
            with self.subTest(algorithm=name):
                array = original[:]
                for left, right in dispatch('/SortArray', {'algorithm': name, 'array': array})['swaps']:
                    array[left], array[right] = array[right], array[left]
                self.assertEqual(array, sorted(original))

    def test_all_searches_find_a_valid_path(self):
        for name in PathFinder.registry:
            with self.subTest(algorithm=name):
                result = dispatch('/runAlgo', {'algorithm': name, 'start': '0-0', 'end': '2-3'})
                path = result['paths'][0]['path']
                self.assertEqual((path[0], path[-1]), ('0-0', '2-3'))
                for left, right in zip(path, path[1:]):
                    r1, c1 = map(int, left.split('-'))
                    r2, c2 = map(int, right.split('-'))
                    self.assertEqual(abs(r1 - r2) + abs(c1 - c2), 1)

    def test_blocked_target_has_no_path(self):
        result = dispatch('/runAlgo', {'algorithm': 'Dijkstra', 'start': '0-0', 'end': '2-3', 'walls': ['0-1', '1-0']})
        self.assertEqual(result['paths'], [])

    def test_negative_cycle_is_reported(self):
        result = dispatch('/runAlgo', {'algorithm': 'Bellman-Ford', 'start': '0-0', 'end': '0-2', 'weights': {'0-1': -3}})
        self.assertLess(result['cycle']['cost'], 0)
        self.assertEqual(result['paths'], [])

    def test_distributions_cover_the_grid_and_respect_bounds(self):
        for name in WeightDistribution.registry:
            weights = dispatch('/generateWeights', {'distribution': name})['weights']
            self.assertEqual(len(weights), 1500)
            self.assertTrue(all(1 <= weight <= 99 for weight in weights.values()))

    def test_invalid_data_is_rejected(self):
        for data in (None, [], {'algorithm': 'Unknown', 'array': [1]}, {'algorithm': 'Quick Sort', 'array': [float('inf')]}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                dispatch('/SortArray', data)

    def test_flask_pages_and_requests_still_work(self):
        client = app.test_client()
        for route in ('/', '/PathFinding', '/SortAlgorithms'):
            response = client.get(route)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'data-runtime="server"', response.data)
            self.assertNotIn(b'pyodide-worker', response.data)
        payload = {'algorithm': 'Heap Sort', 'array': [3, 1, 2]}
        self.assertEqual(client.post('/SortArray', json=payload).get_json(), dispatch('/SortArray', payload))
        self.assertEqual(client.post('/SortArray', json=[]).status_code, 400)


if __name__ == '__main__':
    unittest.main()
