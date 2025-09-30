#!/bin/bash
# Zyra Chess Engine Wrapper for Lucas Chess
# This script allows Lucas Chess to run the Python UCI engine

# Navigate to the Zyra directory
cd "$(dirname "$0")"

# Run the UCI engine
python3 -m interfaces.uci "$@"
