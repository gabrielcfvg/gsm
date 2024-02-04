#!/usr/bin/env bash

# setup errors
set -eu


SCRIPT_HOME=$(dirname -- "$( readlink -f -- "$0"; )";)
source $SCRIPT_HOME/vars.sh


rm -rf $POETRY_HOME
rm -rf .venv