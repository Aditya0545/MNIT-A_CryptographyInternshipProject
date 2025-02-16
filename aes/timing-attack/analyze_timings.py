import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import pandas as pd
from collections import defaultdict
import os

def analyze_timings():
    try:
        # Check if file exists and has data
        if not os.path.exists('timings.csv'):
            print("Error: timings.csv file not found!")
            return
            
        if os.path.getsize('timings.csv') == 0:
            print("Error: timings.csv is empty!")
            return

        # Load timing data
        try:
            data = pd.read_csv('timings.csv')
            print(f"Loaded {len(data)} timing measurements")
        except pd.errors.EmptyDataError:
            print("Error: No data found in timings.csv")
            return
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return

        # Check if required columns exist
        required_columns = ['byte_val', 'timing', 'is_target']
        if not all(col in data.columns for col in required_columns):
            print(f"Error: Missing required columns. Found: {data.columns.tolist()}")
            return

        # Group by byte value and calculate average timing
        grouped_data = data.groupby('byte_val').agg({
            'timing': ['mean', 'std'],
            'is_target': 'first'
        }).reset_index()

        # Plot timing distribution
        plt.figure(figsize=(15, 10))
        
        # Plot mean timings
        plt.subplot(2, 1, 1)
        plt.errorbar(grouped_data['byte_val'], 
                    grouped_data[('timing', 'mean')],
                    yerr=grouped_data[('timing', 'std')],
                    fmt='b.', alpha=0.5)
        plt.xlabel('Plaintext Byte Value')
        plt.ylabel('Mean Encryption Time (cycles)')
        plt.title('AES Timing Distribution with Error Bars')
        plt.grid(True)

        # Analyze cache patterns
        def get_cache_line(byte_val, key_guess):
            return (byte_val ^ key_guess) & 0xF0  # Get cache line number (high 4 bits)

        # Test all possible key bytes
        correlations = []
        cache_patterns = defaultdict(list)
        
        for key_guess in range(256):
            # Create expected cache pattern
            expected_pattern = [get_cache_line(b, key_guess) for b in grouped_data['byte_val']]
            
            # Calculate correlation with timing
            corr, _ = pearsonr(expected_pattern, grouped_data[('timing', 'mean')])
            correlations.append(abs(corr))
            
            # Store cache patterns for top correlations
            cache_patterns[abs(corr)].append(key_guess)

        # Plot correlation analysis
        plt.subplot(2, 1, 2)
        plt.plot(range(256), correlations, 'r-')
        plt.xlabel('Key Byte Candidate')
        plt.ylabel('Absolute Correlation')
        plt.title('Key Byte Correlation Analysis')
        plt.grid(True)

        # Save the plot
        plt.tight_layout()
        plt.savefig('timing_analysis.png')
        
        # Get top key candidates
        top_correlations = sorted(cache_patterns.keys(), reverse=True)[:5]
        print("\nTop 5 key byte candidates:")
        for i, corr in enumerate(top_correlations, 1):
            candidates = cache_patterns[corr]
            print(f"{i}. Correlation {corr:.3f}: 0x{candidates[0]:02x}",
                  f"(and {len(candidates)-1} other candidates)" if len(candidates) > 1 else "")

        # Additional analysis of cache patterns
        plt.figure(figsize=(12, 6))
        best_key = cache_patterns[top_correlations[0]][0]
        cache_lines = [get_cache_line(b, best_key) for b in range(256)]
        plt.scatter(range(256), cache_lines, c='b', alpha=0.5)
        plt.xlabel('Plaintext Byte Value')
        plt.ylabel('Cache Line')
        plt.title(f'Cache Access Pattern for Key 0x{best_key:02x}')
        plt.grid(True)
        plt.savefig('cache_pattern.png')
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_timings() 