// Update Time and Date
function updateDateTime() {
    const now = new Date();
    
    // Format time (12-hour format with AM/PM)
    const hours = now.getHours();
    const minutes = now.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours % 12 || 12;
    const displayMinutes = minutes < 10 ? '0' + minutes : minutes;
    const timeString = `${displayHours}:${displayMinutes} ${ampm}`;
    
    // Format date (MMM DD, YYYY)
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const month = months[now.getMonth()];
    const day = now.getDate();
    const year = now.getFullYear();
    const dateString = `${month} ${day < 10 ? '0' + day : day}, ${year}`;
    
    // Update DOM elements
    const timeElement = document.getElementById('currentTime');
    const dateElement = document.getElementById('currentDate');
    
    if (timeElement) timeElement.textContent = timeString;
    if (dateElement) dateElement.textContent = dateString;
}

// Profile Form Editing
document.addEventListener('DOMContentLoaded', function() {
    // Update time immediately and every minute
    updateDateTime();
    setInterval(updateDateTime, 60000);
    
    const profileForm = document.getElementById('profileForm');
    const editBtn = document.getElementById('editBtn');
    const saveBtn = document.getElementById('saveBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const formInputs = profileForm.querySelectorAll('input');
    
    // Store original values
    let originalValues = {};
    
    // Edit button click
    editBtn.addEventListener('click', function() {
        // Store original values before editing
        formInputs.forEach(input => {
            originalValues[input.id] = input.value;
            input.disabled = false;
        });
        
        // Disable Student ID field (if exists)
        const studentIdInput = document.getElementById('studentId');
        if (studentIdInput) {
            studentIdInput.disabled = true;
        }
        
        // Toggle button visibility
        editBtn.style.display = 'none';
        saveBtn.style.display = 'inline-block';
        cancelBtn.style.display = 'inline-block';
        
        // Add editing class for styling
        profileForm.classList.add('editing');
    });
    
    // Cancel button click
    cancelBtn.addEventListener('click', function() {
        // Restore original values
        formInputs.forEach(input => {
            input.value = originalValues[input.id];
            input.disabled = true;
        });
        
        // Toggle button visibility
        editBtn.style.display = 'inline-block';
        saveBtn.style.display = 'none';
        cancelBtn.style.display = 'none';
        
        // Remove editing class
        profileForm.classList.remove('editing');
    });
    
    // Form submit (Save)
    profileForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(profileForm);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });
        
        // Here you would typically send data to server
        console.log('Saving profile data:', data);
        
        // Simulate save (you'll replace this with actual AJAX call)
        setTimeout(() => {
            // Disable all inputs
            formInputs.forEach(input => {
                input.disabled = true;
            });
            
            // Update stored values
            originalValues = data;
            
            // Toggle button visibility
            editBtn.style.display = 'inline-block';
            saveBtn.style.display = 'none';
            cancelBtn.style.display = 'none';
            
            // Remove editing class
            profileForm.classList.remove('editing');
            
            // Show success message (optional)
            alert('Profile updated successfully!');
        }, 500);
    });
});