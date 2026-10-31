"""
Coded Pad — Secure Ephemeral Notepad (Vercel + Neon compatible)
===============================================================
- Local : SQLite (notes.db)
- Vercel: PostgreSQL via DATABASE_URL environment variable
"""

import os
import hashlib
import base64
import sqlite3
from datetime import datetime, timezone
from typing import Tuple

from flask import Flask, render_template, request, jsonify, redirect, url_for

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
USE_POSTGRES = bool(DATABASE_URL)
CONNECT_TIMEOUT = 15

def get_db():
    if USE_POSTGRES:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        return psycopg2.connect(
            DATABASE_URL,
            cursor_factory=RealDictCursor,
            connect_timeout=CONNECT_TIMEOUT
        )
    conn = sqlite3.connect("notes.db", timeout=CONNECT_TIMEOUT)
    conn.row_factory = sqlite3.Row
    return conn

def hash_code(secret_code: str) -> str:
    """Generate SHA-256 digest of secret code."""
    return hashlib.sha256(secret_code.encode("utf-8")).hexdigest()

def derive_key(secret_code: str) -> bytes:
    """Derive 256-bit AES key using SHA-256."""
    return hashlib.sha256(secret_code.encode("utf-8")).digest()

def encrypt_note(plain_text: str, secret_code: str) -> Tuple[str, str]:
    """Encrypt note using AES-256-CBC with PKCS7 padding and random IV."""
    key = derive_key(secret_code)
    iv = os.urandom(16)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plain_text.encode("utf-8")) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(encrypted_data).decode(), base64.b64encode(iv).decode()

def decrypt_note(encrypted_b64: str, iv_b64: str, secret_code: str) -> str:
    """Decrypt base64-encoded ciphertext using AES-256-CBC and unpad."""
    try:
        if not encrypted_b64 or not iv_b64:
            return ""
        key = derive_key(secret_code)
        iv = base64.b64decode(iv_b64)
        encrypted_data = base64.b64decode(encrypted_b64)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plain = decryptor.update(encrypted_data) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        plain_text = unpadder.update(padded_plain) + unpadder.finalize()
        return plain_text.decode("utf-8", errors="replace")
    except Exception:
        return ""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/open", methods=["POST"])
def open_pad():
    secret_code = request.form.get("secret_code", "").strip()
    if len(secret_code) < 3:
        return redirect(url_for("home"))

    code_hash = hash_code(secret_code)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    conn = get_db()
    try:
        if USE_POSTGRES:
            cur = conn.cursor()
            cur.execute("SELECT code_hash FROM notes WHERE code_hash = %s", (code_hash,))
            if cur.fetchone() is None:
                cur.execute(
                    "INSERT INTO notes (code_hash, encrypted_note, iv, created_time, updated_time) VALUES (%s, '', '', %s, %s)",
                    (code_hash, now, now)
                )
        else:
            row = conn.execute("SELECT code_hash FROM notes WHERE code_hash = ?", (code_hash,)).fetchone()
            if row is None:
                conn.execute(
                    "INSERT INTO notes (code_hash, encrypted_note, iv, created_time, updated_time) VALUES (?, '', '', ?, ?)",
                    (code_hash, now, now)
                )
        conn.commit()
    except Exception:
        return jsonify({"success": False, "error": "Database error while opening note."}), 500
    finally:
        conn.close()

    return redirect(url_for("pad_page", secret_code=secret_code))

@app.route("/pad/<secret_code>")
def pad_page(secret_code):
    code_hash = hash_code(secret_code)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    conn = get_db()
    try:
        if USE_POSTGRES:
            cur = conn.cursor()
            cur.execute("SELECT encrypted_note, iv, created_time, updated_time FROM notes WHERE code_hash = %s", (code_hash,))
            row = cur.fetchone()
            if row is None:
                cur.execute(
                    "INSERT INTO notes (code_hash, encrypted_note, iv, created_time, updated_time) VALUES (%s, '', '', %s, %s)",
                    (code_hash, now, now)
                )
                conn.commit()
                row = {"encrypted_note": "", "iv": "", "created_time": now, "updated_time": now}
        else:
            row = conn.execute("SELECT encrypted_note, iv, created_time, updated_time FROM notes WHERE code_hash = ?", (code_hash,)).fetchone()
            if row is None:
                conn.execute(
                    "INSERT INTO notes (code_hash, encrypted_note, iv, created_time, updated_time) VALUES (?, '', '', ?, ?)",
                    (code_hash, now, now)
                )
                conn.commit()
                row = {"encrypted_note": "", "iv": "", "created_time": now, "updated_time": now}
    finally:
        conn.close()

    note_text = decrypt_note(row["encrypted_note"], row["iv"], secret_code)
    return render_template(
        "pad.html",
        note=note_text,
        secret_code=secret_code,
        created_time=row["created_time"],
        updated_time=row["updated_time"]
    )

@app.route("/api/health")
def api_health():
    return jsonify({
        "status": "ok",
        "database": "postgres" if USE_POSTGRES else "sqlite",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    })

@app.route("/api/save", methods=["POST"])
def api_save():
    data = request.get_json(silent=True) or {}
    secret_code = data.get("secret_code", "").strip()
    note_text = data.get("note", "")

    if not secret_code:
        return jsonify({"success": False, "error": "Missing secret code."}), 400

    max_note_length = 500_000
    if len(note_text) > max_note_length:
        return jsonify({"success": False, "error": f"Note exceeds maximum allowed size of {max_note_length} characters."}), 413

    code_hash = hash_code(secret_code)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    encrypted_note, iv = encrypt_note(note_text, secret_code)

    conn = get_db()
    try:
        if USE_POSTGRES:
            cur = conn.cursor()
            cur.execute("""
                UPDATE notes
                SET encrypted_note = %s, iv = %s, updated_time = %s
                WHERE code_hash = %s
            """, (encrypted_note, iv, now, code_hash))
        else:
            conn.execute("""
                UPDATE notes
                SET encrypted_note = ?, iv = ?, updated_time = ?
                WHERE code_hash = ?
            """, (encrypted_note, iv, now, code_hash))
        conn.commit()
    except Exception:
        return jsonify({"success": False, "error": "Database error while saving note."}), 500
    finally:
        conn.close()

    return jsonify({"success": True, "updated": now})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
