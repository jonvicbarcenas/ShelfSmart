/* ==============================================
   DELETE BUTTON FUNCTIONALITY
   - Handles book deletion with confirmation
   - Shows confirmation popup before deleting
   - Submits delete request to server
   ============================================== */

// Global variable to store the ID of the book to be deleted
let deleteBookId = null;

/**
 * Opens the delete confirmation popup
 * @param {number} bookId - The ID of the book to delete
 */
function deleteBook(bookId) {
    console.log('Opening delete confirmation for book ID:', bookId);
    
    // Store the book ID for later use
    deleteBookId = bookId;
    
    // Find the book row to get book title for confirmation message
    const row = document.querySelector(`tr[data-id="${bookId}"]`);
    
    if (row) {
        const cells = row.querySelectorAll('td');
        const bookTitle = cells[2].textContent.trim();
        
        // Update confirmation message with book title
        const deleteMessage = document.querySelector('.delete-message');
        if (deleteMessage) {
            deleteMessage.innerHTML = `
                Are you certain you wish to proceed with the deletion of 
                <strong>"${bookTitle}"</strong>?<br>
                <small style="color: #666; margin-top: 8px; display: block;">
                    This action cannot be undone.
                </small>
            `;
        }
    }
    
    // Display the confirmation popup with animation
    const popup = document.getElementById('deleteBookPopup');
    popup.style.display = 'flex';
    
    // Add entrance animation
    setTimeout(() => {
        popup.classList.add('active');
    }, 10);
    
    console.log('Delete confirmation popup opened for book ID:', bookId);
}

/**
 * Closes the delete confirmation popup
 */
function closeDeletePopup() {
    console.log('Closing delete confirmation popup');
    
    const popup = document.getElementById('deleteBookPopup');
    
    // Remove active class for exit animation
    popup.classList.remove('active');
    
    // Hide popup and clear stored book ID after animation completes
    setTimeout(() => {
        popup.style.display = 'none';
        deleteBookId = null;
        
        // Reset delete message to default
        const deleteMessage = document.querySelector('.delete-message');
        if (deleteMessage) {
            deleteMessage.innerHTML = 'Are you certain you wish to proceed with the deletion of the selected entry?';
        }
    }, 300);
}

/**
 * Confirms and executes the book deletion
 */
function confirmDelete() {
    if (!deleteBookId) {
        console.error('No book ID stored for deletion');
        alert('Error: No book selected for deletion');
        return;
    }
    
    console.log('Confirming deletion of book ID:', deleteBookId);
    
    // Get CSRF token from the page
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    if (!csrfToken) {
        console.error('CSRF token not found');
        alert('Error: Security token not found. Please refresh the page.');
        return;
    }
    
    // Prepare delete request data
    const formData = new URLSearchParams({
        action: 'delete',
        book_id: deleteBookId
    });
    
    // Disable confirm button to prevent double submission
    const confirmBtn = document.querySelector('.btn-confirm');
    if (confirmBtn) {
        confirmBtn.disabled = true;
        confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting...';
    }
    
    // Submit delete request to server
    fetch('/admin-panel/books/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(response => {
        if (response.ok) {
            console.log('Book deleted successfully');
            closeDeletePopup();
            
            // Show success message
            showSuccessMessage('Book deleted successfully!');
            
            // Remove the row from the table with animation
            const row = document.querySelector(`tr[data-id="${deleteBookId}"]`);
            if (row) {
                row.style.transition = 'all 0.3s ease';
                row.style.opacity = '0';
                row.style.transform = 'translateX(-20px)';
                
                setTimeout(() => {
                    row.remove();
                    
                    // Check if table is empty
                    const tbody = document.getElementById('booksTableBody');
                    if (tbody && tbody.querySelectorAll('tr').length === 0) {
                        tbody.innerHTML = `
                            <tr>
                                <td colspan="9" style="text-align: center; padding: 40px;">
                                    No books found.
                                </td>
                            </tr>
                        `;
                    }
                }, 300);
            } else {
                // If row not found, reload the page
                setTimeout(() => {
                    location.reload();
                }, 1000);
            }
        } else {
            throw new Error('Server returned error status');
        }
    })
    .catch(error => {
        console.error('Error deleting book:', error);
        alert('Error deleting book. Please try again.');
        
        // Re-enable confirm button
        if (confirmBtn) {
            confirmBtn.disabled = false;
            confirmBtn.innerHTML = 'Confirm';
        }
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
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
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
    
    toast.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
    toast.style.opacity = '1';
    
    // Hide after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
    }, 3000);
}

/**
 * Handle keyboard shortcuts for delete popup
 * ESC - Close popup
 * Enter - Confirm deletion
 */
document.addEventListener('keydown', (event) => {
    const deletePopup = document.getElementById('deleteBookPopup');
    
    if (deletePopup && deletePopup.style.display === 'flex') {
        // ESC to close
        if (event.key === 'Escape') {
            event.preventDefault();
            closeDeletePopup();
        }
        
        // Enter to confirm
        if (event.key === 'Enter') {
            event.preventDefault();
            confirmDelete();
        }
    }
});

/**
 * Close popup when clicking outside the popup container
 */
document.addEventListener('click', (event) => {
    const deletePopup = document.getElementById('deleteBookPopup');
    
    if (event.target === deletePopup) {
        closeDeletePopup();
    }
});

// Make functions globally available
window.deleteBook = deleteBook;
window.closeDeletePopup = closeDeletePopup;
window.confirmDelete = confirmDelete;

console.log('Delete button functionality loaded');
