#!/bin/bash

printf "Running the docker image...\n"

# Make sure to update the username
docker run -it registry.rcp.epfl.ch/ml4ed-jchavero/fedbiscuit:v0.2

printf "Closing the container.\n"
