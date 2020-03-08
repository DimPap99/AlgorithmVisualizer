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

# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


@app.route('/')
def hello():


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

@app.route('/tes2t', methods=['POST'])
def get_names():
   if request.method == 'POST':
       names = request.get_json()
       for name in names:
           print(name)
   return '', 200


@app.route('/test')
def index():
    return flask.render_template('index.html')

@app.route('/runAlgo',methods= ['POST'])
def process():


    output = request.get_json()

    neighbors = djikstra(nodes_dict1, nodes_dict1[output[0]], nodes_dict1[output[1]])
    neighbors_list = []
    for node in neighbors:
        neighbors_list.append(node.getNodeid())
    #print(neighbors_list)

    path = findShortestPath( nodes_dict1[output[0]], nodes_dict1[output[1]], nodes_dict1, neighbors)
    path_list = []
    for node in path:
        path_list.append(node.getNodeid())

    if output:
        return jsonify({'output':json.dumps([neighbors_list,path_list])})
    return jsonify({'error' : 'Missing data!'})

if __name__ == '__main__':



    app.run()
