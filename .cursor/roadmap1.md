Here's a C++ implementation for a timing measurement program targeting AES. This example assumes you're using a vulnerable AES implementation (e.g., one that uses lookup tables):

```cpp
#include <iostream>
#include <vector>
#include <cstdint>
#include <chrono>
#include <x86intrin.h>  // For RDTSC

// Replace with your AES implementation's header
extern "C" {
    void aes_encrypt(const uint8_t* plaintext, uint8_t* ciphertext);
}

// Timing measurement function using RDTSC
uint64_t rdtsc() {
    return __rdtsc();
}

int main() {
    const int SAMPLES_PER_BYTE = 1000;
    const int TARGET_BYTE_POS = 0;  // Focus on first byte

    std::vector<uint8_t> plaintext(16, 0);
    std::vector<uint8_t> ciphertext(16);

    // Warm up the encryption function
    for(int i=0; i<100; i++) {
        aes_encrypt(plaintext.data(), ciphertext.data());
    }

    // Collect timing data
    for(int byte_val = 0; byte_val < 256; byte_val++) {
        plaintext[TARGET_BYTE_POS] = static_cast<uint8_t>(byte_val);
        
        std::vector<uint64_t> timings;
        timings.reserve(SAMPLES_PER_BYTE);

        for(int s=0; s<SAMPLES_PER_BYTE; s++) {
            // Flush cache (optional - depends on attack type)
            // _mm_clflush(plaintext.data());
            // _mm_clflush(ciphertext.data());
            
            uint64_t start = rdtsc();
            aes_encrypt(plaintext.data(), ciphertext.data());
            uint64_t end = rdtsc();
            
            timings.push_back(end - start);
        }

        // Calculate median to reduce noise
        std::sort(timings.begin(), timings.end());
        uint64_t median_time = timings[SAMPLES_PER_BYTE/2];
        
        std::cout << static_cast<int>(byte_val) << ","
                  << median_time << "\n";
    }

    return 0;
}
```

### Key Components Explained:

1. **RDTSC Instruction**:
   - Uses `__rdtsc()` intrinsic for cycle-accurate timing
   - More reliable than C++ chrono for small time intervals

2. **Measurement Structure**:
   - Focuses on one target byte position (modify `TARGET_BYTE_POS`)
   - Collects multiple samples per byte value (1000 samples)
   - Uses median instead of mean for noise resistance

3. **Cache Control** (Optional):
   - Uncomment `_mm_clflush` for explicit cache flushing
   - Required for certain types of cache attacks

4. **Output Format**:
   - CSV format: `byte_value,median_cycles`
   - Redirect output to file: `./timing_attack > timings.csv`

### Compilation Instructions:
```bash
g++ -O0 -march=native -o timing_attack timing_attack.cpp -laes  # Link to your AES library
```

### Important Notes:
1. **Vulnerable AES Requirement**:
   - The AES implementation must use data-dependent lookups
   - Example vulnerable code pattern:
     ```c
     // Vulnerable S-box access
     static const uint8_t sbox[256] = {...};
     output = sbox[input ^ key];
     ```

2. **System Configuration**:
   - Disable CPU frequency scaling:
     ```bash
     sudo cpupower frequency-set --governor performance
     ```
   - Use core isolation:
     ```bash
     taskset -c 0 ./timing_attack
     ```

3. **Analysis**:
   - Look for timing variations correlated with:
     - Cache hits/misses in S-box lookups
     - Branch mispredictions in AES code
     - Table entry alignment differences

### Enhanced Version with Statistical Features:
```cpp
// Add these headers
#include <algorithm>
#include <numeric>

// Inside the byte_val loop:
uint64_t min_time = *std::min_element(timings.begin(), timings.end());
uint64_t max_time = *std::max_element(timings.begin(), timings.end());
uint64_t avg_time = std::accumulate(timings.begin(), timings.end(), 0) / SAMPLES_PER_BYTE;

std::cout << static_cast<int>(byte_val) << ","
          << min_time << "," << max_time << ","
          << avg_time << "," << median_time << "\n";
```

### Next Steps:
1. Pair this with Python analysis code that:
   - Looks for timing differences correlated with cache line accesses
   - Uses Pearson correlation or mutual information analysis
   - Recovers key bytes through statistical analysis

2. Test with different:
   - AES implementations (OpenSSL vs custom)
   - Attack positions (different rounds/steps)
   - Noise reduction techniques

Would you like me to provide the companion Python analysis code or dive deeper into any specific aspect?