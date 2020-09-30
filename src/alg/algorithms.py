from pygraphblas import Matrix, BOOL
from pyformlang.cfg import Terminal, CFG
from collections import deque


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


def CYK(grammar, word):
    size = len(word)
    if size == 0:
        return grammar.generate_epsilon()

    cfg = grammar.to_normal_form()
    matrix = [[set() for _ in range(size)] for _ in range(size)]

    for i in range(size):
        for production in cfg.productions:
            if production.body == [Terminal(word[i])]:
                matrix[i][i].add(production.head)

    for i in range(size):
        for j in range(size - i):
            for k in range(i):
                first, second = matrix[j][j + k], matrix[j + k + 1][j + i]
                for production in cfg.productions:
                    if (
                            len(production.body) == 2
                            and production.body[0] in first
                            and production.body[1] in second
                    ):
                        matrix[j][j + i].add(production.head)

    return cfg.start_symbol in matrix[0][size - 1]


def hellings(grammar, graph):
    if graph.vertices_count == 0:
        return False

    result = {}
    variables_deque = deque()

    if grammar.generate_epsilon():
        matrix = Matrix.sparse(BOOL, graph.vertices_count, graph.vertices_count)
        for i in range(graph.vertices_count):
            matrix[i, i] = True
            variables_deque.append((grammar.start_symbol, i, i))
        result[grammar.start_symbol] = matrix

    cfg = grammar.to_normal_form()

    for t, matrix in graph.label_matrices.items():
        for production in cfg.productions:
            if production.body == [Terminal(t)]:
                result[production.head] = matrix

    for variable, matrix in result.items():
        for i, j, _ in zip(*matrix.to_lists()):
            variables_deque.append((variable, i, j))

    while variables_deque:
        add_to_result = []
        variable, start, end = variables_deque.popleft()

        for new_variable, matrix in result.items():
            for new_start, _ in matrix[:, start]:
                for production in cfg.productions:
                    if (
                            len(production.body) == 2
                            and production.body[0] == new_variable
                            and production.body[1] == variable
                            and (
                                    production.head not in result
                                    or result[production.head].get(new_start, end) is None
                                )
                    ):
                        variables_deque.append((production.head, new_start, end))
                        add_to_result.append((production.head, new_start, end))

        for new_variable, matrix in result.items():
            for new_end, _ in matrix[end, :]:
                for production in cfg.productions:
                    if (
                            len(production.body) == 2
                            and production.body[0] == variable
                            and production.body[1] == new_variable
                            and (
                                    production.head not in result
                                    or result[production.head].get(start, new_end) is None
                                )
                    ):
                        variables_deque.append((production.head, start, new_end))
                        add_to_result.append((production.head, start, new_end))

        for variable, start, end in add_to_result:
            matrix = result.get(variable, Matrix.sparse(
                BOOL, graph.vertices_count, graph.vertices_count))
            matrix[start, end] = True
            result[variable] = matrix

    return result.get(cfg.start_symbol, Matrix.sparse(BOOL, graph.vertices_count, graph.vertices_count))
