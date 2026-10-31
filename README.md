# 🔒 Coded Pad v3.0

> Sleek, zero-friction, end-to-end encrypted notepad with instant serverless sync. No account, email, or password required—your secret code is your key.

![Coded Pad Banner](https://img.shields.io/badge/encryption-AES--256--CBC-blue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Python](https://img.shields.io/badge/python-3.11-brightgreen?style=flat-square)
![Release](https://img.shields.io/badge/release-v3.0.0-purple?style=flat-square)

---

## ✨ Features

- 🔑 **Zero Authentication**: Access or create notes instantly using any secret code.
- 🛡️ **AES-256-CBC Encryption**: Notes are deterministically encrypted with per-save cryptographically secure random IVs.
- 🌓 **Design System & Theming**: Native Dark Mode, Light Mode, and System Theme adapter with instant toggle.
- ✍️ **Dynamic Typography**: Switch seamlessly between **Sans** (Inter), **Serif** (Lora), and **Mono** (JetBrains Mono).
- 🔲 **Zen Distraction-Free Mode**: Fullscreen writing canvas hiding all toolbars and UI distractions.
- 📊 **Live Note Metrics**: Real-time word counter, character counter, line counter, and reading time estimation.
- 🎲 **Memorable Key Generator**: One-click generation of phonetic secret keys (e.g. `emerald-lynx-42`).
- 📥 **Export Options**: Export notes directly to Markdown (`.md`) or Plain Text (`.txt`).
- ☁️ **Serverless Dual-Database**: Operates transparently on local **SQLite** and cloud **PostgreSQL** (Neon).

---

## 🚀 Quickstart

### Prerequisites
- Python 3.11+
- Virtualenv or pip

### Local Setup
```bash
# Clone the repository
git clone https://github.com/vishwaksen21/coded-pad.git
cd coded-pad

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run local development server
python app.py
```
Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `⌘ + S` / `Ctrl + S` | Save note immediately |
| `⌘ + Shift + F` / `Ctrl + Shift + F` | Toggle Zen distraction-free mode |
| `Escape` | Exit Zen mode or dismiss modals/menus |

---

## 🔒 Security Architecture

Please consult [docs/security.md](docs/security.md) for full cryptographic specification and threat models.

---

*Coded Pad v3.0 — Crafted with Flask, Cryptography & Modern CSS.*
