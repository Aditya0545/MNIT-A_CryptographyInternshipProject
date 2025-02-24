import subprocess
import time
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import os
import secrets

# Constants
AES_BLOCK_SIZE = 16  # 16 bytes = 128 bits
FIXED_MESSAGE = 'A' * AES_BLOCK_SIZE  # Fixed 128-bit message
FIXED_MESSAGE_COUNT = 500  # Number of messages to encrypt for each key size
KEY_SIZES = {
    "AES-128": 16,  # 16 bytes = 128 bits
    "AES-192": 24,  # 24 bytes = 192 bits
    "AES-256": 32   # 32 bytes = 256 bits
}

def generate_key(size_bytes):
    """Generate a random key of specified size in bytes"""
    return secrets.token_bytes(size_bytes)

def save_key_to_file(key):
    """Save the key to keyfile in hex format"""
    with open('../../keyfile', 'w') as f:
        # Write key in hex format, two characters per byte
        f.write(''.join(f'{b:02x}' for b in key))
        f.write('\n')

def encrypt_message(message):
    """Encrypt a single message using the AES implementation"""
    start_time = time.perf_counter_ns()
    subprocess.run(['../../encrypt'], input=message.encode(), capture_output=True)
    end_time = time.perf_counter_ns()
    
    return (end_time - start_time) / 1e6  # Convert to milliseconds

def run_timing_analysis(key_sizes=KEY_SIZES, message_count=FIXED_MESSAGE_COUNT, iterations=5):
    """Run timing analysis for different key sizes with fixed message count"""
    results = {}
    message = FIXED_MESSAGE
    
    for key_type, key_size in key_sizes.items():
        print(f"\nTesting {key_type} ({key_size * 8} bits)...")
        times = []
        
        for iteration in range(iterations):
            print(f"  Iteration {iteration + 1}/{iterations}")
            
            # Generate and save new key for this iteration
            key = generate_key(key_size)
            save_key_to_file(key)
            
            # Measure encryption time for the fixed number of messages
            batch_start_time = time.perf_counter_ns()
            for _ in range(message_count):
                encrypt_message(message)
            batch_end_time = time.perf_counter_ns()
            
            total_time = (batch_end_time - batch_start_time) / 1e6  # Convert to milliseconds
            times.append(total_time)
        
        results[key_type] = {
            'mean': np.mean(times),
            'std': np.std(times),
            'times': times,
            'key_size_bits': key_size * 8
        }
    
    return results

def plot_results(results, output_dir):
    """Plot the timing results for different key sizes"""
    # Prepare data
    key_types = list(results.keys())
    means = [results[k]['mean'] for k in key_types]
    stds = [results[k]['std'] for k in key_types]
    key_sizes = [results[k]['key_size_bits'] for k in key_types]
    
    # Create bar plot
    plt.figure(figsize=(10, 6))
    bars = plt.bar(key_types, means, yerr=stds, capsize=5)
    
    # Customize plot
    plt.ylabel('Total Time (milliseconds)')
    plt.title(f'AES Encryption Time vs Key Size\n(Fixed {FIXED_MESSAGE_COUNT} messages of 128 bits each)')
    plt.grid(True, axis='y', alpha=0.3)
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}ms',
                ha='center', va='bottom')
    
    # Save plot
    plt.savefig(os.path.join(output_dir, 'key_size_timing.png'))
    plt.close()
    
    # Save raw data
    with open(os.path.join(output_dir, 'key_size_data.txt'), 'w') as f:
        f.write("Key Size,Mean Time (ms),Std Dev (ms)\n")
        for key_type in key_types:
            f.write(f"{key_type},{results[key_type]['mean']:.2f},{results[key_type]['std']:.2f}\n")

def main():
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent / 'results'
    output_dir.mkdir(exist_ok=True)
    
    # Run the analysis
    print(f"Starting timing analysis with {FIXED_MESSAGE_COUNT} messages for each key size...")
    results = run_timing_analysis()
    
    # Plot and save results
    print("\nGenerating plots and saving results...")
    plot_results(results, output_dir)
    
    # Print summary
    print("\nResults Summary:")
    for key_type, data in results.items():
        print(f"{key_type}: {data['mean']:.2f} ± {data['std']:.2f} ms")
    
    print("\nAnalysis complete! Results saved in the results directory.")

if __name__ == "__main__":
    main() 