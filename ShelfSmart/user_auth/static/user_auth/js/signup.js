document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('signupForm');
  if (!form) return;

  const submitBtn = document.querySelector('.btn-primary-wide');
  const generalErrorBox = form.querySelector('.form-errors');
  const fieldErrorBoxes = Array.from(form.querySelectorAll('.field-error'));
  const backBtn = document.querySelector('.btn-signin-outline');

  const originalText = submitBtn.textContent;

  const resetErrors = () => {
    if (generalErrorBox) {
      generalErrorBox.hidden = true;
      generalErrorBox.innerHTML = '';
    }
    fieldErrorBoxes.forEach((box) => {
      box.hidden = true;
      box.innerHTML = '';
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
      const items = errors.map((err) => `<span>${err.message || err}</span>`).join('');
      target.innerHTML = items;
    });
  };

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    resetErrors();

    submitBtn.disabled = true;
    submitBtn.textContent = 'SIGNING UP...';

    try {
      const response = await fetch(window.location.href, {
        method: 'POST',
        body: new FormData(form),
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      });

      const isJson = response.headers.get('content-type')?.includes('application/json');
      const payload = isJson ? await response.json() : null;

      if (response.ok && payload?.success) {
        window.location.href = payload.redirect_url || '/login/';
        return;
      }

      const message = payload?.error || 'Signup failed. Please review the fields below.';
      const fieldErrors = payload?.field_errors || {};
      renderErrors(message, fieldErrors);
    } catch (error) {
      console.error('Signup error:', error);
      renderErrors('An unexpected error occurred. Please try again.');
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
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

  const rightPanel = document.querySelector('.right-panel');
  const leftPanel = document.querySelector('.left-panel');
  if (rightPanel) rightPanel.classList.add('animate__animated', 'animate__fadeInLeft');
  if (leftPanel) leftPanel.classList.add('animate__animated', 'animate__fadeInRight');

  if (backBtn) {
    backBtn.addEventListener('click', (event) => {
      event.preventDefault();
      if (rightPanel) rightPanel.classList.add('animate__animated', 'animate__fadeOutRight');
      if (leftPanel) leftPanel.classList.add('animate__animated', 'animate__fadeOutLeft');
      setTimeout(() => {
        window.location.href = '/login/';
      }, 450);
    });
  }
});
