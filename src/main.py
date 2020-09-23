import sys
from os import listdir
from os.path import isfile, join
from classes.Graph import Graph
from alg.Utils import Utils

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Not enough arguments!")
    else:
        iterations_num = 5
        input_dir_path  = sys.argv[1]
        output_dir_path = sys.argv[2]
        graph = Graph()

        regex_folders_paths = ["LUBM300/regexes", "LUBM500/regexes", "LUBM1M/regexes", "LUBM1.5M/regexes",
                               "LUBM1.9M/regexes"]
        graph_paths = ["LUBM300/LUBM300.txt", "LUBM500/LUBM500.txt", "LUBM1M/LUBM1M.txt", "LUBM1.5M/LUBM1.5M.txt",
                       "LUBM1.9M/LUBM1.9M.txt"]

         for graph_path in graph_paths:
            graph.read_graph_from_file(join(input_dir_path, graph_path))

            closure_result = Utils.measure_transitive_closure(iterations_num)

            output_file = open(join(output_dir_path, "closure_graph.txt"), 'a')
            nvals = len(Utils.get_transitive_closure_adj_matrix(graph).vals())
            output_file.write(graph_path + ' ' + str(nvals) + ' ' + closure_result + '\n')
            output_file.close()

         for regex_folder_path in regex_folders_paths:
            output_file = open(join(output_dir_path, "closure_regex.txt"), 'a')
            output_file.write(regex_folder_path + ':\n')
            output_file.close()

            full_regex_folder_path = join(input_dir_path, regex_folder_path)
            regex_files = [file for file in listdir(full_regex_folder_path) if isfile(join(full_regex_folder_path, file))]
            for regex_file in regex_files:
                graph = Graph()
                graph.parse_regex(join(full_regex_folder_path, regex_file))

                closure_result = Utils.measure_transitive_closure(iterations_num)

                output_file = open(join(output_dir_path, "closure_regex.txt"), 'a')
                nvals = len(Utils.get_transitive_closure_adj_matrix(graph))
                output_file.write(regex_file + ' ' + str(nvals) + ' ' + closure_result + '\n')
                output_file.close()

        for graph_path in graph_paths:
            graph.read_graph_from_file(join(input_dir_path, graph_path))

            output_file = open(join(output_dir_path, "intersection.txt"), 'a')
            output_file.write(graph_path + ':\n')
            output_file.close()

            for regex_folder_path in regex_folders_paths:
                output_file = open(join(output_dir_path, "intersection.txt"), 'a')
                output_file.write('    ' + regex_folder_path + ':\n')
                output_file.close()

                full_regex_folder_path = join(input_dir_path, regex_folder_path)
                regex_files = [file for file in listdir(full_regex_folder_path) if isfile(join(full_regex_folder_path, file))]
                for regex_file in regex_files:
                    aut = Graph()
                    aut.parse_regex(join(full_regex_folder_path, regex_file))

                    intersection = Utils.get_intersection(graph, aut)
                    intersection_result = Utils.measure_intersection(iterations_num)
                    pr_result = Utils.measure_print(iterations_num)

                    output_file = open(join(output_dir_path, "intersection.txt"), 'a')
                    output_file.write('        ' + regex_file + '   ' + intersection_result + '   ' + pr_result + '\n')
                    output_file.close()
