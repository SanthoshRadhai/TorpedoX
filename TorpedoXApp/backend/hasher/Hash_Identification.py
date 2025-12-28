import re

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
    file_path = input("Insert the file:")
    try:
        with open(file_path, 'r') as file:
            user_input = file.read().strip()
            result = identify_hash(user_input)
            print(f"Hash Algorithm: {result}")
    except FileNotFoundError:
        print("File not found. Please check the file path and try again.")