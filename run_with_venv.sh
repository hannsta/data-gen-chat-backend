#!/bin/bash
# Helper script to run commands in the virtual environment
# Usage: ./run_with_venv.sh <command>
# Example: ./run_with_venv.sh python test/demo_test.ipynb

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the project directory
cd "$SCRIPT_DIR"

# Activate virtual environment
source .venv/bin/activate

# Run the command passed as arguments
"$@"
