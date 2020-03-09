from flask import Flask, jsonify
import flask
from flask import request
from flask_cors import CORS
import Node
import json
from djkstra import *
app = Flask(__name__)
nodes_dict1 = dict()

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
def dijkstraNodes():


    for col in range(0, 25):
        for rows in range(0, 50):
            node = Node(col, rows)

            nodes_dict1[str(node.column) + '-' + str(node.row)] = node

    # Fill the neighbors list for every node
    for col in range(0, 25):
        for row in range(0, 50):
            # current node id is the col - row
            key = str(col) + '-' + str(row)
            current_node = nodes_dict1[key]
            # print("Current Node " + str(key))
            # dict ids of all possible neighbor locations
            possible_neighbors = [str(col - 1) + "-" + str(row), str(col) + "-" + str(row - 1),
                                  str(col) + "-" + str(row + 1), str(col + 1) + "-" + str(row),
                                  ]
            for key2 in possible_neighbors:

                # check if a node with that id exists if it does proceed to add it to our current_nodes neighbors.+
                if key2 in nodes_dict1:
                    current_node.neighbors.append(key2)

    return flask.render_template('mainPage.html', nodes = nodes_dict1)




@app.route('/runAlgo',methods= ['POST'])
def dijkstraInfo():

    # output contains the start/end node id in 0 nad 1 location respectively
    # in location 2 it containts the ids of the wall nodes
    output = request.get_json()
    walls = output[2]
    addWalls(walls,nodes_dict1)
    res = djikstra(nodes_dict1, nodes_dict1[output[0]], nodes_dict1[output[1]])
    neighbors = res[0]
    traped =  res[1]
    neighbors_list = []
    for node in neighbors:
        neighbors_list.append(node.getNodeid())


    path = findShortestPath( nodes_dict1[output[0]], nodes_dict1[output[1]], nodes_dict1, neighbors)
    path_list = []
    if not traped:
        for node in path:
            path_list.append(node.getNodeid())

    if output:
        return jsonify({'output':json.dumps([neighbors_list,path_list])})
    return jsonify({'error' : 'Missing data!'})

if __name__ == '__main__':



    app.run()
