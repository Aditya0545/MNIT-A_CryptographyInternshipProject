from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import SHA256
import os
import base64

# Generate a key from a password (or use a random 256-bit key)
def generate_key(password: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

# Encrypt function
def encrypt(plaintext: str, key: bytes):
    # Generate a random 16-byte initialization vector (IV)
    iv = os.urandom(16)
    
    # Pad the plaintext to be a multiple of 16 bytes
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()
    
    # Encrypt the padded plaintext
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    # Return the IV and ciphertext (base64 encoded)
    return base64.b64encode(iv + ciphertext).decode()

# Decrypt function
def decrypt(encrypted_data: str, key: bytes):
    # Decode the base64 encoded encrypted data
    encrypted_data = base64.b64decode(encrypted_data)
    
    # Extract the IV and ciphertext
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    
    # Decrypt the ciphertext
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Remove the padding from the plaintext
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    
    return plaintext.decode()

# Example usage
if __name__ == "__main__":
    password = "my_secure_password"  # Shared secret
    salt = os.urandom(16)  # Random salt for key derivation
    
    # Generate a key
    key = generate_key(password, salt)
    
    # Encrypt a message
    plaintext = "Hello, AES encryption!"
    encrypted = encrypt(plaintext, key)
    print(f"Encrypted: {encrypted}")
    
    # Decrypt the message
    decrypted = decrypt(encrypted, key)
    print(f"Decrypted: {decrypted}")
