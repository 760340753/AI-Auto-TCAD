#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "Setting up environment..."
# Load Sentaurus environment if exists
if [ -f "${SCRIPT_DIR}/sentaurus_env.sh" ]; then
    source "${SCRIPT_DIR}/sentaurus_env.sh"
fi

# Activate Python virtual environment
source "${SCRIPT_DIR}/swb_env/bin/activate"

# Force Python I/O encoding to UTF-8
export PYTHONIOENCODING=UTF-8

# Set language to English
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

echo "Environment ready. Running automated simulation script..."
cd "${SCRIPT_DIR}"

# Use auto_sim_main.py
python3.11 -c "
import os
import sys
sys.path.append('${SCRIPT_DIR}')
from auto_sim.auto_sim_main import main
main()
"

echo "Automated simulation process completed."
deactivate # Deactivate virtual environment 