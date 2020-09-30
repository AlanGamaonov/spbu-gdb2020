import random
import sys
from os import listdir
from os.path import isfile, join
from classes.Graph import Graph
from alg.Utils import Utils


def get_reachable_pairs_count(gr, aut):
    intersec = Utils.get_intersection(gr, aut)
    matrix = Utils.get_transitive_closure_adj_matrix(intersec)
    return len(matrix)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Not enough arguments!")
    else:
        iterations_num = 5
        input_dir_path = sys.argv[1]
        output_dir_path = sys.argv[2]
        graph = Graph()
        automaton = Graph()

        graph_dirs = ['LUBM300', 'LUBM500', 'LUBM1M', 'LUBM1.5M', 'LUBM1.9M']

        for graph_dir in graph_dirs:
            full_graph_file_path = join(input_dir_path, join(graph_dir, graph_dir + ".txt"))
            graph.read_graph_from_file(full_graph_file_path)

            regexes_dir = join(input_dir_path, join(graph_dir, "regexes"))
            all_regex_files = [file for file in listdir(regexes_dir) if isfile(join(regexes_dir, file))]

            for i in range(10):
                current_regex_file = join(regexes_dir, all_regex_files[i])
                automaton.parse_regex(current_regex_file)

                intersection = Utils.get_intersection(graph, automaton)

                intersection_time = Utils.measure_intersection(iterations_num)
                intersection_output_file = open(join(output_dir_path, "intersection.txt"), 'a')
                intersection_output_file.write(
                    graph_dir + '   ' + all_regex_files[i] + '   ' + intersection_time + '\n')
                intersection_output_file.close()

                closure_time = Utils.measure_transitive_closure(iterations_num)
                closure_output_file = open(join(output_dir_path, "closure.txt"), 'a')
                closure_output_file.write(graph_dir + '   ' + all_regex_files[i] + '   ' + closure_time + '\n')
                closure_output_file.close()

                print_time = Utils.measure_print(iterations_num)
                print_output_file = open(join(output_dir_path, "output.txt"), 'a')
                print_output_file.write(graph_dir + '   ' + all_regex_files[i] + '   ' + print_time + '\n')
                print_output_file.close()

        for graph_dir in graph_dirs:
            regexes_dir = join(input_dir_path, join(graph_dir, "regexes"))
            all_regex_files = [file for file in listdir(regexes_dir) if isfile(join(regexes_dir, file))]

            full_graph_file_path = join(input_dir_path, join(graph_dir, graph_dir + ".txt"))
            graph.read_graph_from_file(full_graph_file_path)

            for i in range(2):
                regex_ind = random.randint(0, 100)
                current_regex_file = join(regexes_dir, all_regex_files[regex_ind])
                automaton.parse_regex(current_regex_file)

                reachable_pairs_count = get_reachable_pairs_count(graph, automaton)
                print(graph_dir + ' ' + all_regex_files[regex_ind] + ' ' + str(reachable_pairs_count))
