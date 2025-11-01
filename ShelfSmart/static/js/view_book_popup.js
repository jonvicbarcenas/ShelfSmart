/**
 * ================================================
 * VIEW BOOK POPUP - REUSABLE COMPONENT
 * Can be used across admin and user sides
 * ================================================
 */

/**
 * Configuration object - can be customized per implementation
 */
const ViewBookPopupConfig = {
    apiEndpoint: '/api/book/',  // Default endpoint, can be overridden
    popupId: 'viewBookPopup',
    enableKeyboardShortcuts: true,
    enableClickOutside: true
};

/**
 * Opens the view book popup and populates it with book data
 * Fetches complete data from the backend API
 * @param {number} bookId - The ID of the book to view
 * @param {string} customApiEndpoint - Optional custom API endpoint
 */
async function viewBook(bookId, customApiEndpoint = null) {
    console.log('Opening view popup for book ID:', bookId);
    
    const apiUrl = customApiEndpoint || ViewBookPopupConfig.apiEndpoint;
    const fullApiUrl = `${apiUrl}${bookId}/`;
    
    try {
        // Show loading state
        const popup = document.getElementById(ViewBookPopupConfig.popupId);
        if (!popup) {
            console.error('View book popup element not found');
            return;
        }
        
        popup.style.display = 'flex';
        
        // Set loading placeholders
        setLoadingState();
        
        // Fetch complete book data from API
        const response = await fetch(fullApiUrl);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to load book details');
        }
        
        const book = data.book;
        
        // Populate the view popup with complete data
        populateBookData(book);
        
        // Add entrance animation
        setTimeout(() => {
            popup.classList.add('active');
        }, 10);
        
        console.log('View popup opened successfully with complete data:', book);
        
    } catch (error) {
        console.error('Error loading book details:', error);
        alert('Error loading book details. Please try again.');
        closeViewBookPopup();
    }
}

/**
 * Sets loading placeholders for all fields
 */
function setLoadingState() {
    const loadingText = 'Loading...';
    const fields = [
        'view-book-id', 'view-isbn', 'view-title', 'view-subtitle',
        'view-description', 'view-category', 'view-publisher',
        'view-language', 'view-quantity', 'view-availability',
        'view-publication-date', 'view-edition', 'view-pages',
        'view-total-copies', 'view-authors'
    ];
    
    fields.forEach(fieldId => {
        const element = document.getElementById(fieldId);
        if (element) {
            element.textContent = loadingText;
        }
    });
    
    // Set loading for cover image
    const coverElem = document.getElementById('view-cover-image');
    if (coverElem) {
        coverElem.innerHTML = '<div class="loading-placeholder">Loading...</div>';
    }
}

/**
 * Populates all book data fields
 * @param {Object} book - Book data object
 */
function populateBookData(book) {
    // Basic Information
    setFieldValue('view-book-id', book.book_id);
    setFieldValue('view-isbn', book.isbn);
    setFieldValue('view-title', book.title);
    setFieldValue('view-subtitle', book.subtitle);
    setFieldValue('view-description', book.description);
    
    // Category and Publisher
    setFieldValue('view-category', book.category_name);
    setFieldValue('view-publisher', book.publisher_name);
    
    // Publication Details
    setFieldValue('view-language', book.language);
    setFieldValue('view-publication-date', book.publication_date);
    setFieldValue('view-edition', book.edition);
    setFieldValue('view-pages', book.pages);
    
    // Inventory
    setFieldValue('view-quantity', book.quantity);
    setFieldValue('view-total-copies', book.total_copies);
    
    // Availability (capitalize first letter)
    const availability = book.availability;
    setFieldValue('view-availability', availability ? 
        availability.charAt(0).toUpperCase() + availability.slice(1) : '-');
    
    // Authors (format as list)
    populateAuthors(book.authors);
    
    // Cover Image
    populateCoverImage(book.cover_image_url, book.title);
}

/**
 * Sets a field value with fallback to "-"
 * @param {string} fieldId - Element ID
 * @param {*} value - Value to set
 */
function setFieldValue(fieldId, value) {
    const element = document.getElementById(fieldId);
    if (element) {
        element.textContent = value || '-';
    }
}

/**
 * Populates the authors field
 * @param {Array} authors - Array of author objects
 */
function populateAuthors(authors) {
    const authorsElem = document.getElementById('view-authors');
    if (!authorsElem) return;
    
    if (authors && authors.length > 0) {
        const authorsText = authors.map(a => `${a.name} (${a.role})`).join(', ');
        authorsElem.textContent = authorsText;
    } else {
        authorsElem.textContent = '-';
    }
}

/**
 * Populates the cover image
 * @param {string} coverImageUrl - URL of the cover image
 * @param {string} bookTitle - Title for alt text
 */
function populateCoverImage(coverImageUrl, bookTitle) {
    const coverElem = document.getElementById('view-cover-image');
    if (!coverElem) return;
    
    if (coverImageUrl) {
        // Create image element with proper error handling
        const img = document.createElement('img');
        img.src = coverImageUrl;
        img.alt = `${bookTitle || 'Book'} Cover`;
        
        // Handle image load error
        img.onerror = function() {
            coverElem.innerHTML = getNoImagePlaceholder();
        };
        
        // Clear container and add image
        coverElem.innerHTML = '';
        coverElem.appendChild(img);
    } else {
        coverElem.innerHTML = getNoImagePlaceholder();
    }
}

/**
 * Returns HTML for no image placeholder
 * @returns {string} HTML string
 */
function getNoImagePlaceholder() {
    return `
        <div class="no-cover-placeholder">
            <i class="fas fa-image"></i>
            <div>No Cover Image</div>
        </div>
    `;
}

/**
 * Closes the view book popup
 */
function closeViewBookPopup() {
    console.log('Closing view popup');
    
    const popup = document.getElementById(ViewBookPopupConfig.popupId);
    if (!popup) return;
    
    // Remove active class for exit animation
    popup.classList.remove('active');
    
    // Hide popup after animation completes
    setTimeout(() => {
        popup.style.display = 'none';
    }, 300);
}

/**
 * Initialize keyboard shortcuts if enabled
 */
function initializeKeyboardShortcuts() {
    if (!ViewBookPopupConfig.enableKeyboardShortcuts) return;
    
    document.addEventListener('keydown', (event) => {
        const popup = document.getElementById(ViewBookPopupConfig.popupId);
        
        if (popup && popup.style.display === 'flex') {
            // ESC to close
            if (event.key === 'Escape') {
                event.preventDefault();
                closeViewBookPopup();
            }
        }
    });
}

/**
 * Initialize click outside to close if enabled
 */
function initializeClickOutside() {
    if (!ViewBookPopupConfig.enableClickOutside) return;
    
    document.addEventListener('click', (event) => {
        const popup = document.getElementById(ViewBookPopupConfig.popupId);
        
        if (event.target === popup) {
            closeViewBookPopup();
        }
    });
}

/**
 * Initialize the view book popup functionality
 * Call this on page load
 */
function initializeViewBookPopup(config = {}) {
    // Merge custom config with defaults
    Object.assign(ViewBookPopupConfig, config);
    
    // Initialize event listeners
    initializeKeyboardShortcuts();
    initializeClickOutside();
    
    // Make functions globally available
    window.viewBook = viewBook;
    window.closeViewBookPopup = closeViewBookPopup;
    
    console.log('View book popup initialized with config:', ViewBookPopupConfig);
}

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => initializeViewBookPopup());
} else {
    initializeViewBookPopup();
}
