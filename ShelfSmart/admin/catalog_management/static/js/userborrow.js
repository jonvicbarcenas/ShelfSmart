// userborrow.js - interactions for the User Borrow page

(function() {
  function updateDateTime() {
    const now = new Date();
    const timeEl = document.getElementById('currentTime');
    const dateEl = document.getElementById('currentDate');
    if (timeEl) timeEl.textContent = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });
    if (dateEl) dateEl.textContent = now.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' });
  }
  updateDateTime();
  setInterval(updateDateTime, 60000);

  // Search filter
  const searchInput = document.getElementById('searchInput');
  if (searchInput) {
    searchInput.addEventListener('input', function(e) {
      const term = e.target.value.toLowerCase();
      const rows = document.querySelectorAll('#booksTableBody tr');
      rows.forEach(row => {
        const id = row.children[0]?.textContent.toLowerCase() || '';
        const name = row.children[1]?.textContent.toLowerCase() || '';
        const type = row.children[2]?.textContent.toLowerCase() || '';
        const match = id.includes(term) || type.includes(term) || name.includes(term);
        row.style.display = match ? '' : 'none';
      });
    });
  }

  // Acquire button - demo behaviour
  const acquireBtn = document.getElementById('acquireBtn');
  if (acquireBtn) {
    acquireBtn.addEventListener('click', () => {
      const selected = Array.from(document.querySelectorAll('.cart-checkbox:checked'))
        .map(cb => cb.closest('tr')?.dataset.id || cb.closest('tr')?.children[0].textContent.trim());
      if (!selected.length) {
        alert('No books selected.');
        return;
      }
      // Replace with real POST later
      alert('Acquiring books: ' + selected.join(', '));
    });
  }

  // Disable checkbox if not available
  document.querySelectorAll('#booksTableBody tr').forEach(row => {
    const status = row.querySelector('.status-badge');
    const checkbox = row.querySelector('.cart-checkbox');
    if (status && checkbox) {
      if (status.textContent.trim().toLowerCase() !== 'available') {
        checkbox.disabled = true;
        checkbox.title = 'Not available';
      }
    }
  });
})();
