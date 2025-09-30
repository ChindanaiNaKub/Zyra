#!/bin/bash
# Zyra Chess Engine Wrapper for Lucas Chess
# This script allows Lucas Chess to run the Python UCI engine

# Navigate to the Zyra directory
cd "$(dirname "$0")"

# Log file for debugging
LOG_FILE="/tmp/zyra_engine.log"

# Log start time and environment
echo "=== Zyra Engine Started at $(date) ===" >> "$LOG_FILE" 2>&1
echo "Working directory: $(pwd)" >> "$LOG_FILE" 2>&1
echo "Python version: $(python3 --version)" >> "$LOG_FILE" 2>&1
echo "PYTHONPATH: $PYTHONPATH" >> "$LOG_FILE" 2>&1

# Run the UCI engine and capture stderr only (stdout must go to GUI)
echo "=== Starting UCI loop ===" >> "$LOG_FILE"
python3 -m interfaces.uci "$@" 2>> "$LOG_FILE"
EXIT_CODE=$?
echo "=== Engine exited with code $EXIT_CODE ===" >> "$LOG_FILE"
