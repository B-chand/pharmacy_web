/* PharmaFlow – main.js */

document.addEventListener('DOMContentLoaded', () => {

  // ── Sidebar toggle (mobile) ────────────────────────────────────
  const sidebar  = document.getElementById('sidebar');
  const overlay  = document.getElementById('sidebar-overlay');
  const hamburger = document.getElementById('hamburger');

  function openSidebar() {
    sidebar?.classList.add('open');
    overlay?.classList.add('show');
    document.body.style.overflow = 'hidden';
  }
  function closeSidebar() {
    sidebar?.classList.remove('open');
    overlay?.classList.remove('show');
    document.body.style.overflow = '';
  }

  hamburger?.addEventListener('click', openSidebar);
  overlay?.addEventListener('click', closeSidebar);

  // ── Auto-dismiss alerts ────────────────────────────────────────
  document.querySelectorAll('.alert:not(.alert-permanent)').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity .5s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 500);
    }, 4500);
  });

  // ── Delete confirmation ────────────────────────────────────────
  // Handled via Bootstrap modal – see confirm_delete.html

  // ── Active nav link ────────────────────────────────────────────
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item[href]').forEach(el => {
    const href = el.getAttribute('href');
    if (href !== '/' && path.startsWith(href)) {
      el.classList.add('active');
    } else if (href === '/' && path === '/') {
      el.classList.add('active');
    }
  });

  // ── Purchase/Sale: auto-fill price from medicine selection ─────
  const medicineSelect = document.getElementById('id_medicine');
  const priceInput     = document.getElementById('id_total_price');
  const quantityInput  = document.getElementById('id_quantity');

  if (medicineSelect && priceInput && quantityInput) {
    // Price data embedded in option data attributes (set in template)
    function updatePrice() {
      const opt = medicineSelect.options[medicineSelect.selectedIndex];
      const unitPrice = parseFloat(opt?.dataset?.price || 0);
      const qty = parseInt(quantityInput.value || 1);
      if (unitPrice && qty) {
        priceInput.value = (unitPrice * qty).toFixed(2);
      }
    }
    medicineSelect.addEventListener('change', updatePrice);
    quantityInput.addEventListener('input', updatePrice);
  }

  // ── Table Sorting and Pagination ──────────────────────────────
  // Medicine table sorting and pagination
  const medicineTable = document.getElementById('medicine-table');
  const medicineTbody = document.getElementById('medicine-tbody');
  const paginationControls = document.getElementById('pagination-controls');
  const showingStart = document.getElementById('showing-start');
  const showingEnd = document.getElementById('showing-end');
  const prevPage = document.getElementById('prev-page');
  const nextPage = document.getElementById('next-page');

  if (medicineTable && medicineTbody) {
    let currentSort = { column: null, direction: 'asc' };
    let currentPage = 1;
    const itemsPerPage = 10;
    let allRows = Array.from(medicineTbody.querySelectorAll('tr'));

    // Sort functionality
    medicineTable.querySelectorAll('th[data-sort]').forEach(th => {
      th.addEventListener('click', () => {
        const column = th.dataset.sort;
        if (currentSort.column === column) {
          currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
          currentSort.column = column;
          currentSort.direction = 'asc';
        }

        // Update sort icons
        medicineTable.querySelectorAll('th[data-sort] .sort-icon').forEach(icon => {
          icon.className = 'bi bi-chevron-expand sort-icon';
        });
        th.querySelector('.sort-icon').className = `bi bi-chevron-${currentSort.direction === 'asc' ? 'up' : 'down'} sort-icon`;

        sortTable();
        currentPage = 1;
        paginateTable();
      });
    });

    function sortTable() {
      allRows.sort((a, b) => {
        let aVal = a.dataset[currentSort.column] || '';
        let bVal = b.dataset[currentSort.column] || '';

        // Handle numeric sorting
        if (['stock', 'price'].includes(currentSort.column)) {
          aVal = parseFloat(aVal) || 0;
          bVal = parseFloat(bVal) || 0;
        } else if (currentSort.column === 'expiry') {
          aVal = new Date(aVal);
          bVal = new Date(bVal);
        }

        if (aVal < bVal) return currentSort.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return currentSort.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }

    function paginateTable() {
      const totalItems = allRows.length;
      const totalPages = Math.ceil(totalItems / itemsPerPage);
      const startIndex = (currentPage - 1) * itemsPerPage;
      const endIndex = Math.min(startIndex + itemsPerPage, totalItems);

      // Hide all rows
      allRows.forEach(row => row.style.display = 'none');

      // Show current page rows
      allRows.slice(startIndex, endIndex).forEach(row => row.style.display = '');

      // Update pagination info
      showingStart.textContent = totalItems > 0 ? startIndex + 1 : 0;
      showingEnd.textContent = endIndex;

      // Update pagination controls
      prevPage.classList.toggle('disabled', currentPage === 1);
      nextPage.classList.toggle('disabled', currentPage === totalPages);

      // Show/hide pagination if needed
      paginationControls.style.display = totalItems > itemsPerPage ? '' : 'none';
    }

    // Pagination event listeners
    prevPage.addEventListener('click', (e) => {
      e.preventDefault();
      if (currentPage > 1) {
        currentPage--;
        paginateTable();
      }
    });

    nextPage.addEventListener('click', (e) => {
      e.preventDefault();
      const totalPages = Math.ceil(allRows.length / itemsPerPage);
      if (currentPage < totalPages) {
        currentPage++;
        paginateTable();
      }
    });

    // Initialize pagination
    if (allRows.length > itemsPerPage) {
      paginateTable();
    }
  }

  // Supplier table sorting and pagination
  const supplierTable = document.getElementById('supplier-table');
  const supplierTbody = document.getElementById('supplier-tbody');
  const supplierPaginationControls = document.getElementById('supplier-pagination-controls');
  const supplierShowingStart = document.getElementById('supplier-showing-start');
  const supplierShowingEnd = document.getElementById('supplier-showing-end');
  const supplierPrevPage = document.getElementById('supplier-prev-page');
  const supplierNextPage = document.getElementById('supplier-next-page');

  if (supplierTable && supplierTbody) {
    let supplierCurrentSort = { column: null, direction: 'asc' };
    let supplierCurrentPage = 1;
    const supplierItemsPerPage = 10;
    let supplierAllRows = Array.from(supplierTbody.querySelectorAll('tr'));

    // Sort functionality
    supplierTable.querySelectorAll('th[data-sort]').forEach(th => {
      th.addEventListener('click', () => {
        const column = th.dataset.sort;
        if (supplierCurrentSort.column === column) {
          supplierCurrentSort.direction = supplierCurrentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
          supplierCurrentSort.column = column;
          supplierCurrentSort.direction = 'asc';
        }

        // Update sort icons
        supplierTable.querySelectorAll('th[data-sort] .sort-icon').forEach(icon => {
          icon.className = 'bi bi-chevron-expand sort-icon';
        });
        th.querySelector('.sort-icon').className = `bi bi-chevron-${supplierCurrentSort.direction === 'asc' ? 'up' : 'down'} sort-icon`;

        supplierSortTable();
        supplierCurrentPage = 1;
        supplierPaginateTable();
      });
    });

    function supplierSortTable() {
      supplierAllRows.sort((a, b) => {
        let aVal = a.dataset[supplierCurrentSort.column] || '';
        let bVal = b.dataset[supplierCurrentSort.column] || '';

        // Handle numeric sorting
        if (supplierCurrentSort.column === 'medicines') {
          aVal = parseInt(aVal) || 0;
          bVal = parseInt(bVal) || 0;
        } else if (supplierCurrentSort.column === 'since') {
          aVal = new Date(aVal);
          bVal = new Date(bVal);
        }

        if (aVal < bVal) return supplierCurrentSort.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return supplierCurrentSort.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }

    function supplierPaginateTable() {
      const totalItems = supplierAllRows.length;
      const totalPages = Math.ceil(totalItems / supplierItemsPerPage);
      const startIndex = (supplierCurrentPage - 1) * supplierItemsPerPage;
      const endIndex = Math.min(startIndex + supplierItemsPerPage, totalItems);

      // Hide all rows
      supplierAllRows.forEach(row => row.style.display = 'none');

      // Show current page rows
      supplierAllRows.slice(startIndex, endIndex).forEach(row => row.style.display = '');

      // Update pagination info
      supplierShowingStart.textContent = totalItems > 0 ? startIndex + 1 : 0;
      supplierShowingEnd.textContent = endIndex;

      // Update pagination controls
      supplierPrevPage.classList.toggle('disabled', supplierCurrentPage === 1);
      supplierNextPage.classList.toggle('disabled', supplierCurrentPage === totalPages);

      // Show/hide pagination if needed
      supplierPaginationControls.style.display = totalItems > supplierItemsPerPage ? '' : 'none';
    }

    // Pagination event listeners
    supplierPrevPage.addEventListener('click', (e) => {
      e.preventDefault();
      if (supplierCurrentPage > 1) {
        supplierCurrentPage--;
        supplierPaginateTable();
      }
    });

    supplierNextPage.addEventListener('click', (e) => {
      e.preventDefault();
      const totalPages = Math.ceil(supplierAllRows.length / supplierItemsPerPage);
      if (supplierCurrentPage < totalPages) {
        supplierCurrentPage++;
        supplierPaginateTable();
      }
    });

    // Initialize pagination
    if (supplierAllRows.length > supplierItemsPerPage) {
      supplierPaginateTable();
    }
  }
