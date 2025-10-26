// Search functionality
document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("searchInput");
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const rows = document.querySelectorAll("#authorsTableBody tr");
            rows.forEach((row) => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? "" : "none";
            });
        });
    }
});

// Global variable for delete operation
let deleteAuthorId = null;

// Add Author Popup Functions
function openAddModal() {
    document.getElementById("addAuthorPopup").style.display = "block";
}

function closeAddPopup() {
    document.getElementById("addAuthorPopup").style.display = "none";
    document.getElementById("addAuthorForm").reset();
}

// Add author
function addAuthor(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        action: "add",
        name: formData.get("name"),
        biography: formData.get("biography"),
        nationality: formData.get("nationality"),
    };

    fetch("/admin-panel/authors/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
        },
        body: new URLSearchParams(data),
    })
        .then((response) => {
            if (response.ok) {
                closeAddPopup();
                location.reload();
            } else {
                alert("Error adding author");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            alert("Error adding author");
        });
}

// View Author Popup Functions
function viewAuthor(authorId) {
    const row = document.querySelector(`tr[data-id="${authorId}"]`);
    if (row) {
        const cells = row.querySelectorAll("td");
        
        // Get data from data attributes
        const biography = row.getAttribute("data-biography") || "No biography available";
        const nationality = row.getAttribute("data-nationality") || "-";
        
        document.getElementById("view-author-id").textContent = cells[0].textContent;
        document.getElementById("view-name").textContent = cells[1].textContent.trim();
        document.getElementById("view-biography").textContent = biography;
        document.getElementById("view-nationality").textContent = nationality;
        document.getElementById("view-book-count").textContent = cells[3].textContent.trim();

        document.getElementById("viewAuthorPopup").style.display = "block";
    }
}

function closeViewPopup() {
    document.getElementById("viewAuthorPopup").style.display = "none";
}

// Edit Author Popup Functions
function editAuthor(authorId) {
    const row = document.querySelector(`tr[data-id="${authorId}"]`);
    if (row) {
        const cells = row.querySelectorAll("td");

        // Get data from data attributes
        const biography = row.getAttribute("data-biography") || "";
        const nationality = row.getAttribute("data-nationality") || "";

        document.getElementById("update-author-id").value = authorId;
        document.getElementById("update-name").value = cells[1].textContent.trim();
        document.getElementById("update-biography").value = biography;
        document.getElementById("update-nationality").value = nationality;

        document.getElementById("updateAuthorPopup").style.display = "block";
    }
}

function closeUpdatePopup() {
    document.getElementById("updateAuthorPopup").style.display = "none";
    document.getElementById("updateAuthorForm").reset();
}

// Update author
function updateAuthor(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        action: "edit",
        author_id: formData.get("author_id"),
        name: formData.get("name"),
        biography: formData.get("biography"),
        nationality: formData.get("nationality"),
    };

    fetch("/admin-panel/authors/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
        },
        body: new URLSearchParams(data),
    })
        .then((response) => {
            if (response.ok) {
                closeUpdatePopup();
                location.reload();
            } else {
                alert("Error updating author");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            alert("Error updating author");
        });
}

// Delete Author Popup Functions
function deleteAuthor(authorId) {
    deleteAuthorId = authorId;
    document.getElementById("deleteAuthorPopup").style.display = "block";
}

function closeDeletePopup() {
    document.getElementById("deleteAuthorPopup").style.display = "none";
    deleteAuthorId = null;
}

function confirmDelete() {
    if (deleteAuthorId) {
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

        const formData = new URLSearchParams({
            action: "delete",
            author_id: deleteAuthorId,
        });

        fetch("/admin-panel/authors/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": csrfToken,
            },
            body: formData,
        })
            .then((response) => {
                if (response.ok) {
                    closeDeletePopup();
                    location.reload();
                } else {
                    alert("Error deleting author");
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("Error deleting author");
            });
    }
}

// Close popups when clicking outside
document.addEventListener("click", (event) => {
    const popups = ["addAuthorPopup", "updateAuthorPopup", "viewAuthorPopup", "deleteAuthorPopup"];

    popups.forEach((popupId) => {
        const popup = document.getElementById(popupId);
        if (popup && event.target === popup) {
            popup.style.display = "none";
            if (popupId === "addAuthorPopup") {
                document.getElementById("addAuthorForm").reset();
            } else if (popupId === "updateAuthorPopup") {
                document.getElementById("updateAuthorForm").reset();
            } else if (popupId === "deleteAuthorPopup") {
                deleteAuthorId = null;
            }
        }
    });
});

// Close popups with Escape key
document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        const visiblePopups = document.querySelectorAll('.popup-overlay[style*="block"]');
        visiblePopups.forEach((popup) => {
            popup.style.display = "none";
            if (popup.id === "addAuthorPopup") {
                document.getElementById("addAuthorForm").reset();
            } else if (popup.id === "updateAuthorPopup") {
                document.getElementById("updateAuthorForm").reset();
            } else if (popup.id === "deleteAuthorPopup") {
                deleteAuthorId = null;
            }
        });
    }
});
