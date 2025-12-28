from Crypto.PublicKey import RSA, ECC
from Crypto.Cipher import PKCS1_OAEP, PKCS1_v1_5
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import utils, dsa
from cryptography.hazmat.backends import default_backend
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import argparse
import random
import string

class CryptoDataset:
    def __init__(self, num_samples, plaintext_length=190):
        self.num_samples = num_samples
        self.plaintext_length = plaintext_length

    def __getitem__(self, idx):
        # Generate a random plaintext of specified length
        plaintext = ''.join(random.choices(string.ascii_letters + string.digits, k=self.plaintext_length))
        return plaintext

    def __len__(self):
        return self.num_samples

def chunked_iterable(iterable, chunk_size):
    """Split an iterable into chunks of given size."""
    for i in range(0, len(iterable), chunk_size):
        yield iterable[i:i + chunk_size]

# Moved functions to top-level for pickling

def rsa_encrypt_pkcs1_v15(key_size, plaintext):
    key = RSA.generate(key_size)
    cipher = PKCS1_v1_5.new(key.publickey())
    # Adjust maximum plaintext length based on key size and padding
    max_plaintext_length = (key_size // 8) - 11  # For PKCS#1 v1.5 padding
    plaintext = plaintext[:max_plaintext_length]
    return cipher.encrypt(plaintext.encode()).hex()

def rsa_encrypt_oaep(key_size, plaintext):
    key = RSA.generate(key_size)
    cipher = PKCS1_OAEP.new(key.publickey())
    # Adjust maximum plaintext length based on key size and padding
    max_plaintext_length = (key_size // 8) - 2 * SHA256.digest_size - 2  # For OAEP with SHA-256
    plaintext = plaintext[:max_plaintext_length]
    return cipher.encrypt(plaintext.encode()).hex()

def ecc_sign(plaintext):
    key = ECC.generate(curve='P-256')
    signer = DSS.new(key, 'fips-186-3')
    hash_obj = SHA256.new(plaintext.encode())
    return signer.sign(hash_obj).hex()

def dsa_sign(plaintext):
    plaintext_bytes = plaintext.encode('utf-8')
    private_key = dsa.generate_private_key(
        key_size=1024, backend=default_backend()
    )
    chosen_hash = hashes.SHA256()
    hasher = hashes.Hash(chosen_hash)
    hasher.update(plaintext_bytes)
    digest = hasher.finalize()
    signature = private_key.sign(
        digest,
        utils.Prehashed(chosen_hash)
    )
    return signature.hex()

def save_ciphertext(args):
    """
    Save the ciphertext as a text file.
    """
    ciphertext, algorithm, filename = args
    folder_path = os.path.join("dataset")  # Save all files to 'asymmetric_ciphers' folder
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, filename)
    with open(file_path, "w") as file:
        file.write(ciphertext)

class Generation:
    def __init__(self):
        self.max_workers = os.cpu_count()
        self.sample_counter = 1

    def encrypt_with_pkcs1_v15_bulk(self, plaintexts, key_size: int):
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(rsa_encrypt_pkcs1_v15, key_size, p)
                for p in plaintexts
            ]
            results = [f.result() for f in futures]
        return results

    def encrypt_with_oaep_bulk(self, plaintexts, key_size: int):
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(rsa_encrypt_oaep, key_size, p)
                for p in plaintexts
            ]
            results = [f.result() for f in futures]
        return results

    def ecc_encrypt_batch(self, plaintexts):
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(ecc_sign, plaintext)
                for plaintext in plaintexts
            ]
            results = [f.result() for f in futures]
        return results

    def dsa_encrypt_batch(self, plaintexts):
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(dsa_sign, plaintext)
                for plaintext in plaintexts
            ]
            results = [f.result() for f in futures]
        return results

    def process_batch(self, batch_plaintexts, batch_idx):
        batch_size = len(batch_plaintexts)

        # RSA PKCS1_v1_5 Encryption
        rsa_1024_pkcs1_results = self.encrypt_with_pkcs1_v15_bulk(batch_plaintexts, 1024)

        # RSA OAEP Encryption
        rsa_2048_oaep_results = self.encrypt_with_oaep_bulk(batch_plaintexts, 2048)

        # ECC Encryption (Signature)
        ecc_results = self.ecc_encrypt_batch(batch_plaintexts)

        # DSA Encryption (Signature)
        dsa_results = self.dsa_encrypt_batch(batch_plaintexts)

        save_tasks = []
        for pkcs1, oaep, ecc_sig, dsa_sig in zip(
                rsa_1024_pkcs1_results, rsa_2048_oaep_results, ecc_results, dsa_results):
            save_tasks.extend([
                (pkcs1, "RSA_PKCS1_v15_1024", f"Sample_{self.sample_counter}.txt"),
                (oaep, "RSA_OAEP_2048", f"Sample_{self.sample_counter + 1}.txt"),
                (ecc_sig, "ECC", f"Sample_{self.sample_counter + 2}.txt"),
                (dsa_sig, "DSA", f"Sample_{self.sample_counter + 3}.txt"),
            ])
            self.sample_counter += 4

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(save_ciphertext, args) for args in save_tasks]
            for f in as_completed(futures):
                pass

    def encrypt_and_save(self, num_samples):
        batch_size = 256
        dataset = CryptoDataset(num_samples, plaintext_length=190)
        all_samples = [dataset[i] for i in range(len(dataset))]

        with tqdm(total=num_samples) as pbar:
            for batch_idx, batch_plaintexts in enumerate(chunked_iterable(all_samples, batch_size)):
                self.process_batch(batch_plaintexts, batch_idx)
                pbar.update(len(batch_plaintexts))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encrypt plaintexts using various algorithms.")
    parser.add_argument('--num_samples', type=int, default=10001,
                        help='Number of samples to generate for each algorithm.')
    args = parser.parse_args()
    generator = Generation()
    generator.encrypt_and_save(args.num_samples)
    print("Ciphertexts have been saved as text files.")
