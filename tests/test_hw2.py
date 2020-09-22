import main
from pygraphblas import *


def test_intersection_and_reachability():
    graph = main.Graph()
    aut = main.Graph()

    graph.read_graph_from_file("tests/hw2_test_graph2.txt")
    aut.parse_regex("tests/hw2_test_regex2.txt")
    intersection = main.Utils.get_intersection(graph, aut)
    reachability_matrix = main.Utils.get_total_reachability(intersection)
    assert graph.label_matrices["mama"] == intersection.label_matrices["mama"]
    assert reachability_matrix == Matrix.dense(BOOL, 5, 5).full(True)

    graph.read_graph_from_file("tests/hw2_test_graph1.txt")
    aut.parse_regex("tests/hw2_test_regex1.txt")
    intersection = main.Utils.get_intersection(aut, graph)
    assert intersection.vertices_count == 35
