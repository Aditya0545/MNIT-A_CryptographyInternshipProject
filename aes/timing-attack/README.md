# AES Timing Attack Implementation

This folder contains the implementation of a timing attack against AES-128.

## Requirements

- C++ compiler (g++)
- Python 3.x with required packages (see requirements.txt)
- Linux environment (for taskset command)

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Make the run script executable:
```bash
chmod +x run_attack.sh
```

## Running the Attack

Simply execute:
```bash
./run_attack.sh
```

This will:
1. Compile the timing attack program
2. Collect timing measurements
3. Analyze the data
4. Generate visualization plots

## Output Files

- `timings.csv`: Raw timing measurements
- `timing_distribution.png`: Visualization of timing data
- `correlation_analysis.png`: Key byte correlation analysis 