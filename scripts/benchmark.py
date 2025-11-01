import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import encrypt_note, decrypt_note

def benchmark_crypto(iterations=1000, payload_kb=10):
    payload = "A" * (payload_kb * 1024)
    code = "benchmark-secret-key-2026"

    start = time.perf_counter()
    for _ in range(iterations):
        enc, iv = encrypt_note(payload, code)
    enc_duration = time.perf_counter() - start

    enc, iv = encrypt_note(payload, code)
    start = time.perf_counter()
    for _ in range(iterations):
        decrypted = decrypt_note(enc, iv, code)
    dec_duration = time.perf_counter() - start

    print(f"AES-256 Benchmark ({iterations} ops, {payload_kb} KB payload):")
    print(f"  Encryption: {iterations / enc_duration:.2f} ops/sec ({enc_duration/iterations*1000:.3f} ms/op)")
    print(f"  Decryption: {iterations / dec_duration:.2f} ops/sec ({dec_duration/iterations*1000:.3f} ms/op)")

if __name__ == "__main__":
    benchmark_crypto()
