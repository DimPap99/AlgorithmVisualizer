from Node import *
#

class Graph:

    def __init__(self, rows, columns):
        self.nodes_dict = dict()
        self.rows = rows
        self.columns = columns

    # the total nodes number is equal to rows * cols
    def createNodes(self ):
        for row in range(0, self.rows):
            for col in range(0, self.columns):
                node = Node(row, col)

                self.nodes_dict[str(node.column) + '-' + str(node.row)] = node

        # Fill the neighbors list for every node
        for row in range(0, self.rows):
            for col in range(0, self.columns):
                # current node id is the col - row
                key = str(row) + '-' + str(col)
                current_node = self.nodes_dict[key]
                # print("Current Node " + str(key))
                # dict ids of all possible neighbor locations
                possible_neighbors = [str(row - 1) + "-" + str(col), str(row) + "-" + str(col - 1),
                                      str(row) + "-" + str(col + 1), str(row + 1) + "-" + str(col),
                                      ]
                for key2 in possible_neighbors:

                    # check if a node with that id exists if it does proceed to add it to our current_nodes neighbors.+
                    if key2 in self.nodes_dict:
                        current_node.neighbors.append(key2)

    def printGraph(self):

        for key, val in self.nodes_dict.items():
            print("Nodeid: " + key + " Neighbors: ", val.neighbors)


