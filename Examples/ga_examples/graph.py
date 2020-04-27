from itertools import permutations
from core.agent import Agent

class Node:
    def __init__(self, value):
        self.children = []
        self.parent = None
        self.value = value

class Graph:
    def __init__(self, vertices):
        self.root = None
        self.vertices = vertices
        self.edges = []


    def minimum_spanning_tree(self):
        #make a dictionary of all the possible edges and their lengths
        all_edges = set(map(frozenset, list(permutations(self.vertices, 2))))
        distances = [x[0].distanceTo(x[1]) for x in all_edges]
        edge_data = list(zip(all_edges, distances))
        edge_data.sort(key=lambda x: x[1])
        print(edge_data)
        #sort the possible edges by length


        #make a dictionary of the edges to if it is onn or off
        edges_in_use = dict.fromkeys(all_edges, 0)
        #make a list of all verticies already in the graph
        vertices_in_graph = []

        for edge in all_edges:
            if edge[0] not in vertices_in_graph and edge[1] not in vertices_in_graph:
                edges_in_use[edge] = 1

        #I now have a list of all the edges in the graph that make up the minimum spanning tree
        return edges_in_use



