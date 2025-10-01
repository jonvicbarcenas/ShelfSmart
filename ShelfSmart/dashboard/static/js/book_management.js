document.addEventListener('DOMContentLoaded', function() {
    // Initialize Time and Date Updates
    initializeTimeUpdates();
});

function initializeTimeUpdates() {
    function updateTimeAndDate() {
        const now = new Date();
        const timeElement = document.querySelector('.time');
        const dateElement = document.querySelector('.current-date');
        
        if (timeElement) {
            timeElement.textContent = now.toLocaleTimeString('en-US', { 
                hour: 'numeric', 
                minute: '2-digit',
                hour12: true 
            });
        }
        
        if (dateElement) {
            dateElement.textContent = now.toLocaleDateString('en-US', {
                month: 'short',
                day: '2-digit',
                year: 'numeric'
            });
        }
    }

    // Update time and date immediately and then every minute
    updateTimeAndDate();
    setInterval(updateTimeAndDate, 60000);
}