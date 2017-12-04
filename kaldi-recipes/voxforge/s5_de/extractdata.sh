#!/bin/bash

# Copyright 2012 Vassil Panayotov
# Apache 2.0

# Downloads and extracts the data from VoxForge website

# defines the "DATA_ROOT" variable - the location to store data
source ./path.sh
DATA_TGZ=${DATA_ROOT}/tgz
DATA_EXTRACT=${DATA_ROOT}/extracted

source utils/parse_options.sh

mkdir -p ${DATA_TGZ} 2>/dev/null

mkdir -p ${DATA_EXTRACT}

echo "--- Starting VoxForge archives extraction ..."
for a in ${DATA_TGZ}/*.tgz; do
  tar -C ${DATA_EXTRACT} -xf $a
done

