from flask import Flask, jsonify
import flask
from flask import request
from flask_cors import CORS
from Graph import Graph
from Algorithms.SortAlgorithms import *
from Algorithms.djkstra import *

app = Flask(__name__)
graph = Graph(30, 50)

CORS(app, resources={r'/*': {'origins': '*'}})


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.route('/')
def mainPage():
    return flask.render_template("mainpage.html", algorithm="Algorithm")


@app.route('/dijkstra')
def dijkstraNodes():
    graph.createNodes()
    return flask.render_template('dijkstra.html', nodes=graph.nodes_dict, algorithm="Dijkstra")


@app.route('/SortAlgorithms')
def sortAlgorithms():
    return flask.render_template("sortAlgorithms.html", algorithm="Sort Algorithms")

# output[0] ---> Our array
# output[1] ---> The selected choice
@app.route('/SortArray', methods=['POST'])
def sortResult():
    try:
        swaps = []
        output = request.get_json()
        if output[1] == "Insertion Sort":
            swaps = insertionSort(output[0])
            return jsonify({'output': json.dumps(swaps)})
        if output[1] == "Quick Sort":
            quickSort(output[0], 0, len(output[0]) - 1, swaps)
            return jsonify({'output': json.dumps(swaps)})
        if output[1] == "Bubble Sort":
            swaps = bubbleSort(output[0])
            return jsonify({'output': json.dumps(swaps)})
        if output[1] == "Selection Sort":
            swaps = selectionSort(output[0])
            return jsonify({'output': json.dumps(swaps)})
    except (TypeError, ValueError) as e:
        print("An error occured. " + str(e))
        return jsonify({'error': 'Wrong data!'})


@app.route('/runAlgo', methods=['POST'])
def dijkstraInfo():
    # output contains the start/end node id in 0 nad 1 location respectively
    # in location 2 it containts the ids of the wall nodes
    output = request.get_json()
    walls = output[2]
    addWalls(walls, graph.nodes_dict)
    res = djikstra(graph.nodes_dict, graph.nodes_dict[output[0]], graph.nodes_dict[output[1]])
    neighbors = res[0]
    traped = res[1]
    neighbors_list = []
    for node in neighbors:
        neighbors_list.append(node.getNodeid())

    path = findShortestPath(graph.nodes_dict[output[0]], graph.nodes_dict[output[1]], graph.nodes_dict, neighbors)
    path_list = []
    if not traped:
        for node in path:
            path_list.append(node.getNodeid())

    if output:
        return jsonify({'output': json.dumps([neighbors_list, path_list])})
    return jsonify({'error': 'Missing data!'})


if __name__ == '__main__':
    app.run()
