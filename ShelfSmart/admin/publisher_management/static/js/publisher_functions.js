// Search functionality
document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("searchInput");
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const rows = document.querySelectorAll("#publishersTableBody tr");
            rows.forEach((row) => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? "" : "none";
            });
        });
    }
});

// Global variable for delete operation
let deletePublisherId = null;

// Add Publisher Popup Functions
function openAddModal() {
    document.getElementById("addPublisherPopup").style.display = "block";
}

function closeAddPopup() {
    document.getElementById("addPublisherPopup").style.display = "none";
    document.getElementById("addPublisherForm").reset();
}

// Add publisher
function addPublisher(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        action: "add",
        publisher_name: formData.get("publisher_name"),
        address: formData.get("address"),
        phone: formData.get("phone"),
        email: formData.get("email"),
        website: formData.get("website"),
        established_year: formData.get("established_year"),
    };

    fetch("/admin-panel/publishers/", {
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
                alert("Error adding publisher");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            alert("Error adding publisher");
        });
}

// View Publisher Popup Functions
function viewPublisher(publisherId) {
    const row = document.querySelector(`tr[data-id="${publisherId}"]`);
    if (row) {
        const cells = row.querySelectorAll("td");
        // Table columns: ID, Name, Phone, Email, Website, Established, Books
        document.getElementById("view-publisher-id").textContent = cells[0].textContent;
        document.getElementById("view-publisher-name").textContent = cells[1].textContent.trim();
        
        // Get data from data attributes
        const address = row.getAttribute("data-address") || "-";
        const phone = row.getAttribute("data-phone") || "-";
        const email = row.getAttribute("data-email") || "-";
        const website = row.getAttribute("data-website") || "-";
        const establishedYear = row.getAttribute("data-established-year") || "-";
        
        document.getElementById("view-address").textContent = address;
        document.getElementById("view-phone").textContent = phone;
        document.getElementById("view-email").textContent = email;
        document.getElementById("view-website").textContent = website;
        document.getElementById("view-established-year").textContent = establishedYear;
        document.getElementById("view-book-count").textContent = cells[6].textContent.trim();

        document.getElementById("viewPublisherPopup").style.display = "block";
    }
}

function closeViewPopup() {
    document.getElementById("viewPublisherPopup").style.display = "none";
}

// Edit Publisher Popup Functions
function editPublisher(publisherId) {
    const row = document.querySelector(`tr[data-id="${publisherId}"]`);
    if (row) {
        const cells = row.querySelectorAll("td");

        // Populate update form
        document.getElementById("update-publisher-id").value = publisherId;
        document.getElementById("update-publisher-name").value = cells[1].textContent.trim();
        
        // Get data from data attributes
        const address = row.getAttribute("data-address") || "";
        const phone = row.getAttribute("data-phone") || "";
        const email = row.getAttribute("data-email") || "";
        const website = row.getAttribute("data-website") || "";
        const establishedYear = row.getAttribute("data-established-year") || "";
        
        document.getElementById("update-address").value = address;
        document.getElementById("update-phone").value = phone;
        document.getElementById("update-email").value = email;
        document.getElementById("update-website").value = website;
        document.getElementById("update-established-year").value = establishedYear;

        document.getElementById("updatePublisherPopup").style.display = "block";
    }
}

function closeUpdatePopup() {
    document.getElementById("updatePublisherPopup").style.display = "none";
    document.getElementById("updatePublisherForm").reset();
}

// Update publisher
function updatePublisher(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        action: "edit",
        publisher_id: formData.get("publisher_id"),
        publisher_name: formData.get("publisher_name"),
        address: formData.get("address"),
        phone: formData.get("phone"),
        email: formData.get("email"),
        website: formData.get("website"),
        established_year: formData.get("established_year"),
    };

    fetch("/admin-panel/publishers/", {
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
                alert("Error updating publisher");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            alert("Error updating publisher");
        });
}

// Delete Publisher Popup Functions
function deletePublisher(publisherId) {
    deletePublisherId = publisherId;
    document.getElementById("deletePublisherPopup").style.display = "block";
}

function closeDeletePopup() {
    document.getElementById("deletePublisherPopup").style.display = "none";
    deletePublisherId = null;
}

function confirmDelete() {
    if (deletePublisherId) {
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

        const formData = new URLSearchParams({
            action: "delete",
            publisher_id: deletePublisherId,
        });

        fetch("/admin-panel/publishers/", {
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
                    alert("Error deleting publisher");
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("Error deleting publisher");
            });
    }
}

// Close popups when clicking outside
document.addEventListener("click", (event) => {
    const popups = ["addPublisherPopup", "updatePublisherPopup", "viewPublisherPopup", "deletePublisherPopup"];

    popups.forEach((popupId) => {
        const popup = document.getElementById(popupId);
        if (popup && event.target === popup) {
            popup.style.display = "none";
            if (popupId === "addPublisherPopup") {
                document.getElementById("addPublisherForm").reset();
            } else if (popupId === "updatePublisherPopup") {
                document.getElementById("updatePublisherForm").reset();
            } else if (popupId === "deletePublisherPopup") {
                deletePublisherId = null;
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
            if (popup.id === "addPublisherPopup") {
                document.getElementById("addPublisherForm").reset();
            } else if (popup.id === "updatePublisherPopup") {
                document.getElementById("updatePublisherForm").reset();
            } else if (popup.id === "deletePublisherPopup") {
                deletePublisherId = null;
            }
        });
    }
});
