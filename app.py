from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from Graph import Graph
from Algorithms.SortAlgorithms import SortAlgorithm
from Algorithms.PathFindingAlgorithms import PathFinder

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


# Expects {"algorithm": name, "start": id, "end": id, "walls": [ids]} and returns
# {"visited": [ids in visiting order], "path": [ids from start to end, empty if there is none]}
@app.route('/runAlgo', methods=['POST'])
def pathResult():
    data = getJson()
    start, end = data.get('start'), data.get('end')
    walls = set(data.get('walls') or []) - {start, end}
    graph = Graph(GRID_ROWS, GRID_COLUMNS, walls)
    visited, path = PathFinder.get(data.get('algorithm'))(graph, start, end).run()
    return jsonify({'visited': visited, 'path': path})


if __name__ == '__main__':
    app.run()
