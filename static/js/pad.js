/**
 * pad.js — Interactive controls, autosave, themes, typography, export & Zen mode.
 * Coded Pad v3.0 Modern UI
 */

const noteArea       = document.getElementById("noteArea");
const saveBtn        = document.getElementById("saveBtn");
const copyBtn        = document.getElementById("copyBtn");
const saveStatus     = document.getElementById("saveStatus");
const statusDot      = document.querySelector(".status-dot");
const updatedTime    = document.getElementById("updatedTime");
const charCount      = document.getElementById("charCount");
const wordCount      = document.getElementById("wordCount");
const lineCount      = document.getElementById("lineCount");
const readTime       = document.getElementById("readTime");
const toastContainer = document.getElementById("toastContainer");
const padBody        = document.getElementById("padBody");
const fontLabel      = document.getElementById("fontLabel");
const themeIcon      = document.getElementById("themeIcon");

let autoSaveTimer = null;
let isSaving = false;
let hasUnsavedChanges = false;

// ── Toast Notification System ────────────────────────────────────────────────
function showToast(message, type = "info", duration = 2800) {
    if (!toastContainer) return;
    const toast = document.createElement("div");
    toast.className = `toast-item toast-${type}`;
    const icon = type === "success" ? "✓" : type === "error" ? "⚠" : "ℹ";
    toast.innerHTML = `<span class="toast-icon">${icon}</span><span class="toast-text">${message}</span>`;
    toastContainer.appendChild(toast);
    setTimeout(() => {
        toast.classList.add("toast-fade-out");
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ── Copy Note Content ────────────────────────────────────────────────────────
async function copyNoteContent() {
    if (!noteArea) return;
    try {
        await navigator.clipboard.writeText(noteArea.value);
        showToast("Note copied to clipboard", "success");
    } catch {
        noteArea.select();
        document.execCommand("copy");
        window.getSelection()?.removeAllRanges();
        showToast("Note copied to clipboard", "success");
    }
    if (copyBtn) {
        const orig = copyBtn.textContent;
        copyBtn.textContent = "Copied!";
        copyBtn.classList.add("copied");
        setTimeout(() => {
            copyBtn.textContent = orig;
            copyBtn.classList.remove("copied");
        }, 1800);
    }
}

// ── Copy Secret Code ─────────────────────────────────────────────────────────
async function copySecretCode() {
    try {
        await navigator.clipboard.writeText(SECRET_CODE);
        showToast("Secret key copied to clipboard", "success");
    } catch {
        showToast("Key: " + SECRET_CODE, "info");
    }
}

// ── Typography Switcher ──────────────────────────────────────────────────────
const FONTS = {
    sans: { label: "Sans", class: "font-sans" },
    serif: { label: "Serif", class: "font-serif" },
    mono: { label: "Mono", class: "font-mono" }
};

function setFontFamily(fontKey) {
    if (!FONTS[fontKey]) return;
    padBody.classList.remove("font-sans", "font-serif", "font-mono");
    padBody.classList.add(FONTS[fontKey].class);
    if (fontLabel) fontLabel.textContent = FONTS[fontKey].label;
    localStorage.setItem("codedpad_font", fontKey);
    document.querySelectorAll("#fontMenu .dropdown-item").forEach(item => {
        item.classList.toggle("active", item.dataset.font === fontKey);
    });
    closeDropdowns();
}

function initFont() {
    const saved = localStorage.getItem("codedpad_font") || "sans";
    setFontFamily(saved);
}

// ── Theme Switcher ───────────────────────────────────────────────────────────
const THEMES = ["system", "light", "dark"];
function cycleTheme() {
    const current = localStorage.getItem("codedpad_theme") || "system";
    const next = THEMES[(THEMES.indexOf(current) + 1) % THEMES.length];
    applyTheme(next);
}

function applyTheme(theme) {
    localStorage.setItem("codedpad_theme", theme);
    document.documentElement.removeAttribute("data-theme");
    if (theme === "dark") {
        document.documentElement.setAttribute("data-theme", "dark");
        if (themeIcon) themeIcon.textContent = "🌙";
    } else if (theme === "light") {
        document.documentElement.setAttribute("data-theme", "light");
        if (themeIcon) themeIcon.textContent = "☀️";
    } else {
        if (themeIcon) themeIcon.textContent = "🌓";
    }
    showToast(`Theme: ${theme.toUpperCase()}`, "info", 1500);
}

function initTheme() {
    const saved = localStorage.getItem("codedpad_theme") || "system";
    applyTheme(saved);
}

// ── Zen Mode Toggle ──────────────────────────────────────────────────────────
function toggleZenMode() {
    const isZen = padBody.classList.toggle("zen-mode");
    if (isZen) {
        showToast("Zen mode activated (Press Esc to exit)", "info", 2000);
    }
}

// ── Export Note ──────────────────────────────────────────────────────────────
function exportNote(format) {
    if (!noteArea) return;
    const content = noteArea.value;
    const mime = format === "md" ? "text/markdown" : "text/plain";
    const ext = format === "md" ? "md" : "txt";
    const filename = `coded-pad-${SECRET_CODE}.${ext}`;

    const blob = new Blob([content], { type: `${mime};charset=utf-8` });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    closeDropdowns();
    showToast(`Exported as ${ext.toUpperCase()}`, "success");
}

// ── Clear Note Modal ─────────────────────────────────────────────────────────
function confirmClearNote() {
    closeDropdowns();
    const modal = document.getElementById("clearModal");
    if (modal) modal.style.display = "flex";
}

function closeClearModal() {
    const modal = document.getElementById("clearModal");
    if (modal) modal.style.display = "none";
}

function executeClearNote() {
    if (noteArea) {
        noteArea.value = "";
        updateStats();
        setStatus("Cleared (Unsaved)", false);
        hasUnsavedChanges = true;
    }
    closeClearModal();
    showToast("Note content cleared", "warning");
}

// ── Dropdown Controls ────────────────────────────────────────────────────────
function toggleFontMenu() {
    const menu = document.getElementById("fontMenu");
    const isOpen = menu.classList.contains("show");
    closeDropdowns();
    if (!isOpen) menu.classList.add("show");
}

function toggleExportMenu() {
    const menu = document.getElementById("exportMenu");
    const isOpen = menu.classList.contains("show");
    closeDropdowns();
    if (!isOpen) menu.classList.add("show");
}

function closeDropdowns() {
    document.querySelectorAll(".dropdown-menu").forEach(m => m.classList.remove("show"));
}

window.addEventListener("click", (e) => {
    if (!e.target.closest(".dropdown-wrap")) {
        closeDropdowns();
    }
});

// ── Update Statistics ────────────────────────────────────────────────────────
function updateStats() {
    if (!noteArea) return;
    const text = noteArea.value;
    const chars = text.length;
    const words = text.trim() === "" ? 0 : text.trim().split(/\s+/).length;
    const lines = text === "" ? 0 : text.split("\n").length;
    const minutes = Math.max(1, Math.ceil(words / 200));

    if (charCount) charCount.textContent = `${chars} character${chars === 1 ? "" : "s"}`;
    if (wordCount) wordCount.textContent = `${words} word${words === 1 ? "" : "s"}`;
    if (lineCount) lineCount.textContent = `${lines} line${lines === 1 ? "" : "s"}`;
    if (readTime) readTime.textContent = `~${minutes} min read`;
}

// ── Input & Autosave ─────────────────────────────────────────────────────────
noteArea.addEventListener("input", () => {
    updateStats();
    hasUnsavedChanges = true;
    setStatus("Unsaved changes...", false);
    clearTimeout(autoSaveTimer);
    autoSaveTimer = setTimeout(saveNote, 3000);
});

// ── Keyboard Shortcuts ───────────────────────────────────────────────────────
document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && (e.key === "s" || e.key === "S")) {
        e.preventDefault();
        if (!isSaving) saveNote();
    }
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === "f" || e.key === "F")) {
        e.preventDefault();
        toggleZenMode();
    }
    if (e.key === "Escape") {
        if (padBody.classList.contains("zen-mode")) {
            padBody.classList.remove("zen-mode");
        }
        closeClearModal();
        closeDropdowns();
    }
});

// ── Core Save ────────────────────────────────────────────────────────────────
async function saveNote() {
    if (isSaving) return;
    clearTimeout(autoSaveTimer);
    autoSaveTimer = null;
    isSaving = true;

    saveBtn.disabled = true;
    saveBtn.classList.add("btn-loading");
    setStatus("Saving...", false);

    try {
        const response = await fetch("/api/save", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                secret_code: SECRET_CODE,
                note: noteArea.value
            })
        });

        const data = await response.json();
        if (data.success) {
            hasUnsavedChanges = false;
            setStatus("All changes saved", true);
            if (updatedTime) updatedTime.textContent = "Last saved: " + data.updated;
            showToast("Saved to encrypted storage", "success", 2000);
        } else {
            setStatus("⚠ Save failed", false);
            showToast("Save failed: " + (data.error || "Unknown error"), "error");
        }
    } catch {
        setStatus("⚠ Network error", false);
        showToast("Network error. Retrying later...", "error");
    } finally {
        isSaving = false;
        saveBtn.disabled = false;
        saveBtn.classList.remove("btn-loading");
    }
}

// ── Status Helper ────────────────────────────────────────────────────────────
function setStatus(msg, ok) {
    if (!saveStatus) return;
    saveStatus.textContent = msg;
    if (statusDot) {
        statusDot.className = "status-dot " + (ok ? "dot-saved" : "dot-unsaved");
    }
}

// ── Guard Unsaved Changes ────────────────────────────────────────────────────
window.addEventListener("beforeunload", (e) => {
    if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = "";
    }
});

// ── Initialization ───────────────────────────────────────────────────────────
initTheme();
initFont();
updateStats();

/* [2025-12-02] feat(editor): prevent overlapping background save requests */

/* [2025-12-03] feat(editor): prevent overlapping background save requests */

/* [2025-12-04] feat(editor): prevent overlapping background save requests */

/* [2025-12-08] feat(editor): implement debounced autosave listener in pad.js */

/* [2025-12-09] feat(editor): implement debounced autosave listener in pad.js */

/* [2025-12-11] feat(editor): add keyboard shortcut listener for Ctrl+S and Cmd+S */

/* [2025-12-13] refactor(editor): encapsulate debounce timer in module scope */

/* [2025-12-14] refactor(editor): encapsulate debounce timer in module scope */

/* [2025-12-15] feat(editor): prevent overlapping background save requests */

/* [2025-12-16] feat(editor): prevent overlapping background save requests */

/* [2025-12-17] feat(editor): prevent overlapping background save requests */

/* [2025-12-21] feat(editor): implement debounced autosave listener in pad.js */

/* [2025-12-22] feat(editor): implement debounced autosave listener in pad.js */

/* [2025-12-22] feat(editor): add keyboard shortcut listener for Ctrl+S and Cmd+S */

/* [2025-12-23] feat(editor): add keyboard shortcut listener for Ctrl+S and Cmd+S */

/* [2025-12-24] feat(editor): add keyboard shortcut listener for Ctrl+S and Cmd+S */

/* [2025-12-25] refactor(editor): encapsulate debounce timer in module scope */

/* [2025-12-26] refactor(editor): encapsulate debounce timer in module scope */

/* [2025-12-28] feat(editor): prevent overlapping background save requests */

/* [2025-12-29] feat(editor): prevent overlapping background save requests */

/* [2026-01-05] feat(theme): add theme switcher logic supporting light, dark, and system */

/* [2026-01-08] feat(theme): persist active theme choice in localStorage */

/* [2026-01-08] refactor(theme): cycle through system, light, and dark modes cleanly */

/* [2026-01-09] feat(theme): persist active theme choice in localStorage */

/* [2026-01-09] refactor(theme): cycle through system, light, and dark modes cleanly */

/* [2026-01-10] refactor(theme): cycle through system, light, and dark modes cleanly */

/* [2026-01-15] feat(theme): add theme switcher logic supporting light, dark, and system */

/* [2026-01-16] feat(theme): add theme switcher logic supporting light, dark, and system */

/* [2026-01-18] feat(theme): persist active theme choice in localStorage */

/* [2026-01-19] feat(theme): persist active theme choice in localStorage */

/* [2026-01-19] refactor(theme): cycle through system, light, and dark modes cleanly */
