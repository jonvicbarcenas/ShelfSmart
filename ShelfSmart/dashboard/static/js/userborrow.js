// userborrow.js - JavaScript for userborrow.html page

document.addEventListener('DOMContentLoaded', () => {
  const tabs = document.querySelectorAll('.tab');
  const borrowedTable = document.getElementById('borrowed-table');
  const returnedTable = document.getElementById('returned-table');
  const searchInput = document.getElementById('search-input');

  // Tab switching logic
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      if (tab.dataset.tab === 'borrowed') {
        borrowedTable.style.display = 'table';
        returnedTable.style.display = 'none';
      } else {
        borrowedTable.style.display = 'none';
        returnedTable.style.display = 'table';
      }
      searchInput.value = '';
      filterTable('');
    });
  });

  // Search filter logic
  searchInput.addEventListener('input', (e) => {
    const filter = e.target.value.toLowerCase();
    filterTable(filter);
  });

  function filterTable(filter) {
    let table;
    if (document.querySelector('.tab.active').dataset.tab === 'borrowed') {
      table = borrowedTable;
    } else {
      table = returnedTable;
    }
    const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
    for (let row of rows) {
      const idCell = row.cells[0].textContent.toLowerCase();
      const userIdCell = row.cells[1].textContent.toLowerCase();
      if (idCell.includes(filter) || userIdCell.includes(filter)) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    }
  }

  // Return button click handler
  document.querySelectorAll('.action-btn').forEach(button => {
    button.addEventListener('click', (e) => {
      const row = e.target.closest('tr');
      const bookId = row.cells[0].textContent;
      alert(`Return action triggered for Book ID: ${bookId}`);
      // Here you can add actual return logic, e.g., API call
    });
  });
});
