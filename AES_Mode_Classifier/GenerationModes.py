import os
import random
import nltk
from nltk.corpus import words
from Crypto.Cipher import AES
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

    def encrypt_cpu(self, plaintext, cipher_mode, key=None):
        """
        Encrypt plaintext using AES with the specified mode on CPU.
        """
        key = key or get_random_bytes(32)  # AES-256
        plaintext_padded = pad(plaintext.encode(), AES.block_size)

        if cipher_mode == "ECB":
            cipher = AES.new(key, AES.MODE_ECB)
            ciphertext = cipher.encrypt(plaintext_padded)
            return ciphertext.hex()

        elif cipher_mode == "CBC":
            iv = get_random_bytes(16)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            ciphertext = cipher.encrypt(plaintext_padded)
            return (iv + ciphertext).hex()

        elif cipher_mode == "CFB":
            iv = get_random_bytes(16)
            cipher = AES.new(key, AES.MODE_CFB, iv)
            ciphertext = cipher.encrypt(plaintext.encode())
            return (iv + ciphertext).hex()

        elif cipher_mode == "OFB":
            iv = get_random_bytes(16)
            cipher = AES.new(key, AES.MODE_OFB, iv)
            ciphertext = cipher.encrypt(plaintext.encode())
            return (iv + ciphertext).hex()

        elif cipher_mode == "CTR":
            nonce = get_random_bytes(8)
            cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
            ciphertext = cipher.encrypt(plaintext.encode())
            return (nonce + ciphertext).hex()

        elif cipher_mode == "GCM":
            nonce = get_random_bytes(12)
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
            return (nonce + ciphertext + tag).hex()

        else:
            raise ValueError("Unsupported cipher mode")

    def save_file(self, folder_path, cipher_mode, size_kb, index):
        plaintext = self.generate_text(size_kb)
        ciphertext_hex = self.encrypt_cpu(plaintext, cipher_mode)
        file_name = f"AES_{cipher_mode}_{size_kb}KB_{index}.txt"
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'w') as f:
            f.write(ciphertext_hex)

    def create_dataset(self):
        sizes_kb = [1]  # Example sizes in KB
        # cipher_modes = ["ECB", "CBC", "CFB", "OFB", "CTR", "GCM"]  # AES modes
        cipher_modes = ["ECB","CBC"]
        dataset_folder = "Aes_Modes"  # Base dataset folder

        for cipher_mode in cipher_modes:
            folder_path = os.path.join(dataset_folder, f"{cipher_mode}")
            os.makedirs(folder_path, exist_ok=True)

            for size_kb in sizes_kb:
                # Multithreading for file generation
                with ThreadPoolExecutor() as executor:
                    futures = [
                        executor.submit(
                            self.save_file, folder_path, cipher_mode, size_kb, i
                        )
                        for i in range(1, 1000)  # File indices
                    ]
                    for future in tqdm(futures, desc=f"AES {cipher_mode} {size_kb}KB"):
                        try:
                            future.result()
                        except Exception as e:
                            print(f"Error in ThreadPoolExecutor: {e}")

            print(f"Completed: AES {cipher_mode} with {size_kb}KB")

if __name__ == "__main__":
    generator = CipherGenerator()
    generator.create_dataset()