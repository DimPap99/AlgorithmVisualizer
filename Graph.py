import math
from Node import Node


# A rows x columns grid. Every node is keyed by its id ('row-col') and is linked to its 4 adjacent nodes.
# A new Graph is built for every request so that no search state leaks between runs or users.
class Graph:

    def __init__(self, rows, columns, walls=(), weights=None):
        self.nodes_dict = dict()
        self.rows = rows
        self.columns = columns
        self.createNodes()
        self.addWalls(walls)
        self.addWeights(weights or {})

    def createNodes(self):
        for row in range(self.rows):
            for col in range(self.columns):
                node = Node(row, col)
                self.nodes_dict[node.getNodeid()] = node

        # Fill the neighbors list for every node with the ids of the in-bounds adjacent nodes
        for node in self.nodes_dict.values():
            for row, col in ((node.row - 1, node.column), (node.row, node.column - 1),
                             (node.row, node.column + 1), (node.row + 1, node.column)):
                key = str(row) + '-' + str(col)
                if key in self.nodes_dict:
                    node.neighbors.append(key)

    def addWalls(self, walls_id):
        for node_id in walls_id:
            self.getNode(node_id).is_wall = True

    # weights maps node ids to the cost of moving into that node
    def addWeights(self, weights):
        for node_id, weight in weights.items():
            if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not math.isfinite(weight):
                raise ValueError("Weights must be numbers")
            self.getNode(node_id).weight = weight

    # the lowest weight of a node that isn't a wall
    def minWeight(self):
        return min((node.weight for node in self.nodes_dict.values() if not node.is_wall), default=1)

    def getNode(self, node_id):
        if node_id not in self.nodes_dict:
            raise ValueError("Unknown node id: " + str(node_id))
        return self.nodes_dict[node_id]

    # ids of the adjacent nodes that are not walls
    def openNeighbors(self, node_id):
        return [key for key in self.nodes_dict[node_id].neighbors if not self.nodes_dict[key].is_wall]

    # cost of moving from a node to an adjacent one
    def cost(self, node_id1, node_id2):
        return self.nodes_dict[node_id2].weight

    def pathCost(self, path):
        return sum(self.cost(node_id1, node_id2) for node_id1, node_id2 in zip(path, path[1:]))

    # Manhattan distance, the exact distance between two nodes on an empty grid with no weights
    def distance(self, node_id1, node_id2):
        node1, node2 = self.nodes_dict[node_id1], self.nodes_dict[node_id2]
        return abs(node1.row - node2.row) + abs(node1.column - node2.column)

    def printGraph(self):
        for key, val in self.nodes_dict.items():
            print("Nodeid: " + key + " Neighbors: ", val.neighbors)


# The same graph without some nodes and some directed edges (pairs of node ids)
class GraphView:

    def __init__(self, graph, blocked_nodes=(), blocked_edges=()):
        self.graph = graph
        self.blocked_nodes = set(blocked_nodes)
        self.blocked_edges = set(blocked_edges)

    # everything else comes from the graph
    def __getattr__(self, name):
        return getattr(self.graph, name)

    def openNeighbors(self, node_id):
        return [key for key in self.graph.openNeighbors(node_id)
                if key not in self.blocked_nodes and (node_id, key) not in self.blocked_edges]
