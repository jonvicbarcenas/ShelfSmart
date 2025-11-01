/* ==============================================
   VIEW BUTTON FUNCTIONALITY
   - Handles viewing book details in a popup
   - Fetches data from the table row
   - Displays information in read-only format
   ============================================== */

/**
 * Opens the view book popup and populates it with book data
 * Fetches complete data from the backend API
 * @param {number} bookId - The ID of the book to view
 */
async function viewBook(bookId) {
    console.log('Opening view popup for book ID:', bookId);
    
    try {
        // Show loading state
        const popup = document.getElementById('viewBookPopup');
        popup.style.display = 'flex';
        
        // Set loading placeholders
        document.getElementById('view-book-id').textContent = 'Loading...';
        document.getElementById('view-isbn').textContent = 'Loading...';
        document.getElementById('view-title').textContent = 'Loading...';
        document.getElementById('view-subtitle').textContent = 'Loading...';
        document.getElementById('view-description').textContent = 'Loading...';
        document.getElementById('view-category').textContent = 'Loading...';
        document.getElementById('view-publisher').textContent = 'Loading...';
        document.getElementById('view-language').textContent = 'Loading...';
        document.getElementById('view-quantity').textContent = 'Loading...';
        document.getElementById('view-availability').textContent = 'Loading...';
        
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
        
        // Populate the view popup with complete data
        document.getElementById('view-book-id').textContent = book.book_id || '-';
        document.getElementById('view-isbn').textContent = book.isbn || '-';
        document.getElementById('view-title').textContent = book.title || '-';
        document.getElementById('view-subtitle').textContent = book.subtitle || '-';
        document.getElementById('view-description').textContent = book.description || '-';
        document.getElementById('view-category').textContent = book.category_name || '-';
        document.getElementById('view-publisher').textContent = book.publisher_name || '-';
        document.getElementById('view-language').textContent = book.language || '-';
        document.getElementById('view-quantity').textContent = book.quantity || '-';
        document.getElementById('view-availability').textContent = book.availability?.charAt(0).toUpperCase() + book.availability?.slice(1) || '-';
        document.getElementById('view-publication-date').textContent = book.publication_date || '-';
        document.getElementById('view-edition').textContent = book.edition || '-';
        document.getElementById('view-pages').textContent = book.pages || '-';
        document.getElementById('view-total-copies').textContent = book.total_copies || '-';
        
        // Format authors list
        if (book.authors && book.authors.length > 0) {
            const authorsText = book.authors.map(a => `${a.name} (${a.role})`).join(', ');
            document.getElementById('view-authors').textContent = authorsText;
        } else {
            document.getElementById('view-authors').textContent = '-';
        }
        
        // Display cover image as actual image
        const coverElem = document.getElementById('view-cover-image');
        if (book.cover_image_url) {
            coverElem.innerHTML = `
                <img src="${book.cover_image_url}" 
                     alt="${book.title} Cover" 
                     style="max-width: 300px; max-height: 400px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); object-fit: contain;"
                     onerror="this.onerror=null; this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22300%22%3E%3Crect fill=%22%23ddd%22 width=%22200%22 height=%22300%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 fill=%22%23999%22%3ENo Image%3C/text%3E%3C/svg%3E';">
            `;
        } else {
            coverElem.innerHTML = `
                <div style="width: 200px; height: 300px; background: #f0f0f0; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #999;">
                    <div style="text-align: center;">
                        <i class="fas fa-image" style="font-size: 48px; margin-bottom: 10px;"></i>
                        <div>No Cover Image</div>
                    </div>
                </div>
            `;
        }
        
        // Add entrance animation
        setTimeout(() => {
            popup.classList.add('active');
        }, 10);
        
        console.log('View popup opened successfully with complete data:', book);
        
    } catch (error) {
        console.error('Error loading book details:', error);
        alert('Error loading book details. Please try again.');
        closeViewPopup();
    }
}

/**
 * Closes the view book popup
 */
function closeViewPopup() {
    console.log('Closing view popup');
    
    const popup = document.getElementById('viewBookPopup');
    
    // Remove active class for exit animation
    popup.classList.remove('active');
    
    // Hide popup after animation completes
    setTimeout(() => {
        popup.style.display = 'none';
    }, 300);
}

/**
 * Handle keyboard shortcuts for view popup
 * ESC - Close popup
 */
document.addEventListener('keydown', (event) => {
    const viewPopup = document.getElementById('viewBookPopup');
    
    if (viewPopup && viewPopup.style.display === 'flex') {
        if (event.key === 'Escape') {
            event.preventDefault();
            closeViewPopup();
        }
    }
});

/**
 * Close popup when clicking outside the popup container
 */
document.addEventListener('click', (event) => {
    const viewPopup = document.getElementById('viewBookPopup');
    
    if (event.target === viewPopup) {
        closeViewPopup();
    }
});

// Make functions globally available
window.viewBook = viewBook;
window.closeViewPopup = closeViewPopup;

console.log('View button functionality loaded');
