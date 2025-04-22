#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "Setting up environment..."
source "${SCRIPT_DIR}/sentaurus_env.sh"
source "${SCRIPT_DIR}/swb_env/bin/activate"

# Force Python I/O encoding to UTF-8
export PYTHONIOENCODING=UTF-8

echo "Environment ready. Running automation script..."
cd "${SCRIPT_DIR}"
python3.11 mct_auto_sim.py

echo "Automation script finished."
deactivate # Deactivate virtual environment
