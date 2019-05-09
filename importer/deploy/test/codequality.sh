#!/bin/sh

set -x
set -e
set -x

cd /app/

flake8 --max-complexity 10 .
flake8 .
