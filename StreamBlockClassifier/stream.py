import os
import random
import nltk
from nltk.corpus import words
from Crypto.Cipher import ARC4, ChaCha20, Salsa20
from Crypto.Random import get_random_bytes
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Ensure nltk 'words' corpus is downloaded
nltk.download('words')

class CipherGenerator:
    def __init__(self):
        self.word_list = words.words()

    def generate_text(self, size_kb):
        size_bytes = size_kb * 1024  # Convert KB to bytes
        current_size = 0
        text = ""
        while current_size < size_bytes:
            sentence = " ".join(random.choices(self.word_list, k=10)) + ".\n"
            text += sentence
            current_size += len(sentence)
        return text

    def encrypt_cpu(self, plaintext, cipher_type, key=None, nonce=None):
        """
        Encrypt plaintext using the specified cipher type on CPU.
        """
        if cipher_type == "RC4":
            key = key or get_random_bytes(16)
            cipher = ARC4.new(key)
            ciphertext = cipher.encrypt(plaintext.encode())
        elif cipher_type == "ChaCha20":
            key = key or get_random_bytes(32)
            nonce = nonce or get_random_bytes(12)
            cipher = ChaCha20.new(key=key, nonce=nonce)
            ciphertext = cipher.encrypt(plaintext.encode())
        elif cipher_type == "Salsa20":
            key = key or get_random_bytes(32)
            nonce = nonce or get_random_bytes(8)
            cipher = Salsa20.new(key=key, nonce=nonce)
            ciphertext = cipher.encrypt(plaintext.encode())
        elif cipher_type == "Grain":
            key = key or get_random_bytes(10)  # Simulated key for Grain cipher
            ciphertext = self.simulate_grain_cipher(plaintext, key)
        else:
            raise ValueError("Unsupported cipher type")
        return ciphertext

    def simulate_grain_cipher(self, plaintext, key):
        """
        Simulate the Grain cipher by XOR-ing the plaintext with a pseudo-random keystream.
        """
        random.seed(key)  # Seed a random generator with the key
        keystream = bytes(random.randint(0, 255) for _ in range(len(plaintext)))
        ciphertext = bytes(p ^ k for p, k in zip(plaintext.encode(), keystream))
        return ciphertext

    def save_file(self, folder_path, cipher_type, size_kb, index):
        plaintext = self.generate_text(size_kb)
        ciphertext = self.encrypt_cpu(plaintext, cipher_type)
        file_name = f"{cipher_type}_{size_kb}KB_{index}.txt"
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'w') as f:
            f.write(ciphertext.hex())

    def create_dataset(self):
        sizes_kb = [1]  # Example sizes in KB
        cipher_types = ["RC4", "ChaCha20", "Salsa20", "Grain"]  # New cipher types
        dataset_folder = "stream_ciphers"  # Single folder for all ciphers
        os.makedirs(dataset_folder, exist_ok=True)

        for cipher_type in cipher_types:
            for size_kb in sizes_kb:
                # Multithreading for file generation
                with ThreadPoolExecutor() as executor:
                    futures = [
                        executor.submit(
                            self.save_file, dataset_folder, cipher_type, size_kb, i
                        )
                        for i in range(1, 2501)  # File indices
                    ]
                    for future in tqdm(futures, desc=f"{cipher_type} {size_kb}KB"):
                        try:
                            future.result()
                        except Exception as e:
                            print(f"Error in ThreadPoolExecutor: {e}")

                print(f"Completed: {cipher_type} with {size_kb}KB")

if __name__ == "__main__":
    generator = CipherGenerator()
    generator.create_dataset()
