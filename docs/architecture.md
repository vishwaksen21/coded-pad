# Architecture Overview — Coded Pad

Coded Pad is a zero-friction, end-to-end encrypted notepad designed for fast web deployment.

## Key Design Principles
1. **Zero Registration**: Users identify notes solely by their secret code.
2. **Deterministic Cryptography**: The secret code serves as the pre-image for the lookup hash and encryption key.
3. **Database Independence**: Operates transparently with SQLite locally and PostgreSQL (Neon) in serverless environments.

## Database Strategy
- **Development**: Local SQLite (`notes.db`), initialized automatically on boot.
- **Production**: PostgreSQL via `DATABASE_URL` with a 15-second connect timeout to handle serverless cold starts.

## Editor Frontend (v3.0 UI)
- Complete design system with CSS custom properties and instant theme switching.
- Dynamic typography switching across Inter (Sans), Lora (Serif), and JetBrains Mono.
- Distraction-free Zen writing mode with unobtrusive floating exit controls.
- Live word, character, and line counting with estimated reading times.
- Tabular numeric formatting (`font-variant-numeric: tabular-nums`) preventing layout shift.
- Floating toast notification system for instant feedback.

## Cryptographic Performance
AES-256-CBC throughput benchmark script provided in `scripts/benchmark.py`.
Typical throughput: >10,000 ops/second for 10KB payloads on modern CPUs.

## Accessibility (a11y)
- Live screen reader feedback using `aria-live="polite"` on save status.
- WCAG AA compliant contrast ratio for all text elements.
- `:focus-visible` styling preserving keyboard accessibility.
