class Node():

    is_visited = False
    is_start = False
    is_end = False
    is_Wall = False
    distance = "inf"

    def __init__(self, column, row):
        self.column = column
        self.row = row
        self.is_visited = False
        self.is_start = False
        self.is_end = False
        self.is_wall = False
        self.distance = "infinity"
        self.neighbors = []
        self.predecessor = {}

    def set_is_start(self, is_start):
        self.is_start = is_start

    def getNodeid(self):
        return str(self.column) + "-" + str(self.row)

    def draw(self):

        return "<div class='cell' id='"+str(self.column)+"-"+str(self.row)+"' ></div>"
