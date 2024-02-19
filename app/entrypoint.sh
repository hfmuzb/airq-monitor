#!/bin/bash

set -e

# Let the DB start
python3 backend_pre_start.py

alembic upgrade heads

exec "$@"