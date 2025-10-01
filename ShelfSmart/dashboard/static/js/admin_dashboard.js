document.addEventListener('DOMContentLoaded', function() {
    // Initialize Chart
    initializeBorrowChart();
    
    // Initialize Time Updates
    initializeTimeUpdates();
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

function initializeTimeUpdates() {
    function updateTime() {
        const now = new Date();
        const timeElement = document.querySelector('.time');
        if (timeElement) {
            timeElement.textContent = now.toLocaleTimeString('en-US', { 
                hour: 'numeric', 
                minute: '2-digit',
                hour12: true 
            });
        }
    }

    // Update time immediately and then every minute
    updateTime();
    setInterval(updateTime, 60000);
}