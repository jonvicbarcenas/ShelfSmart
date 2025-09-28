document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const username = this.username.value.trim();
    const password = this.password.value.trim();

    if (!username || !password) {
        alert('Please fill in all fields');
        return;
    }

    // Add loading state
    const submitBtn = this.querySelector('.btn-signin');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'SIGNING IN...';
    submitBtn.disabled = true;

    // Submit the form (you can customize this for your Django backend)
    fetch(window.location.href, {
        method: 'POST',
        body: new FormData(this),
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect_url || '/dashboard/';
        } else {
            alert(data.error || 'Login failed. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    })
    .finally(() => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });
});

// Add input focus animations
document.querySelectorAll('.form-input').forEach(input => {
    input.addEventListener('focus', function() {
        this.style.transform = 'translateY(-2px)';
        this.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
    });

    input.addEventListener('blur', function() {
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = 'none';
    });
});
