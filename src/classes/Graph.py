from pygraphblas.matrix import Matrix
from pygraphblas.types import BOOL
from pyformlang.regular_expression import Regex


class Graph:
    def __init__(self):
        self.vertices_count = 0
        self.label_matrices = dict()
        self.start_vertices = set()
        self.terminal_vertices = set()

    def read_graph_from_file(self, file_path):
        self.__init__()
        # read graph from file
        graph_file = open(file_path, 'r')
        edges = graph_file.read().rstrip().split('\n')
        graph_file.close()

        # get vertices count
        max_vertex = 0
        for edge in edges:
            start, label, end = edge.split(' ')
            max_vertex = max([max_vertex, int(start), int(end)])
        self.vertices_count = max_vertex + 1

        # init label_matrices
        for edge in edges:
            i, label, j = edge.split(" ")
            if label in self.label_matrices:
                self.label_matrices[label][int(i), int(j)] = True
            else:
                bool_matrix = Matrix.sparse(BOOL, self.vertices_count, self.vertices_count)
                bool_matrix[int(i), int(j)] = True
                self.label_matrices[label] = bool_matrix

        # init start and terminal vertices
        for i in range(self.vertices_count):
            self.start_vertices.add(i)
            self.terminal_vertices.add(i)

    def parse_regex(self, file_path):
        self.__init__()
        # read regex from file
        regex_file = open(file_path, 'r')
        regex = Regex(regex_file.read().rstrip())
        regex_file.close()

        # regex to dfa conversion and vertices count init
        dfa = regex.to_epsilon_nfa().to_deterministic().minimize()
        self.vertices_count = len(dfa.states)

        # states enumeration
        states = {}
        start = 0
        for state in dfa._states:
            if state not in states:
                states[state] = start
                start = start + 1

        # init label_matrices
        for start in dfa._states:
            for label in dfa._input_symbols:
                in_states = dfa._transition_function(start, label)
                for end in in_states:
                    if label in self.label_matrices:
                        self.label_matrices[label][states[start], states[end]] = True
                    else:
                        bool_matrix = Matrix.sparse(BOOL, self.vertices_count, self.vertices_count)
                        bool_matrix[states[start], states[end]] = True
                        self.label_matrices[label] = bool_matrix

        # init start and terminal states
        self.start_vertices.add(states[dfa.start_state])
        for state in dfa._final_states:
            self.terminal_vertices.add(states[state])
        return self
