import os
import random
import nltk
from nltk.corpus import words
from Crypto.Cipher import AES, DES, DES3, Blowfish, ChaCha20, Salsa20
from Crypto.Util.Padding import pad
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

    def encrypt_cpu(self, plaintext, cipher_type, key=None, iv=None, nonce=None):
        """
        Encrypt plaintext using the specified cipher type on CPU.
        """
        if cipher_type == "AES":
            key = key or get_random_bytes(32)
            cipher = AES.new(key, AES.MODE_ECB)
            ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
        elif cipher_type == "DES":
            key = key or get_random_bytes(8)
            iv = iv or get_random_bytes(8)
            cipher = DES.new(key, DES.MODE_CBC, iv)
            ciphertext = cipher.encrypt(pad(plaintext.encode(), DES.block_size))
        elif cipher_type == "3DES":
            key = key or get_random_bytes(24)
            iv = iv or get_random_bytes(8)
            cipher = DES3.new(key, DES3.MODE_CBC, iv)
            ciphertext = cipher.encrypt(pad(plaintext.encode(), DES3.block_size))
        elif cipher_type == "Blowfish":
            key = key or get_random_bytes(16)
            cipher = Blowfish.new(key, Blowfish.MODE_ECB)
            ciphertext = cipher.encrypt(pad(plaintext.encode(), Blowfish.block_size))
        else:
            raise ValueError("Unsupported cipher type")
        return ciphertext

    def save_file(self, folder_path, cipher_type, size_kb, index):
        plaintext = self.generate_text(size_kb)
        ciphertext = self.encrypt_cpu(plaintext, cipher_type)
        file_name = f"{size_kb}KB_{index}.txt"
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'w') as f:
            f.write(ciphertext.hex())

    def create_dataset(self):
        sizes_kb = [1]  # Example sizes in KB
        cipher_types = ["AES","DES","3DES","Blowfish"]  # Example cipher types
        dataset_folder = "block"
        os.makedirs(dataset_folder, exist_ok=True)

        for cipher_type in cipher_types:
            cipher_folder = os.path.join(dataset_folder, cipher_type)
            os.makedirs(cipher_folder, exist_ok=True)
            for size_kb in sizes_kb:
                # Multithreading for file generation
                with ThreadPoolExecutor() as executor:
                    futures = [
                        executor.submit(
                            self.save_file, cipher_folder, cipher_type, size_kb, i
                        )
                        for i in range(1, 500)  # File indices
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