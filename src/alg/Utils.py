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
    def cfpq_mxm(graph: Graph, grammar: CFG):
        res = dict()
        terminal_prods = set()
        nonterminal_prods = set()

        if grammar.generate_epsilon():
            matrix = Matrix.sparse(
                BOOL, graph.vertices_count, graph.vertices_count)
            for i in range(graph.vertices_count):
                matrix[i, i] = True
            res[grammar.start_symbol] = matrix

        cfg = grammar.to_normal_form()

        for prod in cfg.productions:
            if len(prod.body) == 1:
                terminal_prods.add(prod)
            else:
                nonterminal_prods.add(prod)

        for t, matrix in graph.label_matrices.items():
            for prod in terminal_prods:
                if prod.body == [Terminal(t)]:
                    if prod.head not in res:
                        res[prod.head] = matrix.dup()
                    else:
                        res[prod.head] += matrix.dup()

        old_changed = set()
        new_changed = cfg.variables

        while len(new_changed) > 0:
            old_changed = new_changed
            new_changed = set()

            for prod in nonterminal_prods:
                if prod.body[0] not in res or prod.body[1] not in res:
                    continue

                if (
                        prod.body[0] in old_changed
                        or prod.body[1] in old_changed
                ):
                    matrix = res.get(prod.head, Matrix.sparse(
                        BOOL, graph.vertices_count, graph.vertices_count))
                    old_nvals = matrix.nvals
                    res[prod.head] = matrix + \
                                     (res[prod.body[0]] @ res[prod.body[1]])

                    if res[prod.head].nvals != old_nvals:
                        new_changed.add(prod.head)

        return res.get(cfg.start_symbol, Matrix.sparse(
            BOOL, graph.vertices_count, graph.vertices_count))

    @staticmethod
    def cfpq_bool_matrix_product(graph, grammar: CFG):
        if graph.vertices_count == 0:
            return False

        result = Graph()
        result.vertices_count = graph.vertices_count

        complex_productions = []

        for production in grammar.productions:
            if len(production.body) == 1:
                if production.head not in result.label_matrices.keys():
                    result.label_matrices[production.head] = Matrix.sparse(BOOL, result.vertices_count, result.vertices_count)
                result.label_matrices[production.head] += graph.label_matrices[production.body[0].value]
            elif len(production.body) == 2:
                complex_productions.append(production)

        if grammar.generate_epsilon():
            if grammar.start_symbol not in result.label_matrices.keys():
                result.label_matrices[grammar.start_symbol] = Matrix.sparse(BOOL, result.vertices_count, result.vertices_count)
            result.label_matrices[grammar.start_symbol] += Matrix.identity(BOOL, result.vertices_count)

        changed = True
        while changed:
            changed = False
            for production in complex_productions:
                old = result.label_matrices[production.head].nvals
                result.label_matrices[production.head] += \
                    result.label_matrices[production.body[0]] @ result.label_matrices[production.body[1]]
                new = result.label_matrices[production.head].nvals
                changed |= not old == new

        return set(zip(*result.label_matrices[grammar.start_symbol].to_lists()[:2]))

    @staticmethod
    def cfpq_tensor(graph: Graph, grammar: CFG):
        res = graph.get_copy()

        rfa = Graph()
        rfa_heads = dict()

        rfa.vertices_count = sum(
            [len(prod.body) + 1 for prod in grammar.productions])
        rfa.states = set(range(rfa.vertices_count))
        index = 0
        for prod in grammar.productions:
            start_state = index
            final_state = index + len(prod.body)

            rfa.start_vertices.add(start_state)
            rfa.terminal_vertices.add(final_state)
            rfa_heads[(start_state, final_state)] = prod.head.value

            for var in prod.body:
                matrix = rfa.label_matrices.get(var.value, Matrix.sparse(
                    BOOL, rfa.vertices_count, rfa.vertices_count))

                matrix[index, index + 1] = True
                rfa.label_matrices[var.value] = matrix
                index += 1

            index += 1

        for prod in grammar.productions:
            if len(prod.body) == 0:
                matrix = Matrix.sparse(
                    BOOL, graph.vertices_count, graph.vertices_count)

                for i in range(graph.vertices_count):
                    matrix[i, i] = True

                res.matrices[prod.head] = matrix

        is_changing = True
        while is_changing:
            is_changing = False
            intersection = Utils.get_intersection(rfa, res)
            closure = Utils.get_transitive_closure_squaring(intersection)

            for i, j, _ in zip(*closure.to_lists()):
                rfa_from, rfa_to = i // res.vertices_count, j // res.vertices_count
                graph_from, graph_to = i % res.vertices_count, j % res.vertices_count

                if (rfa_from, rfa_to) not in rfa_heads:
                    continue

                var = rfa_heads[(rfa_from, rfa_to)]

                matrix = res.label_matrices.get(var, Matrix.sparse(
                    BOOL, graph.vertices_count, graph.vertices_count))

                if matrix.get(graph_from, graph_to) is None:
                    is_changing = True
                    matrix[graph_from, graph_to] = True
                    res.label_matrices[var] = matrix

        return res.label_matrices.get(grammar.start_symbol, Matrix.sparse(
            BOOL, graph.vertices_count, graph.vertices_count))

    @staticmethod
    def get_rfa_from_grammar(grammar: CFG):
        rfa = Graph()
        size = 0
        heads = {}

        for production in grammar.productions:
            if len(production.body) > 0:
                size += len(production.body) + 1
        rfa.vertices_count = size

        vertex = 0
        for production in grammar.productions:
            if len(production.body) > 0:
                rfa.start_vertices.add(vertex)

                for i in range(len(production.body)):
                    key = list(production.body)[i].value
                    if key not in rfa.label_matrices.keys():
                        rfa.label_matrices[key] = Matrix.sparse(BOOL, rfa.vertices_count, rfa.vertices_count)

                    rfa.label_matrices[key][vertex, vertex + 1] = True
                    vertex += 1

                rfa.terminal_vertices.add(vertex)
                heads[vertex - len(production.body), vertex] = production.head.value
                vertex += 1

        return rfa, heads

    @staticmethod
    def cfpq_tensor_product(graph, grammar: CFG):
        result = graph.get_copy()
        result.label_matrices[grammar.start_symbol] = Matrix.sparse(BOOL, result.vertices_count, result.vertices_count)

        if grammar.generate_epsilon():
            result.label_matrices[grammar.start_symbol] += Matrix.identity(BOOL, result.vertices_count)

        rfa, rfa_heads = Utils.get_rfa_from_grammar(grammar)

        intersection = Utils.get_intersection(result, rfa)
        closure = Utils.get_transitive_closure_squaring(intersection)

        changed = True
        while changed:
            last_nvals = closure.nvals
            for i in range(intersection.vertices_count):
                for j in range(intersection.vertices_count):
                    if (i, j) in closure:
                        start_state = i % rfa.vertices_count
                        terminal_state = j % rfa.vertices_count
                        if (start_state in rfa.start_vertices) and (terminal_state in rfa.terminal_vertices):
                            a = i // rfa.vertices_count
                            b = j // rfa.vertices_count

                            key = rfa_heads[(start_state, terminal_state)]
                            if key not in result.label_matrices.keys():
                                result.label_matrices[key] = Matrix.sparse(BOOL, result.vertices_count, result.vertices_count)
                            result.label_matrices[key][a, b] = True

            intersection = Utils.get_intersection(result, rfa)
            closure = Utils.get_transitive_closure_squaring(intersection)

            if closure.nvals == last_nvals:
                changed = False

        return result.label_matrices[grammar.start_symbol]

    @staticmethod
    def get_cnf_from_grammar(cfg):
        if cfg.generate_epsilon():
            cfg = cfg.to_normal_form()
            new_start_symbol = Variable(cfg.start_symbol.value + "'")
            cfg.productions.add(Production(new_start_symbol, []))
            res = CFG(variables=cfg.variables,
                      terminals=cfg.terminals,
                      start_symbol=new_start_symbol)
            res.variables.add(new_start_symbol)
            for production in cfg.productions:
                if production.head == cfg.start_symbol:
                    res.productions.add(Production(new_start_symbol, production.body))
                res.productions.add(production)
            return res
        else:
            return cfg.to_normal_form()
