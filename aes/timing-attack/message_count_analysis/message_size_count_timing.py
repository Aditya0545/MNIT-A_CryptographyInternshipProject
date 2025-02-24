import subprocess
import time
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import os
import secrets
import string

# Constants
MESSAGE_SIZES = {
    "128-bit": 16,  # 16 bytes = 128 bits
    "192-bit": 24,  # 24 bytes = 192 bits
    "256-bit": 32   # 32 bytes = 256 bits
}
MESSAGE_COUNTS = [100, 200, 300, 400, 500, 600, 700, 800]

def generate_random_message(size_bytes):
    """Generate a random message of specified size in bytes"""
    # Use all printable characters except whitespace for better compatibility
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(chars) for _ in range(size_bytes))

def encrypt_message(message):
    """Encrypt a single message using the AES implementation"""
    start_time = time.perf_counter_ns()
    subprocess.run(['../../encrypt'], input=message.encode(), capture_output=True)
    end_time = time.perf_counter_ns()
    
    return (end_time - start_time) / 1e6  # Convert to milliseconds

def run_timing_analysis(message_sizes=MESSAGE_SIZES, message_counts=MESSAGE_COUNTS, iterations=5):
    """Run timing analysis for different message sizes and counts"""
    results = {}
    
    for size_label, size_bytes in message_sizes.items():
        print(f"\nTesting {size_label} messages...")
        results[size_label] = {}
        
        # Generate a new random message of current size
        message = generate_random_message(size_bytes)
        
        for count in message_counts:
            print(f"  Processing {count} messages...")
            times = []
            
            for iteration in range(iterations):
                print(f"    Iteration {iteration + 1}/{iterations}")
                
                # Measure encryption time for the current batch
                batch_start_time = time.perf_counter_ns()
                for _ in range(count):
                    encrypt_message(message)
                batch_end_time = time.perf_counter_ns()
                
                total_time = (batch_end_time - batch_start_time) / 1e6  # Convert to milliseconds
                times.append(total_time)
            
            results[size_label][count] = {
                'mean': np.mean(times),
                'std': np.std(times),
                'times': times
            }
    
    return results

def plot_results(results, output_dir):
    """Plot the timing results"""
    plt.figure(figsize=(12, 7))
    
    # Plot line for each message size
    for size_label, size_data in results.items():
        counts = list(size_data.keys())
        means = [size_data[count]['mean'] for count in counts]
        stds = [size_data[count]['std'] for count in counts]
        
        plt.errorbar(counts, means, yerr=stds, fmt='o-', capsize=5, label=size_label)
    
    plt.xlabel('Number of Messages')
    plt.ylabel('Total Time (milliseconds)')
    plt.title('AES Encryption Time vs Number of Messages\nFor Different Message Sizes')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Save plot
    plt.savefig(os.path.join(output_dir, 'message_size_count_timing.png'))
    plt.close()
    
    # Save raw data
    with open(os.path.join(output_dir, 'message_size_count_data.txt'), 'w') as f:
        f.write("Message Size,Message Count,Mean Time (ms),Std Dev (ms)\n")
        for size_label, size_data in results.items():
            for count, data in size_data.items():
                f.write(f"{size_label},{count},{data['mean']:.2f},{data['std']:.2f}\n")

def plot_size_comparison(results, output_dir):
    """Create a bar plot comparing message sizes for specific message counts"""
    # Select a few representative message counts to compare
    comparison_counts = [100, 400, 800]  # Low, medium, high
    
    # Prepare data for plotting
    size_labels = list(results.keys())
    x = np.arange(len(size_labels))
    width = 0.25  # Width of bars
    
    plt.figure(figsize=(12, 7))
    
    # Plot bars for each message count
    for i, count in enumerate(comparison_counts):
        means = [results[size][count]['mean'] for size in size_labels]
        stds = [results[size][count]['std'] for size in size_labels]
        
        plt.bar(x + i*width, means, width, 
               label=f'{count} messages',
               yerr=stds, capsize=5)
    
    plt.xlabel('Message Size')
    plt.ylabel('Total Time (milliseconds)')
    plt.title('AES Encryption Time Comparison\nFor Different Message Sizes and Counts')
    plt.xticks(x + width, size_labels)
    plt.legend()
    plt.grid(True, axis='y', alpha=0.3)
    
    # Save plot
    plt.savefig(os.path.join(output_dir, 'message_size_comparison.png'))
    plt.close()

def calculate_statistics(results):
    """Calculate and return interesting statistics about the results"""
    stats = {}
    
    for size_label, size_data in results.items():
        # Calculate average time per message for each message count
        times_per_message = {
            count: data['mean'] / count 
            for count, data in size_data.items()
        }
        
        # Find the most efficient message count (lowest time per message)
        most_efficient_count = min(times_per_message.items(), key=lambda x: x[1])
        
        stats[size_label] = {
            'min_time_per_msg': most_efficient_count[1],
            'optimal_msg_count': most_efficient_count[0],
            'total_time_range': (
                min(d['mean'] for d in size_data.values()),
                max(d['mean'] for d in size_data.values())
            )
        }
    
    return stats

def main():
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent / 'results'
    output_dir.mkdir(exist_ok=True)
    
    # Run the analysis
    print("Starting timing analysis...")
    results = run_timing_analysis()
    
    # Generate plots
    print("\nGenerating plots...")
    plot_results(results, output_dir)
    plot_size_comparison(results, output_dir)
    
    # Calculate and print statistics
    print("\nCalculating statistics...")
    stats = calculate_statistics(results)
    
    # Print summary
    print("\nResults Summary:")
    for size_label, size_stats in stats.items():
        print(f"\n{size_label} Messages:")
        print(f"  Optimal message count: {size_stats['optimal_msg_count']}")
        print(f"  Min time per message: {size_stats['min_time_per_msg']:.3f} ms")
        print(f"  Total time range: {size_stats['total_time_range'][0]:.1f} - {size_stats['total_time_range'][1]:.1f} ms")
    
    print("\nAnalysis complete! Results saved in the results directory.")

if __name__ == "__main__":
    main() 