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

// Profile edit functionality
const form = document.getElementById('profileForm');
const editBtn = document.getElementById('editBtn');
const saveBtn = document.getElementById('saveBtn');
const cancelBtn = document.getElementById('cancelBtn');
const inputs = form.querySelectorAll('input:not([type="hidden"])');

let originalValues = {};

// Store original values
inputs.forEach(input => {
    originalValues[input.name] = input.value;
});

// Edit button handler
editBtn.addEventListener('click', function() {
    inputs.forEach(input => {
        if (input.id !== 'studentId') {
            input.disabled = false;
        }
    });
    editBtn.style.display = 'none';
    saveBtn.style.display = 'inline-flex';
    cancelBtn.style.display = 'inline-flex';
});

// Cancel button handler
cancelBtn.addEventListener('click', function() {
    inputs.forEach(input => {
        input.value = originalValues[input.name];
        input.disabled = true;
    });
    editBtn.style.display = 'inline-flex';
    saveBtn.style.display = 'none';
    cancelBtn.style.display = 'none';
});

// Form validation
form.addEventListener('submit', function(e) {
    const name = document.getElementById('fullName').value.trim();
    const email = document.getElementById('email').value.trim();
    
    if (!name || !email) {
        e.preventDefault();
        alert('Name and Email are required fields!');
        return false;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        e.preventDefault();
        alert('Please enter a valid email address!');
        return false;
    }
});

// Auto-dismiss alerts after 5 seconds
setTimeout(() => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        alert.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => alert.remove(), 300);
    });
}, 5000);