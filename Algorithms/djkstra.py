import pprint, json
from collections import deque
from Node import *


# follows a BFS logic
def visitNeighbors(node: Node, graph, end_point):
    visited_nodes = []
    end_point_Found = False
    for neighbor_id in node.neighbors:

        neighbor = graph[neighbor_id]
        # print(neighbor.getNodeid())

        if neighbor_id == end_point.getNodeid():
            visited_nodes.append(neighbor)
            end_point.distance = node.distance + 1

            end_point_Found = True
            break
        if not neighbor.is_wall and not neighbor.is_visited:
            neighbor.distance = node.distance + 1
            neighbor.is_visited = True
            visited_nodes.append(neighbor)
        # give a large distance so that the node is inaccessible
        if neighbor.is_wall:
            neighbor.distance = 999999999

    return visited_nodes, end_point_Found


def djikstra(graph, start_point, end_point):

    traped = False
    start_point.is_visited = True
    start_point.distance = 0
    visited_nodes_in_order, end_point_Found = visitNeighbors(start_point, graph, end_point)

    # visit the nodes and save the order in which they were visited while we havent found the end point and
    # i has'nt surpassed the number of nodes
    i = 0
    while i < len(visited_nodes_in_order) and not end_point_Found:
        new_neighbors, end_point_Found = visitNeighbors(visited_nodes_in_order[i], graph, end_point)

        visited_nodes_in_order = visited_nodes_in_order + new_neighbors

        i += 1

    if not end_point_Found:
        traped = True

    return visited_nodes_in_order, traped


def findShortestPath(start_point: Node, end_point: Node, graph, neighbors):
    shortest_path = []

    current_node: Node = end_point

    min_distance = current_node.distance
    min_neighbor = None

    # check if our current node has a neighbor node with lesser distance from the start point if there is such a
    # neighbor and that neighbor is also in the list with neighbors from djikstra algo (neighbors) its the
    # min_neighbor and it becomes the next current_node. The previous current_node is removed from our neighbors
    # list. if at some point we reach a node that is a neighbor of our start_point this means that its the closest
    # one distance wise And we break the loop.Its time we add to our shortest path the min_neighbor we find.

    try:
        while True:

            for neighbor in neighbors:

                if neighbor.distance == "infinity" or current_node.distance == "infinity":
                    continue
                if neighbor.distance < current_node.distance and neighbor.getNodeid() in current_node.neighbors and not neighbor.is_wall:
                    min_distance = min_distance + neighbor.distance
                    min_neighbor = neighbor

            if current_node in neighbors:
                neighbors.remove(current_node)

            current_node = min_neighbor

            shortest_path.append(current_node)

            if current_node.getNodeid() in start_point.neighbors:
                break
        return shortest_path

    except AttributeError:
        print("An error occured.The walls probably traped the start point!")
        return None


def addWalls(walls_id: list, graph):
    for node_id in walls_id:
        graph[node_id].is_wall = True
