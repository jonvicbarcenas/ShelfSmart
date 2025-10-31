// Settings page specific behavior and safety rails
(() => {
  document.addEventListener('DOMContentLoaded', () => {
    // Add a scoped class to body so CSS only affects this page
    if (document.body && !document.body.classList.contains('settings-page')) {
      document.body.classList.add('settings-page');
    }

    // Detect if a global sidebar exists to adjust layout
    const wrapper = document.querySelector('.settings-wrap');
    if (wrapper) {
      const hasSidebar = document.querySelector('.sidebar');
      if (hasSidebar) wrapper.classList.add('has-global-sidebar');
    }

    // Prevent double-submit on settings form
    const form = document.querySelector('#settings-form');
    if (form) {
      form.addEventListener('submit', e => {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn && !submitBtn.disabled) {
          submitBtn.disabled = true;
          submitBtn.classList.add('disabled');
          setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.classList.remove('disabled');
          }, 3000);
        }
      });
    }

    // Update time and date in header
    function updateDateTime() {
      const now = new Date();
      const timeElement = document.getElementById('currentTime');
      if (timeElement) {
        timeElement.textContent = now.toLocaleTimeString('en-US', {
          hour: '2-digit', minute: '2-digit', hour12: true
        });
      }
    }
    updateDateTime();
    setInterval(updateDateTime, 1000);
  });
})();
