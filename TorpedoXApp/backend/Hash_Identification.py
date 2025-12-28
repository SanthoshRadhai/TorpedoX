import re
import sys

def identify_hash(hash_string):
    hash_patterns = {
        'MD5': re.compile(r'^[a-f0-9]{32}$', re.IGNORECASE),
        'SHA-1': re.compile(r'^[a-f0-9]{40}$', re.IGNORECASE),
        'SHA-256': re.compile(r'^[a-f0-9]{64}$', re.IGNORECASE),
        'SHA-384': re.compile(r'^[a-f0-9]{96}$', re.IGNORECASE),
        'SHA-512': re.compile(r'^[a-f0-9]{128}$', re.IGNORECASE),
        'BLAKE2b': re.compile(r'^[a-f0-9]{128}$', re.IGNORECASE),
        'BLAKE2s': re.compile(r'^[a-f0-9]{64}$', re.IGNORECASE),
        'RIPEMD-160': re.compile(r'^[a-f0-9]{40}$', re.IGNORECASE),
        'HMAC-SHA256': re.compile(r'^[a-f0-9]{64}$', re.IGNORECASE),
    }

    for hash_name, pattern in hash_patterns.items():
        if pattern.match(hash_string):
            return hash_name

    return "Not Found"

if __name__ == "__main__":
    # Get the input text (the hash string) from command-line arguments
    if len(sys.argv) < 2:
        print("Error: No input provided.")
        sys.exit(1)

    hash_string = sys.argv[1].strip()  # Read the argument from the command line

    # Identify the hash algorithm
    result = identify_hash(hash_string)

    # Output the result
    print(f"Hash Algorithm: {result}")
