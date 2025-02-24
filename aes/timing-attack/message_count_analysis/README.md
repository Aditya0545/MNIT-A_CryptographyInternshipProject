# AES Encryption Timing Analysis

This directory contains scripts for analyzing AES encryption timing characteristics under different conditions.

## Available Analysis Scripts

1. `message_count_timing.py`: Analyzes encryption time vs number of messages (fixed 128-bit size)
2. `key_size_timing.py`: Analyzes encryption time with different key sizes (128, 192, 256 bits)
3. `message_size_count_timing.py`: Analyzes encryption time with varying message sizes and counts

## Setup

1. Make sure you have Python 3.7+ installed
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure the AES encryption executable is compiled in the parent directory

## Running the Analyses

### 1. Message Count Analysis
```bash
python message_count_timing.py
```
- Tests encryption timing for 100-800 messages (steps of 100)
- Uses fixed 128-bit message size
- Generates timing_analysis.png and timing_data.txt

### 2. Key Size Analysis
```bash
python key_size_timing.py
```
- Tests different key sizes: 128-bit, 192-bit, 256-bit
- Uses fixed message count (500) for each key size
- Generates key_size_timing.png and key_size_data.txt

### 3. Message Size and Count Analysis
```bash
python message_size_count_timing.py
```
- Tests different message sizes: 128-bit, 192-bit, 256-bit
- Tests message counts from 100 to 800
- Uses random message content
- Generates:
  - message_size_count_timing.png (line plot)
  - message_size_comparison.png (bar plot)
  - message_size_count_data.txt (raw data)

## Output Files

Each script generates output in the `results` directory:
- PNG files: Visualization plots with error bars and trend lines
- TXT files: Raw timing data in CSV format with means and standard deviations

## Analysis Features

- High-precision timing measurements (nanosecond precision)
- Multiple iterations for statistical significance
- Error bars showing standard deviation
- Trend line analysis
- Detailed statistics including:
  - Mean encryption time
  - Standard deviation
  - Time per message
  - Optimal message counts
  - Performance scaling characteristics

## Notes

- Times are measured in milliseconds
- Each script runs 5 iterations by default for statistical significance
- Error bars indicate standard deviation of measurements
- Random messages use cryptographically secure random generation
- Results may vary based on system load and hardware capabilities

## Requirements

- Python 3.7+
- numpy >= 1.21.0
- matplotlib >= 3.4.0
- Compiled AES encryption executable