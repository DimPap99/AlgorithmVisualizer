from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from Graph import Graph
from Algorithms.SortAlgorithms import SortAlgorithm
from Algorithms.PathFindingAlgorithms import PathFinder
from WeightDistributions import WeightDistribution, MIN_WEIGHT, MAX_WEIGHT

app = Flask(__name__)
GRID_ROWS, GRID_COLUMNS = 30, 50

CORS(app, resources={r'/*': {'origins': '*'}})


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to stop the browser from caching the rendered pages.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


# The algorithms and the Graph raise ValueError on bad input, which is returned to the client as a 400
@app.errorhandler(ValueError)
def badRequest(error):
    return jsonify({'error': str(error)}), 400


def getJson():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object")
    return data


@app.route('/')
def mainPage():
    return render_template("mainpage.html", algorithm="Algorithm")


@app.route('/PathFinding')
def pathFinding():
    return render_template('pathFinding.html', algorithm="Path Finding", algorithms=PathFinder.registry,
                           distributions=WeightDistribution.registry, max_weight=MAX_WEIGHT,
                           nodes=Graph(GRID_ROWS, GRID_COLUMNS).nodes_dict, rows=GRID_ROWS, columns=GRID_COLUMNS)


@app.route('/SortAlgorithms')
def sortAlgorithms():
    return render_template("sortAlgorithms.html", algorithm="Sort Algorithms", algorithms=SortAlgorithm.registry)


# Expects {"algorithm": name, "array": [numbers]} and returns {"swaps": [[index1, index2], ...]}
@app.route('/SortArray', methods=['POST'])
def sortResult():
    data = getJson()
    num_array = data.get('array')
    if not isinstance(num_array, list) or not all(isinstance(num, (int, float)) for num in num_array):
        raise ValueError("'array' must be a list of numbers")
    return jsonify({'swaps': SortAlgorithm.get(data.get('algorithm'))(num_array).run()})


# Expects {"algorithm": name, "params": {name: value}, "start": id, "end": id, "walls": [ids],
# "weights": {id: cost of moving into it}} and returns {"visited": [ids in visiting order],
# "paths": [{"path": [ids from start to end], "cost": cost}, ...] (cheapest first, empty if there is none),
# "cycle": {"nodes": [ids], "cost": cost of going around it once} or null} where cycle is a negative cycle
@app.route('/runAlgo', methods=['POST'])
def pathResult():
    data = getJson()
    start, end = data.get('start'), data.get('end')
    walls = set(data.get('walls') or []) - {start, end}
    weights = data.get('weights') or {}
    if not isinstance(weights, dict):
        raise ValueError("'weights' must map node ids to weights")
    graph = Graph(GRID_ROWS, GRID_COLUMNS, walls, weights)
    finder = PathFinder.get(data.get('algorithm'))(graph, start, end, data.get('params'))
    visited, paths = finder.run()
    cycle = finder.negative_cycle
    return jsonify({'visited': visited, 'paths': [{'path': path, 'cost': graph.pathCost(path)} for path in paths],
                    'cycle': {'nodes': cycle, 'cost': graph.pathCost(cycle + cycle[:1])} if cycle else None})


# Expects {"distribution": name, "params": {name: value}, "min_weight": lowest weight allowed} and returns
# {"weights": {id: weight}} for every grid node
@app.route('/generateWeights', methods=['POST'])
def generateWeights():
    data = getJson()
    min_weight = data.get('min_weight', MIN_WEIGHT)
    if isinstance(min_weight, bool) or not isinstance(min_weight, (int, float)):
        raise ValueError("'min_weight' must be a number")
    distribution = WeightDistribution.get(data.get('distribution'))(data.get('params'))
    return jsonify({'weights': distribution.weights(Graph(GRID_ROWS, GRID_COLUMNS).nodes_dict, min_weight)})


if __name__ == '__main__':
    app.run()
