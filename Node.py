class Node:

    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.is_wall = False
        # cost of moving into this node
        self.weight = 1
        # ids of the adjacent nodes (up, left, right, down), filled in by the Graph
        self.neighbors = []

    def getNodeid(self):
        return str(self.row) + "-" + str(self.column)

    def draw(self):
        return "<div class='cell' id='" + self.getNodeid() + "'></div>"
