from classes.Graph import Graph
from alg import intersection_and_reachability
from pygraphblas import *


def test_intersection_and_reachability():
    graph = Graph()
    graph.read_graph_from_file("tests/hw2_test_graph.txt")

    aut = Graph()
    aut.parse_regex("tests/hw2_test_regex.txt")
