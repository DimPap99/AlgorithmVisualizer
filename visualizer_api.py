"""Shared JSON operations for Flask and the browser's Python runtime."""

import math

from Algorithms.PathFindingAlgorithms import PathFinder
from Algorithms.SortAlgorithms import SortAlgorithm
from Graph import Graph
from WeightDistributions import MAX_WEIGHT, MIN_WEIGHT, WeightDistribution

GRID_ROWS, GRID_COLUMNS = 30, 50


def sort_array(data):
    numbers = data.get("array")
    if not isinstance(numbers, list) or not all(
        isinstance(number, (int, float)) and not isinstance(number, bool) and math.isfinite(number)
        for number in numbers
    ):
        raise ValueError("'array' must be a list of finite numbers")
    return {"swaps": SortAlgorithm.get(data.get("algorithm"))(numbers).run()}


def find_path(data):
    start, end = data.get("start"), data.get("end")
    walls = data.get("walls") or []
    if not isinstance(walls, list) or not all(isinstance(node, str) for node in walls):
        raise ValueError("'walls' must be a list of node ids")
    weights = data.get("weights") or {}
    if not isinstance(weights, dict):
        raise ValueError("'weights' must map node ids to weights")
    graph = Graph(GRID_ROWS, GRID_COLUMNS, set(walls) - {start, end}, weights)
    finder = PathFinder.get(data.get("algorithm"))(graph, start, end, data.get("params"))
    visited, paths = finder.run()
    cycle = finder.negative_cycle
    return {
        "visited": visited,
        "paths": [{"path": path, "cost": graph.pathCost(path)} for path in paths],
        "cycle": {"nodes": cycle, "cost": graph.pathCost(cycle + cycle[:1])} if cycle else None,
    }


def generate_weights(data):
    minimum = data.get("min_weight", MIN_WEIGHT)
    if isinstance(minimum, bool) or not isinstance(minimum, (int, float)) or not math.isfinite(minimum):
        raise ValueError("'min_weight' must be a finite number")
    distribution = WeightDistribution.get(data.get("distribution"))(data.get("params"))
    return {"weights": distribution.weights(Graph(GRID_ROWS, GRID_COLUMNS).nodes_dict, minimum)}


def dispatch(action, data):
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object")
    handlers = {"/SortArray": sort_array, "/runAlgo": find_path, "/generateWeights": generate_weights}
    if action not in handlers:
        raise ValueError("Unknown operation: " + str(action))
    return handlers[action](data)
