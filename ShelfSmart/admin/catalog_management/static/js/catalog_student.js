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

// Tab switching function
function switchTab(tabName) {
    // Get all tab buttons and contents
    const tabs = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    // Remove 'active' from all tabs and contents
    tabs.forEach(tab => tab.classList.remove('active'));
    tabContents.forEach(content => content.classList.remove('active'));

    // Find the correct tab button and content by tabName
    const activeTab = document.querySelector('.tab-btn[data-tab="' + tabName + '"]');
    const activeContent = document.getElementById(tabName + '-tab');

    // Add 'active' to the selected button and content
    if (activeTab) activeTab.classList.add('active');
    if (activeContent) activeContent.classList.add('active');
}