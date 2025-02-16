#!/bin/bash

# Exit on error
set -e

# Activate virtual environment
source venv/bin/activate

# Create output directory if it doesn't exist
mkdir -p output

# Remove old timing data if it exists
rm -f timings.csv

# Compile the timing attack program
echo "Compiling timing attack program..."
g++ -O0 -march=native -DTIMING_ATTACK ../tables.cpp ../encrypt.cpp timing_attack.cpp -o timing_attack

# Run the timing collection (pinned to CPU core 0)
echo "Collecting timing data..."
taskset -c 0 ./timing_attack

# Check if timing data was collected
if [ ! -s timings.csv ]; then
    echo "Error: No timing data collected!"
    exit 1
fi

# Run the analysis
echo "Analyzing timing data..."
python3 analyze_timings.py

# Deactivate virtual environment
deactivate

echo "Generated files:"
echo "- timings.csv (raw timing data)"
echo "- timing_distribution.png (visualization of timing measurements)"
echo "- correlation_analysis.png (key byte correlation analysis)" 