import subprocess
import time
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import os

# Constants for AES-128
AES_BLOCK_SIZE = 16  # 16 bytes = 128 bits
FIXED_MESSAGE = 'A' * AES_BLOCK_SIZE  # Fixed 128-bit message

def generate_fixed_size_message():
    """Generate a fixed 128-bit (16-byte) message"""
    return FIXED_MESSAGE

def encrypt_message(message):
    """Encrypt a single 128-bit message using the existing AES implementation"""
    # Create a temporary message file
    with open('temp_message.txt', 'w') as f:
        f.write(message)
    
    # Call the encryption program
    start_time = time.perf_counter_ns()
    subprocess.run(['../../encrypt'], input=message.encode(), capture_output=True)
    end_time = time.perf_counter_ns()
    
    return (end_time - start_time) / 1e6  # Convert to milliseconds

def run_timing_analysis(message_counts, iterations=5):
    """Run timing analysis for different message counts using fixed 128-bit messages"""
    results = {}
    message = FIXED_MESSAGE  # Use the fixed 128-bit message
    
    for count in message_counts:
        print(f"Processing {count} messages (128-bit each)...")
        times = []
        
        for _ in range(iterations):
            batch_start_time = time.perf_counter_ns()
            for _ in range(count):
                encrypt_message(message)
            batch_end_time = time.perf_counter_ns()
            
            total_time = (batch_end_time - batch_start_time) / 1e6  # Convert to milliseconds
            times.append(total_time)
        
        results[count] = {
            'mean': np.mean(times),
            'std': np.std(times),
            'times': times
        }
    
    return results

def plot_results(results, output_dir):
    """Plot the timing results"""
    counts = list(results.keys())
    means = [results[count]['mean'] for count in counts]
    stds = [results[count]['std'] for count in counts]
    
    plt.figure(figsize=(10, 6))
    plt.errorbar(counts, means, yerr=stds, fmt='o-', capsize=5)
    plt.xlabel('Number of 128-bit Messages')
    plt.ylabel('Total Time (milliseconds)')
    plt.title('AES-128 Encryption Time vs Number of Messages\n(Fixed 128-bit Message Size)')
    plt.grid(True)
    
    # Add trend line
    z = np.polyfit(counts, means, 1)
    p = np.poly1d(z)
    plt.plot(counts, p(counts), "r--", alpha=0.8, label=f'Trend line (slope: {z[0]:.2f} ms/msg)')
    
    plt.legend()
    plt.savefig(os.path.join(output_dir, 'timing_analysis.png'))
    plt.close()
    
    # Save raw data
    with open(os.path.join(output_dir, 'timing_data.txt'), 'w') as f:
        f.write("Message Count,Mean Time (ms),Std Dev (ms)\n")
        for count in counts:
            f.write(f"{count},{results[count]['mean']:.2f},{results[count]['std']:.2f}\n")

def main():
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent / 'results'
    output_dir.mkdir(exist_ok=True)
    
    # Define message counts to test
    message_counts = [100, 200, 300, 400, 500, 600, 700, 800]
    
    # Run the analysis
    print(f"Starting timing analysis with fixed {AES_BLOCK_SIZE * 8}-bit messages...")
    results = run_timing_analysis(message_counts)
    
    # Plot and save results
    print("Generating plots and saving results...")
    plot_results(results, output_dir)
    
    print("Analysis complete! Results saved in the results directory.")

if __name__ == "__main__":
    main() 