# TorpedoX  

**TorpedoX** is an AI-powered tool designed to identify cryptographic algorithms and hash functions. It leverages advanced machine learning techniques to classify and analyze both classical and modern ciphers with high accuracy.  

## Multi-Layer Approach in TorpedoX  

TorpedoX utilizes a **Multi-Layered approach** to classify and analyze cryptographic data provided by the user. The system works step-by-step to identify the exact algorithm or hash function used, ensuring accuracy and efficiency. The process is outlined below:  

### Step 1: Input File  
The user provides a file containing **hexadecimal values (hex values)** for analysis.  

---

### Layer 1: Hash or Ciphertext Detection  
- The first model determines whether the input hex data represents a **hash** or **ciphertext**.  
  - **If Hash** → The system proceeds to detect the specific hashing algorithm (e.g., SHA-1, SHA-256, RIPEMD, etc.).  
  - **If Ciphertext** → It advances to Layer 2.  

---

### Layer 2: Classical or Modern Cipher Detection  
- If the input is ciphertext, this layer determines whether the encryption algorithm is:  
  - **Classical Cipher** → Classical cipher detection models classify the cipher (e.g., Vigenère, Playfair, One-Time Pad, etc.).  
  - **Modern Cipher** → The process moves to Layer 3.  

---

### Layer 3: Symmetric or Asymmetric Cipher Classification  
- If the input belongs to modern cryptography, this layer determines whether the cipher is:  
  - **Symmetric Encryption** → Moves to Layer 4 for further classification.  
  - **Asymmetric Encryption** → Directly classifies the specific asymmetric algorithm (e.g., RSA, ECDSA, DSA, Paillier, ElGamal, etc.).  

---

### Layer 4: Block or Stream Cipher Classification  
- If the cipher is symmetric, this layer identifies whether it is:  
  - **Block Cipher** → Proceeds to Layer 5 to narrow down the exact block cipher algorithm.  
  - **Stream Cipher** → Proceeds to Layer 5 to identify the stream cipher algorithm.  

---

### Layer 5: Algorithm Detection  
- Based on the results from the previous layers, TorpedoX performs a final classification to accurately identify the specific algorithm used:  
  - **Block Ciphers**: AES, DES, Blowfish, Twofish, etc.  
  - **Stream Ciphers**: ChaCha20, Salsa20, etc.  

---

### Classification into Modes  
Once the algorithm is identified, TorpedoX further classifies the encryption algorithm into one of six modes of operation:  
1. **Electronic Codebook (ECB)**  
2. **Cipher Block Chaining (CBC)**  
3. **Counter Mode (CTR)**  
4. **Output Feedback (OFB)**  
5. **Cipher Feedback (CFB)**  
6. **Galois/Counter Mode (GCM)**  

This additional classification ensures deeper insights into the cryptographic method and its configuration.  

---

### Summary  
This **layered approach** ensures that TorpedoX delivers precise and reliable cryptographic algorithm identification, making it a powerful tool for cryptography and cybersecurity professionals.  
