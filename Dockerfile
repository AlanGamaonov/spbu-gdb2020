FROM continuumio/miniconda3

RUN mkdir /flt
WORKDIR /flt
COPY . /flt

COPY environment.yml .
RUN conda env create -f environment.yml
SHELL ["conda", "run", "-n", "flt_env", "/bin/bash", "-c"]

ADD src/main.py /flt/src
ADD src/classes/Graph.py /flt/src/classes
ADD src/alg/intersection_and_reachability.py /flt/src/alg

ARG graph_file
ARG regex_file

RUN pip3 install pyformlang
ENTRYPOINT ["conda", "run", "-n", "flt_env", "python", "src/main.py", $graph_file, $regex_file]
RUN python3 -m pytest -v -s
