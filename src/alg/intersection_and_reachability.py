from pygraphblas.matrix import Matrix
from pygraphblas.types import BOOL
from src.classes.Graph import Graph

def get_transitive_closure(graph):
    matrix = Matrix.sparse(BOOL, graph.vertices_count, graph.vertices_count)

    for label_matrix in graph.label_matrices.values():
            matrix = matrix | label_matrix

    for k in range(graph.vertices_count):
            matrix += matrix @ matrix

    return matrix
#end of get_transitive_closure


def get_intersection(graph1, graph2):
    result = Graph()
    result.vertices_count = graph1.vertices_count * graph2.vertices_count

    for i in graph1.start_vertices:
        for j in graph2.start_vertices:
            result.start_vertices.add(i * graph1.vertices_count + j)

    for i in graph1.terminal_vertices:
        for j in graph2.terminal_vertices:
            result.terminal_vertices.add(i * graph1.vertices_count + j)

    for label in graph1.label_matrices.keys():
        if label in graph2.label_matrices.keys():
            result.label_matrices[label] = graph1.label_matrices[label].kronecker(graph2.label_matrices[label])

    return result
#end of get_intersection


#just for uniformity
def get_total_reachability(graph):
    return get_transitive_closure(graph)
#end of get_total_reachability


def get_reachability_from_set(graph, set):
    result = get_transitive_closure(graph)

    for i in range(graph.vertices_count):
        if i not in set:
            result.assign_row(i, Vector.sparse(BOOL, graph.vertices_count).full(0))

    return result
#end of get_reachability_from_set


def get_reachability_from_set_to_set(graph, set_from, set_to):
    result = get_transitive_closure(graph)

    for i in range(graph.vertices_count):
        if i not in set_from:
            res.assign_row(i, Vector.sparse(BOOL, graph.vertices_count).full(0))
        if i not in set_to:
            res.assign_col(i, Vector.sparse(BOOL, graph.vertices_count).full(0))

    return result
#end of get_reachability_from_set_to_set
