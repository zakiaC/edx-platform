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

  document.addEventListener('DOMContentLoaded', function () {
    bindSidebarNav();
    bindQuickNavLinks();
    bindFilters();
    bindAlertClose();
  });
})();
