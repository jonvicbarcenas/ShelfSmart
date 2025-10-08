document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('resetPasswordForm');
    if (!form) return;

    const usernameInput = document.getElementById('username');
    const newPasswordInput = document.getElementById('newPassword');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const resetButton = document.getElementById('resetButton');
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');

    const fieldErrors = {
        username: form.querySelector('.field-error[data-field="username"]'),
        new_password1: form.querySelector('.field-error[data-field="new_password1"]'),
        new_password2: form.querySelector('.field-error[data-field="new_password2"]'),
    };

    const resetMessages = () => {
        errorMessage.hidden = true;
        errorMessage.textContent = '';
        successMessage.hidden = true;
        successMessage.textContent = '';
        Object.values(fieldErrors).forEach((el) => {
            if (!el) return;
            el.hidden = true;
            el.innerHTML = '';
        });
    };

    const renderFieldErrors = (errors = {}) => {
        Object.entries(errors).forEach(([name, messages]) => {
            const target = fieldErrors[name];
            if (!target) return;
            target.hidden = false;
            target.innerHTML = messages
                .map((item) => `<span>${item.message || item}</span>`)
                .join('');
        });
    };

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        resetMessages();

        const username = usernameInput.value.trim();
        const newPassword = newPasswordInput.value.trim();
        const confirmPassword = confirmPasswordInput.value.trim();

        if (!username) {
            errorMessage.hidden = false;
            errorMessage.textContent = 'Please enter your username.';
            fieldErrors.username.hidden = false;
            fieldErrors.username.innerHTML = '<span>Please enter your username.</span>';
            return;
        }

        if (newPassword !== confirmPassword) {
            errorMessage.hidden = false;
            errorMessage.textContent = 'Passwords do not match';
            fieldErrors.new_password2.hidden = false;
            fieldErrors.new_password2.innerHTML = '<span>Passwords do not match</span>';
            return;
        }

        if (newPassword.length < 8) {
            errorMessage.hidden = false;
            errorMessage.textContent = 'Password must be at least 8 characters long';
            fieldErrors.new_password1.hidden = false;
            fieldErrors.new_password1.innerHTML = '<span>Password must be at least 8 characters long</span>';
            return;
        }

        resetButton.disabled = true;
        const originalText = resetButton.textContent;
        resetButton.textContent = 'RESETTING...';

        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
            });

            const payload = await response.json();

            if (response.ok && payload.success) {
                successMessage.hidden = false;
                successMessage.textContent = 'Password reset successful! Redirecting to login...';
                setTimeout(() => {
                    window.location.href = payload.redirect_url || '/login/';
                }, 2000);
                return;
            }

            const errorText = payload.error || 'Failed to reset password. Please try again.';
            errorMessage.hidden = false;
            errorMessage.textContent = errorText;
            renderFieldErrors(payload.field_errors);
        } catch (error) {
            console.error('[forgot_password] Reset password error:', error);
            errorMessage.hidden = false;
            errorMessage.textContent = 'An error occurred. Please try again.';
        } finally {
            resetButton.disabled = false;
            resetButton.textContent = originalText;
        }
    });

    confirmPasswordInput.addEventListener('input', () => {
        if (!confirmPasswordInput.value) {
            confirmPasswordInput.style.borderColor = '#ddd';
            return;
        }
        if (confirmPasswordInput.value !== newPasswordInput.value) {
            confirmPasswordInput.style.borderColor = '#dc3545';
        } else {
            confirmPasswordInput.style.borderColor = '#ddd';
        }
    });

    [usernameInput, newPasswordInput, confirmPasswordInput].forEach((input) => {
        if (!input) return;
        input.addEventListener('focus', () => {
            input.style.transform = 'translateY(-2px)';
            input.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
        });
        input.addEventListener('blur', () => {
            input.style.transform = 'translateY(0)';
            input.style.boxShadow = 'none';
        });
    });
});
