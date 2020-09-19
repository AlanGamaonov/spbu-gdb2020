from pygraphblas.matrix import Matrix
from pygraphblas.types import BOOL
from pyformlang.regular_expression import Regex

class Graph():
    def __init__(self):
        self.vertices_count = 0
        self.label_matrices = dict()
        self.start_vertices = set()
        self.terminal_vertices = set()


    def read_graph_from_file(self, file_path):
        #read edges from file
        graph_file = open(file_path, 'r')
        edges = graph_file.read().rstrip().split('\n')
        graph_file.close()

        #get vertices count
        max_vertex = 0
        for edge in edges:
            start, label, end = edge.split(' ')
            max_vertex = max([max_vertex, int(start), int(end)])
        self.vertices_count = max_vertex + 1

        #init label_matrix
        for edge in edges:
            start, label, end = edge.split(' ')
            #add label to label_matrix if it is not there yet
            if label not in self.label_matrices.keys():
                self.label_matrices[label] = Matrix.sparse(BOOL, self.vertices_count, self.vertices_count)
            self.label_matrices[label][int(start), int(end)] = True

        #init start and terminal states
        for vertex in range(self.vertices_count):
            self.start_vertices.add(vertex)
            self.terminal_vertices.add(vertex)
    #end of read_graph_from_file


    def parse_regex(self, file_path):
        #read regex from file
        regex_file = open(file_path, 'r')
        regex = Regex(regex_file.read().rstrip())
        regex_file.close()

        dfa = regex.to_epsilon_nfa().to_deterministic().minimize()
        print(dfa._states)
        self.vertices_count = len(dfa.states)

        #states enumeration
        state_indices = dict()
        for index, state in enumerate(dfa.states):
            state_indices[state] = index

        #init label_matrix
        for start, label, end in dfa._transition_function.get_edges():
            label = str(label)
            #add label to label_matrix if it is not there yet
            if label not in self.label_matrices.keys():
                self.label_matrices[label] = Matrix.sparse(BOOL, self.vertices_count, self.vertices_count)
            self.label_matrices[label][state_indices[start], state_indices[end]] = True

        #init start and terminal states
        self.start_vertices.add(state_indices[dfa.start_state])
        for state in dfa.final_states:
            self.terminal_vertices.add(state_indices[state])
    #end of parse_regex
