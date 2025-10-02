document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
    if (!form) return;

    const submitBtn = form.querySelector('.btn-signin');
    const generalErrorBox = form.querySelector('.form-errors');
    const fieldErrorBoxes = Array.from(form.querySelectorAll('.field-error'));
    const signupBtn = document.querySelector('.btn-signup');

    const originalBtnText = submitBtn.textContent;

    const resetErrors = () => {
        if (generalErrorBox) {
            generalErrorBox.hidden = true;
            generalErrorBox.innerHTML = '';
        }
        fieldErrorBoxes.forEach(box => {
            box.innerHTML = '';
            box.hidden = true;
        });
    };

    const renderErrors = (message, fieldErrors = {}) => {
        if (generalErrorBox) {
            generalErrorBox.hidden = false;
            generalErrorBox.innerHTML = message ? `<p>${message}</p>` : '';
        }

        Object.entries(fieldErrors).forEach(([name, errors]) => {
            const target = form.querySelector(`.field-error[data-field="${name}"]`);
            if (!target) return;
            target.hidden = false;
            const items = errors.map(err => `<span>${err.message || err}</span>`).join('');
            target.innerHTML = items;
        });
    };

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        resetErrors();

        const formData = new FormData(form);
        const username = (formData.get('username') || '').toString().trim();
        const password = (formData.get('password') || '').toString().trim();
        if (!username || !password) {
            renderErrors('Please provide both username and password.');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'SIGNING IN...';

        try {
            const response = await fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
            });

            const isJson = response.headers.get('content-type')?.includes('application/json');
            const payload = isJson ? await response.json() : null;

            if (response.ok && payload?.success) {
                window.location.href = payload.redirect_url || '/dashboard/';
                return;
            }

            const message = payload?.error || 'Login failed. Please try again.';
            const fieldErrors = payload?.field_errors || {};
            renderErrors(message, fieldErrors);
        } catch (error) {
            console.error('Login error:', error);
            renderErrors('An unexpected error occurred. Please try again.');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalBtnText;
        }
    });

    document.querySelectorAll('.form-input').forEach((input) => {
        input.addEventListener('focus', function () {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
        });
        input.addEventListener('blur', function () {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });

    if (signupBtn) {
        signupBtn.addEventListener('click', () => {
            window.location.href = '/signup/';
        });
    }
});
