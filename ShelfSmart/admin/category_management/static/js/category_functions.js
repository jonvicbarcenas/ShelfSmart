// Search functionality
document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("searchInput");
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const rows = document.querySelectorAll("#categoriesTableBody tr");
            rows.forEach((row) => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? "" : "none";
            });
        });
    }
});

// Global variable for delete operation
let deleteCategoryId = null;

// Add Category Popup Functions
function openAddModal() {
    document.getElementById("addCategoryPopup").style.display = "block";
}

function closeAddPopup() {
    document.getElementById("addCategoryPopup").style.display = "none";
    document.getElementById("addCategoryForm").reset();
}

// Add category
function addCategory(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        action: "add",
        category_name: formData.get("category_name"),
        description: formData.get("description"),
        parent_category_id: formData.get("parent_category_id"),
    };

    fetch("/admin-panel/categories/", {
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
                alert("Error adding category");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            alert("Error adding category");
        });
}

// View Category Popup Functions
function viewCategory(categoryId) {
    const row = document.querySelector(`tr[data-id="${categoryId}"]`);
    if (row) {
        const cells = row.querySelectorAll("td");
        // Table columns: ID, Name, Full Path, Description, Parent, Books, Subcategories
        document.getElementById("view-category-id").textContent = cells[0].textContent;
        document.getElementById("view-category-name").textContent = cells[1].textContent;
        document.getElementById("view-full-path").textContent = cells[2].textContent.trim();
        document.getElementById("view-description").textContent = cells[3].textContent.trim() || "No description";
        document.getElementById("view-parent-category").textContent = cells[4].textContent.trim();
        document.getElementById("view-book-count").textContent = cells[5].textContent.trim();
        document.getElementById("view-subcategory-count").textContent = cells[6].textContent.trim();

        document.getElementById("viewCategoryPopup").style.display = "block";
    }
}

function closeViewPopup() {
    document.getElementById("viewCategoryPopup").style.display = "none";
}

// Edit Category Popup Functions
function editCategory(categoryId) {
    const row = document.querySelector(`tr[data-id="${categoryId}"]`);
    if (row) {
        const cells = row.querySelectorAll("td");

        // Populate update form
        document.getElementById("update-category-id").value = categoryId;
        document.getElementById("update-category-name").value = cells[1].textContent;
        document.getElementById("update-description").value = cells[3].textContent.trim() === "-" ? "" : cells[3].textContent.trim();

        // Set parent category - we need to get the parent ID from data attribute or find by text
        const parentText = cells[4].textContent.trim();
        const parentSelect = document.getElementById("update-parent-category");
        if (parentText === "-") {
            parentSelect.value = "";
        } else {
            // Find option by text
            for (let option of parentSelect.options) {
                if (option.text === parentText) {
                    parentSelect.value = option.value;
                    break;
                }
            }
        }

        document.getElementById("updateCategoryPopup").style.display = "block";
    }
}

function closeUpdatePopup() {
    document.getElementById("updateCategoryPopup").style.display = "none";
    document.getElementById("updateCategoryForm").reset();
}

// Update category
function updateCategory(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        action: "edit",
        category_id: formData.get("category_id"),
        category_name: formData.get("category_name"),
        description: formData.get("description"),
        parent_category_id: formData.get("parent_category_id"),
    };

    fetch("/admin-panel/categories/", {
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
                alert("Error updating category");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            alert("Error updating category");
        });
}

// Delete Category Popup Functions
function deleteCategory(categoryId) {
    deleteCategoryId = categoryId;
    document.getElementById("deleteCategoryPopup").style.display = "block";
}

function closeDeletePopup() {
    document.getElementById("deleteCategoryPopup").style.display = "none";
    deleteCategoryId = null;
}

function confirmDelete() {
    if (deleteCategoryId) {
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

        const formData = new URLSearchParams({
            action: "delete",
            category_id: deleteCategoryId,
        });

        fetch("/admin-panel/categories/", {
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
                    alert("Error deleting category");
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("Error deleting category");
            });
    }
}

// Close popups when clicking outside
document.addEventListener("click", (event) => {
    const popups = ["addCategoryPopup", "updateCategoryPopup", "viewCategoryPopup", "deleteCategoryPopup"];

    popups.forEach((popupId) => {
        const popup = document.getElementById(popupId);
        if (popup && event.target === popup) {
            popup.style.display = "none";
            if (popupId === "addCategoryPopup") {
                document.getElementById("addCategoryForm").reset();
            } else if (popupId === "updateCategoryPopup") {
                document.getElementById("updateCategoryForm").reset();
            } else if (popupId === "deleteCategoryPopup") {
                deleteCategoryId = null;
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
            if (popup.id === "addCategoryPopup") {
                document.getElementById("addCategoryForm").reset();
            } else if (popup.id === "updateCategoryPopup") {
                document.getElementById("updateCategoryForm").reset();
            } else if (popup.id === "deleteCategoryPopup") {
                deleteCategoryId = null;
            }
        });
    }
});
