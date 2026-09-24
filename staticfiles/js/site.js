/* ==========================================================================
   Public site JavaScript
   --------------------------------------------------------------------------
   Deliberately small: theme toggle, header border on scroll, the project
   gallery lightbox and a contact-form double-submit guard. The admin panel
   still uses main.js.
   ========================================================================== */

(function () {
    'use strict';

    // --- Theme (light / dark) ---
    // The initial theme is applied by the inline script in base.html's <head>
    // so the page never flashes the wrong colours. The 'dark_mode' key is the
    // same one the admin panel uses, so the choice carries across both.
    var root = document.documentElement;
    var toggle = document.getElementById('themeToggle');

    function isDark() {
        return root.getAttribute('data-bs-theme') === 'dark';
    }

    function applyTheme(dark) {
        root.setAttribute('data-bs-theme', dark ? 'dark' : 'light');
        // parallax.css / gaming-zone.css still key off this body class.
        document.body.classList.toggle('dark-mode', dark);
        if (toggle) {
            var icon = toggle.querySelector('i');
            if (icon) icon.className = dark ? 'fas fa-sun' : 'fas fa-moon';
            toggle.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
            toggle.setAttribute('title', dark ? 'Light theme' : 'Dark theme');
        }
    }

    applyTheme(isDark());

    if (toggle) {
        toggle.addEventListener('click', function () {
            var dark = !isDark();
            applyTheme(dark);
            try {
                localStorage.setItem('dark_mode', String(dark));
            } catch (e) {
                // Storage can be unavailable (private mode); the toggle still
                // works for this page view.
            }
        });
    }

    // --- Header: show a divider once the page is scrolled ---
    var header = document.getElementById('siteHeader');
    if (header) {
        var onScroll = function () {
            header.classList.toggle('is-scrolled', window.scrollY > 8);
        };
        onScroll();
        window.addEventListener('scroll', onScroll, { passive: true });
    }

    // --- Project gallery lightbox ---
    // Templates group items per project with data-fancybox="gallery-<pk>";
    // binding the bare attribute covers every group.
    if (typeof Fancybox !== 'undefined') {
        Fancybox.bind('[data-fancybox]', {});
    }

    // --- Contact form: prevent accidental double submission ---
    document.querySelectorAll('form[data-submit-once]').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                form.classList.add('was-validated');
                return;
            }
            var btn = form.querySelector('[type="submit"]');
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>Sending…';
            }
        });
    });
})();
