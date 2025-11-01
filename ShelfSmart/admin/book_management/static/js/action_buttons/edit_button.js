/* ==============================================
   EDIT BUTTON FUNCTIONALITY
   - Handles editing book details via popup form
   - Fetches data from the table row
   - Submits updates to the server
   ============================================== */

/**
 * Opens the edit book popup and populates it with current book data
 * Fetches complete data from the backend API
 * @param {number} bookId - The ID of the book to edit
 */
async function editBook(bookId) {
    console.log('Opening edit popup for book ID:', bookId);
    
    try {
        // Show loading state
        const popup = document.getElementById('updateBookPopup');
        popup.style.display = 'flex';
        
        // Fetch complete book data from API
        const response = await fetch(`/admin-panel/books/api/book/${bookId}/`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch book details');
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to load book details');
        }
        
        const book = data.book;
        
        // Populate all form fields with complete data
        document.getElementById('update-book-id').value = book.id;
        document.getElementById('update-isbn').value = book.isbn || '';
        document.getElementById('update-title').value = book.title || '';
        document.getElementById('update-subtitle').value = book.subtitle || '';
        document.getElementById('update-description').value = book.description || '';
        document.getElementById('update-publication-date').value = book.publication_date || '';
        document.getElementById('update-edition').value = book.edition || '';
        document.getElementById('update-pages').value = book.pages || '';
        document.getElementById('update-language').value = book.language || '';
        document.getElementById('update-cover-image').value = book.cover_image_url || '';
        document.getElementById('update-total-copies').value = book.total_copies || '';
        document.getElementById('update-quantity').value = book.quantity || '';
        
        // Set category dropdown by ID
        const categorySelect = document.getElementById('update-category');
        if (book.category_id) {
            categorySelect.value = book.category_id;
        }
        
        // Set publisher dropdown by ID
        const publisherSelect = document.getElementById('update-publisher');
        if (book.publisher_id) {
            publisherSelect.value = book.publisher_id;
        }
        
        // Add entrance animation
        setTimeout(() => {
            popup.classList.add('active');
        }, 10);
        
        console.log('Edit popup opened successfully with complete data:', book);
        
    } catch (error) {
        console.error('Error loading book details:', error);
        alert('Error loading book details for editing. Please try again.');
        closeUpdatePopup();
    }
}

/**
 * Closes the edit book popup and resets the form
 */
function closeUpdatePopup() {
    console.log('Closing edit popup');
    
    const popup = document.getElementById('updateBookPopup');
    const form = document.getElementById('updateBookForm');
    
    // Remove active class for exit animation
    popup.classList.remove('active');
    
    // Hide popup and reset form after animation completes
    setTimeout(() => {
        popup.style.display = 'none';
        form.reset();
    }, 300);
}

/**
 * Handles the book update form submission
 * @param {Event} event - The form submit event
 */
function updateBook(event) {
    event.preventDefault();
    console.log('Submitting book update');
    
    const formData = new FormData(event.target);
    
    // Validate required fields
    if (!formData.get('title') || !formData.get('category_id') || 
        !formData.get('publisher_id') || !formData.get('quantity')) {
        alert('Please fill in all required fields');
        return;
    }
    
    // Prepare data for submission
    const data = {
        action: 'edit',
        book_id: formData.get('book_id'),
        title: formData.get('title'),
        isbn: formData.get('isbn'),
        subtitle: formData.get('subtitle'),
        description: formData.get('description'),
        publication_date: formData.get('publication_date'),
        edition: formData.get('edition'),
        pages: formData.get('pages'),
        category_id: formData.get('category_id'),
        publisher_id: formData.get('publisher_id'),
        language: formData.get('language'),
        cover_image_url: formData.get('cover_image_url'),
        total_copies: formData.get('total_copies'),
        quantity: formData.get('quantity')
    };
    
    console.log('Sending update data:', data);
    
    // Submit the update to the server
    fetch('/admin-panel/books/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        },
        body: new URLSearchParams(data)
    })
    .then(response => {
        if (response.ok) {
            console.log('Book updated successfully');
            closeUpdatePopup();
            
            // Show success message
            showSuccessMessage('Book updated successfully!');
            
            // Reload page to reflect changes
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            throw new Error('Server returned error status');
        }
    })
    .catch(error => {
        console.error('Error updating book:', error);
        alert('Error updating book. Please check all fields and try again.');
    });
}

/**
 * Shows a success message toast
 * @param {string} message - The message to display
 */
function showSuccessMessage(message) {
    // Create toast element if it doesn't exist
    let toast = document.getElementById('success-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'success-toast';
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        document.body.appendChild(toast);
    }
    
    toast.textContent = message;
    toast.style.opacity = '1';
    
    // Hide after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
    }, 3000);
}

/**
 * Handle keyboard shortcuts for edit popup
 * ESC - Close popup
 * Ctrl/Cmd + Enter - Submit form
 */
document.addEventListener('keydown', (event) => {
    const editPopup = document.getElementById('updateBookPopup');
    
    if (editPopup && editPopup.style.display === 'flex') {
        // ESC to close
        if (event.key === 'Escape') {
            event.preventDefault();
            closeUpdatePopup();
        }
        
        // Ctrl/Cmd + Enter to submit
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            event.preventDefault();
            const form = document.getElementById('updateBookForm');
            form.dispatchEvent(new Event('submit'));
        }
    }
});

/**
 * Close popup when clicking outside the popup container
 */
document.addEventListener('click', (event) => {
    const editPopup = document.getElementById('updateBookPopup');
    
    if (event.target === editPopup) {
        closeUpdatePopup();
    }
});

// Make functions globally available
window.editBook = editBook;
window.closeUpdatePopup = closeUpdatePopup;
window.updateBook = updateBook;

console.log('Edit button functionality loaded');
