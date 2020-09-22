import main
from pygraphblas import *
from pyformlang.finite_automaton import State, Symbol, DeterministicFiniteAutomaton


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


def test_matrix_prod():
    A = Matrix.from_lists(
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [0, 1, 2, 0, 1, 2, 0, 1, 2],
        [1, 2, 1, 2, 1, 2, 1, 2, 1])

    B = Matrix.from_lists(
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [0, 1, 2, 0, 1, 2, 0, 1, 2],
        [2, 1, 2, 1, 2, 1, 2, 1, 2])

    A_x_B = Matrix.from_lists(
        [0, 0, 0, 1, 1, 1, 2, 2, 2],
        [0, 1, 2, 0, 1, 2, 0, 1, 2],
        [6, 6, 6, 9, 6, 9, 6, 6, 6])

    assert A_x_B.iseq(A @ B)


def test_DFA_intersection():
    char_a = Symbol("a")
    char_b = Symbol("b")

    state_start = State(0)
    state_final = State(1)

    dfa_fst = DeterministicFiniteAutomaton()
    dfa_fst.add_start_state(state_start)
    dfa_fst.add_final_state(state_final)

    dfa_snd = DeterministicFiniteAutomaton()
    dfa_snd.add_start_state(state_start)
    dfa_snd.add_final_state(state_final)

    dfa_fst.add_transition(state_start, char_a, state_final)
    dfa_fst.add_transition(state_final, char_b, state_start)

    dfa_snd.add_transition(state_start, char_a, state_final)
    dfa_snd.add_transition(state_final, char_b, state_final)

    dfa_intersection = dfa_fst & dfa_snd

    assert not dfa_fst.accepts("abbbb")
    assert dfa_fst.accepts("ababa")
    assert dfa_fst.accepts("a")

    assert not dfa_snd.accepts("ababa")
    assert dfa_snd.accepts("abbbb")
    assert dfa_snd.accepts("a")

    assert not dfa_intersection.accepts("ababa")
    assert not dfa_intersection.accepts("abbbb")
    assert dfa_intersection.accepts("a")
