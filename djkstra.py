import pprint, json
from collections import deque
from Node import *



def visitNeighbors(node, graph, end_point):
    visited_nodes = []
    end_point_Found = False

    # node = Node(node)
    # print(end_point.getNodeid())
    for neighbor_id in node.neighbors:

        neighbor = graph[neighbor_id]
        # print(neighbor.getNodeid())

        if neighbor_id == end_point.getNodeid():
            visited_nodes.append(neighbor)
            end_point.distance = node.distance + 1
            print("Found the end point")
            end_point_Found = True
            break
        if not neighbor.is_wall and not neighbor.is_visited:
            neighbor.distance = node.distance + 1
            neighbor.is_visited = True
            visited_nodes.append(neighbor)

    return visited_nodes, end_point_Found


def sortNodesByDistance(unvisited_Nodes):
    return unvisited_Nodes.sort(key=lambda node: node.distance)


def updateUnvisitedNeighbors(unvisited_nodes):
    deq = deque()
    for node in unvisited_nodes:
        if not node.is_visited:
            deq.append(node)


def findMinDistance(current_Node: Node, min_dist_neighbor: Node, graph):
    minimum = 99999
    min_neighbor = None
    for neighbor in current_node.neighbors:
        if graph[neighbor].distance < minimum:
            minimum = graph[neighbor].distance
            min_neighbor = graph[neighbor]
    return min_neighbor


def findShortestPath(start_point: Node, end_point: Node, graph, neighbors):
    shortest_path = set()
    #shortest_path.add(start_point)
    current_node: Node = end_point
    #shortest_path.add(current_node)
    min_distance = current_node.distance
    min_neighbor = None
    neighbors.append(current_node)
    # check if our current node has a neighbor node with lesser distance from the start point if there is such a
    # neighbor and that neighbor is also in the list with neighbors from djikstra algo (neighbors) its the
    # min_neighbor and it becomes the next current_node. The previous current_node is removed from our neighbors
    # list. if at some point we reach a node that is a neighbor of our start_point this means that its the closest
    # one distance wise And we break the loop.Its time we add to our shortest path the min_neighbor we find.
    try:
        while True:

            for neighbor in neighbors:

                if neighbor.distance < current_node.distance and neighbor.getNodeid() in current_node.neighbors:
                    min_distance = min_distance + neighbor.distance
                    min_neighbor = neighbor

            if current_node in neighbors:
                neighbors.remove(current_node)

            current_node = min_neighbor
            shortest_path.add(current_node)

            if current_node.getNodeid() in start_point.neighbors:
                break

        #shortest_path.add(end_point)
        l = []
        for node in shortest_path:

            l.append(node.getNodeid())
        print(l)
        return shortest_path

    except AttributeError:
        print("An error occured")
        return None



def djikstra(graph, start_point, end_point):
    start_point.is_visited = True
    start_point.distance = 0
    visited_nodes_in_order, end_point_Found = visitNeighbors(start_point, graph, end_point)
    i = 0
    while i < len(visited_nodes_in_order) and not end_point_Found:
        new_neighbors, end_point_Found = visitNeighbors(visited_nodes_in_order[i], graph, end_point)
        visited_nodes_in_order = visited_nodes_in_order + new_neighbors
        i += 1


    #l = []
    #for node in visited_nodes_in_order:
     #   l.append(node.getNodeid())
      #  print(l)
    #for node in visited_nodes_in_order:
    #    print(node.distance)

    return visited_nodes_in_order


nodes = []
nodes_dict = dict()
for col in range(0, 5):
    for rows in range(0, 5):
        node = Node(col, rows)

        nodes_dict[str(node.column) + '-' + str(node.row)] = node

# Fill the neighbors list for every node
for col in range(0, 5):
    for row in range(0, 5):
        # current node id is the col - row
        key = str(col) + '-' + str(row)
        current_node = nodes_dict[key]
        # print("Current Node " + str(key))
        # dict ids of all possible neighbor locations
        possible_neighbors = [str(col - 1) + "-" + str(row), str(col) + "-" + str(row - 1),
                              str(col) + "-" + str(row + 1), str(col + 1) + "-" + str(row),
                              ]
        for key2 in possible_neighbors:

            # check if a node with that id exists if it does proceed to add it to our current_nodes neighbors.+
            if key2 in nodes_dict:
                current_node.neighbors.append(key2)
    # print(current_node.getNodeid())
    # print(current_node.neighbors)
#neighbors = djikstra(nodes_dict, nodes_dict['0-0'], nodes_dict['3-2'])
#print(neighbors)
# print(nodes_dict["0-0"])
# print(nodes_dict["2-2"])
#print(findShortestPath(nodes_dict['0-0'], nodes_dict['3-2'], nodes_dict, neighbors))
