from classes.Graph import Graph
from alg import intersection_and_reachability


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Not enough arguments!")
    else:
        graph = Graph()
        graph.read_graph_from_file(sys.argv[1])

        aut = Graph()
        aut.parse_regex(sys.argv[2])

        get_intersection(graph, aut)
