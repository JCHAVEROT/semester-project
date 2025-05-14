#!/bin/bash

for X in {10..100..10}; do
    echo "Cloning FedBiscuit for ${X}%..."
    git clone git@github.com:schole-ai/FedBiscuit.git
    mv FedBiscuit FedBiscuit-${X}pct
    cd FedBiscuit-${X}pct || exit
    git checkout Data_Experiment
    cd ..
done