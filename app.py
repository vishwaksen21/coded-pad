"""
Coded Pad — Secure Note App (Vercel + Neon compatible)
=======================================================
- Local : SQLite
- Vercel: PostgreSQL via DATABASE_URL environment variable
"""

import os
import hashlib
import base64
from datetime import datetime

from flask import Flask, render_template, request, jsonify, redirect, url_for

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# ─────────────────────────────────────────────────────
# App Setup
# ─────────────────────────────────────────────────────

app = Flask(__name__)

# Use PostgreSQL on Vercel, SQLite locally
DATABASE_URL = os.environ.get("DATABASE_URL", "")
USE_POSTGRES = bool(DATABASE_URL)

# Remove unsupported channel_binding parameter
if USE_POSTGRES and "channel_binding" in DATABASE_URL:
    import urllib.parse as _up

    parsed = _up.urlparse(DATABASE_URL)
    qs = _up.parse_qs(parsed.query)

    qs.pop("channel_binding", None)

    new_qs = _up.urlencode({k: v[0] for k, v in qs.items()})

    DATABASE_URL = _up.urlunparse(
        parsed._replace(query=new_qs)
    )

# ─────────────────────────────────────────────────────
# Database Helpers
# ─────────────────────────────────────────────────────

def get_db():

    if USE_POSTGRES:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        return psycopg2.connect(
            DATABASE_URL,
            cursor_factory=RealDictCursor,
            connect_timeout=15
        )

    else:
        import sqlite3

        conn = sqlite3.connect("notes.db")
        conn.row_factory = sqlite3.Row

        return conn


def init_db():

    conn = get_db()

    query = """
        CREATE TABLE IF NOT EXISTS notes (
            code_hash TEXT PRIMARY KEY,
            encrypted_note TEXT NOT NULL DEFAULT '',
            iv TEXT NOT NULL DEFAULT '',
            created_time TEXT NOT NULL,
            updated_time TEXT NOT NULL
        )
    """

    if USE_POSTGRES:
        cur = conn.cursor()
        cur.execute(query)
    else:
        conn.execute(query)

    conn.commit()
    conn.close()


# Initialize DB only for local SQLite
if not USE_POSTGRES:
    try:
        init_db()
    except Exception as e:
        print("Database Init Error:", e)

# ─────────────────────────────────────────────────────
# Encryption Helpers
# ─────────────────────────────────────────────────────

def hash_code(secret_code):

    return hashlib.sha256(
        secret_code.encode("utf-8")
    ).hexdigest()


def derive_key(secret_code):

    return hashlib.sha256(
        secret_code.encode("utf-8")
    ).digest()


def encrypt_note(plain_text, secret_code):

    key = derive_key(secret_code)

    iv = os.urandom(16)

    padder = padding.PKCS7(128).padder()

    padded_data = (
        padder.update(plain_text.encode("utf-8"))
        + padder.finalize()
    )

    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )

    encryptor = cipher.encryptor()

    encrypted_data = (
        encryptor.update(padded_data)
        + encryptor.finalize()
    )

    return (
        base64.b64encode(encrypted_data).decode(),
        base64.b64encode(iv).decode()
    )


def decrypt_note(encrypted_b64, iv_b64, secret_code):

    try:

        if not encrypted_b64 or not iv_b64:
            return ""

        key = derive_key(secret_code)

        iv = base64.b64decode(iv_b64)

        encrypted_data = base64.b64decode(encrypted_b64)

        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )

        decryptor = cipher.decryptor()

        padded_plain = (
            decryptor.update(encrypted_data)
            + decryptor.finalize()
        )

        unpadder = padding.PKCS7(128).unpadder()

        plain_text = (
            unpadder.update(padded_plain)
            + unpadder.finalize()
        )

        return plain_text.decode("utf-8")

    except Exception:
        return ""

# ─────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────

@app.route("/")
def home():

    return render_template("index.html")


@app.route("/open", methods=["POST"])
def open_pad():

    secret_code = request.form.get(
        "secret_code",
        ""
    ).strip()

    if len(secret_code) < 3:
        return redirect(url_for("home"))

    code_hash = hash_code(secret_code)

    now = datetime.utcnow().strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    conn = get_db()

    try:

        if USE_POSTGRES:

            cur = conn.cursor()

            cur.execute(
                "SELECT code_hash FROM notes WHERE code_hash = %s",
                (code_hash,)
            )

            row = cur.fetchone()

            if row is None:

                cur.execute(
                    """
                    INSERT INTO notes
                    (code_hash, encrypted_note, iv, created_time, updated_time)
                    VALUES (%s, '', '', %s, %s)
                    """,
                    (code_hash, now, now)
                )

        else:

            row = conn.execute(
                "SELECT code_hash FROM notes WHERE code_hash = ?",
                (code_hash,)
            ).fetchone()

            if row is None:

                conn.execute(
                    """
                    INSERT INTO notes
                    (code_hash, encrypted_note, iv, created_time, updated_time)
                    VALUES (?, '', '', ?, ?)
                    """,
                    (code_hash, now, now)
                )

        conn.commit()

    finally:
        conn.close()

    return redirect(
        url_for(
            "pad_page",
            secret_code=secret_code
        )
    )


@app.route("/pad/<secret_code>")
def pad_page(secret_code):

    code_hash = hash_code(secret_code)

    conn = get_db()

    try:

        if USE_POSTGRES:

            cur = conn.cursor()

            cur.execute(
                """
                SELECT encrypted_note, iv, created_time, updated_time
                FROM notes
                WHERE code_hash = %s
                """,
                (code_hash,)
            )

            row = cur.fetchone()

        else:

            row = conn.execute(
                """
                SELECT encrypted_note, iv, created_time, updated_time
                FROM notes
                WHERE code_hash = ?
                """,
                (code_hash,)
            ).fetchone()

    finally:
        conn.close()

    if row is None:
        return redirect(url_for("home"))

    note_text = decrypt_note(
        row["encrypted_note"],
        row["iv"],
        secret_code
    )

    return render_template(
        "pad.html",
        note=note_text,
        secret_code=secret_code,
        created_time=row["created_time"],
        updated_time=row["updated_time"]
    )


@app.route("/api/save", methods=["POST"])
def api_save():

    # FIXED
    data = request.get_json() or {}

    secret_code = data.get(
        "secret_code",
        ""
    ).strip()

    note_text = data.get(
        "note",
        ""
    )

    if not secret_code:
        return jsonify({
            "success": False,
            "error": "Missing secret code."
        }), 400

    code_hash = hash_code(secret_code)

    now = datetime.utcnow().strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    encrypted_note, iv = encrypt_note(
        note_text,
        secret_code
    )

    conn = get_db()

    try:

        if USE_POSTGRES:

            cur = conn.cursor()

            cur.execute(
                """
                UPDATE notes
                SET encrypted_note = %s,
                    iv = %s,
                    updated_time = %s
                WHERE code_hash = %s
                """,
                (
                    encrypted_note,
                    iv,
                    now,
                    code_hash
                )
            )

        else:

            conn.execute(
                """
                UPDATE notes
                SET encrypted_note = ?,
                    iv = ?,
                    updated_time = ?
                WHERE code_hash = ?
                """,
                (
                    encrypted_note,
                    iv,
                    now,
                    code_hash
                )
            )

        conn.commit()

    finally:
        conn.close()

    return jsonify({
        "success": True,
        "updated": now
    })

# ─────────────────────────────────────────────────────
# Run App
# ─────────────────────────────────────────────────────

if __name__ == "__main__":

    print("=" * 50)
    print("Coded Pad is running!")
    print("Open: http://127.0.0.1:5000")
    print("=" * 50)

    # FIXED
    app.run(debug=False)