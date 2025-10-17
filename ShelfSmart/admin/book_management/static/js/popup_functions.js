// Update time and date
function updateDateTime() {
    const now = new Date()
    document.getElementById("currentTime").textContent = now.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    })
    document.getElementById("currentDate").textContent = now.toLocaleDateString("en-US", {
      month: "short",
      day: "2-digit",
      year: "numeric",
    })
  }
  
  // Initialize date/time updates
  document.addEventListener("DOMContentLoaded", () => {
    updateDateTime()
    setInterval(updateDateTime, 60000)
  })
  
  // Search functionality
  document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("searchInput")
    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        const searchTerm = e.target.value.toLowerCase()
        const rows = document.querySelectorAll("#booksTableBody tr")
        rows.forEach((row) => {
          const text = row.textContent.toLowerCase()
          row.style.display = text.includes(searchTerm) ? "" : "none"
        })
      })
    }
  })
  
  // Global variable to store book data for operations
  const currentBookData = {}
  let deleteBookId = null
  
  // Add Book Popup Functions
  function openAddModal() {
    document.getElementById("addBookPopup").style.display = "block"
  }
  
  function closeAddPopup() {
    document.getElementById("addBookPopup").style.display = "none"
    document.getElementById("addBookForm").reset()
  }
  
  // Add book
  function addBook(event) {
    event.preventDefault()
    const formData = new FormData(event.target)
    const data = {
      action: "add",
      name: formData.get("name"),
      type: formData.get("type"),
      language: formData.get("language"),
      quantity: formData.get("quantity"),
      availability: "Available",
    }
  
    fetch("/admin-panel/books/", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
      },
      body: new URLSearchParams(data),
    })
      .then((response) => {
        if (response.ok) {
          closeAddPopup()
          location.reload()
        } else {
          alert("Error adding book")
        }
      })
      .catch((error) => {
        console.error("Error:", error)
        alert("Error adding book")
      })
  }
  
  // View Book Popup Functions
  function viewBook(bookId) {
    // Find book data from the table
    const row = document.querySelector(`tr[data-id="${bookId}"]`)
    if (row) {
      const cells = row.querySelectorAll("td")
      document.getElementById("view-book-id").textContent = cells[0].textContent
      document.getElementById("view-name").textContent = cells[1].textContent
      document.getElementById("view-type").textContent = cells[2].textContent
      document.getElementById("view-language").textContent = cells[3].textContent
      document.getElementById("view-quantity").textContent = cells[4].textContent
      document.getElementById("view-availability").textContent = cells[5].textContent.trim()
  
      document.getElementById("viewBookPopup").style.display = "block"
    }
  }
  
  function closeViewPopup() {
    document.getElementById("viewBookPopup").style.display = "none"
  }
  
  // Edit Book Popup Functions
  function editBook(bookId) {
    // Find book data from the table
    const row = document.querySelector(`tr[data-id="${bookId}"]`)
    if (row) {
      const cells = row.querySelectorAll("td")
  
      // Populate update form
      document.getElementById("update-book-id").value = bookId
      document.getElementById("update-name").value = cells[1].textContent
      document.getElementById("update-type").value = cells[2].textContent
      document.getElementById("update-language").value = cells[3].textContent
      document.getElementById("update-quantity").value = cells[4].textContent
      document.getElementById("update-availability").value = cells[5].textContent.trim()
  
      document.getElementById("updateBookPopup").style.display = "block"
    }
  }
  
  function closeUpdatePopup() {
    document.getElementById("updateBookPopup").style.display = "none"
    document.getElementById("updateBookForm").reset()
  }
  
  // Update book
  function updateBook(event) {
    event.preventDefault()
    const formData = new FormData(event.target)
    const data = {
      action: "edit",
      book_id: formData.get("book_id"),
      name: formData.get("name"),
      type: formData.get("type"),
      language: formData.get("language"),
      quantity: formData.get("quantity"),
      availability: formData.get("availability"),
    }
  
    fetch("/admin-panel/books/", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
      },
      body: new URLSearchParams(data),
    })
      .then((response) => {
        if (response.ok) {
          closeUpdatePopup()
          location.reload()
        } else {
          alert("Error updating book")
        }
      })
      .catch((error) => {
        console.error("Error:", error)
        alert("Error updating book")
      })
  }
  
  // Delete Book Popup Functions
  function deleteBook(bookId) {
    deleteBookId = bookId
    document.getElementById("deleteBookPopup").style.display = "block"
  }
  
  function closeDeletePopup() {
    document.getElementById("deleteBookPopup").style.display = "none"
    deleteBookId = null
  }
  
  function confirmDelete() {
    if (deleteBookId) {
      // Get CSRF token from the page
      const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value
  
      const formData = new URLSearchParams({
        action: "delete",
        book_id: deleteBookId,
      })
  
      fetch("/admin-panel/books/", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": csrfToken,
        },
        body: formData,
      })
        .then((response) => {
          if (response.ok) {
            closeDeletePopup()
            location.reload()
          } else {
            alert("Error deleting book")
          }
        })
        .catch((error) => {
          console.error("Error:", error)
          alert("Error deleting book")
        })
    }
  }
  
  // Close popups when clicking outside
  document.addEventListener("click", (event) => {
    const popups = ["addBookPopup", "updateBookPopup", "viewBookPopup", "deleteBookPopup"]
  
    popups.forEach((popupId) => {
      const popup = document.getElementById(popupId)
      if (popup && event.target === popup) {
        popup.style.display = "none"
        if (popupId === "addBookPopup") {
          document.getElementById("addBookForm").reset()
        } else if (popupId === "updateBookPopup") {
          document.getElementById("updateBookForm").reset()
        } else if (popupId === "deleteBookPopup") {
          deleteBookId = null
        }
      }
    })
  })
  
  // Close popups with Escape key
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      const visiblePopups = document.querySelectorAll('.popup-overlay[style*="block"]')
      visiblePopups.forEach((popup) => {
        popup.style.display = "none"
        if (popup.id === "addBookPopup") {
          document.getElementById("addBookForm").reset()
        } else if (popup.id === "updateBookPopup") {
          document.getElementById("updateBookForm").reset()
        } else if (popup.id === "deleteBookPopup") {
          deleteBookId = null
        }
      })
    }
  })
  