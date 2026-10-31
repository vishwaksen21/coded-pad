# Changelog

All notable changes to Coded Pad are documented in this file.

## [3.0.0] - 2026-10-31
### Added
- Complete UI Design System overhaul with CSS custom properties.
- Light, Dark, and System theme switcher with instant switching and local storage persistence.
- Typography switcher supporting Inter (Sans), Lora (Serif), and JetBrains Mono (Monospace).
- Zen distraction-free fullscreen writing mode with escape handling and exit pill.
- Real-time text metrics engine (word count, character count, line count, reading time).
- Memorable phonetic slug key generator on homepage (e.g. `cosmic-falcon-73`).
- Password visibility toggle (show/hide code) for secret key input.
- Export note menu supporting Markdown (`.md`) and Plain Text (`.txt`) downloads.
- Non-intrusive floating toast notification system for feedback alerts.
- Client-side Recent Pads history storage on homepage.
- Clear note confirmation modal dialog preventing accidental data loss.

### Changed
- Elevated homepage with ambient glow, modern card elevation, and responsive feature pills.
- Re-architected pad header toolbar with modular dropdowns and button groups.
- Tabular numeric rendering across all status counters to eliminate layout shifts.

### Security & Performance
- Verified AES-256-CBC cipher with PKCS7 padding and per-save random 16-byte IV.
- Hardened database connection pool lifecycle for serverless deployments.
- Full regression and UI contract test coverage.

## [2.0.0] - 2026-10-24
### Summary
- Streamlined single secret-code note creation & lookup flow.
- AES-256-CBC authenticated encryption with per-save random IV.
- Live editor statistics and quick clipboard copy.
- SQLite and Neon PostgreSQL dual-database abstraction.

## [1.0.0] - 2026-05-08
### Initial Release
- Initial deployment of serverless encrypted notepad on Vercel.
