#!/bin/bash

printf "Building the docker image for FedBiscuit on RunAI...\n"

# Make sure to update the username, GID and UID
docker build . --tag registry.rcp.epfl.ch/ml4ed-jchavero/fedbiscuit:v0.2 \
    --build-arg LDAP_GROUPNAME=ml4ed \
    --build-arg LDAP_GID=30204 \
    --build-arg LDAP_USERNAME=jchavero \
    --build-arg LDAP_UID=216858 \
    --build-arg HF_TOKEN=[ADD YOUR TOKEN HERE]

printf "Docker image building done.\n"
