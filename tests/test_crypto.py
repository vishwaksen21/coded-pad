import unittest
import hashlib
from app import hash_code, derive_key, encrypt_note, decrypt_note

class TestCryptoHelpers(unittest.TestCase):
    def test_hash_code(self):
        code = "my-secret-test-code"
        expected = hashlib.sha256(code.encode("utf-8")).hexdigest()
        self.assertEqual(hash_code(code), expected)

    def test_derive_key(self):
        code = "my-secret-test-code"
        expected = hashlib.sha256(code.encode("utf-8")).digest()
        self.assertEqual(derive_key(code), expected)
        self.assertEqual(len(derive_key(code)), 32)

    def test_encrypt_decrypt_roundtrip(self):
        code = "user-secret-123"
        note = "Hello, this is a top-secret encrypted note! 🔐"
        encrypted_b64, iv_b64 = encrypt_note(note, code)
        self.assertTrue(bool(encrypted_b64))
        self.assertTrue(bool(iv_b64))
        decrypted = decrypt_note(encrypted_b64, iv_b64, code)
        self.assertEqual(decrypted, note)

    def test_decrypt_with_wrong_code(self):
        code = "correct-code"
        wrong_code = "wrong-code"
        encrypted_b64, iv_b64 = encrypt_note("Sensitive Data", code)
        decrypted = decrypt_note(encrypted_b64, iv_b64, wrong_code)
        self.assertEqual(decrypted, "")

    def test_empty_string_encryption(self):
        code = "any-code"
        encrypted_b64, iv_b64 = encrypt_note("", code)
        self.assertEqual(decrypt_note(encrypted_b64, iv_b64, code), "")

    def test_block_size_multiples(self):
        code = "block-code"
        for size in [16, 32, 64, 128]:
            text = "A" * size
            enc, iv = encrypt_note(text, code)
            dec = decrypt_note(enc, iv, code)
            self.assertEqual(dec, text)

    def test_unicode_and_emojis(self):
        code = "unicode-key-🔑"
        note = "Testing emojis 🚀🎉✨ and complex scripts: 日本語, العربية, தமிழ்"
        enc, iv = encrypt_note(note, code)
        dec = decrypt_note(enc, iv, code)
        self.assertEqual(dec, note)

    def test_non_ascii_secret_code(self):
        code = "пароль-12345"
        note = "Secret note encrypted with Cyrillic key"
        enc, iv = encrypt_note(note, code)
        dec = decrypt_note(enc, iv, code)
        self.assertEqual(dec, note)

    def test_random_iv_uniqueness(self):
        code = "same-code"
        note = "same-note"
        enc1, iv1 = encrypt_note(note, code)
        enc2, iv2 = encrypt_note(note, code)
        self.assertNotEqual(iv1, iv2)
        self.assertNotEqual(enc1, enc2)
        self.assertEqual(decrypt_note(enc1, iv1, code), note)
        self.assertEqual(decrypt_note(enc2, iv2, code), note)

if __name__ == "__main__":
    unittest.main()

# [2025-11-02] test(crypto): add test suite for key derivation and block cipher

# [2025-11-03] test(crypto): test PKCS7 padding boundaries
