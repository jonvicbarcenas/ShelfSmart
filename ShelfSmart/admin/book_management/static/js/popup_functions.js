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
  let authorFieldIndex = 1 // Start at 1 since we have one field by default
  
  // Note: deleteBookId is now managed in js/action_buttons/delete_button.js

  // Add Book Popup Functions
  function openAddModal() {
    document.getElementById("addBookPopup").style.display = "flex"
  }

  function closeAddPopup() {
    document.getElementById("addBookPopup").style.display = "none"
    document.getElementById("addBookForm").reset()
    // Reset to one author field
    const authorsContainer = document.getElementById("authorsContainer")
    const firstAuthor = authorsContainer.querySelector(".author-entry")
    authorsContainer.innerHTML = ""
    if (firstAuthor) {
      firstAuthor.querySelectorAll("select").forEach(select => select.value = "")
      authorsContainer.appendChild(firstAuthor)
    }
    authorFieldIndex = 1
  }

  // Add author field dynamically
  function addAuthorField() {
    const authorsContainer = document.getElementById("authorsContainer")
    const authorEntry = document.createElement("div")
    authorEntry.className = "author-entry"
    authorEntry.setAttribute("data-author-index", authorFieldIndex)
  
    // Get the author select options from the first author field
    const firstSelect = document.querySelector(".author-select")
    let authorOptions = '<option value="">Select Author</option>'
    if (firstSelect) {
      Array.from(firstSelect.options).slice(1).forEach(option => {
        authorOptions += `<option value="${option.value}">${option.textContent}</option>`
      })
    }
  
    authorEntry.innerHTML = `
      <div class="form-group">
        <label for="author-${authorFieldIndex}">Author Name</label>
        <select id="author-${authorFieldIndex}" name="authors[]" class="author-select" required>
          ${authorOptions}
        </select>
      </div>
      <div class="form-group">
        <label for="author-role-${authorFieldIndex}">Role</label>
        <select id="author-role-${authorFieldIndex}" name="author_roles[]" class="author-role-select" required>
          <option value="primary">Primary Author</option>
          <option value="co-author">Co-Author</option>
          <option value="editor">Editor</option>
          <option value="translator">Translator</option>
        </select>
      </div>
      <button type="button" class="remove-author-btn" onclick="removeAuthorField(this)">
        <i class="fas fa-trash"></i>
      </button>
    `
  
    authorsContainer.appendChild(authorEntry)
    authorFieldIndex++
  }

  // Remove author field
  function removeAuthorField(button) {
    const authorsContainer = document.getElementById("authorsContainer")
    const authorEntries = authorsContainer.querySelectorAll(".author-entry")
  
    // Don't allow removing the last author field
    if (authorEntries.length <= 1) {
      alert("At least one author is required!")
      return
    }
  
    button.closest(".author-entry").remove()
  }

  // Add book
  function addBook(event) {
    event.preventDefault()
    const formData = new FormData(event.target)
  
    // Validate at least one author is selected
    const authors = formData.getAll("authors[]")
    const validAuthors = authors.filter(a => a !== "")
    if (validAuthors.length === 0) {
      alert("Please select at least one author!")
      return
    }
  
    const data = {
      action: "add",
      title: formData.get("title"),
      isbn: formData.get("isbn"),
      subtitle: formData.get("subtitle"),
      description: formData.get("description"),
      publication_date: formData.get("publication_date"),
      edition: formData.get("edition"),
      pages: formData.get("pages"),
      language: formData.get("language"),
      cover_image_url: formData.get("cover_image_url"),
      category_id: formData.get("category_id"),
      publisher_id: formData.get("publisher_id"),
      total_copies: formData.get("total_copies"),
      quantity: formData.get("quantity"),
    }
  
    // Add authors and their roles
    const authorRoles = formData.getAll("author_roles[]")
    validAuthors.forEach((authorId, index) => {
      data[`author_${index}`] = authorId
      data[`author_role_${index}`] = authorRoles[index] || "primary"
    })
    data["author_count"] = validAuthors.length

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
          alert("Error adding book. Please check all required fields.")
        }
      })
      .catch((error) => {
        console.error("Error:", error)
        alert("Error adding book. Please try again.")
      })
  }
  
  // Note: View, Edit, and Delete book functions have been moved to separate files:
  // - js/action_buttons/view_button.js
  // - js/action_buttons/edit_button.js
  // - js/action_buttons/delete_button.js
  
  // Close add popup when clicking outside
  document.addEventListener("click", (event) => {
    const addPopup = document.getElementById("addBookPopup")
    
    if (addPopup && event.target === addPopup) {
      addPopup.style.display = "none"
      document.getElementById("addBookForm").reset()
    }
  })
  
  // Close add popup with Escape key
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      const addPopup = document.getElementById("addBookPopup")
      if (addPopup && addPopup.style.display === "flex") {
        addPopup.style.display = "none"
        document.getElementById("addBookForm").reset()
      }
    }
  })
  
  // Note: Click-outside and ESC handlers for view/edit/delete popups are now in their respective files

  // ISBN Validation Function
  async function validateISBN() {
    const isbnInput = document.getElementById('add-isbn')
    const statusDiv = document.getElementById('isbn-status')
    const validateBtn = document.querySelector('.btn-validate-isbn')
    
    const isbn = isbnInput.value.trim().replace(/-/g, '').replace(/\s/g, '')
    
    // Clear previous status completely (including any quick-add success messages)
    statusDiv.innerHTML = ''
    statusDiv.className = ''
    
    if (!isbn) {
      statusDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> Please enter an ISBN'
      statusDiv.className = 'isbn-status error'
      return
    }
    
    // Validate ISBN format
    if (!(isbn.length === 10 || isbn.length === 13) || !/^\d+$/.test(isbn)) {
      statusDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> Invalid ISBN format. Must be 10 or 13 digits.'
      statusDiv.className = 'isbn-status error'
      return
    }
    
    // Show loading state
    validateBtn.disabled = true
    validateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Validating...'
    statusDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Fetching book details...'
    statusDiv.className = 'isbn-status loading'
    
    try {
      const response = await fetch('/api/isbn/validate/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ isbn: isbn })
      })
      
      const data = await response.json()
      
      if (response.ok && data.success) {
        // Show success message
        statusDiv.innerHTML = '<i class="fas fa-check-circle"></i> ISBN validated! Book details loaded.'
        statusDiv.className = 'isbn-status success'
        
        // Auto-populate form fields
        if (data.title) {
          document.getElementById('add-title').value = data.title
        }
        
        if (data.subtitle) {
          document.getElementById('add-subtitle').value = data.subtitle
        }
        
        if (data.description) {
          document.getElementById('add-description').value = data.description
        }
        
        if (data.language) {
          document.getElementById('add-language').value = data.language.toUpperCase()
        }
        
        if (data.publishedDate) {
          // Convert date format from YYYY or YYYY-MM or YYYY-MM-DD to YYYY-MM-DD
          let dateValue = data.publishedDate
          if (dateValue.length === 4) {
            dateValue = dateValue + '-01-01'
          } else if (dateValue.length === 7) {
            dateValue = dateValue + '-01'
          }
          document.getElementById('add-publication-date').value = dateValue
        }
        
        if (data.pageCount) {
          document.getElementById('add-pages').value = data.pageCount
        }
        
        if (data.imageLinks && data.imageLinks.thumbnail) {
          document.getElementById('add-cover-image').value = data.imageLinks.thumbnail
        }
        
        // Auto-select matched category from database
        if (data.matched_category_id) {
          const categorySelect = document.getElementById('add-category')
          categorySelect.value = data.matched_category_id
          console.log('Auto-selected category ID:', data.matched_category_id)
        }
        
        // Auto-select matched publisher from database
        if (data.matched_publisher_id) {
          const publisherSelect = document.getElementById('add-publisher')
          publisherSelect.value = data.matched_publisher_id
          console.log('Auto-selected publisher ID:', data.matched_publisher_id)
        }
        
        // Auto-select matched authors from database
        if (data.matched_author_ids && data.matched_author_ids.length > 0) {
          // Get the first author field
          const firstAuthorSelect = document.getElementById('author-0')
          if (firstAuthorSelect && data.matched_author_ids[0]) {
            firstAuthorSelect.value = data.matched_author_ids[0].id
            console.log('Auto-selected author ID:', data.matched_author_ids[0].id)
          }
          
          // If there are more authors, add additional author fields
          for (let i = 1; i < data.matched_author_ids.length; i++) {
            // Add a new author field if we have more matched authors
            addAuthorField()
            // Wait a bit for the DOM to update, then set the value
            setTimeout(() => {
              const authorSelect = document.getElementById(`author-${i}`)
              if (authorSelect && data.matched_author_ids[i]) {
                authorSelect.value = data.matched_author_ids[i].id
                console.log(`Auto-selected author ${i} ID:`, data.matched_author_ids[i].id)
              }
            }, 100 * i)
          }
        }
        
        // Show additional info with match status and Add buttons
        let additionalInfo = ''
        
        // Authors
        if (data.authors && data.authors.length > 0) {
          const unmatchedAuthors = []
          data.authors.forEach(authorName => {
            const isMatched = data.matched_author_ids && data.matched_author_ids.some(a => 
              a.name.toLowerCase() === authorName.toLowerCase()
            )
            if (!isMatched) {
              unmatchedAuthors.push(authorName)
            }
          })
          
          let matchStatus = ''
          if (data.matched_author_ids && data.matched_author_ids.length > 0) {
            matchStatus = ' ✓ <span style="color: #28a745;">Matched in DB</span>'
          } else {
            matchStatus = ' ⚠ <span style="color: #ffc107;">Not found in DB</span>'
          }
          
          additionalInfo += `<strong>Authors:</strong> ${data.authors.join(', ')}${matchStatus}`
          
          // Add buttons for unmatched authors
          if (unmatchedAuthors.length > 0) {
            unmatchedAuthors.forEach(authorName => {
              additionalInfo += ` <button type="button" class="btn-quick-add" onclick="quickAddAuthor('${authorName.replace(/'/g, "\\'")}')">+ Add "${authorName}"</button>`
            })
          }
          additionalInfo += '<br>'
        }
        
        // Publisher
        if (data.publisher) {
          let matchStatus = ''
          let addButton = ''
          
          if (data.matched_publisher_id) {
            matchStatus = ' ✓ <span style="color: #28a745;">Matched in DB</span>'
          } else {
            matchStatus = ' ⚠ <span style="color: #ffc107;">Not found in DB</span>'
            addButton = ` <button type="button" class="btn-quick-add" onclick="quickAddPublisher('${data.publisher.replace(/'/g, "\\'")}')">+ Add "${data.publisher}"</button>`
          }
          
          additionalInfo += `<strong>Publisher:</strong> ${data.publisher}${matchStatus}${addButton}<br>`
        }
        
        // Categories
        if (data.categories && data.categories.length > 0) {
          let matchStatus = ''
          let addButton = ''
          const categoryName = data.categories[0] // Use first category
          
          if (data.matched_category_id) {
            matchStatus = ' ✓ <span style="color: #28a745;">Matched in DB</span>'
          } else {
            matchStatus = ' ⚠ <span style="color: #ffc107;">Not found in DB</span>'
            addButton = ` <button type="button" class="btn-quick-add" onclick="quickAddCategory('${categoryName.replace(/'/g, "\\'")}')">+ Add "${categoryName}"</button>`
          }
          
          additionalInfo += `<strong>Categories:</strong> ${data.categories.join(', ')}${matchStatus}${addButton}`
        }
        
        if (additionalInfo) {
          statusDiv.innerHTML += '<div class="isbn-info">' + additionalInfo + '</div>'
        }
        
      } else {
        // Show error message
        statusDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> ' + (data.error || 'Book not found')
        statusDiv.className = 'isbn-status error'
      }
      
    } catch (error) {
      console.error('ISBN validation error:', error)
      statusDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> Network error. Please try again.'
      statusDiv.className = 'isbn-status error'
    } finally {
      // Reset button state
      validateBtn.disabled = false
      validateBtn.innerHTML = '<i class="fas fa-check-circle"></i> Validate ISBN'
    }
  }
  
  // Make validateISBN globally available
  window.validateISBN = validateISBN
  
  // Note: Quick-add functions are now in quick_add.js for easier debugging