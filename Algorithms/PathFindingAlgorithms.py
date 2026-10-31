import heapq
import itertools
from collections import deque


# Every path finding algorithm is a PathFinder subclass with a display name, which registers it automatically.
# Subclasses implement search(): it appends node ids to self.visited in the order they are visited, records in
# self.previous the node each one was reached from, and returns True once the end node is visited.
# Usage: visited, path = PathFinder.get("A* Search")(graph, start_id, end_id).run()
class PathFinder:
    registry = {}
    name = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.name:
            PathFinder.registry[cls.name] = cls

    @classmethod
    def get(cls, name):
        if name not in cls.registry:
            raise ValueError("Unknown path finding algorithm: " + str(name))
        return cls.registry[name]

    def __init__(self, graph, start_id, end_id):
        for node_id in (start_id, end_id):
            graph.getNode(node_id)
        self.graph = graph
        self.start = start_id
        self.end = end_id
        self.visited = []
        self.previous = {start_id: None}

    def search(self):
        raise NotImplementedError

    # walks back from the end node to the start node
    def findPath(self):
        path = [self.end]
        while path[-1] != self.start:
            path.append(self.previous[path[-1]])
        return path[::-1]

    # returns the visited node ids in order and the path from start to end (empty if the end can't be reached)
    def run(self):
        found = self.search()
        return self.visited, self.findPath() if found else []


# Always visits the frontier node with the lowest priority(). Subclasses only define the priority.
class PriorityFirstSearch(PathFinder):

    def priority(self, node_id, distance):
        raise NotImplementedError

    def search(self):
        distance = {self.start: 0}
        order = itertools.count()  # breaks priority ties in insertion order
        frontier = [(self.priority(self.start, 0), next(order), self.start)]
        seen = set()
        while frontier:
            node_id = heapq.heappop(frontier)[2]
            if node_id in seen:
                continue
            seen.add(node_id)
            self.visited.append(node_id)
            if node_id == self.end:
                return True
            for neighbor in self.graph.openNeighbors(node_id):
                new_distance = distance[node_id] + 1
                if neighbor not in seen and new_distance < distance.get(neighbor, float('inf')):
                    distance[neighbor] = new_distance
                    self.previous[neighbor] = node_id
                    heapq.heappush(frontier, (self.priority(neighbor, new_distance), next(order), neighbor))
        return False


# Visits the nodes closest to the start first. Every step costs 1 on this grid, so it finds a shortest path.
class Dijkstra(PriorityFirstSearch):
    name = "Dijkstra"

    def priority(self, node_id, distance):
        return distance


# Dijkstra guided towards the end by the Manhattan distance. Still finds a shortest path, visiting far fewer nodes.
class AStarSearch(PriorityFirstSearch):
    name = "A* Search"

    def priority(self, node_id, distance):
        remaining = self.graph.distance(node_id, self.end)
        # on ties prefer the node closer to the end
        return distance + remaining, remaining


# Only looks at the Manhattan distance to the end. Fast, but its path is not always the shortest.
class GreedyBestFirstSearch(PriorityFirstSearch):
    name = "Greedy Best-First Search"

    def priority(self, node_id, distance):
        return self.graph.distance(node_id, self.end)


# Visits the nodes in rings of increasing distance from the start, so its path is a shortest one.
class BreadthFirstSearch(PathFinder):
    name = "Breadth-First Search"

    def search(self):
        queue = deque([self.start])
        while queue:
            node_id = queue.popleft()
            self.visited.append(node_id)
            if node_id == self.end:
                return True
            for neighbor in self.graph.openNeighbors(node_id):
                if neighbor not in self.previous:
                    self.previous[neighbor] = node_id
                    queue.append(neighbor)
        return False


# Goes as deep as it can in one direction before backtracking, so its path is usually far from the shortest.
class DepthFirstSearch(PathFinder):
    name = "Depth-First Search"

    def search(self):
        stack = [self.start]
        seen = set()
        while stack:
            node_id = stack.pop()
            if node_id in seen:
                continue
            seen.add(node_id)
            self.visited.append(node_id)
            if node_id == self.end:
                return True
            # pushed in reverse so that the first neighbor is explored first
            for neighbor in reversed(self.graph.openNeighbors(node_id)):
                if neighbor not in seen:
                    self.previous[neighbor] = node_id
                    stack.append(neighbor)
        return False
