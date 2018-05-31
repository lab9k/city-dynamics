#!/bin/sh

set -x
set -e
set -x

cd /app/

flake8 --max-complexity 6 .
flake8 .
