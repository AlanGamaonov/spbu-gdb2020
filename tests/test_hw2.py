from src.classes.Graph import Graph
from src.alg.intersection_and_reachability import *
from pygraphblas import *


def test_intersection_and_reachability():
    graph = Graph()
    aut = Graph()

    graph.read_graph_from_file("tests/hw2_test_graph2.txt")
    aut.parse_regex("tests/hw2_test_regex2.txt")
    intersection = get_intersection(graph, aut)
    matrix = get_total_reachability(intersection)
    assert graph.label_matrices["mama"] == intersection.label_matrices["mama"]
    assert matrix == Matrix.dense(BOOL, 5, 5).full(True)

    graph.read_graph_from_file("tests/hw2_test_graph1.txt")
    aut.parse_regex("tests/hw2_test_regex1.txt")
    intersection = get_intersection(aut, graph)
    assert intersection.vertices_count == 35
#end of test_intersection_and_reachability
