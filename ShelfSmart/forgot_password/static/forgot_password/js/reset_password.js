document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('resetPasswordForm');
    if (!form) return;

    const usernameInput = document.getElementById('username');
    const newPasswordInput = document.getElementById('newPassword');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const otpInput = document.getElementById('otpCode');
    const sendOtpButton = document.getElementById('sendOtpButton');
    const resetButton = document.getElementById('resetButton');
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    const infoMessage = document.getElementById('infoMessage');
    const otpStatusMessage = document.getElementById('otpStatusMessage');

    const fieldErrors = {
        username: form.querySelector('.field-error[data-field="username"]'),
        new_password1: form.querySelector('.field-error[data-field="new_password1"]'),
        new_password2: form.querySelector('.field-error[data-field="new_password2"]'),
        otp: form.querySelector('.field-error[data-field="otp"]'),
    };

    const resetMessages = () => {
        errorMessage.hidden = true;
        errorMessage.textContent = '';
        successMessage.hidden = true;
        successMessage.textContent = '';
        infoMessage.hidden = true;
        infoMessage.textContent = '';
        Object.values(fieldErrors).forEach((el) => {
            if (!el) return;
            el.hidden = true;
            el.innerHTML = '';
        });
        otpStatusMessage.hidden = true;
        otpStatusMessage.textContent = '';
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

    const startOtpCountdown = (expiresAtISO) => {
        if (!expiresAtISO) return;

        const targetDate = new Date(expiresAtISO);
        let countdownInterval = null;

        const updateCountdown = () => {
            const now = new Date();
            const diff = targetDate - now;

            if (diff <= 0) {
                clearInterval(countdownInterval);
                otpStatusMessage.hidden = false;
                otpStatusMessage.textContent = 'OTP has expired. Please request a new one.';
                otpInput.value = '';
                sendOtpButton.disabled = false;
                sendOtpButton.textContent = 'SEND OTP';
                return;
            }

            const minutes = Math.floor(diff / 1000 / 60);
            const seconds = Math.floor((diff / 1000) % 60);

            sendOtpButton.disabled = true;
            sendOtpButton.textContent = `OTP SENT (${minutes}:${seconds.toString().padStart(2, '0')})`;
        };

        countdownInterval = setInterval(updateCountdown, 1000);
        updateCountdown();
    };

    const sendOtp = async () => {
        resetMessages();

        const username = usernameInput.value.trim();
        if (!username) {
            errorMessage.hidden = false;
            errorMessage.textContent = 'Please enter your username before requesting an OTP.';
            fieldErrors.username.hidden = false;
            fieldErrors.username.innerHTML = '<span>Please enter your username.</span>';
            return;
        }

        sendOtpButton.disabled = true;
        const originalText = sendOtpButton.textContent;
        sendOtpButton.textContent = 'SENDING...';

        try {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('send_otp', '1');
            const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]').value;

            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken,
                },
            });

            const payload = await response.json();

            if (response.ok && payload.success) {
                infoMessage.hidden = false;
                infoMessage.textContent = payload.message || 'OTP sent successfully.';
                otpStatusMessage.hidden = false;
                otpStatusMessage.textContent = 'Enter the OTP sent to your registered email.';
                otpInput.focus();
                if (payload.expires_at) {
                    startOtpCountdown(payload.expires_at);
                }
                return;
            }

            const errorText = payload.message || 'Failed to send OTP. Please try again.';
            errorMessage.hidden = false;
            errorMessage.textContent = errorText;
            if (payload.field_errors) {
                renderFieldErrors(payload.field_errors);
            }
        } catch (error) {
            console.error('[forgot_password] Send OTP error:', error);
            errorMessage.hidden = false;
            errorMessage.textContent = 'An error occurred. Please try again.';
        } finally {
            if (!sendOtpButton.disabled) {
                sendOtpButton.disabled = false;
                sendOtpButton.textContent = originalText;
            }
        }
    };

    if (sendOtpButton) {
        sendOtpButton.addEventListener('click', () => {
            void sendOtp();
        });
    }

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

        if (!otpInput.value.trim()) {
            errorMessage.hidden = false;
            errorMessage.textContent = 'Please enter the OTP sent to your email.';
            fieldErrors.otp.hidden = false;
            fieldErrors.otp.innerHTML = '<span>Please enter your OTP.</span>';
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
