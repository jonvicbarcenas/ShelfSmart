// Update time and date
function updateDateTime() {
    const now = new Date();
    document.getElementById('currentTime').textContent = now.toLocaleTimeString('en-US', { 
        hour: '2-digit', minute: '2-digit', hour12: true 
    });
    document.getElementById('currentDate').textContent = now.toLocaleDateString('en-US', { 
        month: 'short', day: '2-digit', year: 'numeric' 
    });
}
updateDateTime();
setInterval(updateDateTime, 60000);

// Create Chart
document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('borrowChart');
    if (ctx) {
        new Chart(ctx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Borrowed Books', 'Returned Books'],
                datasets: [{
                    data: [borrowedCount, returnedCount],
                    backgroundColor: ['#4A90E2', '#7CB342'],
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + ' books';
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
    }
});