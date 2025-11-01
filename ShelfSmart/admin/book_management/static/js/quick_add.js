// Quick Add Functions for ISBN Validation
// Separate file for easier debugging and maintenance

// Global state for quick-add confirmation
let quickAddPendingAction = null;

// Show custom confirmation popup
function showQuickAddConfirm(type, name) {
  return new Promise((resolve) => {
    const popup = document.getElementById('quickAddConfirmPopup');
    const message = document.getElementById('quickAddMessage');
    const typeSpan = document.getElementById('quickAddType');
    const nameSpan = document.getElementById('quickAddName');
    
    // Set the message
    typeSpan.textContent = type;
    nameSpan.textContent = name;
    
    // Store the resolve function
    quickAddPendingAction = resolve;
    
    // Show the popup
    popup.style.display = 'flex';
  });
}

// Confirm quick add action
function confirmQuickAdd() {
  if (quickAddPendingAction) {
    quickAddPendingAction(true);
    quickAddPendingAction = null;
  }
  closeQuickAddConfirm();
}

// Cancel quick add action
function cancelQuickAdd() {
  if (quickAddPendingAction) {
    quickAddPendingAction(false);
    quickAddPendingAction = null;
  }
  closeQuickAddConfirm();
}

// Close quick add confirmation popup
function closeQuickAddConfirm() {
  const popup = document.getElementById('quickAddConfirmPopup');
  popup.style.display = 'none';
}

// Quick Add Category
async function quickAddCategory(categoryName) {
  const confirmed = await showQuickAddConfirm('category', categoryName);
  if (!confirmed) return;
  
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
  const statusDiv = document.getElementById('isbn-status');
  
  try {
    // Show loading state
    statusDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding category...';
    statusDiv.className = 'isbn-status loading';
    
    const response = await fetch('/admin-panel/categories/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrfToken,
      },
      body: new URLSearchParams({
        action: 'add',
        category_name: categoryName,
        description: `Added from ISBN validation`,
        parent_category_id: ''
      })
    });
    
    if (response.ok) {
      statusDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Category added! Updating dropdown...';
      statusDiv.className = 'isbn-status loading';
      
      const refreshed = await refreshCategoryDropdown(categoryName);
      if (refreshed) {
        statusDiv.innerHTML = `<i class="fas fa-check-circle"></i> Category "${categoryName}" added and selected!`;
        statusDiv.className = 'isbn-status success';
      } else {
        statusDiv.innerHTML = `<i class="fas fa-check-circle"></i> Category "${categoryName}" added successfully!<br><small>Please select it from the dropdown.</small>`;
        statusDiv.className = 'isbn-status success';
      }
      
      // Auto re-validate ISBN to show other unmatched items
      setTimeout(() => {
        if (window.validateISBN) {
          window.validateISBN();
        }
      }, 2000);
    } else {
      statusDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> Error adding category. It may already exist.`;
      statusDiv.className = 'isbn-status error';
    }
  } catch (error) {
    console.error('Error adding category:', error);
    statusDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> Network error while adding category.';
    statusDiv.className = 'isbn-status error';
  }
}

// Quick Add Publisher
async function quickAddPublisher(publisherName) {
  const confirmed = await showQuickAddConfirm('publisher', publisherName);
  if (!confirmed) return;
  
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
  const statusDiv = document.getElementById('isbn-status');
  
  try {
    // Show loading state
    statusDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding publisher...';
    statusDiv.className = 'isbn-status loading';
    
    const response = await fetch('/admin-panel/publishers/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrfToken,
      },
      body: new URLSearchParams({
        action: 'add',
        publisher_name: publisherName,
        address: '',
        phone: '',
        email: '',
        website: '',
        established_year: ''
      })
    });
    
    if (response.ok) {
      statusDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Publisher added! Updating dropdown...';
      statusDiv.className = 'isbn-status loading';
      
      const refreshed = await refreshPublisherDropdown(publisherName);
      if (refreshed) {
        statusDiv.innerHTML = `<i class="fas fa-check-circle"></i> Publisher "${publisherName}" added and selected!`;
        statusDiv.className = 'isbn-status success';
      } else {
        statusDiv.innerHTML = `<i class="fas fa-check-circle"></i> Publisher "${publisherName}" added successfully!<br><small>Please select it from the dropdown.</small>`;
        statusDiv.className = 'isbn-status success';
      }
      
      // Auto re-validate ISBN to show other unmatched items
      setTimeout(() => {
        if (window.validateISBN) {
          window.validateISBN();
        }
      }, 2000);
    } else {
      statusDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> Error adding publisher. It may already exist.`;
      statusDiv.className = 'isbn-status error';
    }
  } catch (error) {
    console.error('Error adding publisher:', error);
    statusDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> Network error while adding publisher.';
    statusDiv.className = 'isbn-status error';
  }
}

// Quick Add Author
async function quickAddAuthor(authorName) {
  const confirmed = await showQuickAddConfirm('author', authorName);
  if (!confirmed) return;
  
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
  const statusDiv = document.getElementById('isbn-status');
  
  try {
    // Show loading state
    statusDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding author...';
    statusDiv.className = 'isbn-status loading';
    
    const response = await fetch('/admin-panel/authors/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrfToken,
      },
      body: new URLSearchParams({
        action: 'add',
        name: authorName,
        biography: '',
        nationality: ''
      })
    });
    
    if (response.ok) {
      statusDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Author added! Updating dropdown...';
      statusDiv.className = 'isbn-status loading';
      
      const refreshed = await refreshAuthorDropdown(authorName);
      if (refreshed) {
        statusDiv.innerHTML = `<i class="fas fa-check-circle"></i> Author "${authorName}" added and selected!`;
        statusDiv.className = 'isbn-status success';
      } else {
        statusDiv.innerHTML = `<i class="fas fa-check-circle"></i> Author "${authorName}" added successfully!<br><small>Please select it from the dropdown.</small>`;
        statusDiv.className = 'isbn-status success';
      }
      
      setTimeout(() => {
        if (window.validateISBN) {
          window.validateISBN();
        }
      }, 2000);
    } else {
      statusDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> Error adding author. It may already exist.`;
      statusDiv.className = 'isbn-status error';
    }
  } catch (error) {
    console.error('Error adding author:', error);
    statusDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> Network error while adding author.';
    statusDiv.className = 'isbn-status error';
  }
}

// Dropdown refresh functions - Fetch fresh data and rebuild dropdowns
async function refreshCategoryDropdown(newCategoryName) {
  try {
    // Fetch fresh page content
    const response = await fetch('/admin-panel/books/');
    if (response.ok) {
      const html = await response.text();
      
      // Extract category options using regex
      const categoryMatch = html.match(/<select[^>]*id="add-category"[^>]*>([\s\S]*?)<\/select>/);
      if (categoryMatch) {
        const currentSelect = document.getElementById('add-category');
        currentSelect.innerHTML = categoryMatch[1];
        
        // Auto-select the newly added category
        const newOption = Array.from(currentSelect.options).find(option => 
          option.text.trim().toLowerCase() === newCategoryName.toLowerCase()
        );
        if (newOption) {
          currentSelect.value = newOption.value;
          return true;
        }
      }
    }
  } catch (error) {
    console.error('Error refreshing category dropdown:', error);
  }
  return false;
}

async function refreshPublisherDropdown(newPublisherName) {
  try {
    // Fetch fresh page content
    const response = await fetch('/admin-panel/books/');
    if (response.ok) {
      const html = await response.text();
      
      // Extract publisher options using regex
      const publisherMatch = html.match(/<select[^>]*id="add-publisher"[^>]*>([\s\S]*?)<\/select>/);
      if (publisherMatch) {
        const currentSelect = document.getElementById('add-publisher');
        currentSelect.innerHTML = publisherMatch[1];
        
        // Auto-select the newly added publisher
        const newOption = Array.from(currentSelect.options).find(option => 
          option.text.trim().toLowerCase() === newPublisherName.toLowerCase()
        );
        if (newOption) {
          currentSelect.value = newOption.value;
          return true;
        }
      }
    }
  } catch (error) {
    console.error('Error refreshing publisher dropdown:', error);
  }
  return false;
}

async function refreshAuthorDropdown(newAuthorName) {
  try {
    // Fetch fresh page content
    const response = await fetch('/admin-panel/books/');
    if (response.ok) {
      const html = await response.text();
      
      // Extract author options using regex
      const authorMatch = html.match(/<select[^>]*id="author-0"[^>]*>([\s\S]*?)<\/select>/);
      if (authorMatch) {
        const newOptionsHTML = authorMatch[1];
        
        // Update all author dropdowns
        const allAuthorSelects = document.querySelectorAll('.author-select');
        allAuthorSelects.forEach(select => {
          const currentValue = select.value;
          select.innerHTML = newOptionsHTML;
          
          // Restore previous selection if it still exists
          if (currentValue && Array.from(select.options).some(opt => opt.value === currentValue)) {
            select.value = currentValue;
          }
        });
        
        // Auto-select the newly added author in the first dropdown
        const firstAuthorSelect = document.getElementById('author-0');
        const newOption = Array.from(firstAuthorSelect.options).find(option => 
          option.text.trim().toLowerCase() === newAuthorName.toLowerCase()
        );
        if (newOption) {
          firstAuthorSelect.value = newOption.value;
          return true;
        }
      }
    }
  } catch (error) {
    console.error('Error refreshing author dropdown:', error);
  }
  return false;
}

// Make functions globally available
window.quickAddCategory = quickAddCategory;
window.quickAddPublisher = quickAddPublisher;
window.quickAddAuthor = quickAddAuthor;
window.confirmQuickAdd = confirmQuickAdd;
window.cancelQuickAdd = cancelQuickAdd;
window.closeQuickAddConfirm = closeQuickAddConfirm;
