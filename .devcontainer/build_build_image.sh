#!/usr/bin/env bash

# forward errors
set -e

# get script directory
SCRIPT_HOME=$(dirname -- "$( readlink -f -- "$0"; )";)

# build the build_env image
docker build --target build_env -t gsm_build_env -f $SCRIPT_HOME/Dockerfile .
