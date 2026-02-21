(function () {
  "use strict";

  var BRAND_COPY = {
    login: {
      title: "Votre espace<br>de <em>formation</em><br>vous attend",
      subtitle:
        "Connectez-vous avec les identifiants reçus par email lors de votre inscription à la formation. Accédez à vos parcours, suivez votre progression et obtenez vos certifications.",
    },
    register: {
      title: "Créez votre<br>compte de<br><em>formation</em>",
      subtitle:
        "Inscrivez-vous pour accéder à votre espace apprenant, suivre vos cours et obtenir vos certifications.",
    },
    reset: {
      title: "Réinitialisez<br>votre mot de<br><em>passe</em>",
      subtitle:
        "Pas de panique. Entrez votre adresse email et nous vous enverrons un lien pour choisir un nouveau mot de passe.",
    },
    reset_sent: {
      title: "Vérifiez votre<br>boîte de<br><em>réception</em>",
      subtitle:
        "Un email vient de vous être envoyé. Cliquez sur le lien qu'il contient pour finaliser l'opération.",
    },
  };

  var lastResetEmail = "";

  function getMode() {
    if (document.querySelector("#login-form.mf-reset-sent-active .js-password-reset-success")) {
      return "reset_sent";
    }
    if (document.querySelector("#register-form.form-wrapper:not(.hidden)")) {
      return "register";
    }
    if (document.querySelector("#password-reset-form.form-wrapper:not(.hidden)")) {
      return "reset";
    }
    return "login";
  }

  function updateBrandPanel(mode) {
    var titleNode = document.getElementById("mf-brand-title");
    var subtitleNode = document.getElementById("mf-brand-subtitle");
    var copy = BRAND_COPY[mode] || BRAND_COPY.login;
    if (titleNode) {
      titleNode.innerHTML = copy.title;
    }
    if (subtitleNode) {
      subtitleNode.textContent = copy.subtitle;
    }
  }

  function updateBodyMode(mode) {
    var body = document.body;
    body.classList.remove("mode-login", "mode-register", "mode-password-reset", "mode-reset-sent");
    if (mode === "register") {
      body.classList.add("mode-register");
    } else if (mode === "reset") {
      body.classList.add("mode-password-reset");
    } else if (mode === "reset_sent") {
      body.classList.add("mode-reset-sent");
    } else {
      body.classList.add("mode-login");
    }
  }

  function setPlaceholders() {
    var placeholders = {
      "login-email": "votre@email.com",
      "login-password": "••••••••",
      "register-name": "Nom complet",
      "register-username": "Nom d'utilisateur public",
      "register-email": "votre@email.com",
      "register-password": "••••••••",
      "password-reset-email": "votre@email.com",
    };

    Object.keys(placeholders).forEach(function (id) {
      var input = document.getElementById(id);
      if (input) {
        input.setAttribute("placeholder", placeholders[id]);
      }
    });
  }

  function attachPasswordToggles() {
    var fields = document.querySelectorAll(
      "#login-and-registration-container .form-field input[type='password']"
    );

    fields.forEach(function (input) {
      if (input.dataset.mfToggleAttached === "1") {
        return;
      }

      var wrapper = input.closest(".form-field");
      if (!wrapper) {
        return;
      }

      var button = document.createElement("button");
      button.type = "button";
      button.className = "mf-toggle-pw";
      button.textContent = "Afficher";
      button.addEventListener("click", function () {
        if (input.type === "password") {
          input.type = "text";
          button.textContent = "Masquer";
        } else {
          input.type = "password";
          button.textContent = "Afficher";
        }
      });

      wrapper.appendChild(button);
      input.dataset.mfToggleAttached = "1";
    });
  }

  function rememberResetEmail() {
    var field = document.getElementById("password-reset-email");
    if (field) {
      lastResetEmail = field.value.trim();
    }
  }

  function applyResetSentLayout() {
    var loginRoot = document.getElementById("login-form");
    var successNode = document.querySelector("#login-form .js-password-reset-success");
    var emailPill;
    var backButton;

    if (!loginRoot) {
      return;
    }

    if (!successNode) {
      loginRoot.classList.remove("mf-reset-sent-active");
      return;
    }

    if (successNode.dataset.mfEnhanced !== "1") {
      successNode.dataset.mfEnhanced = "1";
      successNode.classList.add("mf-reset-sent-card");
      successNode.innerHTML =
        '<div class="mf-success-icon">✓</div>' +
        "<h2>Email envoyé !</h2>" +
        "<p>Nous avons envoyé un email à l'adresse suivante.<br>Cliquez sur le lien dans l'email pour continuer.</p>" +
        '<div class="mf-email-pill js-reset-email-value">votre@email.com</div>' +
        '<p class="mf-reset-help">Vous ne trouvez pas l\'email ? Vérifiez votre dossier spam ou courrier indésirable.</p>' +
        '<button type="button" class="btn-submit js-back-login"><span>Retour à la connexion</span></button>' +
        '<div class="form-bottom">Besoin d\'aide ? <a class="help-link" href="mailto:contact@missionformations.com">Contactez-nous</a></div>' +
        '<div class="form-footer"><a href="#">Mentions légales</a> · <a href="#">RGPD</a> · <a href="#">Aide</a><br>© 2026 Académie Mission Formations</div>';
    }

    loginRoot.classList.add("mf-reset-sent-active");

    emailPill = successNode.querySelector(".js-reset-email-value");
    if (emailPill) {
      emailPill.textContent = lastResetEmail || "votre@email.com";
    }

    backButton = successNode.querySelector(".js-back-login");
    if (backButton && backButton.dataset.mfBound !== "1") {
      backButton.dataset.mfBound = "1";
      backButton.addEventListener("click", function () {
        window.location.href = "/login";
      });
    }
  }

  function refreshUi() {
    applyResetSentLayout();
    updateBrandPanel(getMode());
    updateBodyMode(getMode());
    setPlaceholders();
    attachPasswordToggles();
  }

  function watchContainer() {
    var container = document.getElementById("login-and-registration-container");
    if (!container) {
      return;
    }

    var observer = new MutationObserver(function () {
      window.requestAnimationFrame(refreshUi);
    });

    observer.observe(container, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["class"],
    });
  }

  document.addEventListener("click", function (event) {
    if (event.target.closest(".js-reset")) {
      rememberResetEmail();
    }
    if (event.target.closest(".form-toggle")) {
      window.setTimeout(refreshUi, 50);
    }
  });

  document.addEventListener("submit", function (event) {
    if (event.target && event.target.id === "password-reset") {
      rememberResetEmail();
    }
  });

  document.addEventListener("DOMContentLoaded", function () {
    refreshUi();
    watchContainer();
  });
})();
