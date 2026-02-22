(function () {
  'use strict';

  const pageTitles = {
    overview: "Vue d'ensemble",
    analytics: 'Analytics',
    formateurs: 'Formateurs',
    apprenants: 'Apprenants',
    formations: 'Formations',
    academies: 'Academies',
    planning: 'Planning',
    revenus: 'Revenus',
    frais: 'Frais formateurs',
    factures: 'Factures',
    notifications: 'Notifications',
    parametres: 'Parametres',
  };

  function navigateTo(page) {
    document.querySelectorAll('.mf-admin-page').forEach((p) => p.classList.remove('is-active'));
    document.querySelectorAll('.sb-lk').forEach((l) => l.classList.remove('active'));

    const target = document.getElementById('page-' + page);
    if (target) {
      target.classList.add('is-active');
    }

    const link = document.querySelector('.sb-lk[data-page="' + page + '"]');
    if (link) {
      link.classList.add('active');
    }

    const title = document.getElementById('page-title');
    if (title) {
      title.textContent = pageTitles[page] || page;
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function bindSidebarNav() {
    document.querySelectorAll('.sb-lk[data-page]').forEach((link) => {
      link.addEventListener('click', () => navigateTo(link.dataset.page));
    });
  }

  function bindQuickNavLinks() {
    document.querySelectorAll('.js-nav-link[data-target-page]').forEach((link) => {
      link.addEventListener('click', (event) => {
        event.preventDefault();
        navigateTo(link.dataset.targetPage);
      });
    });
  }

  function bindFilters() {
    document.querySelectorAll('.filters').forEach((group) => {
      group.querySelectorAll('.flt').forEach((btn) => {
        btn.addEventListener('click', () => {
          group.querySelectorAll('.flt').forEach((b) => b.classList.remove('on'));
          btn.classList.add('on');
        });
      });
    });
  }

  function bindAlertClose() {
    document.querySelectorAll('.alert .close').forEach((btn) => {
      btn.addEventListener('click', () => {
        const alert = btn.closest('.alert');
        if (alert) {
          alert.style.display = 'none';
        }
      });
    });
  }

  function getActivePage() {
    return document.querySelector('.mf-admin-page.is-active') || document.getElementById('page-overview');
  }

  function clearSearchHighlights() {
    document.querySelectorAll('.mf-hit').forEach((el) => el.classList.remove('mf-hit'));
  }

  function runHeaderSearch() {
    const rawQuery = window.prompt('Recherche (formateur, apprenant, formation...)');
    if (!rawQuery) {
      return;
    }

    const query = rawQuery.trim().toLowerCase();
    if (!query) {
      return;
    }

    clearSearchHighlights();

    const selectors = [
      '.tbl-name',
      '.tbl-sub',
      '.fc-name',
      '.fc-meta',
      '.item-name',
      '.item-meta',
      '.act-text',
      '.notif-title',
      '.notif-desc',
      '.card-t',
      '.set-label',
      '.set-desc',
      '.status',
      'h1',
      'h2',
      'h3',
      'p',
      'td',
      'th',
    ].join(',');

    let match = null;
    document.querySelectorAll('.mf-admin-page').forEach((page) => {
      if (match) {
        return;
      }
      page.querySelectorAll(selectors).forEach((el) => {
        if (match) {
          return;
        }
        const text = (el.textContent || '').trim().toLowerCase();
        if (text && text.includes(query)) {
          match = {
            page: page.id.replace('page-', ''),
            element: el,
          };
        }
      });
    });

    if (!match) {
      window.alert('Aucun résultat pour : ' + rawQuery);
      return;
    }

    navigateTo(match.page);
    window.setTimeout(() => {
      match.element.classList.add('mf-hit');
      match.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 120);
  }

  function escapeCsvValue(value) {
    const normalized = String(value || '').replace(/\s+/g, ' ').trim();
    return '"' + normalized.replace(/"/g, '""') + '"';
  }

  function downloadCsv(filename, rows) {
    const csv = rows.map((row) => row.map(escapeCsvValue).join(';')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function exportActivePageCsv() {
    const page = getActivePage();
    if (!page) {
      return;
    }

    const pageName = page.id.replace('page-', '');
    const rows = [];
    const tables = page.querySelectorAll('table.tbl');

    if (tables.length) {
      tables.forEach((table, tableIndex) => {
        const headers = Array.from(table.querySelectorAll('thead th')).map((th) => (th.textContent || '').trim());
        if (headers.length) {
          rows.push(headers);
        }

        table.querySelectorAll('tbody tr').forEach((tr) => {
          const values = Array.from(tr.querySelectorAll('td')).map((td) => (td.textContent || '').trim());
          if (values.length) {
            rows.push(values);
          }
        });

        if (tableIndex < tables.length - 1) {
          rows.push(['']);
        }
      });
    } else {
      const fallbackItems = page.querySelectorAll('.item, .formation-card, .act, .notif');
      fallbackItems.forEach((item) => {
        const text = (item.textContent || '').replace(/\s+/g, ' ').trim();
        if (text) {
          rows.push([text]);
        }
      });
    }

    if (!rows.length) {
      window.alert('Aucune donnée exportable sur cet onglet.');
      return;
    }

    const date = new Date().toISOString().slice(0, 10);
    downloadCsv('mission-admin-' + pageName + '-' + date + '.csv', rows);
  }

  function bindHeaderActions() {
    document.querySelectorAll('.top-btn[data-action]').forEach((button) => {
      button.addEventListener('click', () => {
        const action = button.dataset.action;
        if (action === 'search') {
          runHeaderSearch();
          return;
        }
        if (action === 'notifications') {
          navigateTo('notifications');
          return;
        }
        if (action === 'export') {
          exportActivePageCsv();
        }
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    bindSidebarNav();
    bindQuickNavLinks();
    bindFilters();
    bindAlertClose();
    bindHeaderActions();
  });
})();
