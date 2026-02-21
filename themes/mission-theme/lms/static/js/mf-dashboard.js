(function () {
  'use strict';

  var dashboard = window.MF_DASHBOARD || {};
  var courseProgressById = {};
  var fetchedCertificates = [];
  var ACTIVITY_STORAGE_KEY = 'mf_activity_tracker_v2';
  var ACTIVITY_ESTIMATED_MINUTES_PER_MODULE = 30;
  var ACTIVITY_WEEK_GOAL_MINUTES = 8 * 60;
  var ACTIVITY_DAY_NAMES = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];

  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }

  function qsa(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function numberOr(value, fallback) {
    var n = Number(value);
    return Number.isFinite(n) ? n : fallback;
  }

  function setText(sel, value) {
    var el = qs(sel);
    if (el) {
      el.textContent = value;
    }
  }

  function setupSidebarCertificatesDropdown() {
    var root = qs('#mf-sidebar-certs');
    var toggle = qs('#mf-sidebar-certs-toggle');
    if (!root || !toggle) {
      return;
    }

    function closeMenu() {
      root.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    }

    toggle.addEventListener('click', function () {
      var willOpen = !root.classList.contains('open');
      if (willOpen) {
        root.classList.add('open');
        toggle.setAttribute('aria-expanded', 'true');
      } else {
        closeMenu();
      }
    });

    document.addEventListener('click', function (event) {
      if (!root.contains(event.target)) {
        closeMenu();
      }
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        closeMenu();
      }
    });
  }

  function normalizeCourseId(value) {
    return (value || '').toString();
  }

  function getCertificateDateText(cert) {
    var date = cert.created_date ? new Date(cert.created_date) : null;
    return date && !Number.isNaN(date.getTime()) ? date.toLocaleDateString('fr-FR') : 'Date non disponible';
  }

  function buildSidebarCertificateItems() {
    var onlyObtained = dashboard.onlyObtainedMenu === true || dashboard.onlyObtainedMenu === 'true';
    var items = [];
    var certByCourseId = {};
    var seenCourseIds = {};

    if (onlyObtained) {
      fetchedCertificates.forEach(function (cert) {
        var certUrl = cert.download_url || cert.url || '#';
        if (!certUrl || certUrl === '#') {
          return;
        }
        items.push({
          title: cert.course_display_name || cert.course_key || cert.course_id || 'Certificat',
          status: 'obtenu',
          dateText: getCertificateDateText(cert),
          certUrl: certUrl
        });
      });
      return items;
    }

    fetchedCertificates.forEach(function (cert) {
      var certCourseId = normalizeCourseId(cert.course_key || cert.course_id);
      if (certCourseId) {
        certByCourseId[certCourseId] = cert;
      }
    });

    qsa('.ci[data-course-id]').forEach(function (card) {
      var courseId = normalizeCourseId(card.getAttribute('data-course-id'));
      if (!courseId) {
        return;
      }
      seenCourseIds[courseId] = true;

      var cert = certByCourseId[courseId];
      var courseNameEl = qs('.ci-n', card);
      var title = (courseNameEl && courseNameEl.textContent ? courseNameEl.textContent.trim() : '') || courseId;
      var progressPct = courseProgressById[courseId];
      var status = 'non_obtenu';

      if (cert) {
        status = 'obtenu';
      } else if (Number.isFinite(progressPct)) {
        status = progressPct > 0 && progressPct < 100 ? 'en_cours' : 'non_obtenu';
      } else {
        status = card.getAttribute('data-status') === 'active' ? 'en_cours' : 'non_obtenu';
      }

      items.push({
        title: title,
        status: status,
        dateText: cert ? getCertificateDateText(cert) : '',
        certUrl: cert ? (cert.download_url || cert.url || '#') : '#'
      });
    });

    fetchedCertificates.forEach(function (cert) {
      var courseId = normalizeCourseId(cert.course_key || cert.course_id);
      if (courseId && seenCourseIds[courseId]) {
        return;
      }

      items.push({
        title: cert.course_display_name || courseId || 'Certificat',
        status: 'obtenu',
        dateText: getCertificateDateText(cert),
        certUrl: cert.download_url || cert.url || '#'
      });
    });

    return items;
  }

  function renderSidebarCertificates() {
    var list = qs('#mf-sidebar-certs-list');
    if (!list) {
      return;
    }

    list.innerHTML = '';
    var items = buildSidebarCertificateItems();

    if (!items.length) {
      var empty = document.createElement('span');
      empty.className = 'sb-cert-empty';
      empty.textContent = 'Aucun certificat disponible.';
      list.appendChild(empty);
      return;
    }

    items.forEach(function (item) {
      var row = document.createElement('div');
      row.className = 'sb-cert-row';

      var head = document.createElement('div');
      head.className = 'sb-cert-head';

      var titleEl = document.createElement('span');
      titleEl.className = 'sb-cert-item-title';
      titleEl.textContent = item.title;

      var statusEl = document.createElement('span');
      statusEl.className = 'sb-cert-status ' + item.status;
      statusEl.textContent = item.status === 'obtenu' ? 'Obtenu' : (item.status === 'en_cours' ? 'En cours' : 'Non obtenu');

      head.appendChild(titleEl);
      head.appendChild(statusEl);
      row.appendChild(head);

      if (item.status === 'obtenu' && item.certUrl && item.certUrl !== '#') {
        var dateEl = document.createElement('span');
        dateEl.className = 'sb-cert-item-date';
        dateEl.textContent = 'Delivre le ' + item.dateText;
        row.appendChild(dateEl);

        var actions = document.createElement('div');
        actions.className = 'sb-cert-actions';

        var previewBtn = document.createElement('button');
        previewBtn.type = 'button';
        previewBtn.className = 'sb-cert-btn';
        previewBtn.textContent = 'Preview';
        previewBtn.addEventListener('click', function () {
          openCertificatePreview(item.certUrl, item.title);
        });

        var pdfLink = document.createElement('a');
        pdfLink.className = 'sb-cert-btn';
        pdfLink.href = item.certUrl;
        pdfLink.target = '_blank';
        pdfLink.rel = 'noopener';
        pdfLink.textContent = 'PDF';

        var linkedinLink = document.createElement('a');
        linkedinLink.className = 'sb-cert-btn';
        linkedinLink.href = 'https://www.linkedin.com/profile/add?startTask=CERTIFICATION_NAME&certUrl=' + encodeURIComponent(item.certUrl);
        linkedinLink.target = '_blank';
        linkedinLink.rel = 'noopener';
        linkedinLink.textContent = 'LinkedIn';

        var emailLink = document.createElement('a');
        emailLink.className = 'sb-cert-btn';
        emailLink.href = 'mailto:?subject=' + encodeURIComponent('Mon certificat Mission Formations') + '&body=' + encodeURIComponent('Bonjour,\n\nVoici mon certificat: ' + item.certUrl);
        emailLink.textContent = 'Email';

        actions.appendChild(previewBtn);
        actions.appendChild(pdfLink);
        actions.appendChild(linkedinLink);
        actions.appendChild(emailLink);
        row.appendChild(actions);
      }

      list.appendChild(row);
    });
  }

  function ensureCertificatePreviewModal() {
    if (qs('#mf-cert-preview-modal')) {
      return;
    }

    var modal = document.createElement('div');
    modal.id = 'mf-cert-preview-modal';
    modal.className = 'mf-cert-modal';
    modal.innerHTML = '' +
      '<div class="mf-cert-modal-dialog" role="dialog" aria-modal="true" aria-label="Preview certificat">' +
      '<div class="mf-cert-modal-head">' +
      '<strong id="mf-cert-modal-title">Certificat</strong>' +
      '<button type="button" class="mf-cert-modal-close" id="mf-cert-modal-close" aria-label="Fermer">x</button>' +
      '</div>' +
      '<div class="mf-cert-modal-body">' +
      '<iframe id="mf-cert-modal-frame" title="Certificat"></iframe>' +
      '</div>' +
      '</div>';
    document.body.appendChild(modal);

    var closeBtn = qs('#mf-cert-modal-close', modal);
    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        closeCertificatePreview();
      });
    }

    modal.addEventListener('click', function (event) {
      if (event.target === modal) {
        closeCertificatePreview();
      }
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        closeCertificatePreview();
      }
    });
  }

  function openCertificatePreview(url, title) {
    ensureCertificatePreviewModal();
    var modal = qs('#mf-cert-preview-modal');
    var frame = qs('#mf-cert-modal-frame');
    var titleEl = qs('#mf-cert-modal-title');
    if (!modal || !frame) {
      return;
    }
    if (titleEl) {
      titleEl.textContent = title || 'Certificat';
    }
    frame.src = url;
    modal.classList.add('open');
  }

  function closeCertificatePreview() {
    var modal = qs('#mf-cert-preview-modal');
    var frame = qs('#mf-cert-modal-frame');
    if (!modal || !modal.classList.contains('open')) {
      return;
    }
    modal.classList.remove('open');
    if (frame) {
      frame.src = 'about:blank';
    }
  }

  function formatHoursMinutes(totalMinutes) {
    var safeMinutes = Math.max(numberOr(totalMinutes, 0), 0);
    var hours = Math.floor(safeMinutes / 60);
    var minutes = safeMinutes % 60;
    var paddedMinutes = minutes < 10 ? '0' + minutes : String(minutes);
    return hours + 'h ' + paddedMinutes + 'min';
  }

  function getDayKey(date) {
    var y = date.getFullYear();
    var m = date.getMonth() + 1;
    var d = date.getDate();
    var mm = m < 10 ? '0' + m : String(m);
    var dd = d < 10 ? '0' + d : String(d);
    return y + '-' + mm + '-' + dd;
  }

  function parseDayKey(dayKey) {
    var parts = (dayKey || '').split('-');
    if (parts.length !== 3) {
      return null;
    }
    var year = Number(parts[0]);
    var month = Number(parts[1]);
    var day = Number(parts[2]);
    if (!Number.isFinite(year) || !Number.isFinite(month) || !Number.isFinite(day)) {
      return null;
    }
    return new Date(year, month - 1, day);
  }

  function getMonday(date) {
    var d = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    var day = (d.getDay() + 6) % 7;
    d.setDate(d.getDate() - day);
    return d;
  }

  function getDayDiff(a, b) {
    var d1 = new Date(a.getFullYear(), a.getMonth(), a.getDate());
    var d2 = new Date(b.getFullYear(), b.getMonth(), b.getDate());
    var msPerDay = 24 * 60 * 60 * 1000;
    return Math.floor((d1.getTime() - d2.getTime()) / msPerDay);
  }

  function loadActivityState() {
    var fallback = {
      lastTotalComplete: null,
      dailyModules: {}
    };
    try {
      var raw = window.localStorage.getItem(ACTIVITY_STORAGE_KEY);
      if (!raw) {
        return fallback;
      }
      var parsed = JSON.parse(raw);
      if (!parsed || typeof parsed !== 'object') {
        return fallback;
      }
      return {
        lastTotalComplete: Number.isFinite(parsed.lastTotalComplete) ? parsed.lastTotalComplete : null,
        dailyModules: parsed.dailyModules && typeof parsed.dailyModules === 'object' ? parsed.dailyModules : {}
      };
    } catch (e) {
      return fallback;
    }
  }

  function saveActivityState(state) {
    try {
      window.localStorage.setItem(ACTIVITY_STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      // Ignore storage failures (private mode/full quota).
    }
  }

  function pruneActivityState(state, today) {
    Object.keys(state.dailyModules || {}).forEach(function (key) {
      var asDate = parseDayKey(key);
      if (!asDate) {
        delete state.dailyModules[key];
        return;
      }
      if (getDayDiff(today, asDate) > 60) {
        delete state.dailyModules[key];
      }
    });
  }

  function renderActivityFromState(state, today) {
    var barsRoot = qs('#mf-activity-bars');
    var deltaEl = qs('#mf-activity-delta');
    var totalEl = qs('#mf-activity-total');
    var goalEl = qs('#mf-activity-goal');
    if (!barsRoot) {
      return;
    }

    var weekStart = getMonday(today);
    var currentMinutes = [];
    for (var i = 0; i < 7; i += 1) {
      var d = new Date(weekStart.getFullYear(), weekStart.getMonth(), weekStart.getDate());
      d.setDate(d.getDate() + i);
      var key = getDayKey(d);
      var dayModules = numberOr(state.dailyModules[key], 0);
      currentMinutes.push(Math.max(dayModules, 0) * ACTIVITY_ESTIMATED_MINUTES_PER_MODULE);
    }

    var previousWeekStart = new Date(weekStart.getFullYear(), weekStart.getMonth(), weekStart.getDate());
    previousWeekStart.setDate(previousWeekStart.getDate() - 7);
    var previousTotalMinutes = 0;
    for (var j = 0; j < 7; j += 1) {
      var pd = new Date(previousWeekStart.getFullYear(), previousWeekStart.getMonth(), previousWeekStart.getDate());
      pd.setDate(pd.getDate() + j);
      var pkey = getDayKey(pd);
      previousTotalMinutes += Math.max(numberOr(state.dailyModules[pkey], 0), 0) * ACTIVITY_ESTIMATED_MINUTES_PER_MODULE;
    }

    var currentTotalMinutes = currentMinutes.reduce(function (acc, value) {
      return acc + value;
    }, 0);

    var maxDayMinutes = currentMinutes.reduce(function (acc, value) {
      return value > acc ? value : acc;
    }, 0);

    barsRoot.innerHTML = '';
    currentMinutes.forEach(function (minutes, index) {
      var height = 0;
      if (maxDayMinutes > 0 && minutes > 0) {
        height = Math.max(Math.round((minutes / maxDayMinutes) * 100), 8);
      }

      var col = document.createElement('div');
      col.className = 'bw';

      var bar = document.createElement('div');
      bar.className = 'br';
      bar.style.height = height + '%';

      var label = document.createElement('div');
      label.className = 'bl-l';
      label.textContent = ACTIVITY_DAY_NAMES[index];

      col.appendChild(bar);
      col.appendChild(label);
      barsRoot.appendChild(col);
    });

    if (totalEl) {
      totalEl.textContent = formatHoursMinutes(currentTotalMinutes);
    }
    if (goalEl) {
      goalEl.textContent = (ACTIVITY_WEEK_GOAL_MINUTES / 60) + 'h/sem';
    }
    if (deltaEl) {
      var delta = 0;
      if (previousTotalMinutes > 0) {
        delta = Math.round(((currentTotalMinutes - previousTotalMinutes) / previousTotalMinutes) * 100);
      } else if (currentTotalMinutes > 0) {
        delta = 100;
      }
      deltaEl.textContent = (delta >= 0 ? '+' : '') + delta + '%';
      deltaEl.style.color = delta < 0 ? 'var(--rouge)' : 'var(--vert2)';
    }
  }

  function updateActivityWidget(totalCompleteModules) {
    var card = qs('#mf-activity-card');
    if (!card) {
      return;
    }

    var modules = Math.max(numberOr(totalCompleteModules, 0), 0);
    var today = new Date();
    var todayKey = getDayKey(today);
    var state = loadActivityState();

    if (!Number.isFinite(state.lastTotalComplete)) {
      state.lastTotalComplete = modules;
    }

    var deltaModules = modules - state.lastTotalComplete;
    if (deltaModules > 0) {
      state.dailyModules[todayKey] = Math.max(numberOr(state.dailyModules[todayKey], 0), 0) + deltaModules;
    }

    state.lastTotalComplete = modules;
    pruneActivityState(state, today);
    saveActivityState(state);
    renderActivityFromState(state, today);
  }

  function updatePlanningStatus(globalPct, totalModules) {
    var statusEl = qs('#mf-planning-status');
    var textEl = qs('#mf-planning-status-text');
    var iconEl = qs('#mf-planning-status-icon');
    if (!statusEl || !textEl) {
      return;
    }

    var text = 'Planning en attente';
    var color = 'var(--gris2)';

    if (totalModules > 0) {
      if (globalPct >= 70) {
        text = 'En avance sur le planning';
        color = 'var(--vert2)';
      } else if (globalPct >= 40) {
        text = 'Dans le planning';
        color = 'var(--bleu)';
      } else {
        text = 'En retard sur le planning';
        color = 'var(--rouge)';
      }
    }

    textEl.textContent = text;
    statusEl.style.color = color;
    if (iconEl) {
      iconEl.style.stroke = color;
    }
  }

  function updateHeroAndStats(globalPct, completeModules, totalModules) {
    var circumference = 251.3;
    var offset = circumference - ((globalPct / 100) * circumference);

    var heroRing = qs('#mf-hero-ring-fg');
    if (heroRing) {
      heroRing.setAttribute('stroke-dasharray', String(circumference));
      heroRing.setAttribute('stroke-dashoffset', String(offset));
    }

    setText('#mf-hero-ring-val', globalPct + '%');
    setText('#mf-hero-global-mini', globalPct + '%');
    setText('#mf-small-progress-txt', globalPct + '%');
    setText('#mf-stat-taux', globalPct + '%');
    setText('#mf-stat-formations', String(dashboard.totalEnrollments || qsa('.ci[data-course-id]').length));

    var remaining = Math.max(totalModules - completeModules, 0);
    setText('#mf-stat-modules', completeModules + '/' + totalModules);
    setText('#mf-stat-restant', remaining + 'h');
    setText('#mf-modules-summary', completeModules + ' modules sur ' + totalModules + ' complétés');

    var smallRing = qs('#mf-small-progress-ring');
    if (smallRing) {
      var c = 163.4;
      var o = c - ((globalPct / 100) * c);
      smallRing.setAttribute('stroke-dasharray', String(c));
      smallRing.setAttribute('stroke-dashoffset', String(o));
    }

    var subtitle = qs('#mf-hero-subtitle');
    if (subtitle) {
      subtitle.textContent =
        'Vous avez ' + (dashboard.totalEnrollments || qsa('.ci[data-course-id]').length) +
        ' formation(s) en cours et une progression globale de ' + globalPct + '%. Continuez.';
    }

    var heroDesc = qs('#mf-hero-global-desc');
    if (heroDesc) {
      heroDesc.textContent = (dashboard.totalEnrollments || qsa('.ci[data-course-id]').length) + ' formation(s) · ' + totalModules + ' modules';
    }

    updatePlanningStatus(globalPct, totalModules);
  }

  function applyFilters() {
    qsa('.flt').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var group = btn.closest('.filters') || document;
        qsa('.flt', group).forEach(function (b) {
          b.classList.remove('on');
        });
        btn.classList.add('on');

        var filter = btn.getAttribute('data-filter') || 'all';
        qsa('.ci[data-course-id]').forEach(function (card) {
          var status = card.getAttribute('data-status');
          var mode = card.getAttribute('data-mode') || 'distanciel';
          var visible = true;

          if (filter === 'active' || filter === 'done') {
            visible = status === filter;
          } else if (filter === 'presentiel' || filter === 'distanciel') {
            visible = mode === filter;
          }

          card.style.display = visible ? '' : 'none';
        });
      });
    });
  }

  function setupCourseCardsNavigation() {
    qsa('.ci[data-course-url]').forEach(function (card) {
      var courseUrl = card.getAttribute('data-course-url');
      if (!courseUrl) {
        return;
      }

      card.setAttribute('role', 'link');
      card.setAttribute('tabindex', '0');

      function isInteractiveTarget(target) {
        return Boolean(target && target.closest('a,button,input,select,textarea,label'));
      }

      card.addEventListener('click', function (event) {
        if (isInteractiveTarget(event.target)) {
          return;
        }
        window.location.href = courseUrl;
      });

      card.addEventListener('keydown', function (event) {
        if (event.key !== 'Enter' && event.key !== ' ') {
          return;
        }
        if (isInteractiveTarget(event.target) && event.target !== card) {
          return;
        }
        event.preventDefault();
        window.location.href = courseUrl;
      });
    });
  }

  function loadProgress() {
    var cards = qsa('.ci[data-course-id]');
    if (!cards.length) {
      updateHeroAndStats(0, 0, 0);
      updateActivityWidget(0);
      return;
    }

    var csrfToken = dashboard.csrfToken || '';
    var headers = {
      'Content-Type': 'application/json'
    };
    if (csrfToken) {
      headers['X-CSRFToken'] = csrfToken;
    }

    var totalComplete = 0;
    var totalModules = 0;

    var sequence = Promise.resolve();

    cards.forEach(function (card) {
      sequence = sequence.then(function () {
        var courseId = card.getAttribute('data-course-id');
        if (!courseId) {
          return null;
        }

        var url = '/api/course_home/progress/' + encodeURIComponent(courseId);

        return fetch(url, {
          method: 'GET',
          headers: headers,
          credentials: 'same-origin'
        }).then(function (res) {
          if (!res.ok) {
            throw new Error('HTTP ' + res.status);
          }
          return res.json();
        }).then(function (data) {
          var summary = data && data.completion_summary ? data.completion_summary : {};
          var complete = numberOr(summary.complete_count, 0);
          var total = Math.max(numberOr(summary.total_count, 0), 1);
          var pct = Math.round((complete / total) * 100);
          courseProgressById[courseId] = pct;

          totalComplete += complete;
          totalModules += total;

          var bar = qs('.pf', card);
          var pctEl = qs('.pct', card);
          var lblEl = qs('.lbl', card);

          if (bar) {
            bar.style.width = pct + '%';
          }
          if (pctEl) {
            pctEl.textContent = pct + '%';
          }
          if (lblEl) {
            lblEl.textContent = complete + '/' + total + ' modules';
          }

          if (pct >= 100) {
            card.setAttribute('data-status', 'done');
          } else if (!card.getAttribute('data-status')) {
            card.setAttribute('data-status', 'active');
          }
        }).catch(function () {
          delete courseProgressById[courseId];
          var lbl = qs('.lbl', card);
          if (lbl) {
            lbl.textContent = 'Progression indisponible';
          }
        });
      });
    });

    sequence.finally(function () {
      var computedPct = totalModules > 0 ? Math.round((totalComplete / totalModules) * 100) : 0;
      updateHeroAndStats(computedPct, totalComplete, totalModules);
      updateActivityWidget(totalComplete);
      renderSidebarCertificates();
    });
  }

  function loadCertificates() {
    if (!dashboard.username) {
      return;
    }

    var target = qs('#mf-certificates-list');
    if (!target) {
      return;
    }

    fetch('/api/certificates/v0/certificates/' + encodeURIComponent(dashboard.username), {
      method: 'GET',
      credentials: 'same-origin'
    }).then(function (res) {
      if (!res.ok) {
        throw new Error('HTTP ' + res.status);
      }
      return res.json();
    }).then(function (payload) {
      var certs = Array.isArray(payload) ? payload : (payload && payload.results ? payload.results : []);
      fetchedCertificates = certs;
      renderSidebarCertificates();
      if (!certs.length) {
        return;
      }

      var html = '';
      certs.forEach(function (cert) {
        var title = cert.course_display_name || cert.course_key || 'Certificat';
        var date = cert.created_date ? new Date(cert.created_date) : null;
        var dateText = date && !Number.isNaN(date.getTime()) ? date.toLocaleDateString('fr-FR') : 'Date non disponible';
        var downloadUrl = cert.download_url || cert.url || '#';

        html += '<div class="crt">' +
          '<div class="crt-i"><svg class="ic" viewBox="0 0 24 24" style="stroke:#fff"><circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline></svg></div>' +
          '<div class="crt-inf">' +
          '<div class="crt-n">' + title + '</div>' +
          '<div class="crt-dt">Délivré le ' + dateText + '</div>' +
          '</div>' +
          '<div class="crt-acts">' +
          '<a class="crt-btn" href="' + downloadUrl + '" target="_blank" rel="noopener">PDF</a>' +
          '<button class="crt-btn linkedin" type="button" data-cert-url="' + downloadUrl + '">LinkedIn</button>' +
          '</div>' +
          '</div>';
      });

      target.innerHTML = html;

      qsa('.crt-btn.linkedin', target).forEach(function (btn) {
        btn.addEventListener('click', function () {
          var certUrl = btn.getAttribute('data-cert-url') || '';
          var liUrl = 'https://www.linkedin.com/profile/add?startTask=CERTIFICATION_NAME&certUrl=' + encodeURIComponent(certUrl);
          window.open(liUrl, '_blank', 'noopener');
        });
      });
    }).catch(function () {
      fetchedCertificates = [];
      renderSidebarCertificates();
      // Keep static fallback block already rendered in template.
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    setupSidebarCertificatesDropdown();
    setupCourseCardsNavigation();
    ensureCertificatePreviewModal();
    renderSidebarCertificates();
    applyFilters();
    loadProgress();
    loadCertificates();
  });
})();
