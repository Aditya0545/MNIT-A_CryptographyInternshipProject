#include <iostream>
#include <vector>
#include <cstdint>
#include <chrono>
#include <x86intrin.h> // For RDTSC
#include <bits/algorithmfwd.h>

// Replace with your AES implementation's header
extern "C"
{
	void aes_encrypt(const uint8_t *plaintext, uint8_t *ciphertext);
}

// Timing measurement function using RDTSC
uint64_t rdtsc()
{
	return __rdtsc();
}

int main()
{
	const int SAMPLES_PER_BYTE = 1000;
	const int TARGET_BYTE_POS = 0; // Focus on first byte

	std::vector<uint8_t> plaintext(16, 0);
	std::vector<uint8_t> ciphertext(16);

	// Warm up the encryption function
	for (int i = 0; i < 100; i++)
	{
		aes_encrypt(plaintext.data(), ciphertext.data());
	}

	// Collect timing data
	for (int byte_val = 0; byte_val < 256; byte_val++)
	{
		plaintext[TARGET_BYTE_POS] = static_cast<uint8_t>(byte_val);

		std::vector<uint64_t> timings;
		timings.reserve(SAMPLES_PER_BYTE);

		for (int s = 0; s < SAMPLES_PER_BYTE; s++)
		{
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
		uint64_t median_time = timings[SAMPLES_PER_BYTE / 2];

		std::cout << static_cast<int>(byte_val) << ","
				  << median_time << "\n";
	}

	return 0;
}