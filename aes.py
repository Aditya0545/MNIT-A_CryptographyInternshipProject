import numpy as np

# AES S-box (Substitution Box)
# S-box for SubBytes operation
S_BOX = [
    [99, 124, 119, 123, 242, 107, 111, 197, 48, 1, 103, 43, 254, 215, 171, 118],
    [202, 130, 201, 125, 250, 89, 71, 240, 173, 212, 162, 175, 156, 164, 114, 192],
    [183, 253, 147, 38, 54, 63, 247, 204, 52, 165, 229, 241, 113, 216, 49, 21],
    [4, 199, 35, 195, 24, 150, 5, 154, 7, 18, 128, 226, 235, 39, 178, 117],
    [9, 131, 44, 26, 27, 110, 90, 160, 82, 59, 214, 179, 41, 227, 47, 132],
    [83, 209, 0, 237, 32, 252, 177, 91, 106, 203, 190, 57, 74, 76, 88, 207],
    [208, 239, 170, 251, 67, 77, 51, 133, 69, 249, 2, 127, 80, 60, 159, 168],
    [81, 163, 64, 143, 146, 157, 56, 245, 188, 182, 218, 33, 16, 255, 243, 210],
    [205, 12, 19, 236, 95, 151, 68, 23, 196, 167, 126, 61, 100, 93, 25, 115],
    [96, 129, 79, 220, 34, 42, 144, 136, 70, 238, 184, 20, 222, 94, 11, 219],
    [224, 50, 58, 10, 73, 6, 36, 92, 194, 211, 172, 98, 145, 149, 228, 121],
    [231, 200, 55, 109, 141, 213, 78, 169, 108, 86, 244, 234, 101, 122, 174, 8],
    [186, 120, 37, 46, 28, 166, 180, 198, 232, 221, 116, 31, 75, 189, 139, 138],
    [112, 62, 181, 102, 72, 3, 246, 14, 97, 53, 87, 185, 134, 193, 29, 158],
    [225, 248, 152, 17, 105, 217, 142, 148, 155, 30, 135, 233, 206, 85, 40, 223],
    [140, 161, 137, 13, 191, 230, 66, 104, 65, 153, 45, 15, 176, 84, 187, 22],
]

# Example of 128-bit plaintext and key (both should be 16 bytes for AES-128)
plaintext = [0x32, 0x43, 0xF6, 0xA8, 0x88, 0x5A, 0x30, 0x8D, 0x31, 0x31, 0x98, 0xA2, 0xE0, 0x37, 0x07, 0x34]
key = [0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6, 0xAB, 0xF7, 0x4D, 0x3E, 0x4D, 0x4E, 0x7C, 0xE5]

# AES operates on a 4x4 matrix (state)
def matrixify(data):
    return [[data[i + 4 * j] for j in range(4)] for i in range(4)]

# SubBytes step
def sub_bytes(state):
    for i in range(4):
        for j in range(4):
            state[i][j] = S_BOX[state[i][j]]
    return state

# ShiftRows step
def shift_rows(state):
    for i in range(1, 4):  # Row 0 stays unchanged
        state[i] = state[i][i:] + state[i][:i]
    return state

# AddRoundKey step
def add_round_key(state, round_key):
    for i in range(4):
        for j in range(4):
            state[i][j] ^= round_key[i][j]
    return state

# MixColumns step (simplified for demonstration; not optimized for speed)
def mix_columns(state):
    def mix_single_column(column):
        # MixColumn operations (Galois field math)
        temp = column[:]
        column[0] = (2 * temp[0]) ^ (3 * temp[1]) ^ temp[2] ^ temp[3]
        column[1] = temp[0] ^ (2 * temp[1]) ^ (3 * temp[2]) ^ temp[3]
        column[2] = temp[0] ^ temp[1] ^ (2 * temp[2]) ^ (3 * temp[3])
        column[3] = (3 * temp[0]) ^ temp[1] ^ temp[2] ^ (2 * temp[3])
        return column

    for i in range(4):
        state[i] = mix_single_column(state[i])
    return state

# Example AES-128 Encryption (Skeleton)
def aes_encrypt(plaintext, key):
    state = matrixify(plaintext)
    round_key = matrixify(key)

    # Initial round
    state = add_round_key(state, round_key)

    # Main rounds
    for _ in range(9):  # AES-128 has 10 rounds
        state = sub_bytes(state)
        state = shift_rows(state)
        state = mix_columns(state)
        state = add_round_key(state, round_key)

    # Final round (no MixColumns)
    state = sub_bytes(state)
    state = shift_rows(state)
    state = add_round_key(state, round_key)

    # Return encrypted state as a flat list
    return [state[i][j] for i in range(4) for j in range(4)]

# Run the encryption
ciphertext = aes_encrypt(plaintext, key)
print("Ciphertext:", ciphertext)
