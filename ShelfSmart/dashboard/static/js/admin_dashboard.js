document.addEventListener('DOMContentLoaded', function() {
    // Initialize Chart
    initializeBorrowChart();
    
    // Initialize Time and Date Updates
    initializeTimeAndDateUpdates();
    
    // Initialize Logout Link
    initializeLogoutLink();
});

function initializeBorrowChart() {
    const ctx = document.getElementById('borrowChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [70, 30],
                backgroundColor: ['#333', '#666'],
                borderWidth: 0,
                cutout: '70%'
            }],
            labels: ['Total Borrowed Books', 'Total Returned Books']
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true
            }
        }
    });
}

function initializeTimeAndDateUpdates() {
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

function initializeLogoutLink() {
    const logoutLink = document.querySelector('.logout .nav-link');
    if (!logoutLink) {
        return;
    }

    const logoutUrl = '/logout/';
    logoutLink.setAttribute('href', logoutUrl);
}