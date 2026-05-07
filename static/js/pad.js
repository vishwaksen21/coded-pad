/**
 * pad.js — Save logic for the note editor.
 *
 * - Manual save: clicking the "Save" button.
 * - Auto-save: 3 seconds after the user stops typing (debounced).
 * - Keyboard shortcut: Ctrl+S / Cmd+S.
 */

const noteArea    = document.getElementById("noteArea");
const saveBtn     = document.getElementById("saveBtn");
const saveStatus  = document.getElementById("saveStatus");
const updatedTime = document.getElementById("updatedTime");

let autoSaveTimer = null;   // debounce timer handle
let isSaving      = false;  // prevent overlapping saves

// ── Auto-save on typing (debounced 3 s) ──────────────────────────────────────
noteArea.addEventListener("input", () => {
    setStatus("Unsaved changes...", false);
    clearTimeout(autoSaveTimer);
    autoSaveTimer = setTimeout(saveNote, 3000);
});

// ── Keyboard shortcut: Ctrl+S / Cmd+S ────────────────────────────────────────
document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "s") {
        e.preventDefault();
        saveNote();
    }
});

// ── Core save function ────────────────────────────────────────────────────────
async function saveNote() {
    if (isSaving) return;   // skip if already saving
    isSaving = true;
    clearTimeout(autoSaveTimer);

    saveBtn.disabled     = true;
    saveBtn.textContent  = "Saving...";
    setStatus("Saving...", false);

    try {
        const response = await fetch("/api/save", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({
                secret_code: SECRET_CODE,       // injected by Flask in pad.html
                note:        noteArea.value
            })
        });

        const data = await response.json();

        if (data.success) {
            setStatus("✓ Saved", true);
            updatedTime.textContent = "Last saved: " + data.updated;
        } else {
            setStatus("⚠ Save failed", false);
        }

    } catch (err) {
        setStatus("⚠ Network error", false);
    } finally {
        isSaving            = false;
        saveBtn.disabled    = false;
        saveBtn.textContent = "Save";
    }
}

// ── Status helper ─────────────────────────────────────────────────────────────
function setStatus(msg, ok) {
    saveStatus.textContent  = msg;
    saveStatus.style.color  = ok ? "#2a9d8f" : "#e63946";
}
