#!/usr/bin/env bash

# setup errors
set -eu


SCRIPT_HOME=$(dirname -- "$( readlink -f -- "$0"; )";)
source $SCRIPT_HOME/vars.sh

# delete poetry env
rm -rf .venv
