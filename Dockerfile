FROM graphblas/pygraphblas-minimal:latest

RUN mkdir /flt
WORKDIR /flt
COPY . /flt

RUN pip3 install -r requirements.txt
CMD ["pytest"]