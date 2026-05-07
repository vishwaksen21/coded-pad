"""
Coded Pad — Production-ready Flask app
======================================
- Local dev  : uses SQLite (notes.db)
- Vercel/Prod: uses PostgreSQL via DATABASE_URL environment variable

The switch is automatic — if DATABASE_URL is set, PostgreSQL is used.
"""

import os
import hashlib
import base64
from datetime import datetime

from flask import Flask, render_template, request, jsonify, redirect, url_for

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# ─── App Setup ────────────────────────────────────────────────────────────────

app = Flask(__name__)

# DATABASE_URL is set in Vercel environment variables (PostgreSQL connection string)
# If not set, fall back to local SQLite
DATABASE_URL = os.environ.get("DATABASE_URL")
USE_POSTGRES  = DATABASE_URL is not None

# ─── Database helpers ─────────────────────────────────────────────────────────

def get_db():
    """Return a database connection (PostgreSQL or SQLite based on environment)."""
    if USE_POSTGRES:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    else:
        import sqlite3
        conn = sqlite3.connect("notes.db")
        conn.row_factory = sqlite3.Row
        return conn


def db_execute(conn, sql, params=()):
    """
    Run a SQL statement on either Postgres or SQLite.
    Postgres uses %s placeholders; SQLite uses ?.
    This helper converts automatically.
    """
    if USE_POSTGRES:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur
    else:
        return conn.execute(sql, params)


def init_db():
    """Create the notes table if it doesn't exist."""
    conn = get_db()
    # Both SQLite and Postgres support this syntax
    db_execute(conn, """
        CREATE TABLE IF NOT EXISTS notes (
            code_hash      TEXT PRIMARY KEY,
            encrypted_note TEXT NOT NULL DEFAULT '',
            iv             TEXT NOT NULL DEFAULT '',
            created_time   TEXT NOT NULL,
            updated_time   TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# Run table creation at startup (works for both local and Vercel cold starts)
try:
    init_db()
except Exception as e:
    print(f"[init_db] Warning: {e}")

# ─── Encryption helpers ───────────────────────────────────────────────────────

def hash_code(secret_code: str) -> str:
    """SHA-256 hash of the secret code — used as the DB primary key."""
    return hashlib.sha256(secret_code.encode("utf-8")).hexdigest()


def derive_key(secret_code: str) -> bytes:
    """Derive a 32-byte AES key from the secret code."""
    return hashlib.sha256(secret_code.encode("utf-8")).digest()


def encrypt_note(plain_text: str, secret_code: str) -> tuple[str, str]:
    """AES-256-CBC encrypt. Returns (encrypted_b64, iv_b64)."""
    key     = derive_key(secret_code)
    iv      = os.urandom(16)
    padder  = padding.PKCS7(128).padder()
    padded  = padder.update(plain_text.encode("utf-8")) + padder.finalize()
    cipher  = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    enc     = cipher.encryptor()
    data    = enc.update(padded) + enc.finalize()
    return base64.b64encode(data).decode(), base64.b64encode(iv).decode()


def decrypt_note(encrypted_b64: str, iv_b64: str, secret_code: str) -> str:
    """AES-256-CBC decrypt. Returns plain text or '' on error/empty."""
    try:
        if not encrypted_b64 or not iv_b64:
            return ""
        key      = derive_key(secret_code)
        iv       = base64.b64decode(iv_b64)
        data     = base64.b64decode(encrypted_b64)
        cipher   = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        dec      = cipher.decryptor()
        padded   = dec.update(data) + dec.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        plain    = unpadder.update(padded) + unpadder.finalize()
        return plain.decode("utf-8")
    except Exception:
        return ""

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/open", methods=["POST"])
def open_pad():
    """Check/create a note for the given secret code, then redirect to editor."""
    secret_code = request.form.get("secret_code", "").strip()
    if len(secret_code) < 3:
        return redirect(url_for("home"))

    code_hash = hash_code(secret_code)
    now       = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    conn = get_db()
    cur  = db_execute(conn, "SELECT code_hash FROM notes WHERE code_hash = %s" if USE_POSTGRES else
                            "SELECT code_hash FROM notes WHERE code_hash = ?", (code_hash,))
    row  = cur.fetchone() if USE_POSTGRES else conn.execute(
        "SELECT code_hash FROM notes WHERE code_hash = ?", (code_hash,)).fetchone()

    if row is None:
        sql = ("INSERT INTO notes (code_hash, encrypted_note, iv, created_time, updated_time) VALUES (%s,'','', %s, %s)"
               if USE_POSTGRES else
               "INSERT INTO notes (code_hash, encrypted_note, iv, created_time, updated_time) VALUES (?,'','',?,?)")
        db_execute(conn, sql, (code_hash, now, now))
        conn.commit()

    conn.close()
    return redirect(url_for("pad_page", secret_code=secret_code))


@app.route("/pad/<secret_code>")
def pad_page(secret_code: str):
    """Load and decrypt the note, render the editor."""
    code_hash = hash_code(secret_code)

    conn = get_db()
    sql  = ("SELECT encrypted_note, iv, created_time, updated_time FROM notes WHERE code_hash = %s"
            if USE_POSTGRES else
            "SELECT encrypted_note, iv, created_time, updated_time FROM notes WHERE code_hash = ?")
    cur  = db_execute(conn, sql, (code_hash,))
    row  = cur.fetchone() if USE_POSTGRES else cur.fetchone()
    conn.close()

    if row is None:
        return redirect(url_for("home"))

    note_text = decrypt_note(row["encrypted_note"], row["iv"], secret_code)

    return render_template(
        "pad.html",
        note         = note_text,
        secret_code  = secret_code,
        created_time = row["created_time"],
        updated_time = row["updated_time"],
    )


@app.route("/api/save", methods=["POST"])
def api_save():
    """Encrypt and save the note content."""
    data        = request.get_json()
    secret_code = data.get("secret_code", "").strip()
    note_text   = data.get("note", "")

    if not secret_code:
        return jsonify({"success": False, "error": "Missing secret code."}), 400

    code_hash     = hash_code(secret_code)
    now           = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    encrypted, iv = encrypt_note(note_text, secret_code)

    conn = get_db()
    sql  = ("UPDATE notes SET encrypted_note = %s, iv = %s, updated_time = %s WHERE code_hash = %s"
            if USE_POSTGRES else
            "UPDATE notes SET encrypted_note = ?, iv = ?, updated_time = ? WHERE code_hash = ?")
    db_execute(conn, sql, (encrypted, iv, now, code_hash))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "updated": now})


# ─── Entry Point (local dev only) ────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  Coded Pad is running!")
    print("  Open: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True)
