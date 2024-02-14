#!/bin/bash

set -e

# Let the DB start
python3 backend_pre_start.py

cd ..
alembic upgrade heads
cd app

exec "$@"