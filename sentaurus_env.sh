#!/bin/bash

# Set Sentaurus installation root
export STROOT=/usr/synopsys/sentaurus/V-2024.03

# Set Sentaurus release version
export STRELEASE=V-2024.03

# Update PATH
# Prioritize Python 3.11 and Sentaurus binaries
export PATH=/usr/local/bin:$STROOT/bin:$PATH

# Update LD_LIBRARY_PATH
# Include Sentaurus libraries and the custom OpenSSL 1.1.1 library
export LD_LIBRARY_PATH=/usr/local/openssl111/lib:$STROOT/tcad/$STRELEASE/linux64/lib/:$LD_LIBRARY_PATH

# Set STROOT_LIB
export STROOT_LIB=$STROOT/tcad/$STRELEASE/lib

echo "Sentaurus environment variables set."
echo "Python version: $(python3.11 --version)"
echo "PATH: $PATH"
echo "LD_LIBRARY_PATH: $LD_LIBRARY_PATH" 