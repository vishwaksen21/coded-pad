/**
 * create.js — Handles the "Create Note" form submission.
 * Sends note + password to POST /api/create and shows the resulting note ID.
 */

const form       = document.getElementById("createForm");
const saveBtn    = document.getElementById("saveBtn");
const successBox = document.getElementById("successBox");
const errorBox   = document.getElementById("errorBox");
const errorMsg   = document.getElementById("errorMsg");
const generatedId = document.getElementById("generatedId");

// Store the note ID so we can copy it later
let lastNoteId = "";

form.addEventListener("submit", async (e) => {
    e.preventDefault();  // prevent default browser form submission

    const note     = document.getElementById("noteText").value.trim();
    const password = document.getElementById("notePassword").value.trim();

    // Hide any previous results
    successBox.classList.add("hidden");
    errorBox.classList.add("hidden");

    // Basic client-side validation
    if (!note) {
        showError("Please write a note before saving.");
        return;
    }
    if (password.length < 4) {
        showError("Password must be at least 4 characters.");
        return;
    }

    // Disable button while saving
    saveBtn.disabled = true;
    saveBtn.textContent = "Saving...";

    try {
        // Send POST request to Flask backend
        const response = await fetch("/api/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ note, password })
        });

        const data = await response.json();

        if (data.success) {
            // Show the generated note ID to the user
            lastNoteId = data.note_id;
            generatedId.textContent = data.note_id;
            successBox.classList.remove("hidden");
            form.reset();  // clear the form
        } else {
            showError(data.error || "Failed to save note.");
        }

    } catch (err) {
        showError("Network error. Is the server running?");
    } finally {
        // Re-enable the button
        saveBtn.disabled = false;
        saveBtn.textContent = "🔒 Save & Encrypt Note";
    }
});


/** Show an error message inside the error box. */
function showError(message) {
    errorMsg.textContent = message;
    errorBox.classList.remove("hidden");
}


/** Copy the generated note ID to the clipboard. */
function copyId() {
    navigator.clipboard.writeText(lastNoteId)
        .then(() => alert(`Copied: ${lastNoteId}`))
        .catch(() => alert("Could not copy. Please copy manually: " + lastNoteId));
}
