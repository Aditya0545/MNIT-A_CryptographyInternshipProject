#include <iostream>
#include <vector>
#include <cstdint>
#include <chrono>
#include <x86intrin.h>
#include <algorithm>
#include <fstream>
#include <map>
#include "../structures.h"

// Declare external functions from encrypt.cpp
extern void KeyExpansion(unsigned char* key, unsigned char* expandedKey);
extern void AESEncrypt(unsigned char* message, unsigned char* expandedKey, unsigned char* encryptedMessage);

// Timing measurement function using RDTSC
uint64_t rdtsc()
{
	return __rdtsc();
}

// Our AES encryption wrapper with known key for verification
void aes_encrypt(const uint8_t* plaintext, uint8_t* ciphertext, bool use_target_key = false)
{
	unsigned char expandedKey[176];
	unsigned char key[16];
	
	if (use_target_key) {
		// Use the key we want to attack
		for(int i = 0; i < 16; i++) {
			key[i] = 0x42;  // Example target key
		}
	} else {
		// Use a different key for comparison
		for(int i = 0; i < 16; i++) {
			key[i] = 0x01;
		}
	}
	
	KeyExpansion(key, expandedKey);
	AESEncrypt((unsigned char*)plaintext, expandedKey, ciphertext);
}

// Function to analyze timing patterns and predict key byte
uint8_t predict_key_byte(const std::vector<std::pair<uint8_t, uint64_t>>& timings) {
	std::map<uint8_t, std::vector<uint64_t>> timing_by_cacheline;
	
	// Group timings by cache line
	for (const auto& [byte_val, timing] : timings) {
		uint8_t cache_line = byte_val >> 4;  // High 4 bits = cache line
		timing_by_cacheline[cache_line].push_back(timing);
	}
	
	// Find cache line with highest average timing (likely cache miss)
	uint8_t likely_cache_line = 0;
	uint64_t max_avg_timing = 0;
	
	for (const auto& [cache_line, line_timings] : timing_by_cacheline) {
		uint64_t avg_timing = 0;
		for (uint64_t t : line_timings) {
			avg_timing += t;
		}
		avg_timing /= line_timings.size();
		
		if (avg_timing > max_avg_timing) {
			max_avg_timing = avg_timing;
			likely_cache_line = cache_line;
		}
	}
	
	return likely_cache_line << 4;  // Convert cache line back to key byte candidate
}

int main()
{
	const int SAMPLES_PER_BYTE = 2000;
	const int TARGET_BYTE_POS = 0;
	const int NUM_EXPERIMENTS = 10;

	std::vector<uint8_t> plaintext(16, 0);
	std::vector<uint8_t> ciphertext(16);
	std::vector<uint8_t> target_ciphertext(16);
	std::vector<std::pair<uint8_t, uint64_t>> timings;

	// Create output files
	std::ofstream outfile("timings.csv");
	std::ofstream keyfile("key_predictions.txt");
	outfile << "byte_val,timing,is_target,predicted_key\n";

	// Get target ciphertext
	aes_encrypt(plaintext.data(), target_ciphertext.data(), true);

	// Warm up the encryption function
	for(int i=0; i<100; i++) {
		aes_encrypt(plaintext.data(), ciphertext.data());
	}

	// Collect timing data and predict key bytes
	for(int byte_val = 0; byte_val < 256; byte_val++) {
		plaintext[TARGET_BYTE_POS] = static_cast<uint8_t>(byte_val);
		
		for(int exp = 0; exp < NUM_EXPERIMENTS; exp++) {
			std::vector<uint64_t> exp_timings;
			exp_timings.reserve(SAMPLES_PER_BYTE);

			for(int s=0; s<SAMPLES_PER_BYTE; s++) {
				// Flush cache to ensure consistent timing
				_mm_clflush(plaintext.data());
				_mm_clflush(ciphertext.data());
				_mm_clflush((void*)&s);
				
				uint64_t start = rdtsc();
				aes_encrypt(plaintext.data(), ciphertext.data());
				uint64_t end = rdtsc();
				
				exp_timings.push_back(end - start);
			}

			// Calculate median to reduce noise
			std::sort(exp_timings.begin(), exp_timings.end());
			uint64_t median_time = exp_timings[SAMPLES_PER_BYTE/2];
			
			// Store timing data
			timings.push_back({static_cast<uint8_t>(byte_val), median_time});
			
			// Every 16 bytes, try to predict the key
			if (timings.size() % 16 == 0) {
				uint8_t predicted_key = predict_key_byte(timings);
				keyfile << "After " << timings.size() << " measurements, predicted key byte: 0x" 
					   << std::hex << static_cast<int>(predicted_key) << std::dec << std::endl;
			}
			
			// Check if this matches the target ciphertext
			bool is_target = (ciphertext[0] == target_ciphertext[0]);
			
			outfile << byte_val << "," << median_time << "," << (is_target ? "1" : "0") << ","
				   << std::hex << static_cast<int>(predict_key_byte(timings)) << std::dec << "\n";
			outfile.flush();
		}
		
		// Progress indicator
		if (byte_val % 16 == 0) {
			std::cout << "Progress: " << (byte_val * 100 / 256) << "% - Current key prediction: 0x" 
					 << std::hex << static_cast<int>(predict_key_byte(timings)) << std::dec << "\r" << std::flush;
		}
	}

	// Final key prediction
	uint8_t final_key = predict_key_byte(timings);
	std::cout << "\nFinal key byte prediction: 0x" << std::hex << static_cast<int>(final_key) << std::dec << std::endl;
	
	outfile.close();
	keyfile.close();
	return 0;
}