import heapq
import itertools
from collections import deque
from Algorithms.Registry import Registry
from Graph import GraphView


# Every path finding algorithm is a PathFinder subclass with a display name, which registers it automatically.
# Subclasses implement search(): it appends node ids to self.visited in the order they are visited (again if a node
# is updated later), records in self.previous the node each one was reached from, and returns whether the end node
# was reached. The cost of moving into a node is its weight, graph.cost(). Most algorithms need weights of at least 1
# (A* even for its heuristic), the ones that don't lower min_weight.
# Usage: visited, paths = PathFinder.get("A* Search")(graph, start_id, end_id).run()
class PathFinder(Registry):
    kind = "path finding algorithm"
    min_weight = 1

    def __init__(self, graph, start_id, end_id, params=None):
        for node_id in (start_id, end_id):
            graph.getNode(node_id)
        if graph.minWeight() < self.min_weight:
            others = [name for name, cls in self.registry.items() if cls.min_weight <= graph.minWeight()]
            raise ValueError(self.name + " needs weights of at least " + str(self.min_weight) + ", use " +
                             " or ".join(others))
        self.setParams(params)
        self.graph = graph
        self.start = start_id
        self.end = end_id
        self.visited = []
        self.previous = {start_id: None}
        # nodes of a negative cycle (when going around it lowers the cost forever there is no cheapest path)
        self.negative_cycle = []

    def search(self):
        raise NotImplementedError

    # walks back from the end node to the start node
    def findPath(self):
        path = [self.end]
        while path[-1] != self.start:
            path.append(self.previous[path[-1]])
        return path[::-1]

    # the paths that were found, cheapest first
    def findPaths(self):
        return [self.findPath()]

    # returns the visited node ids in order and the paths from start to end (none if the end can't be reached)
    def run(self):
        found = self.search()
        return self.visited, self.findPaths() if found else []


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
                new_distance = distance[node_id] + self.graph.cost(node_id, neighbor)
                if neighbor not in seen and new_distance < distance.get(neighbor, float('inf')):
                    distance[neighbor] = new_distance
                    self.previous[neighbor] = node_id
                    heapq.heappush(frontier, (self.priority(neighbor, new_distance), next(order), neighbor))
        return False


# Visits the nodes with the cheapest path from the start first, so it finds a cheapest path.
class Dijkstra(PriorityFirstSearch):
    name = "Dijkstra"

    def priority(self, node_id, distance):
        return distance


# Dijkstra guided towards the end by the Manhattan distance. Still finds a cheapest path, visiting far fewer nodes.
class AStarSearch(PriorityFirstSearch):
    name = "A* Search"

    def priority(self, node_id, distance):
        remaining = self.graph.distance(node_id, self.end)
        # on ties prefer the node closer to the end
        return distance + remaining, remaining


# Only looks at the Manhattan distance to the end. Fast, but its path is often not the cheapest.
class GreedyBestFirstSearch(PriorityFirstSearch):
    name = "Greedy Best-First Search"

    def priority(self, node_id, distance):
        return self.graph.distance(node_id, self.end)


# Runs Dijkstra from the start and backwards from the end at the same time, and stops once no path through the nodes
# both searches still have to visit can be cheaper than the cheapest path where they met. Two small searches visit
# far fewer nodes than one big one, unless the points are so far apart that both searches fill the grid anyway.
class BidirectionalDijkstra(PathFinder):
    name = "Bidirectional Dijkstra"

    def search(self):
        self.next = {self.end: None}
        self.meeting = self.start
        if self.start == self.end:
            self.visited.append(self.start)
            return True
        # for the forward and the backward search: distances, pointers, frontier, visited nodes, cost of a step
        searches = [({self.start: 0}, self.previous, [(0, self.start)], set(), self.graph.cost),
                    ({self.end: 0}, self.next, [(0, self.end)], set(), self.backwardCost)]
        best = float('inf')
        side = 0
        while searches[0][2] and searches[1][2] and searches[0][2][0][0] + searches[1][2][0][0] < best:
            distance, pointers, frontier, seen, cost = searches[side]
            other_distance = searches[1 - side][0]
            node_distance, node_id = heapq.heappop(frontier)
            if node_id not in seen:
                seen.add(node_id)
                self.visited.append(node_id)
                for neighbor in self.graph.openNeighbors(node_id):
                    new_distance = node_distance + cost(node_id, neighbor)
                    if new_distance < distance.get(neighbor, float('inf')):
                        distance[neighbor] = new_distance
                        pointers[neighbor] = node_id
                        heapq.heappush(frontier, (new_distance, neighbor))
                    if neighbor in other_distance and distance[neighbor] + other_distance[neighbor] < best:
                        best = distance[neighbor] + other_distance[neighbor]
                        self.meeting = neighbor
            side = 1 - side
        return best < float('inf')

    # stepping backwards from a node to a neighbor costs what moving from the neighbor to the node costs
    def backwardCost(self, node_id, neighbor):
        return self.graph.cost(neighbor, node_id)

    # from the start to the meeting node with the forward pointers, then to the end with the backward ones
    def findPath(self):
        path = [self.meeting]
        while path[-1] != self.start:
            path.append(self.previous[path[-1]])
        path.reverse()
        while path[-1] != self.end:
            path.append(self.next[path[-1]])
        return path


# Finds the cheapest paths without repeated nodes, not only the cheapest one. Every next path branches off a path found
# before: for every node of the last path it finds (with A*) the cheapest way to the end that avoids the part of the
# path before that node and the branches already taken from there, and the cheapest of those becomes the next path.
class YensKShortestPaths(PathFinder):
    name = "Yen's K Shortest Paths"
    params = {'paths': 3}
    MAX_PATHS = 10

    def __init__(self, graph, start_id, end_id, params=None):
        super().__init__(graph, start_id, end_id, params)
        if self.paths != int(self.paths) or not 1 <= self.paths <= self.MAX_PATHS:
            raise ValueError("'paths' must be a whole number from 1 to " + str(self.MAX_PATHS))
        self.paths = int(self.paths)
        self.found_paths = []
        self.seen = set()

    # cheapest path from node_id to the end avoiding the blocked nodes and edges, None if there is none
    def cheapestPath(self, node_id, blocked_nodes=(), blocked_edges=()):
        visited, paths = AStarSearch(GraphView(self.graph, blocked_nodes, blocked_edges), node_id, self.end).run()
        for visited_id in visited:
            if visited_id not in self.seen:
                self.seen.add(visited_id)
                self.visited.append(visited_id)
        return paths[0] if paths else None

    def search(self):
        path = self.cheapestPath(self.start)
        if path is None:
            return False
        self.found_paths.append(path)
        candidates, order, seen_candidates = [], itertools.count(), {tuple(path)}
        while len(self.found_paths) < self.paths:
            last_path = self.found_paths[-1]
            for i in range(len(last_path) - 1):
                root = last_path[:i + 1]
                taken = {(path[i], path[i + 1]) for path in self.found_paths if path[:i + 1] == root}
                branch = self.cheapestPath(last_path[i], root[:-1], taken)
                if branch is not None and tuple(root[:-1] + branch) not in seen_candidates:
                    candidate = root[:-1] + branch
                    seen_candidates.add(tuple(candidate))
                    heapq.heappush(candidates, (self.graph.pathCost(candidate), next(order), candidate))
            if not candidates:
                break
            self.found_paths.append(heapq.heappop(candidates)[2])
        return True

    def findPaths(self):
        return self.found_paths


# Relaxes the edges pass after pass until no distance improves: after pass k every cheapest path with at most k steps
# is known. It can't stop at the end node, since a later pass may still find a cheaper way there, so it is slower
# than Dijkstra, but it also works with negative weights. If going around a cycle lowers the cost (a negative cycle),
# there is no cheapest path and the distances would improve forever, so it stops as soon as the previous pointers
# form a cycle, which happens only for a negative cycle.
class BellmanFord(PathFinder):
    name = "Bellman-Ford"
    min_weight = float('-inf')

    def search(self):
        distance = {self.start: 0}
        changed = [self.start]
        self.visited.append(self.start)
        while changed:
            # only the edges out of the nodes improved by the last pass can improve anything, and they are relaxed
            # with the distances from before this pass
            sources = [(node_id, distance[node_id]) for node_id in changed]
            changed = []
            for node_id, node_distance in sources:
                for neighbor in self.graph.openNeighbors(node_id):
                    new_distance = node_distance + self.graph.cost(node_id, neighbor)
                    if new_distance < distance.get(neighbor, float('inf')):
                        distance[neighbor] = new_distance
                        self.previous[neighbor] = node_id
                        changed.append(neighbor)
            changed = list(dict.fromkeys(changed))
            self.visited.extend(changed)
            self.negative_cycle = self.findCycle(changed)
            if self.negative_cycle:
                return False
        return self.end in distance

    # a cycle in the previous pointers through one of the changed nodes, in walking order, or [] if there is none
    def findCycle(self, changed):
        done = set()
        for node_id in changed:
            walk = {}  # node id -> position in this walk back through the previous pointers
            while node_id is not None and node_id not in done:
                if node_id in walk:
                    cycle = [key for key, position in walk.items() if position >= walk[node_id]]
                    return cycle[::-1]
                walk[node_id] = len(walk)
                node_id = self.previous[node_id]
            done.update(walk)
        return []


# Visits the nodes in rings of increasing steps from the start. Ignores the weights: its path has the fewest steps.
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


# Goes as deep as it can in one direction before backtracking. Ignores the weights, its path is usually long.
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
