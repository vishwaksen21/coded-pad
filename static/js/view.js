/**
 * view.js — Handles the "Open Note" form submission.
 * Sends note_id + password to POST /api/view and displays the decrypted note.
 */

const form       = document.getElementById("viewForm");
const openBtn    = document.getElementById("openBtn");
const noteDisplay = document.getElementById("noteDisplay");
const errorBox   = document.getElementById("errorBox");
const errorMsg   = document.getElementById("errorMsg");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const note_id  = document.getElementById("noteId").value.trim().toUpperCase();
    const password = document.getElementById("viewPassword").value.trim();

    // Hide previous results
    noteDisplay.classList.add("hidden");
    errorBox.classList.add("hidden");

    // Basic validation
    if (!note_id) {
        showError("Please enter a Note ID.");
        return;
    }
    if (!password) {
        showError("Please enter the password.");
        return;
    }

    // Disable button while loading
    openBtn.disabled = true;
    openBtn.textContent = "Decrypting...";

    try {
        // Send POST request to Flask backend
        const response = await fetch("/api/view", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ note_id, password })
        });

        const data = await response.json();

        if (data.success) {
            // Show the decrypted note
            document.getElementById("displayedId").textContent   = note_id;
            document.getElementById("displayedTime").textContent  = data.created_time;
            document.getElementById("noteContent").textContent    = data.note;
            noteDisplay.classList.remove("hidden");
        } else {
            showError(data.error || "Could not open note.");
        }

    } catch (err) {
        showError("Network error. Is the server running?");
    } finally {
        openBtn.disabled = false;
        openBtn.textContent = "🔓 Decrypt & Open Note";
    }
});


/** Show an error message inside the error box. */
function showError(message) {
    errorMsg.textContent = message;
    errorBox.classList.remove("hidden");
}


/** Copy the displayed note content to the clipboard. */
function copyNote() {
    const noteText = document.getElementById("noteContent").textContent;
    navigator.clipboard.writeText(noteText)
        .then(() => alert("Note copied to clipboard!"))
        .catch(() => alert("Could not copy automatically."));
}
