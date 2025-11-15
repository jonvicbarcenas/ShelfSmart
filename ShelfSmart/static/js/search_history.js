/**
 * Search History Management
 * Handles saving, retrieving, and displaying user search history
 */

// Global search history manager
const SearchHistory = {
    // Configuration
    config: {
        maxHistoryDisplay: 10,
        debounceDelay: 1000, // 1 second delay before saving
        saveEndpoint: '/search-history/api/save/',
        getEndpoint: '/search-history/api/',
        clearEndpoint: '/search-history/api/clear/'
    },

    // State
    state: {
        currentQuery: '',
        debounceTimer: null,
        isPopupOpen: false
    },

    /**
     * Initialize search history functionality
     */
    init: function() {
        console.log('Initializing search history...');
        this.attachEventListeners();
        this.setupSearchTracking();
    },

    /**
     * Attach event listeners
     */
    attachEventListeners: function() {
        // Close popup when clicking outside
        const overlay = document.querySelector('.search-history-overlay');
        if (overlay) {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    this.closePopup();
                }
            });
        }

        // Close button
        const closeBtn = document.querySelector('.search-history-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closePopup());
        }

        // Clear history button
        const clearBtn = document.querySelector('.search-history-clear-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearHistory());
        }

        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.state.isPopupOpen) {
                this.closePopup();
            }
        });
    },

    /**
     * Setup search tracking on the search input
     */
    setupSearchTracking: function() {
        const searchInput = document.getElementById('searchInput');
        if (!searchInput) return;

        // Track search input with debouncing
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            
            if (query.length >= 3) {
                // Clear previous timer
                if (this.state.debounceTimer) {
                    clearTimeout(this.state.debounceTimer);
                }

                // Set new timer to save after delay
                this.state.debounceTimer = setTimeout(() => {
                    this.saveSearch(query);
                }, this.config.debounceDelay);
            }
        });

        // Also track on Enter key
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const query = e.target.value.trim();
                if (query.length >= 3) {
                    // Clear any pending timer
                    if (this.state.debounceTimer) {
                        clearTimeout(this.state.debounceTimer);
                    }
                    this.saveSearch(query);
                }
            }
        });
    },

    /**
     * Save search query to history
     */
    saveSearch: function(query) {
        if (!query || query === this.state.currentQuery) return;

        this.state.currentQuery = query;

        // Count visible results
        const table = document.querySelector('table');
        let resultsCount = 0;
        
        if (table) {
            const rows = table.querySelectorAll('tbody tr:not([style*="display: none"])');
            resultsCount = rows.length;
        }

        // Get CSRF token
        const csrftoken = this.getCookie('csrftoken');

        // Send to server
        fetch(this.config.saveEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                search_query: query,
                search_type: 'general',
                results_count: resultsCount
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Search history saved:', query);
            }
        })
        .catch(error => {
            console.error('Error saving search history:', error);
        });
    },

    /**
     * Open search history popup
     */
    openPopup: function() {
        const overlay = document.querySelector('.search-history-overlay');
        if (!overlay) return;

        this.state.isPopupOpen = true;
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';

        // Load history
        this.loadHistory();
    },

    /**
     * Close search history popup
     */
    closePopup: function() {
        const overlay = document.querySelector('.search-history-overlay');
        if (!overlay) return;

        this.state.isPopupOpen = false;
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    },

    /**
     * Load search history from server
     */
    loadHistory: function() {
        const contentContainer = document.querySelector('.search-history-content');
        if (!contentContainer) return;

        // Show loading state
        contentContainer.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #718096;">
                <i class="fas fa-spinner fa-spin" style="font-size: 32px; color: #667eea;"></i>
                <p style="margin-top: 12px;">Loading search history...</p>
            </div>
        `;

        // Fetch history
        fetch(`${this.config.getEndpoint}?limit=${this.config.maxHistoryDisplay}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.renderHistory(data.history);
                    this.updateFooterInfo(data.history.length);
                } else {
                    this.showError('Failed to load search history');
                }
            })
            .catch(error => {
                console.error('Error loading search history:', error);
                this.showError('An error occurred while loading history');
            });
    },

    /**
     * Render search history items
     */
    renderHistory: function(historyItems) {
        const contentContainer = document.querySelector('.search-history-content');
        if (!contentContainer) return;

        // Check if empty
        if (!historyItems || historyItems.length === 0) {
            contentContainer.innerHTML = `
                <div class="search-history-empty">
                    <i class="fas fa-clock"></i>
                    <h3>No Search History</h3>
                    <p>Your recent searches will appear here</p>
                </div>
            `;
            return;
        }

        // Build history list HTML
        let html = '<div class="search-history-list">';
        
        historyItems.forEach(item => {
            const timeAgo = this.getTimeAgo(item.created_at);
            
            html += `
                <div class="search-history-item" data-query="${this.escapeHtml(item.search_query)}">
                    <div class="search-history-item-content">
                        <div class="search-history-item-query">
                            <i class="fas fa-search"></i>
                            <span>${this.escapeHtml(item.search_query)}</span>
                        </div>
                        <div class="search-history-item-meta">
                            <span>
                                <i class="far fa-clock"></i>
                                ${timeAgo}
                            </span>
                            <span>
                                <i class="fas fa-hashtag"></i>
                                ${item.results_count} results
                            </span>
                        </div>
                    </div>
                    <div class="search-history-item-actions">
                        <button class="search-history-item-btn" onclick="SearchHistory.applySearch('${this.escapeHtml(item.search_query)}')">
                            <i class="fas fa-redo"></i>
                            Search Again
                        </button>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        contentContainer.innerHTML = html;
    },

    /**
     * Apply a search from history
     */
    applySearch: function(query) {
        const searchInput = document.getElementById('searchInput');
        if (!searchInput) return;

        // Set the search input value
        searchInput.value = query;

        // Trigger the search
        const event = new Event('keyup', { bubbles: true });
        searchInput.dispatchEvent(event);

        // Close the popup
        this.closePopup();

        // Scroll to results
        setTimeout(() => {
            const tableContainer = document.querySelector('.table-container');
            if (tableContainer) {
                tableContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }, 100);
    },

    /**
     * Clear all search history
     */
    clearHistory: function() {
        if (!confirm('Are you sure you want to clear all search history?')) {
            return;
        }

        const csrftoken = this.getCookie('csrftoken');

        fetch(this.config.clearEndpoint, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Search history cleared');
                this.loadHistory(); // Reload to show empty state
            } else {
                alert('Failed to clear search history');
            }
        })
        .catch(error => {
            console.error('Error clearing search history:', error);
            alert('An error occurred while clearing history');
        });
    },

    /**
     * Update footer info
     */
    updateFooterInfo: function(count) {
        const infoElement = document.querySelector('.search-history-info');
        if (!infoElement) return;

        infoElement.innerHTML = `
            <i class="fas fa-info-circle"></i>
            <span>Showing ${count} recent ${count === 1 ? 'search' : 'searches'}</span>
        `;
    },

    /**
     * Show error message
     */
    showError: function(message) {
        const contentContainer = document.querySelector('.search-history-content');
        if (!contentContainer) return;

        contentContainer.innerHTML = `
            <div class="search-history-empty">
                <i class="fas fa-exclamation-triangle" style="color: #f56565;"></i>
                <h3>Error</h3>
                <p>${message}</p>
            </div>
        `;
    },

    /**
     * Calculate time ago from timestamp
     */
    getTimeAgo: function(timestamp) {
        const now = new Date();
        // Backend now sends ISO format timestamps with timezone info
        const pastTime = new Date(timestamp);
        
        const diffMs = now - pastTime;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        
        return pastTime.toLocaleDateString();
    },

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml: function(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Get cookie value
     */
    getCookie: function(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    SearchHistory.init();
});
