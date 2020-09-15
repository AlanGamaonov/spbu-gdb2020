# FormalLanguageTheory
### Practical assignments for the formal language theory course at SPBU
 - PR build results avaliable at 
[![Build Status](https://travis-ci.org/github/AlekseiPrivalihin/FormalLanguageTheory/pull_requests)](https://travis-ci.org/github/AlekseiPrivalihin/FormalLanguageTheory/pull_requests)
 - Only Docker and git are required to run the tests
  - First, clone this repo by running
    `git clone https://github.com/AlekseiPrivalihin/FormalLanguageTheory.git`
  - Then go to the repo folder and build the docker image by running
    `docker build -t formal_language_theory .`
  - Lastly, run the image using
    `docker run formal_language_theory`