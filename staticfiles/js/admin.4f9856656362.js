/* ==========================================================================
   Admin panel JavaScript
   --------------------------------------------------------------------------
   Kept small on purpose: the phone-size navigation drawer and the light /
   dark theme toggle. Bootstrap's bundle handles dropdowns, modals and
   dismissible alerts. (The public creative design uses main.js; the admin
   no longer loads it.)
   ========================================================================== */

(function () {
    'use strict';

    // --- Theme (light / dark) ---
    // base.html applies the saved theme before paint. 'dark_mode' is the same
    // key the public site uses, so the choice carries across both.
    var root = document.documentElement;
    var themeButtons = document.querySelectorAll('[data-theme-toggle]');

    function isDark() {
        return root.getAttribute('data-bs-theme') === 'dark';
    }

    function renderThemeButtons() {
        var dark = isDark();
        themeButtons.forEach(function (btn) {
            var icon = btn.querySelector('i');
            var label = btn.querySelector('[data-theme-label]');
            if (icon) icon.className = dark ? 'fas fa-sun' : 'fas fa-moon';
            if (label) label.textContent = dark ? 'Light theme' : 'Dark theme';
            btn.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
        });
    }

    themeButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            var dark = !isDark();
            root.setAttribute('data-bs-theme', dark ? 'dark' : 'light');
            try {
                localStorage.setItem('dark_mode', String(dark));
            } catch (e) {
                // Storage may be unavailable; the toggle still works for this page.
            }
            renderThemeButtons();
        });
    });
    renderThemeButtons();

    // --- Navigation drawer on small screens ---
    var body = document.body;
    var sidebar = document.getElementById('adminSidebar');
    var openButton = document.getElementById('adminMenuButton');
    var closeButton = document.getElementById('adminMenuClose');
    var backdrop = document.getElementById('adminBackdrop');

    if (sidebar && openButton && backdrop) {
        var setOpen = function (open) {
            body.classList.toggle('sidebar-open', open);
            openButton.setAttribute('aria-expanded', String(open));
            backdrop.hidden = !open;
            if (open) {
                var first = sidebar.querySelector('a, button');
                if (first) first.focus();
            } else {
                openButton.focus();
            }
        };

        openButton.addEventListener('click', function () { setOpen(true); });
        if (closeButton) closeButton.addEventListener('click', function () { setOpen(false); });
        backdrop.addEventListener('click', function () { setOpen(false); });

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && body.classList.contains('sidebar-open')) setOpen(false);
        });

        window.addEventListener('resize', function () {
            if (window.innerWidth >= 992 && body.classList.contains('sidebar-open')) {
                body.classList.remove('sidebar-open');
                backdrop.hidden = true;
                openButton.setAttribute('aria-expanded', 'false');
            }
        });
    }
})();
