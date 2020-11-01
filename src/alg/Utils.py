from pygraphblas import *
from classes.Graph import Graph
from statistics import fmean
from pyformlang.cfg import CFG, Variable, Production, Terminal
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

    @staticmethod
    def read_grammar_from_file(file_path):
        productions = []

        with open(file_path, 'r') as file:
            for line in file:
                raw_current_production = line.split()
                # "S a S b S" to "S -> a S b S"
                current_production = raw_current_production[0] + ' -> ' + ' '.join(raw_current_production[1:])
                productions.append(current_production)

        productions = '\n'.join(productions)
        return CFG.from_text(productions)

    @staticmethod
    def cfpq_matrix_product(graph: Graph, grammar: CFG):
        if graph.vertices_count == 0:
            return False

        result = dict()
        terminal_productions = set()
        non_terminal_productions = set()

        if grammar.generate_epsilon():
            matrix = Matrix.sparse(BOOL, graph.vertices_count, graph.vertices_count)
            matrix += Matrix.identity(BOOL, graph.vertices_count)
            result[grammar.start_symbol] = matrix

        cfg = grammar.to_normal_form()

        for production in cfg.productions:
            if len(production.body) == 1:
                terminal_productions.add(production)
            else:
                non_terminal_productions.add(production)

        for t, matrix in graph.label_matrices.items():
            for production in terminal_productions:
                if production.body == [Terminal(t)]:
                    if production.head not in result:
                        result[production.head] = matrix.dup()
                    else:
                        result[production.head] += matrix.dup()

        old_changed = set()
        new_changed = cfg.variables

        while len(new_changed) > 0:
            old_changed = new_changed
            new_changed = set()

            for production in non_terminal_productions:
                if production.body[0] not in result or production.body[1] not in result:
                    continue

                if (
                        production.body[0] in old_changed
                        or production.body[1] in old_changed
                ):
                    matrix = result.get(production.head, Matrix.sparse(BOOL, graph.vertices_count, graph.vertices_count))
                    old_nvals = matrix.nvals
                    result[production.head] = matrix + (result[production.body[0]] @ result[production.body[1]])

                    if result[production.head].nvals != old_nvals:
                        new_changed.add(production.head)

        return result.get(cfg.start_symbol, Matrix.sparse(BOOL, graph.vertices_count, graph.vertices_count))

    @staticmethod
    def cfpq_tensor_product(graph: Graph, grammar: CFG):
        if graph.vertices_count == 0:
            return False

        result = graph.get_copy()

        rfa = Graph()
        rfa_heads = dict()

        rfa.vertices_count = sum([len(production.body) + 1 for production in grammar.productions])
        index = 0
        for production in grammar.productions:
            start_state = index
            terminal_state = index + len(production.body)

            rfa.start_vertices.add(start_state)
            rfa.terminal_vertices.add(terminal_state)
            rfa_heads[(start_state, terminal_state)] = production.head.value

            for variable in production.body:
                matrix = rfa.label_matrices.get(variable.value, Matrix.sparse(BOOL, rfa.vertices_count, rfa.vertices_count))
                matrix[index, index + 1] = True
                rfa.label_matrices[variable.value] = matrix
                index += 1

            index += 1

        for production in grammar.productions:
            if len(production.body) == 0:
                matrix = Matrix.sparse(BOOL, graph.vertices_count, graph.vertices_count)
                matrix += Matrix.identity(BOOL, graph.vertices_count)

                result.label_matrices[production.head] = matrix

        changed = True
        while changed:
            changed = False
            intersection = Utils.get_intersection(rfa, result)
            closure = Utils.get_transitive_closure_squaring(intersection)

            for i, j, _ in zip(*closure.to_lists()):
                rfa_from, rfa_to = i // result.vertices_count, j // result.vertices_count
                graph_from, graph_to = i % result.vertices_count, j % result.vertices_count

                if (rfa_from, rfa_to) not in rfa_heads:
                    continue

                variable = rfa_heads[(rfa_from, rfa_to)]

                matrix = result.label_matrices.get(variable, Matrix.sparse(BOOL, graph.vertices_count, graph.vertices_count))

                if matrix.get(graph_from, graph_to) is None:
                    changed = True
                    matrix[graph_from, graph_to] = True
                    result.label_matrices[variable] = matrix

        return result.label_matrices.get(grammar.start_symbol, Matrix.sparse(BOOL, graph.vertices_count, graph.vertices_count))
