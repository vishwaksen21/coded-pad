# Coded Pad — Modern UI Design System (v3.0)

## Design Tokens & Variables
Coded Pad implements a structured CSS Custom Properties design system supporting automatic and manual light/dark theming.

### Colors
- `--bg`: Root page background color.
- `--surface`: Elevated container / card background.
- `--surface-hover`: Subtle hover state background for interactive items.
- `--border`: Crisp 1px border separator.
- `--primary`: Vibrant primary blue accent (`#3b82f6`).
- `--text`: High-contrast foreground typography.
- `--text-muted`: Secondary metadata and helper labels.

### Typography
- **Sans-Serif**: `Inter`, system-ui.
- **Serif**: `Lora`, Georgia.
- **Monospace**: `JetBrains Mono`, Courier.

### Components
1. **Brand Bar**: Logo with lock glyph, responsive secret code pill.
2. **Editor Canvas**: Spacious textarea with customizable fonts and generous margins.
3. **Pills & Badges**: Tabular numeric counters and status pills.
4. **Toast Alerts**: Non-intrusive floating feedback messages at bottom right.
5. **Zen Mode**: Complete distraction elimination for pure writing focus.

### Mobile Compact Responsive Architecture
- **Safe Area Insets**: Native support for iPhone notches and dynamic home indicator bars via `env(safe-area-inset-*)` and `viewport-fit=cover`.
- **Ultra-Compact Mobile Top Bar**: Streamlines toolbar to 34px touch icon buttons (`Aa▾`, `📥▾`, `📋`, `💾 Save`, `🌓`, `🔲`) with a compact key pill displaying truncated keys with tap-to-copy.
- **Dynamic Viewport Unit (`100dvh`)**: Automatically accommodates mobile browser address bar collapse/expand.
- **Zero iOS Safari Zoom**: Enforces 16px (`1rem`) font sizing on inputs and textareas to avoid disruptive iOS auto-zoom behavior on focus.
- **Slim Single-Line Bottom Bar**: Mobile status bar collapses verbose metadata while keeping live word & character counts accessible without wasting writing space.
