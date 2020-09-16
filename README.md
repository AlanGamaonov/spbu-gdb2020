# SPBU FLT-2020
 - [CI](https://travis-ci.com/github/AlanGamaonov/spbu-gdb2020)

 - Only Docker and git are required to run the tests
 - Clone the repo 
 - Run:
    `docker build --build-arg graph_file=path --build-arg regex_file=path -t flt .`
 - Note that file must be in repos folder
 - Run:
    `docker run flt`
