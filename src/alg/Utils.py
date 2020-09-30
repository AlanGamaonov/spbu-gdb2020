from pygraphblas import *
from classes.Graph import Graph
from statistics import fmean
import timeit


class Utils:
    @staticmethod
    def get_transitive_closure_adj_matrix(graph):
        result = Matrix.sparse(BOOL, graph.vertices_count, graph.vertices_count)

        for label in graph.label_matrices:
            result = result + graph.label_matrices[label]

        adj = result.dup()
        for k in range(graph.vertices_count):
            nvals = result.nvals
            result += adj @ result
            if nvals == result.nvals:
                break

        return result

    @staticmethod
    def get_transitive_closure_squaring(graph):
        result = Matrix.sparse(BOOL, graph.vertices_count, graph.vertices_count)

        for label in graph.label_matrices:
            result = result + graph.label_matrices[label]

        for k in range(graph.vertices_count):
            nvals = result.nvals
            result += result @ result
            if nvals == result.nvals:
                break

        return result

    @staticmethod
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

    # just for uniformity
    @staticmethod
    def get_total_reachability(graph):
        return Utils.get_transitive_closure_squaring(graph)

    @staticmethod
    def get_reachability_from_set(graph, set):
        result = Utils.get_transitive_closure_squaring(graph)

        for i in range(graph.vertices_count):
            if i not in set:
                result.assign_row(i, Vector.sparse(BOOL, graph.vertices_count).full(0))

        return result

    @staticmethod
    def get_reachability_from_set_to_set(graph, set_from, set_to):
        result = Utils.get_transitive_closure_squaring(graph)

        for i in range(graph.vertices_count):
            if i not in set_from:
                result.assign_row(i, Vector.sparse(BOOL, graph.vertices_count).full(0))
            if i not in set_to:
                result.assign_col(i, Vector.sparse(BOOL, graph.vertices_count).full(0))

        return result

    @staticmethod
    def print_label_matrices(graph):
        for label in graph.label_matrices:
            print(label + ' = ' + str(graph.label_matrices[label].nvals))

    @staticmethod
    def measure_transitive_closure(iterations_num):
        adj = timeit.repeat("Utils.get_transitive_closure_adj_matrix(intersection)",
                            setup="from __main__ import Utils, intersection",
                            repeat=iterations_num,
                            number=1)
        sqr = timeit.repeat("Utils.get_transitive_closure_squaring(intersection)",
                            setup="from __main__ import Utils, intersection",
                            repeat=iterations_num,
                            number=1)
        average_adj = round(fmean(adj), 6)
        average_sqr = round(fmean(sqr), 6)

        result = str(average_adj) + '   ' + str(average_sqr)
        return result

    @staticmethod
    def measure_intersection(iterations_num):
        intersection = timeit.repeat("Utils.get_intersection(graph, automaton)",
                                     setup="from __main__ import Utils, graph, automaton",
                                     repeat=iterations_num,
                                     number=1)
        average = round(fmean(intersection), 6)

        result = str(average)
        return result

    @staticmethod
    def measure_print(iterations_num):
        pr = timeit.repeat("Utils.print_label_matrices(intersection)",
                           setup="from __main__ import Utils, intersection",
                           repeat=iterations_num,
                           number=1)
        average = round(fmean(pr), 6)

        result = str(average)
        return result
