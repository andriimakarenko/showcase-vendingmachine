#!/usr/bin/env bash

set -euo pipefail


# Change into this directory for consistent and easy relative path usage
cd "$(dirname "$0")"

# Default to production if FLASK_ENV isn't set to anything
export FLASK_ENV=${FLASK_ENV-production}

# Default to port 8080
export FLASK_PORT=${FLASK_PORT-8080}

export FLASK_APP="../main.py"

flask run